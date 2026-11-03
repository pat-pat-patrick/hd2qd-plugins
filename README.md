# HD2 Mod Quick Deploy plugins

The official list of plugins for [HD2 Mod Quick Deploy](https://github.com/pat-pat-patrick/hd2-mod-cli),
and the documentation for writing one. This repository holds no plugin itself: each plugin is
built and released in its own repository, and [`plugins.json`](plugins.json) names them.

## Official plugins

| Plugin | File | Repository |
|---|---|---|
| HD2 Mod Console: each mod's settings, the enabled mods first | `HD2QD.Settings.dll` | [hd2-mod-setting-gui](https://github.com/pat-pat-patrick/hd2-mod-setting-gui) |
| Asset check: models and textures against the game's, and video memory | `HD2QD.AssetCheck.dll` | hd2qd-asset-check |
| Model repair: mod models made for an earlier version of the game, brought up to the current one | `HD2QD.Repatch.dll` | hd2qd-repatch |
| Member licenses: sign-in for mods available only to their author's members | `HD2QD.License.dll` | hd2-mod-license |

The list holds the manager's author's plugins only. Any other plugin can still be added by hand.

## Adding a plugin

1. In HD2 Mod Quick Deploy, open the Plugins page (the jigsaw piece beside the gear).
2. Choose **Add plugin…** and select the plugin's `HD2QD.<name>.dll`, or drop the file on the page.
3. Confirm. A plugin runs with the manager's permissions: add only plugins from a source you trust.

**Remove** on a plugin's card deletes it again. On the command line: `hd2qd plugins`,
`hd2qd plugin-add <file>`, `hd2qd plugin-remove <name>`.

## `plugins.json`

The manager reads this file from the `main` branch of this repository and keeps a copy in its
settings folder, so a plugin added here shows in every copy of the manager without a new release.

| Field | Meaning |
|---|---|
| `file` | The plugin's file name, `HD2QD.<name>.dll`. |
| `title`, `title_zh`, `summary`, `summary_zh` | What the list shows, in English and Chinese. |
| `author`, `repository` | Who makes it, and the GitHub repository whose releases carry it. |
| `asset` | The release asset to download. |
| `api` | The contract version it speaks. |
| `wanted_by_file` | Optional: the manager marks the mods that ship this file as needing the plugin. |
| `versions` | Each released version: `{version, tag, sha256}`. The manager checks a download against `sha256`. |

## Writing a plugin

See [docs/plugin-authors.md](docs/plugin-authors.md) ([中文](docs/plugin-authors.zh-CN.md)) and
the complete example in [example/](example).

---

# HD2 Mod Quick Deploy 插件

[HD2 Mod Quick Deploy](https://github.com/pat-pat-patrick/hd2-mod-cli) 的官方插件列表，以及编写插件的
文档。本仓库不包含插件本身：每个插件在各自的仓库中构建和发布，[`plugins.json`](plugins.json)
列出它们。

## 官方插件

| 插件 | 文件 | 仓库 |
|---|---|---|
| HD2 MOD 控制台：编辑各 MOD 的设置，已启用的 MOD 列在前面 | `HD2QD.Settings.dll` | [hd2-mod-setting-gui](https://github.com/pat-pat-patrick/hd2-mod-setting-gui) |
| 资源检查：模型与贴图和原版资源的对比，以及显存占用 | `HD2QD.AssetCheck.dll` | hd2qd-asset-check |
| 模型修复：将为旧版游戏制作的 MOD 模型更新为当前游戏的格式 | `HD2QD.Repatch.dll` | hd2qd-repatch |
| 会员授权：为仅供作者会员使用的 MOD 登录 | `HD2QD.License.dll` | hd2-mod-license |

列表只收录管理器作者本人的插件。其他插件仍可手动添加。

## 添加插件

1. 在 HD2 Mod Quick Deploy 中打开“插件”页（齿轮旁的拼图按钮）。
2. 点击“添加插件…”，选择插件的 `HD2QD.<名称>.dll`，或将文件拖到插件页上。
3. 确认添加。插件以管理器的权限运行，请仅添加来源可信的插件。

插件卡片上的“移除”可将其删除。命令行：`hd2qd plugins`、`hd2qd plugin-add <文件>`、
`hd2qd plugin-remove <名称>`。

## `plugins.json`

管理器从本仓库的 `main` 分支读取此文件，并在设置目录中保留一份副本。因此在这里加入的插件，
无需发布新版管理器即可显示。

| 字段 | 含义 |
|---|---|
| `file` | 插件文件名，`HD2QD.<名称>.dll`。 |
| `title`、`title_zh`、`summary`、`summary_zh` | 列表中显示的名称和简介，英文与中文。 |
| `author`、`repository` | 作者，以及发布该插件的 GitHub 仓库。 |
| `asset` | 要下载的 release 附件。 |
| `api` | 插件使用的接口版本。 |
| `wanted_by_file` | 可选：带有此文件的 MOD 会被标记为需要该插件。 |
| `versions` | 每个已发布的版本：`{version, tag, sha256}`。管理器下载后按 `sha256` 核对。 |

## 编写插件

见 [docs/plugin-authors.zh-CN.md](docs/plugin-authors.zh-CN.md)（[English](docs/plugin-authors.md)）
以及 [example/](example) 中的完整示例。
