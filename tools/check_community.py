"""Checks community.json, the community plugin list: what the pull request that adds a plugin or
a version must pass before the maintainer merges it. Run by .github/workflows/community.yml; by
hand from the repository's folder:

    pip install dnfile==0.18.0
    python tools/check_community.py [--base old-community.json] [--root folder]

With --base (the list on main), versions already listed must keep their tag and SHA-256, and what
the pull request adds is summarised for the maintainer ($GITHUB_STEP_SUMMARY in Actions). Reads
GitHub's API, with $GITHUB_TOKEN when set. Exits 1 when a check fails.

It checks what can be checked without reading the source: the repository is public and its
licence is one of LICENCES, each listed version is a release of that repository whose file has
the listed SHA-256 and is a .NET assembly with a public type Plugin whose assembly version is the
listed version, the file was built by GitHub Actions from the commit of that version's tag (a
build provenance attestation, verified with `gh attestation verify`, so gh must be installed),
and the source of each version can be downloaded. It does not review the code: community plugins
are listed as not reviewed.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

# The licences a community plugin may have (SPDX ids as GitHub reports them). Permissive ones, the
# weak copylefts and the GPL; never AGPL or a licence not named here (the user, 2026-11-28: "OSI
# 太宽泛"). The mirror keeps each listed version's source beside its file, so a GPL plugin's
# source is offered wherever its file is.
LICENCES = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD", "Unlicense",
    "MPL-2.0", "LGPL-2.1", "LGPL-3.0", "GPL-2.0", "GPL-3.0",
}
NAME = re.compile(r"^HD2QD\.[A-Za-z0-9_-]+\.dll$", re.I)
VERSION = re.compile(r"^\d+\.\d+\.\d+$")
API = 2
FILE_MAX = 25 * 1024 * 1024          # what one file of the Cloudflare mirror may be
TEXT_MAX = {"title": 60, "summary": 400}
REQUIRED = ("file", "title", "summary", "author", "repository", "license", "api", "versions")

# Each version is built by GitHub Actions, on a runner GitHub hosts, from the commit its tag names,
# and carries a build provenance attestation (actions/attest-build-provenance): then the file the
# list offers is the one the tag's source makes, not a file built elsewhere (the user, 2026-11-29). The versions
# listed before the rule are named here; this set only gets shorter.
BEFORE_PROVENANCE = {("hd2qd.bilimusic.dll", "1.3.11")}

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def get(url, binary=False, method="GET"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "hd2qd-plugins-check"})
    if url.startswith("https://api.github.com/"):
        req.add_header("Accept", "application/vnd.github+json")
        if os.environ.get("GITHUB_TOKEN"):
            req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read() if method == "GET" else b""
    if method != "GET":
        return None
    return data if binary else json.loads(data.decode("utf-8"))


def vkey(v):
    return tuple(int(x) for x in v.split("."))


def inspect(data):
    """The assembly's version (three numbers) and whether it has a public type named Plugin, as
    the manager looks for it; None when the file is not a .NET assembly."""
    import dnfile
    pe = dnfile.dnPE(data=data)
    try:
        if pe.net is None or pe.net.mdtables is None or not pe.net.mdtables.Assembly:
            return None
        a = pe.net.mdtables.Assembly.rows[0]
        version = "%d.%d.%d" % (a.MajorVersion, a.MinorVersion, a.BuildNumber)
        plugin = False
        for t in pe.net.mdtables.TypeDef.rows if pe.net.mdtables.TypeDef else []:
            # public and not nested (tdPublic), as the manager's IsPublic
            if str(t.TypeName) == "Plugin" and getattr(t.Flags, "tdPublic", False):
                plugin = True
        return version, plugin
    finally:
        pe.close()


class Check:
    def __init__(self):
        self.errors, self.notes, self.rows = [], [], []

    def fail(self, where, what):
        self.errors.append("%s: %s" % (where, what))

    def note(self, where, what):
        self.notes.append("%s: %s" % (where, what))


def check_entry(c, p, base_entry):
    f = p.get("file") or "(no file)"
    for k in REQUIRED:
        if k not in p:
            c.fail(f, "missing \"%s\"" % k)
    if c.errors and any(e.startswith(f + ": missing") for e in c.errors):
        return
    if not NAME.match(p["file"]):
        c.fail(f, "the file must be named HD2QD.<name>.dll")
    for k, n in TEXT_MAX.items():
        if not isinstance(p[k], str) or not p[k].strip():
            c.fail(f, "\"%s\" is empty" % k)
        elif len(p[k]) > n:
            c.fail(f, "\"%s\" is %d characters, at most %d" % (k, len(p[k]), n))
    if p["api"] != API:
        c.fail(f, "\"api\" must be %d" % API)
    if p["license"] not in LICENCES:
        c.fail(f, "licence %s is not accepted; accepted: %s" % (p["license"], ", ".join(sorted(LICENCES))))
    if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", p["repository"]):
        c.fail(f, "\"repository\" must be owner/name of a GitHub repository")
        return
    if base_entry and base_entry.get("repository") != p["repository"]:
        c.note(f, "the repository changed from %s to %s" % (base_entry.get("repository"), p["repository"]))

    try:
        repo = get("https://api.github.com/repos/" + p["repository"])
    except urllib.error.HTTPError as e:
        c.fail(f, "repository %s cannot be read (%d): it must be public" % (p["repository"], e.code))
        return
    if repo.get("private"):
        c.fail(f, "repository %s is private" % p["repository"])
    spdx = (repo.get("license") or {}).get("spdx_id")
    if spdx != p["license"]:
        c.fail(f, "GitHub reads the repository's licence as %s, the list says %s (a LICENSE file GitHub recognises is needed)"
               % (spdx or "none", p["license"]))

    versions = p["versions"]
    if not isinstance(versions, list) or not versions:
        c.fail(f, "\"versions\" lists no version")
        return
    seen = set()
    old = {v.get("version"): v for v in (base_entry or {}).get("versions", [])}
    for v in versions:
        w = "%s %s" % (f, v.get("version"))
        if not all(isinstance(v.get(k), str) for k in ("version", "tag", "sha256")):
            c.fail(w, "each version is {version, tag, sha256}")
            continue
        if not VERSION.match(v["version"]):
            c.fail(w, "the version must be three numbers, as the assembly's")
            continue
        if v["version"] in seen:
            c.fail(w, "listed twice")
        seen.add(v["version"])
        if v["version"] in old:
            o = old[v["version"]]
            if o.get("tag") != v["tag"] or o.get("sha256", "").lower() != v["sha256"].lower():
                c.fail(w, "a version already listed cannot change its tag or file; release a new version")
            continue                        # checked when it was added
        check_version(c, p, v, w)

    if base_entry is None:
        c.rows.append((p, None, max(versions, key=lambda v: vkey(v["version"]) if VERSION.match(v.get("version", "")) else (0,))))
    else:
        new = [v for v in versions if v.get("version") not in old]
        if new:
            prev = max(old.values(), key=lambda v: vkey(v["version"])) if old else None
            c.rows.append((p, prev, max(new, key=lambda v: vkey(v["version"]) if VERSION.match(v.get("version", "")) else (0,))))


def check_version(c, p, v, w):
    asset = p.get("asset") or p["file"]
    try:
        rel = get("https://api.github.com/repos/%s/releases/tags/%s" % (p["repository"], urllib.request.quote(v["tag"], safe="")))
    except urllib.error.HTTPError as e:
        c.fail(w, "no release with tag %s (%d)" % (v["tag"], e.code))
        return
    if rel.get("draft") or rel.get("prerelease"):
        c.fail(w, "release %s is a draft or a pre-release" % v["tag"])
    a = next((x for x in rel.get("assets") or [] if x["name"] == asset), None)
    if a is None:
        c.fail(w, "release %s has no file %s" % (v["tag"], asset))
        return
    if a["size"] > FILE_MAX:
        c.fail(w, "%s is %.1f MB, at most %d MB" % (asset, a["size"] / 1048576, FILE_MAX // 1048576))
        return
    data = get(a["browser_download_url"], binary=True)
    sha = hashlib.sha256(data).hexdigest()
    if sha != v["sha256"].lower():
        c.fail(w, "the release's %s has SHA-256 %s, the list says %s" % (asset, sha, v["sha256"]))
        return
    got = inspect(data)
    if got is None:
        c.fail(w, "%s is not a .NET assembly" % asset)
        return
    version, plugin = got
    if not plugin:
        c.fail(w, "%s has no public type named Plugin" % asset)
    if version != v["version"]:
        c.fail(w, "the assembly's version is %s, the list says %s" % (version, v["version"]))
    if (p["file"].lower(), v["version"]) not in BEFORE_PROVENANCE:
        why = provenance(p["repository"], v["tag"], data)
        if why:
            c.fail(w, "%s was not shown to be built by GitHub Actions from the commit of tag %s: %s (README, Requirements 2)"
                   % (asset, v["tag"], why))
    # the source of this version: what the mirror keeps beside the file
    try:
        get("https://api.github.com/repos/%s/zipball/%s" % (p["repository"], urllib.request.quote(v["tag"], safe="")), method="HEAD")
    except urllib.error.HTTPError as e:
        c.fail(w, "the source at tag %s cannot be downloaded (%d)" % (v["tag"], e.code))


def provenance(repo, tag, data):
    """None when the file carries a build provenance attestation that GitHub signed for a workflow
    run of repo, on a runner GitHub hosts, at the commit tag names; otherwise why not."""
    try:
        commit = get("https://api.github.com/repos/%s/commits/%s" % (repo, urllib.request.quote(tag, safe="")))["sha"]
    except urllib.error.HTTPError as e:
        return "the commit of tag %s cannot be read (%d)" % (tag, e.code)
    exe = shutil.which("gh")
    if not exe:
        return "gh (GitHub CLI) is needed to verify the attestation and is not installed here"
    env = dict(os.environ)
    if env.get("GITHUB_TOKEN") and not env.get("GH_TOKEN"):
        env["GH_TOKEN"] = env["GITHUB_TOKEN"]
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "file.dll")
        with open(path, "wb") as f:
            f.write(data)
        try:
            # the commit, not the ref: a release workflow may run on a branch at the tag's commit
            r = subprocess.run([exe, "attestation", "verify", path, "--repo", repo,
                                "--source-digest", commit, "--deny-self-hosted-runners"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=300)
        except subprocess.TimeoutExpired:
            return "gh attestation verify did not answer in 5 minutes"
    if r.returncode == 0:
        return None
    text = r.stderr + "\n" + r.stdout
    if "HTTP 404" in text or "no attestations found" in text:
        return "the file has no build provenance attestation in %s (actions/attest-build-provenance)" % repo
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    return " / ".join(lines[-3:]) or "gh attestation verify failed (%d)" % r.returncode


def check_locales(c, files):
    d = os.path.join(ROOT, "locales")
    for n in sorted(os.listdir(d)):
        if not n.endswith(".json"):
            continue
        try:
            loc = json.load(open(os.path.join(d, n), encoding="utf-8"))
        except ValueError as e:
            c.fail("locales/" + n, "not JSON: %s" % e)
            continue
        for f, t in loc.items():
            if f.lower() not in files:
                c.fail("locales/" + n, "%s is in neither list" % f)
            elif not isinstance(t, dict) or set(t) - {"title", "summary"}:
                c.fail("locales/%s %s" % (n, f), "only \"title\" and \"summary\" are translated")
            else:
                for k, m in TEXT_MAX.items():
                    if len(t.get(k) or "") > m:
                        c.fail("locales/%s %s" % (n, f), "\"%s\" is over %d characters" % (k, m))


def summary(c):
    lines = ["## Community list", ""]
    if c.errors:
        lines += ["**%d check(s) failed.**" % len(c.errors), ""] + ["- " + e for e in c.errors] + [""]
    else:
        lines += ["Every check passed. Nothing here reviews the code: read the changes below before merging.", ""]
    if c.notes:
        lines += ["Look at:", ""] + ["- " + n for n in c.notes] + [""]
    if c.rows:
        lines += ["| Plugin | Version | Licence | Source | Changes |", "|---|---|---|---|---|"]
        for p, prev, v in c.rows:
            r = p["repository"]
            src = "[%s](https://github.com/%s/tree/%s)" % (v["tag"], r, v["tag"])
            ch = ("[%s...%s](https://github.com/%s/compare/%s...%s)" % (prev["tag"], v["tag"], r, prev["tag"], v["tag"])
                  if prev else "new plugin")
            lines.append("| %s `%s` | %s | %s | %s | %s |" % (p["title"], p["file"], v["version"], p["license"], src, ch))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="community.json as it is on main")
    ap.add_argument("--root", help="the repository's folder (default: this script's parent)")
    a = ap.parse_args()
    global ROOT
    ROOT = a.root or ROOT
    c = Check()
    try:
        listed = json.load(open(os.path.join(ROOT, "community.json"), encoding="utf-8"))
    except ValueError as e:
        print("community.json is not JSON: %s" % e)
        return 1
    base = {}
    if a.base and os.path.exists(a.base) and os.path.getsize(a.base) > 0:
        base = {p.get("file", "").lower(): p for p in json.load(open(a.base, encoding="utf-8")).get("plugins", [])}
    official = {p["file"].lower() for p in json.load(open(os.path.join(ROOT, "plugins.json"), encoding="utf-8"))["plugins"]}
    if listed.get("format") != 1 or not isinstance(listed.get("plugins"), list):
        c.fail("community.json", "must be {\"format\": 1, \"plugins\": [...]}")
    else:
        files = set()
        for p in listed["plugins"]:
            f = (p.get("file") or "").lower()
            if f in official:
                c.fail(p.get("file"), "an official plugin has this file name")
            if f in files:
                c.fail(p.get("file"), "listed twice")
            files.add(f)
            check_entry(c, p, base.get(f))
        for f in set(base) - files:
            c.note(base[f].get("file"), "removed from the list")
        check_locales(c, files | official)
    text = summary(c)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as s:
            s.write(text)
    return 1 if c.errors else 0


if __name__ == "__main__":
    sys.exit(main())
