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
| `Api` | `const int` | The contract's version: `1`. A plugin of another version is refused. |
| `Kind` | `const string` | `"window"` or `"panel"` (below). |
| `Title(bool zh)` | `string` | The plugin's name, in Chinese when `zh`. |
| `Summary(bool zh)` | `string` | One sentence on what it does. |

### By kind

| Kind | Member | Meaning |
|---|---|---|
| `"window"` | `void Open(Window owner, Dictionary<string, object> host)` | The card shows the summary and an **Open** button, which calls this. Make the window with `host["window"]` so it has the manager's frame. |
| `"panel"` | `FrameworkElement Panel(Window owner, Dictionary<string, object> host)` | The plugin draws the card's body on the Plugins page. The manager draws the title, file, version and **Remove** above it. |

### Optional

| Member | Meaning |
|---|---|
| `Dictionary<string, object> ModNote(string modFolder, Dictionary<string, object> host)` | A word on a mod's row, or `null`: `text`, `text_zh`, `tip`, `tip_zh`, `colour` (`"Yellow"`, `"Blue"` or `"Muted"`). Called for every mod whenever the manager reads its state, so it must be cheap. |
| `static readonly string[][] Commands` | Commands added to the command line, as rows of `[name, help]`. A name the manager has itself is left out. |
| `int Run(string command, string[] args, TextWriter output, Dictionary<string, object> host)` | Runs one of `Commands`: `0` done, `1` refused, `2` a wrong command line. An exception is reported as a refusal. |
| `bool Start(Dictionary<string, object> host)` | Runs once in the background when the window starts (a renewal, a cache). Return `true` when the manager should read its state again. |

## The host

Every call gets the same dictionary.

| Key | Type | Meaning |
|---|---|---|
| `api` | `long` | The contract's version. |
| `home` | `string` | The manager's settings folder. Keep the plugin's own files there. |
| `appdata` | `string` | The player's roaming AppData (the game's `Arrowhead\Helldivers2`). |
| `zh` | `bool` | The window's language is Chinese. |
| `data` | `string` | The game's `data` folder; `null` when no game folder is set. |
| `mods` | `Func<List<Dictionary<string, object>>>` | The enabled mods in load order, each `{name, archives}`: the patch archives it deploys. The last mod to load wins a resource two mods ship. |
| `library` | `Func<List<Dictionary<string, object>>>` | Every mod in the library, each `{name, path, enabled, settings}`; `settings` are the HD2 Mod Setting GUI lists its Lua writes. It may read archives: call it off the UI thread. |

In the window only:

| Key | Type | Meaning |
|---|---|---|
| `window` | `Func<string, FrameworkElement, Window>` | A window with the manager's frame, for a title and content. |
| `ask` | `Func<string, string, bool>` | The manager's question dialog: text and the action's label; `true` when chosen. |
| `tell` | `Action<string>` | The manager's message dialog. |
| `foot` | `Action<string, string>` | A line in the manager's status bar: text and colour. |
| `refresh` | `Action` | The manager reads its state again and redraws the Plugins page. |

The manager's application carries its styles and colours. A panel or window can use them with
`Application.Current.TryFindResource`: the styles `Ghost` and `Primary`; the brushes `Ink`,
`Muted`, `Yellow`, `Blue`, `Grid`, `Ground700`, `Ground900`.

## Rules

- Write the text a player reads in a formal register, in both English and Chinese.
- Never block the window: read files and the network off the UI thread.
- A plugin runs with the manager's permissions. Read and write only what the plugin needs.
- The official list ([`plugins.json`](../plugins.json)) holds the manager's author's plugins only.
  Publish your plugin in your own repository; players add it with **Add plugin…**.
