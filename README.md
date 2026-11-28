# HD2 Mod Quick Deploy plugins

The lists of plugins for [HD2 Mod Quick Deploy](https://github.com/pat-pat-patrick/hd2-mod-cli),
official and community, and the documentation for writing one. This repository holds no plugin
itself: each plugin is built and released in its own repository, and
[`plugins.json`](plugins.json) (official) and [`community.json`](community.json) (community, not
reviewed) name them.

## Official plugins

| Plugin | File | Version | Repository |
|---|---|---|---|
| HD2 Mod Console: each mod's settings, the enabled mods first | `HD2QD.Settings.dll` | [1.20.1](https://github.com/pat-pat-patrick/hd2-mod-setting-gui/releases/tag/v1.20.1) | [hd2-mod-setting-gui](https://github.com/pat-pat-patrick/hd2-mod-setting-gui) |
| Asset check: models and textures against the game's, and video memory | `HD2QD.AssetCheck.dll` | [1.4.2](https://github.com/pat-pat-patrick/hd2qd-asset-check/releases/tag/v1.4.2) | [hd2qd-asset-check](https://github.com/pat-pat-patrick/hd2qd-asset-check) |
| Mod repair: mods a game update broke — models that no longer load, sound mods that leave parts of the game silent, subtitle mods that miss the game's new lines (sound banks and subtitles by [x402](https://github.com/x402); the sound bank repair method comes from Sound Restoration Studio (音效维修台) by [40Hour](https://space.bilibili.com/157681854)) | `HD2QD.Repatch.dll` | [1.2.1](https://github.com/pat-pat-patrick/hd2qd-repatch/releases/tag/v1.2.1) | [hd2qd-repatch](https://github.com/pat-pat-patrick/hd2qd-repatch) |
| Member licenses: sign-in for mods available only to their author's members, and their member content (code, and large data such as voice recordings), kept encrypted and unlocked while the game runs | `HD2QD.License.dll` | [1.13.0](https://github.com/pat-pat-patrick/hd2-mod-license/releases/tag/plugin-v1.13.0) | [hd2-mod-license](https://github.com/pat-pat-patrick/hd2-mod-license) |
| Resource names: HD2SDK's resource and game archive name lists, downloaded from its repository, so conflicts and the asset check name resources (manager 0.16.0 or later) | `HD2QD.ResourceNames.dll` | [1.1.1](https://github.com/pat-pat-patrick/hd2qd-resource-names/releases/tag/v1.1.1) | [hd2qd-resource-names](https://github.com/pat-pat-patrick/hd2qd-resource-names) |
| Speed Dial for Liberty: one-key stratagem calls. You press one key, and the plugin enters the stratagem code with your own stratagem keys. Requires the mod Speed Dial for Liberty (v0.24.0 or later), enabled, and the manager running while you play | `HD2QD.SpeedDial.dll` | [1.6.2](https://github.com/pat-pat-patrick/hd2qd-speed-dial/releases/tag/v1.6.2) | [hd2qd-speed-dial](https://github.com/pat-pat-patrick/hd2qd-speed-dial) |
| HellForge: launches HellForge, the offline Helldivers 2, and makes it a deploy target of the manager: the library's mods converted for HellForge's game version, sessions, a profile editor, settings, lobbies, logs and licensed mods (deploying the library's mods needs manager 0.20.0 or later) | `HD2QD.HellForge.dll` | [0.15.0](https://github.com/pat-pat-patrick/hd2qd-hellforge/releases/tag/v0.15.0) | [hd2qd-hellforge](https://github.com/pat-pat-patrick/hd2qd-hellforge) |

They need HD2 Mod Quick Deploy 0.15.0 or later (plugin Api 2). None is installed by default.
Official plugins are the maintainer's own; plugins by other authors are listed as
[community plugins](#community-plugins), and any plugin can still be added from its file.

## Adding a plugin

1. In HD2 Mod Quick Deploy, open the Plugins page (the jigsaw piece beside the gear).
2. A listed plugin: on the **Plugin store** tab, find it by searching or with the filters (All,
   Official, Community), select it and choose **Download and add**. The manager downloads the
   newest release named in [`plugins.json`](plugins.json) (official) or
   [`community.json`](community.json) (community) and adds it only if its SHA-256 matches. A
   community plugin has not been reviewed: you confirm that you trust its author first.
3. Any other plugin: choose **Add plugin…** and select its `HD2QD.<name>.dll`, or drop the file on
   the page.
4. Confirm. A plugin runs with the manager's permissions: add only plugins from a source you trust.

**Remove** on a plugin's card deletes it again. On the command line: `hd2qd plugins`,
`hd2qd plugin-add <name or file>` (a name downloads the official plugin), `hd2qd plugin-remove <name>`.

## `plugins.json`

The manager reads this file from the `main` branch of this repository and keeps a copy in its
settings folder, so a plugin added here shows in every copy of the manager without a new release.

| Field | Meaning |
|---|---|
| `file` | The plugin's file name, `HD2QD.<name>.dll`. |
| `title`, `summary` | What the list shows, in English. Translations are in `locales/` (below). |
| `author`, `repository` | Who makes it, and the GitHub repository whose releases carry it. |
| `asset` | The release asset to download. |
| `api` | The contract version it speaks. |
| `license` | The plugin's licence as an SPDX identifier (`MIT`, `Apache-2.0`, ...). For people reading the list; the manager does not use it. |
| `wanted_by_file` | Optional: the manager marks the mods that ship this file as needing the plugin. |
| `button` | Optional: `true` gives the plugin a button in the manager's title bar, drawn with its own `app.ico`. Only a plugin listed here, whose installed file matches one of its `versions`, can have one. |
| `versions` | Each released version: `{version, tag, sha256}`. The manager downloads the newest and checks it against `sha256`. |

## Community plugins

Any author can list a plugin here, so that players find it in the manager: on the Plugins page's
**Plugin store** tab, marked Community, with **Download and add**. Community plugins are not reviewed. The manager
says so beside each one and asks the player before adding one; a community plugin never gets a
button in the manager's title bar. The list is [`community.json`](community.json), in the same
shape as `plugins.json` (without `button`). Quick Deploy shows it from version 0.26.0; earlier
versions do not read it.

### Requirements

1. **Public source.** The plugin's repository is public on GitHub, and GitHub recognises its
   `LICENSE` file as one of these licences (SPDX): `MIT`, `Apache-2.0`, `BSD-2-Clause`,
   `BSD-3-Clause`, `ISC`, `0BSD`, `Unlicense`, `MPL-2.0`, `LGPL-2.1`, `LGPL-3.0`, `GPL-2.0`,
   `GPL-3.0`. Other licences, including `AGPL-3.0` and closed source, are not listed.
2. **Built and released on GitHub.** Each version is a release (not a draft or pre-release) of
   that repository, with the DLL attached, at most 25 MB. The DLL is built by GitHub Actions on a
   runner GitHub hosts, from the commit the release's tag names, and carries a build provenance
   attestation ([`actions/attest-build-provenance`](https://github.com/actions/attest-build-provenance)).
   This shows that the file players download is the one the published source makes. A DLL built
   on your own computer or on a self-hosted runner is not listed. [`example/release.yml`](example/release.yml)
   is a workflow that does all of this when you push a tag. The manager downloads only from GitHub
   and from this list's mirror on Cloudflare; nothing is listed from other hosts.
3. **A plugin of this manager.** The file is `HD2QD.<name>.dll`, a name no official plugin uses, with
   a public type `Plugin` and `Api = 2` ([docs/plugin-authors.md](docs/plugin-authors.md)). Its
   assembly version is the version listed.
4. **Short texts.** `title` at most 60 characters, `summary` at most 400, in English. Translations
   go in `locales/` (below), in the same pull request.

Requirement 2's build by GitHub Actions applies from 2026-11-29: versions listed before then stay
listed, and every version added after it must meet it.

### Listing a plugin or a new version

1. Publish the release in your repository by pushing its tag, so that your release workflow builds,
   attests and attaches the DLL.
2. Open a pull request against `main` that adds your entry to `community.json`, or adds
   `{version, tag, sha256}` to your entry's `versions`. `sha256` is the SHA-256 of the attached
   file as GitHub serves it.
3. The pull request's check (`tools/check_community.py`) reads your repository and release:
   licence, tag, SHA-256, that the file is a .NET assembly with a public `Plugin`, its version,
   the file's build provenance attestation (`gh attestation verify`), and that the source of the
   tag can be downloaded. A version already listed cannot change.
4. The maintainer merges the pull request once the check passes. From then on, every copy of the
   manager offers the version, and players who added an earlier one are offered the update.

The mirror keeps the source archive of each listed version beside its file, so the code of
everything the list offers stays readable even if a repository is deleted. A plugin can be
removed from the list at any time, by its author's pull request or by the maintainer.

## Maintaining the list

This section is for the maintainer of this repository. No one else can add a plugin to the list or a version to a plugin: the manager reads the list
only from this repository's `main`, and installs an official plugin only when its file matches a
SHA-256 written here. Suggestions are welcome as issues or pull requests.

To release a new version of an official plugin:

1. Build it with its `build.bat`, which signs the DLL with the maintainer's key
   (`hd2-mod-cli/tools/sign_plugin.py`; the key is kept outside every repository). Quick Deploy
   0.26.0 and later show a signed build as an official plugin whatever its version, listed here or
   not; earlier versions know an official plugin only by the SHA-256 written here.
2. Publish a release in the plugin's repository with the DLL attached under the name in `asset`.
3. Add `{version, tag, sha256}` to the plugin's `versions` here: the release's tag, and the SHA-256
   of the attached file as GitHub serves it.
4. Push to `main`. Every copy of the manager offers the new version from then on; the manager
   itself needs no release.

Keep the format readable by the managers already released: add fields, never rename or remove one.

## Translations

`plugins.json` and `community.json` hold English only. Each language has one file of its own,
`locales/<language>.json`, named by its language tag (`zh-CN`, `de`, `pt-BR`, ...): for each plugin
file, its `title` and `summary` in that language. The manager reads the file of the language it
shows; a plugin or a field missing there is shown in English. Adding a language is adding one
file; nothing else changes.

```json
{
  "HD2QD.Repatch.dll": { "title": "MOD 修复", "summary": "..." }
}
```

## Writing a plugin

See [docs/plugin-authors.md](docs/plugin-authors.md) ([中文](docs/plugin-authors.zh-CN.md)) and
the complete example in [example/](example).

---

# HD2 Mod Quick Deploy 插件

[HD2 Mod Quick Deploy](https://github.com/pat-pat-patrick/hd2-mod-cli) 的插件列表（官方与社区），以及编写插件的
文档。本仓库不包含插件本身：每个插件在各自的仓库中构建和发布，[`plugins.json`](plugins.json)（官方）和
[`community.json`](community.json)（社区，未经审核）列出它们。

## 官方插件

| 插件 | 文件 | 版本 | 仓库 |
|---|---|---|---|
| HD2 MOD 控制台：编辑各 MOD 的设置，已启用的 MOD 列在前面 | `HD2QD.Settings.dll` | [1.20.1](https://github.com/pat-pat-patrick/hd2-mod-setting-gui/releases/tag/v1.20.1) | [hd2-mod-setting-gui](https://github.com/pat-pat-patrick/hd2-mod-setting-gui) |
| 资源检查：模型与贴图和原版资源的对比，以及显存占用 | `HD2QD.AssetCheck.dll` | [1.4.2](https://github.com/pat-pat-patrick/hd2qd-asset-check/releases/tag/v1.4.2) | [hd2qd-asset-check](https://github.com/pat-pat-patrick/hd2qd-asset-check) |
| MOD 修复：修复游戏更新后出问题的 MOD——无法加载的模型、让游戏部分声音消失的音效 MOD、缺少游戏新增内容的字幕 MOD（音库与字幕修复由 [x402](https://github.com/x402) 贡献；音库修复方法来自 [40Hour](https://space.bilibili.com/157681854) 的音效维修台） | `HD2QD.Repatch.dll` | [1.2.1](https://github.com/pat-pat-patrick/hd2qd-repatch/releases/tag/v1.2.1) | [hd2qd-repatch](https://github.com/pat-pat-patrick/hd2qd-repatch) |
| 会员授权：为仅供创作者会员使用的 MOD 登录，并下载其会员内容（代码，以及语音录音等大体积数据），在本机加密保存、仅在游戏运行时解锁 | `HD2QD.License.dll` | [1.13.0](https://github.com/pat-pat-patrick/hd2-mod-license/releases/tag/plugin-v1.13.0) | [hd2-mod-license](https://github.com/pat-pat-patrick/hd2-mod-license) |
| 资源名称：从 HD2SDK 的仓库下载资源名称表和游戏包名称表，冲突和资源检查中显示资源的名称（需要管理器 0.16.0 或更新） | `HD2QD.ResourceNames.dll` | [1.1.1](https://github.com/pat-pat-patrick/hd2qd-resource-names/releases/tag/v1.1.1) | [hd2qd-resource-names](https://github.com/pat-pat-patrick/hd2qd-resource-names) |
| Speed Dial for Liberty：一键呼叫战备。你按一个键，插件用你自己的战备输入键替你输入战备代码。需要同时启用 MOD Speed Dial for Liberty（v0.24.0 或更新），游戏时管理器保持运行 | `HD2QD.SpeedDial.dll` | [1.6.2](https://github.com/pat-pat-patrick/hd2qd-speed-dial/releases/tag/v1.6.2) | [hd2qd-speed-dial](https://github.com/pat-pat-patrick/hd2qd-speed-dial) |
| HellForge：启动离线版《绝地潜兵2》HellForge，并把它作为管理器的部署目标：库里的 MOD 转换为 HellForge 的游戏版本、会话、档案编辑器、设置、联机大厅、日志和会员 MOD（部署库里的 MOD 需要管理器 0.20.0 或更新） | `HD2QD.HellForge.dll` | [0.15.0](https://github.com/pat-pat-patrick/hd2qd-hellforge/releases/tag/v0.15.0) | [hd2qd-hellforge](https://github.com/pat-pat-patrick/hd2qd-hellforge) |

需要 HD2 Mod Quick Deploy 0.15.0 或更新版本（插件接口 Api 2）。默认均不安装。官方插件均由维护者自己
维护；其他创作者的插件登记为[社区插件](#社区插件)，任何插件仍可从文件添加。

## 添加插件

1. 在 HD2 Mod Quick Deploy 中打开“插件”页（齿轮旁的拼图按钮）。
2. 列表中的插件：在“插件商店”标签页中搜索或用筛选（全部、官方、社区）找到它，选中后点击**下载并添加**。
   管理器会下载 [`plugins.json`](plugins.json)（官方）或 [`community.json`](community.json)（社区）中
   记录的最新版本，SHA-256 一致才会添加。社区插件未经审核，添加前需确认你信任其作者。
3. 其他插件：点击“添加插件…”，选择其 `HD2QD.<名称>.dll`，或将文件拖到插件页上。
4. 确认添加。插件以管理器的权限运行，请仅添加来源可信的插件。

插件卡片上的“移除”可将其删除。命令行：`hd2qd plugins`、`hd2qd plugin-add <名称或文件>`（给出名称时下载
官方插件）、`hd2qd plugin-remove <名称>`。

## `plugins.json`

管理器从本仓库的 `main` 分支读取此文件，并在设置目录中保留一份副本。因此在这里加入的插件，
无需发布新版管理器即可显示。

| 字段 | 含义 |
|---|---|
| `file` | 插件文件名，`HD2QD.<名称>.dll`。 |
| `title`、`summary` | 列表中显示的名称和简介，英文。译文见 `locales/`（见下文）。 |
| `author`、`repository` | 创作者，以及发布该插件的 GitHub 仓库。 |
| `asset` | 要下载的 release 附件。 |
| `api` | 插件使用的接口版本。 |
| `license` | 插件的许可证，使用 SPDX 标识符（`MIT`、`Apache-2.0` 等）。供阅读列表的人参考，管理器不使用。 |
| `wanted_by_file` | 可选：带有此文件的 MOD 会被标记为需要该插件。 |
| `button` | 可选：为 `true` 时，该插件在管理器标题栏有自己的按钮，图标为插件自带的 `app.ico`。只有列在这里、且已安装文件与其某个 `versions` 一致的插件才能有按钮。 |
| `versions` | 每个已发布的版本：`{version, tag, sha256}`。管理器下载其中最新的版本，并按 `sha256` 核对。 |

## 社区插件

任何创作者都可以在这里登记插件，让玩家在管理器中找到它：插件页的“插件商店”标签页，标有“社区”，带“下载并添加”按钮。
社区插件未经审核。管理器会在每个社区插件旁注明这一点，并在添加前询问玩家；社区插件不会在管理器标题栏中拥有
按钮。列表文件是 [`community.json`](community.json)，格式与 `plugins.json` 相同（没有 `button`）。Quick Deploy 0.26.0 起显示该列表，更早的版本不读取它。

### 条件

1. **公开源码**：插件仓库在 GitHub 上公开，且 GitHub 将其 `LICENSE` 文件识别为以下许可证之一（SPDX）：
   `MIT`、`Apache-2.0`、`BSD-2-Clause`、`BSD-3-Clause`、`ISC`、`0BSD`、`Unlicense`、`MPL-2.0`、
   `LGPL-2.1`、`LGPL-3.0`、`GPL-2.0`、`GPL-3.0`。其他许可证（包括 `AGPL-3.0`）和闭源插件不予登记。
2. **在 GitHub 上构建并发布**：每个版本都是该仓库的一个 release（不是草稿或预发布），附带 DLL，大小
   不超过 25 MB。DLL 须由 GitHub Actions 在 GitHub 托管的 runner 上，从该 release 的 tag 所指的提交
   构建，并附带构建来源证明（[`actions/attest-build-provenance`](https://github.com/actions/attest-build-provenance)），
   以证明玩家下载的文件正是由公开源码生成的。在自己电脑上或自托管 runner 上构建的 DLL 不予登记。
   [`example/release.yml`](example/release.yml) 是一个现成的 workflow，推送 tag 时会自动完成上述步骤。
   管理器只从 GitHub 和本列表在 Cloudflare 上的镜像下载，不登记其他网站上的文件。
3. **是本管理器的插件**：文件名为 `HD2QD.<名称>.dll`，且不与官方插件重名；包含公开类型 `Plugin` 和
   `Api = 2`（[docs/plugin-authors.zh-CN.md](docs/plugin-authors.zh-CN.md)）。程序集版本即登记的版本。
4. **简短的文字**：`title` 不超过 60 个字符，`summary` 不超过 400 个字符，使用英文。译文放在
   `locales/`（见下文），在同一个拉取请求中提交。

第 2 条中由 GitHub Actions 构建的要求自 2026-11-29 起执行：此前已登记的版本保留，此后加入的每个版本都须满足。

### 登记插件或新版本

1. 推送 tag，由你的 release workflow 构建 DLL、生成证明并附加到 release。
2. 向 `main` 提交拉取请求：在 `community.json` 中加入你的条目，或在你的条目的 `versions` 中加入
   `{version, tag, sha256}`。`sha256` 是 GitHub 提供的附件文件的 SHA-256。
3. 拉取请求的检查（`tools/check_community.py`）会读取你的仓库和 release：许可证、tag、SHA-256、
   文件是否为包含公开 `Plugin` 的 .NET 程序集、程序集版本、文件的构建来源证明
   （`gh attestation verify`），以及该 tag 的源码能否下载。已登记的版本不能修改。
4. 检查通过后由维护者合并。此后每个管理器都会提供这个版本，已添加旧版本的玩家会收到更新提示。

镜像会在每个登记版本的文件旁保存该版本的源码压缩包，因此即使仓库被删除，列表提供过的所有代码仍可查阅。
插件可随时从列表中移除：由作者提交拉取请求，或由维护者移除。

## 维护列表

本节供本仓库的维护者使用。其他人无法向列表加入插件，也无法为插件
加入新版本：管理器只从本仓库的 `main` 读取列表，并且只有文件的 SHA-256 与这里记录的一致时，才会作为
官方插件安装。欢迎通过 issue 或 pull request 提出建议。

发布官方插件的新版本：

1. 用插件自己的 `build.bat` 构建，它会用维护者的私钥给 DLL 签名（`hd2-mod-cli/tools/sign_plugin.py`；私钥不在任何
   仓库中）。Quick Deploy 0.26.0 及更新版本会把带签名的构建显示为官方插件，不论版本、不论是否已在本仓库登记；更早的版本
   只按这里记录的 SHA-256 识别官方插件。
2. 在插件自己的仓库发布 release，附件文件名与 `asset` 一致。
3. 在本仓库该插件的 `versions` 中加入 `{version, tag, sha256}`：release 的标签，以及 GitHub 上该附件的
   SHA-256。
4. 推送到 `main`。此后所有管理器都会提供新版本，管理器本身无需发布新版。

列表格式须保持已发布的管理器能够读取：只能新增字段，不要改名或删除字段。

## 翻译

`plugins.json` 和 `community.json` 只包含英文。每种语言各有一个文件 `locales/<语言>.json`，以语言标记命名（`zh-CN`、
`de`、`pt-BR` 等），其中按插件文件名列出该语言的 `title` 和 `summary`。管理器读取其当前显示语言的
文件；文件中缺少的插件或字段以英文显示。新增一种语言只需新增一个文件，其他内容无需改动。

```json
{
  "HD2QD.Repatch.dll": { "title": "MOD 修复", "summary": "..." }
}
```

## 编写插件

见 [docs/plugin-authors.zh-CN.md](docs/plugin-authors.zh-CN.md)（[English](docs/plugin-authors.md)）
以及 [example/](example) 中的完整示例。
