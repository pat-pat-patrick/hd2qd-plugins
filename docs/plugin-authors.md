# Writing a plugin for HD2 Mod Quick Deploy

A plugin is a .NET Framework 4.8 class library named `HD2QD.<name>.dll`. The player adds it on the
manager's Plugins page (the jigsaw piece beside the gear), or with `hd2qd plugin-add <file>`. The
manager keeps it in its settings folder (`%USERPROFILE%\.hd2-mod-cli\plugins`) and loads it at
start. Nothing ships with the manager: a plugin is added when it is needed.

The manager calls the plugin by name. It shares no types with it, only strings, numbers, bools,
delegates and Json shapes: `Dictionary<string, object>`, `List<object>`, `long`, `double`,
`string`, `bool`.

[`example/`](../example) is a complete plugin that uses every call below.

## The class

The assembly has exactly one public class named `Plugin`. The manager reads its `Api` before
anything of the plugin runs, so `Api` must be a `const`.

### Required

| Member | Type | Meaning |
|---|---|---|
| `Api` | `const int` | The contract's version: `2`. A plugin of another version is refused. |
| `Kind` | `const string` | `"window"` or `"panel"` (below). |
| `Title(string lang)` | `string` | The plugin's name in the language `lang` (see [Languages](#languages)). |
| `Summary(string lang)` | `string` | One sentence on what it does, in `lang`. |

### By kind

| Kind | Member | Meaning |
|---|---|---|
| `"window"` | `void Open(Window owner, Dictionary<string, object> host)` | The card shows the summary and an **Open** button, which calls this. Show the content as a tab with `host["tab"]` when the host has it; otherwise make the window with `host["window"]` so it has the manager's frame (see [A tab or a window](#a-tab-or-a-window)). |
| `"panel"` | `FrameworkElement Panel(Window owner, Dictionary<string, object> host)` | The plugin draws the card's body on the Plugins page. The manager draws the title, file, version and **Remove** above it. |

### Optional

| Member | Meaning |
|---|---|
| `Dictionary<string, object> ModNote(string modFolder, Dictionary<string, object> host)` | A word on a mod's row, or `null`: `text`, `tip` (in `host["lang"]`) and `colour` (`"Yellow"`, `"Blue"` or `"Muted"`). Called for every mod whenever the manager reads its state, so it must be cheap. |
| `List<Dictionary<string, object>> ModTags(string modFolder, Dictionary<string, object> host)` | What the mod holds, as short tags drawn like the manager's own `LUA` tag (a blue box), side by side: each `{text, tip}` in `host["lang"]`, or `null` for none. For the kinds of mod a target's game knows (the HellForge plugin: `C`, `DLL`, `STATS`); not for a mod's target or state. Called for every mod whenever the manager reads its state, so it must be cheap. |
| `app.ico` | Not a member: the plugin's own icon, an embedded resource named `app.ico` (or a WPF `Resource` of that name). The manager draws it on the title-bar button that an official plugin gets when the official list gives it one (`"button": true`); no other plugin has a title-bar button. From Quick Deploy 0.25.0 it is also drawn on the plugin's tab, for every plugin. |
| `byte[] Icon(Dictionary<string, object> host)` | Optional: an icon read at run time, the bytes of an `.ico`, or `null`. When it gives one, the title-bar button and the tab draw it instead of `app.ico`; `null` keeps `app.ico`. For an icon the plugin may not ship, such as another program's, read from that program on the player's computer. Called whenever the title bar is drawn, so keep what it reads. Read by Quick Deploy later than 0.19.0; earlier versions draw `app.ico`. |
| `static readonly string[][] Commands` | Commands added to the command line, as rows of `[name, help]`. A name the manager has itself is left out. |
| `int Run(string command, string[] args, TextWriter output, Dictionary<string, object> host)` | Runs one of `Commands`: `0` done, `1` refused, `2` a wrong command line. An exception is reported as a refusal. |
| `bool Start(Dictionary<string, object> host)` | Runs once in the background when the window starts (a renewal, a cache). Return `true` when the manager should read its state again. |
| `Dictionary<string, object> ModSource(string modFolder, Dictionary<string, object> host)` | For a protected mod (its `hd2_license.json` has `payload.deploy` `"game"`), where the manager deploys its files from: `{folder, mode}` when they are ready, `folder` laid out as the mod's own folder; `{folder: "", mode, why}` when they are not (`why` in `host["lang"]`, shown on the mod's row; the mod is left out of the deploy); `null` for a mod that is not the plugin's. Called once per mod whenever the manager reads its state, so it must be cheap. From Quick Deploy 0.23.0. |
| `bool PrepareDeploy(Dictionary<string, object> host)` | Makes the protected mods' files ready, before a deploy and before the manager starts the game (on a background thread; it may take a while). `host["for_session"]` `true`: also the mods whose `payload.mode` is `"session"`. Return `false` when one could not be made ready. From Quick Deploy 0.23.0. |
| `void EndSession(Dictionary<string, object> host)` | The game the manager started has ended and the manager has deployed without the session-mode mods: remove their files. Never called while the game runs. From Quick Deploy 0.23.0. |
| `static string OverlayKey` | A window plugin only: the key that brings its tab (or window) up over the game, by the name HD2 Mod Setting GUI writes, such as `"page down"` or `"ctrl+shift+f10"`; `""` for a plugin that can have a key but brings none. A field, a constant or a property. See [A key in the game](#a-key-in-the-game). From Quick Deploy 0.26.0. |

## The host

Every call gets the same dictionary.

| Key | Type | Meaning |
|---|---|---|
| `api` | `long` | The contract's version. |
| `version` | `string` | The manager's own version, such as `"0.22.0"` (from 0.22.0; absent before). |
| `home` | `string` | The manager's settings folder. Keep the plugin's own files there. |
| `appdata` | `string` | The player's roaming AppData (the game's `Arrowhead\Helldivers2`). |
| `lang` | `string` | The language the manager shows, as a language tag (see [Languages](#languages)). The command line is `"en"`. |
| `data` | `string` | The game's `data` folder; `null` when no game folder is set. |
| `mods` | `Func<List<Dictionary<string, object>>>` | The enabled mods in load order, each `{name, archives}`: the patch archives it deploys. The last mod to load wins a resource two mods ship. |
| `library` | `Func<List<Dictionary<string, object>>>` | Every mod in the library, each `{name, path, enabled, settings}`; `settings` are the HD2 Mod Setting GUI lists its Lua writes. It may read archives: call it off the UI thread. |
| `stage` | `string` | A folder on the game's drive (`<game>\hd2qd_stage`) where `ModSource` folders may live, so the manager deploys them by hard link; `null` when no game folder is set (from 0.23.0). |
| `for_session` | `bool` | Only in `PrepareDeploy`: see above. |

In the window only:

| Key | Type | Meaning |
|---|---|---|
| `tab` | `Func<string, FrameworkElement, Action, Dictionary<string, object>>` | A tab of the manager's window, shown at once: a title, the content, and an action the manager calls once the tab is closed. Returns `show` and `close`, both `Action`. From Quick Deploy 0.25.0; absent before. See [A tab or a window](#a-tab-or-a-window). |
| `window` | `Func<string, FrameworkElement, Window>` | A window with the manager's frame, for a title and content. For a manager without `tab`. |
| `ask` | `Func<string, string, bool>` | The manager's question dialog: text and the action's label; `true` when chosen. |
| `tell` | `Action<string>` | The manager's message dialog. |
| `foot` | `Action<string, string>` | A line in the manager's status bar: text and colour. |
| `refresh` | `Action` | The manager reads its state again and redraws the Plugins page. |

The manager's application carries its styles and colours. A panel or window can use them with
`Application.Current.TryFindResource`: the styles `Ghost` and `Primary`; the brushes `Ink`,
`Muted`, `Yellow`, `Blue`, `Grid`, `Ground700`, `Ground900`.

## A tab or a window

From Quick Deploy 0.25.0 a window plugin opens as a tab of the manager's window, as in a browser:
the manager is the first tab, and each open plugin is one more. A plugin asks for a tab with
`host["tab"]`. A plugin that does not use it keeps working: it opens its window with
`host["window"]` (or its own) as before, and has no tab.

```csharp
static Action showTab;   // the plugin's tab, while it is open

public static void Open(Window owner, Dictionary<string, object> host)
{
    if (showTab != null) { showTab(); return; }       // opened again: its tab is shown
    var lang = Words.Lang(host);
    FrameworkElement content = MakeContent(host);      // the plugin's own content
    if (host.TryGetValue("tab", out var t) && t is Func<string, FrameworkElement, Action, Dictionary<string, object>> tab)
    {
        var handle = tab(Title(lang), content, () => showTab = null);
        showTab = handle.TryGetValue("show", out var show) ? show as Action : null;
        return;
    }
    // a manager before 0.25.0: a window of its own
    ((Func<string, FrameworkElement, Window>)host["window"])(Title(lang), content).Show();
}
```

| What | How it works |
|---|---|
| The tab | Its head shows the plugin's title and icon (`app.ico`, or `Icon` when it gives one). The tab takes the whole window below the row of tabs; the manager's title bar and status bar are hidden while it is shown. |
| Closing | The tab's ×, a middle click on it, or Ctrl+W. The manager then calls the plugin's action once: stop timers, write what is pending, release files and hotkeys. It also calls it when the program ends with the tab open. Esc does not close a tab. |
| The handle | `show` brings the tab forward, and the window with it from the notification area. `close` closes the tab as × does. Calling `tab` again with the same content shows its tab and makes no second one. |
| No window of its own | Content in a tab is not in a window of the plugin: do not close or hide one. For a dialog's owner, use `Window.GetWindow(content)`. Content that was a window's must be taken out of it first (`window.Content = null`). |
| Keys | Ctrl+W, Ctrl+Tab and Ctrl+Shift+Tab belong to the manager while a plugin's tab is shown. |
| Opened at start | With the manager's setting *Reopen the previous tabs at start*, the plugins whose tabs were open when the program was closed get `Open` again at its next start. `Open` must therefore work without a click from the player. |

## A key in the game

From Quick Deploy 0.26.0 a window plugin can be brought up while the game runs, as HD2 Mod
Setting GUI is: the plugin declares `OverlayKey`, and the manager does the rest.

```csharp
public const string OverlayKey = "page down";   // "" : none until the player chooses one
```

| What | How |
|---|---|
| The key | Held with `RegisterHotKey`, only while `helldivers2.exe` runs, so other programs have it the rest of the time. Nothing goes into the game's process. |
| Pressed | The manager calls `Open` (as the card's button does), then puts the tab, or the plugin's own window, over the game, on top and with the keys. Pressed again, it is put away and the game gets the keys back. The game has to run in borderless windowed mode. |
| The player's choice | The plugin's card shows the key; the player can change or clear it there. The plugin's value is only the default. |
| Two plugins, one key | The first one keeps it; the card of the second says so. A key another program holds is said on the card too. |
| Do not | Register the key yourself, or hook the keyboard: the manager would hold it twice, and anti-cheat software may refuse a hook. |
| Key names | Letters and digits (`"a"`, `"5"`), `"f1"` to `"f24"`, `"numpad 0"` to `"numpad 9"`, `"page up"`, `"page down"`, `"home"`, `"end"`, `"insert"`, `"delete"`, the arrows (`"up"` …), `"backtick"`, `"minus"`, `"equal"` and the other punctuation by name; modifiers `ctrl+`, `alt+`, `shift+`. No mouse buttons. |

## Languages

The manager names a language by its tag ([BCP 47](https://www.rfc-editor.org/info/bcp47)): `en`,
`zh-CN`, `de`, `pt-BR`. It passes the tag to `Title` and `Summary`, and as `host["lang"]` to every
other call. The plugin answers in that language when it has it, and in English otherwise.

- Keep each language's text in a file of its own, never as pairs of fields or a switch between
  two languages. Adding a language must be adding one file.
- English is the language every plugin has; any text missing in another language falls back to it.
- Look a tag up exactly first, then by its language alone (`de` for `de-AT`), then English.
- A text with a count can have a second key ending in `_1`, the form for exactly one, in the
  languages that need it.

The example keeps `Lang/en.json` and `Lang/zh-CN.json` (a flat object of keys and texts) as
embedded resources and reads them with `Words` ([`example/Words.cs`](../example/Words.cs)).

## Rules

- Write the text a player reads in a formal register. English is required; each other language is a file of its own.
- Never block the window: read files and the network off the UI thread.
- A plugin runs with the manager's permissions. Read and write only what the plugin needs.
- To have players find your plugin in the manager's plugin store, list it in the community list
  ([`community.json`](../community.json)): see
  [Community plugins](../README.md#community-plugins) for the requirements (public source on
  GitHub, an accepted licence, each version a release built by GitHub Actions with a build
  provenance attestation, as [`example/release.yml`](../example/release.yml) does) and how to
  list it. Any plugin can also be
  added from its file with **Add plugin…**.
