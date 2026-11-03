# 为 HD2 Mod Quick Deploy 编写插件

插件是一个 .NET Framework 4.8 类库，文件名为 `HD2QD.<名称>.dll`。玩家在管理器的“插件”页
（齿轮旁的拼图按钮）添加，或使用 `hd2qd plugin-add <文件>`。管理器将其保存在设置目录
（`%USERPROFILE%\.hd2-mod-cli\plugins`），启动时加载。管理器不自带任何插件：需要时再添加。

管理器按名称调用插件，与插件不共享任何类型，只传递字符串、数字、布尔值、委托和 Json 结构：
`Dictionary<string, object>`、`List<object>`、`long`、`double`、`string`、`bool`。

[`example/`](../example) 是一个完整的插件，用到了下面所有调用。

## 插件类

程序集中只能有一个名为 `Plugin` 的公开类。管理器在运行插件的任何代码之前读取 `Api`，因此
`Api` 必须是 `const`。

### 必需成员

| 成员 | 类型 | 含义 |
|---|---|---|
| `Api` | `const int` | 接口版本：`2`。其他版本的插件会被拒绝。 |
| `Kind` | `const string` | `"window"` 或 `"panel"`（见下文）。 |
| `Title(string lang)` | `string` | 插件名称，使用语言 `lang`（见[语言](#语言)）。 |
| `Summary(string lang)` | `string` | 一句话说明插件的用途，使用语言 `lang`。 |

### 按类型

| 类型 | 成员 | 含义 |
|---|---|---|
| `"window"` | `void Open(Window owner, Dictionary<string, object> host)` | 卡片显示简介和“打开”按钮，点击时调用此方法。请用 `host["window"]` 创建窗口，使其使用管理器的窗口外框。 |
| `"panel"` | `FrameworkElement Panel(Window owner, Dictionary<string, object> host)` | 由插件绘制卡片正文。管理器在其上方绘制标题、文件名、版本和“移除”按钮。 |

### 可选成员

| 成员 | 含义 |
|---|---|
| `Dictionary<string, object> ModNote(string modFolder, Dictionary<string, object> host)` | 在 MOD 行上显示的标记，或 `null`：`text`、`tip`（使用 `host["lang"]` 的语言）和 `colour`（`"Yellow"`、`"Blue"` 或 `"Muted"`）。管理器每次读取状态时对每个 MOD 调用一次，须保持开销很小。 |
| `const string Icon` | 仅限 `"window"` 类型：Segoe Fluent Icons（Windows 10 上为 Segoe MDL2 Assets）中的一个字符，例如 `"\uE9E9"`。有此成员的插件会在管理器标题栏的插件按钮旁多一个按钮，点击即打开插件；玩家可在插件卡片上关闭该按钮。只建议玩家常用的插件提供。 |
| `static readonly string[][] Commands` | 添加到命令行的命令，每行为 `[名称, 说明]`。与管理器自身命令重名的会被忽略。 |
| `int Run(string command, string[] args, TextWriter output, Dictionary<string, object> host)` | 运行 `Commands` 中的命令：`0` 完成，`1` 拒绝，`2` 命令行有误。抛出的异常按拒绝处理。 |
| `bool Start(Dictionary<string, object> host)` | 窗口启动时在后台运行一次（续期、缓存等）。需要管理器重新读取状态时返回 `true`。 |

## host

每次调用都会传入同一个字典。

| 键 | 类型 | 含义 |
|---|---|---|
| `api` | `long` | 接口版本。 |
| `home` | `string` | 管理器的设置目录。插件自己的文件请保存在这里。 |
| `appdata` | `string` | 玩家的 Roaming AppData（游戏的 `Arrowhead\Helldivers2` 位于其中）。 |
| `lang` | `string` | 管理器当前显示的语言，为语言标记（见[语言](#语言)）。命令行为 `"en"`。 |
| `data` | `string` | 游戏的 `data` 文件夹；未设置游戏目录时为 `null`。 |
| `mods` | `Func<List<Dictionary<string, object>>>` | 按加载顺序排列的已启用 MOD，每项为 `{name, archives}`：该 MOD 部署的 patch 文件。两个 MOD 带有同一资源时，后加载者生效。 |
| `library` | `Func<List<Dictionary<string, object>>>` | 库中所有 MOD，每项为 `{name, path, enabled, settings}`；`settings` 为其 Lua 写给 HD2 Mod Setting GUI 的设置列表名。可能需要读取 patch 文件，请在后台线程调用。 |

仅窗口中提供：

| 键 | 类型 | 含义 |
|---|---|---|
| `window` | `Func<string, FrameworkElement, Window>` | 使用管理器外框的窗口，参数为标题和内容。 |
| `ask` | `Func<string, string, bool>` | 管理器的询问对话框：正文和操作按钮的文字；选择该操作时返回 `true`。 |
| `tell` | `Action<string>` | 管理器的消息对话框。 |
| `foot` | `Action<string, string>` | 在管理器状态栏显示一行：文字和颜色。 |
| `refresh` | `Action` | 管理器重新读取状态并重绘插件页。 |

管理器的应用程序资源中带有其样式和颜色，面板或窗口可通过 `Application.Current.TryFindResource`
使用：样式 `Ghost`、`Primary`；画刷 `Ink`、`Muted`、`Yellow`、`Blue`、`Grid`、`Ground700`、
`Ground900`。

## 语言

管理器以语言标记（[BCP 47](https://www.rfc-editor.org/info/bcp47)）表示语言，例如 `en`、`zh-CN`、`de`、
`pt-BR`。它将该标记传给 `Title` 和 `Summary`，并在其他所有调用中以 `host["lang"]` 传入。插件有该语言时
使用该语言，否则使用英文。

- 每种语言的文字各放在一个文件中，不要使用成对的字段或在两种语言之间切换的开关。新增一种语言
  只需新增一个文件。
- 每个插件都必须有英文；其他语言中缺少的文字一律以英文显示。
- 查找顺序：先按完整标记查找，再按语言部分查找（`de-AT` 找 `de`），最后使用英文。
- 带数量的文字可另设一个以 `_1` 结尾的键，作为数量恰好为 1 时的形式，供需要区分的语言使用。

示例插件将 `Lang/en.json` 和 `Lang/zh-CN.json`（键与文字组成的单层对象）作为嵌入资源，通过
`Words`（[`example/Words.cs`](../example/Words.cs)）读取。

## 规则

- 玩家看到的文字使用书面语。必须提供英文；其他每种语言各为一个文件。
- 不得阻塞窗口：读取文件和访问网络请在后台线程进行。
- 插件以管理器的权限运行。只读写插件需要的内容。
- 官方列表（[`plugins.json`](../plugins.json)）只收录管理器创作者本人的插件。请在你自己的仓库
  发布插件，玩家通过“添加插件…”安装。
