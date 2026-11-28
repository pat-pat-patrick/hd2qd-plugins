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
| `"window"` | `void Open(Window owner, Dictionary<string, object> host)` | 卡片显示简介和“打开”按钮，点击时调用此方法。host 提供 `host["tab"]` 时，请用它将内容显示为标签页；否则用 `host["window"]` 创建窗口，使其使用管理器的窗口外框（见[标签页或窗口](#标签页或窗口)）。 |
| `"panel"` | `FrameworkElement Panel(Window owner, Dictionary<string, object> host)` | 由插件绘制卡片正文。管理器在其上方绘制标题、文件名、版本和“移除”按钮。 |

### 可选成员

| 成员 | 含义 |
|---|---|
| `Dictionary<string, object> ModNote(string modFolder, Dictionary<string, object> host)` | 在 MOD 行上显示的标记，或 `null`：`text`、`tip`（使用 `host["lang"]` 的语言）和 `colour`（`"Yellow"`、`"Blue"` 或 `"Muted"`）。管理器每次读取状态时对每个 MOD 调用一次，须保持开销很小。 |
| `List<Dictionary<string, object>> ModTags(string modFolder, Dictionary<string, object> host)` | MOD 所含内容的简短标签，与管理器自己的 `LUA` 标签样式相同（蓝色边框），并排显示：每项为 `{text, tip}`，使用 `host["lang"]` 的语言；没有则返回 `null`。用于目标游戏所区分的 MOD 种类（HellForge 插件：`C`、`DLL`、`数值`），不用于适用目标或状态。管理器每次读取状态时对每个 MOD 调用一次，须保持开销很小。 |
| `app.ico` | 不是类成员：插件自己的图标，即名为 `app.ico` 的嵌入资源（或同名的 WPF `Resource`）。官方列表为某个官方插件设置按钮（`"button": true`）时，管理器用它绘制标题栏按钮；其他插件没有标题栏按钮。Quick Deploy 0.25.0 起，所有插件的标签上也显示此图标。 |
| `byte[] Icon(Dictionary<string, object> host)` | 可选：运行时读取的图标，即一个 `.ico` 的字节，或 `null`。返回图标时，标题栏按钮和标签用它代替 `app.ico`；返回 `null` 时仍用 `app.ico`。用于插件不能随附的图标，例如另一个程序的图标，从玩家电脑上的该程序读取。每次绘制标题栏都会调用，读取结果应自行缓存。0.19.0 之后的 Quick Deploy 才会读取；更早的版本使用 `app.ico`。 |
| `static readonly string[][] Commands` | 添加到命令行的命令，每行为 `[名称, 说明]`。与管理器自身命令重名的会被忽略。 |
| `int Run(string command, string[] args, TextWriter output, Dictionary<string, object> host)` | 运行 `Commands` 中的命令：`0` 完成，`1` 拒绝，`2` 命令行有误。抛出的异常按拒绝处理。 |
| `bool Start(Dictionary<string, object> host)` | 窗口启动时在后台运行一次（续期、缓存等）。需要管理器重新读取状态时返回 `true`。 |
| `Dictionary<string, object> ModSource(string modFolder, Dictionary<string, object> host)` | 受保护的 MOD（其 `hd2_license.json` 中 `payload.deploy` 为 `"game"`）的文件从哪里部署：文件已就绪时返回 `{folder, mode}`，`folder` 的目录结构与该 MOD 自身的相同；未就绪时返回 `{folder: "", mode, why}`（`why` 使用 `host["lang"]` 的语言，显示在 MOD 行上；该 MOD 不参与部署）；不是本插件的 MOD 返回 `null`。管理器每次读取状态时对每个 MOD 调用一次，须保持开销很小。Quick Deploy 0.23.0 起。 |
| `bool PrepareDeploy(Dictionary<string, object> host)` | 在部署前、以及管理器启动游戏前，准备好受保护 MOD 的文件（在后台线程调用，可以较慢）。`host["for_session"]` 为 `true` 时，`payload.mode` 为 `"session"` 的 MOD 也要准备。有 MOD 未能准备好时返回 `false`。Quick Deploy 0.23.0 起。 |
| `void EndSession(Dictionary<string, object> host)` | 管理器启动的游戏已结束，管理器也已在不含会话模式 MOD 的情况下重新部署：删除这些 MOD 的文件。游戏运行期间不会调用。Quick Deploy 0.23.0 起。 |
| `static string OverlayKey` | 仅限 window 类插件：在游戏中呼出其标签页（或窗口）的按键，按键名称与 HD2 Mod Setting GUI 相同，例如 `"page down"`、`"ctrl+shift+f10"`；可以设置按键但不提供默认键时为 `""`。可以是字段、常量或属性。见[在游戏中呼出](#在游戏中呼出)。Quick Deploy 0.26.0 起。 |

## host

每次调用都会传入同一个字典。

| 键 | 类型 | 含义 |
|---|---|---|
| `api` | `long` | 接口版本。 |
| `version` | `string` | 管理器自身的版本号，例如 `"0.22.0"`（0.22.0 起提供，之前没有此键）。 |
| `home` | `string` | 管理器的设置目录。插件自己的文件请保存在这里。 |
| `appdata` | `string` | 玩家的 Roaming AppData（游戏的 `Arrowhead\Helldivers2` 位于其中）。 |
| `lang` | `string` | 管理器当前显示的语言，为语言标记（见[语言](#语言)）。命令行为 `"en"`。 |
| `data` | `string` | 游戏的 `data` 文件夹；未设置游戏目录时为 `null`。 |
| `mods` | `Func<List<Dictionary<string, object>>>` | 按加载顺序排列的已启用 MOD，每项为 `{name, archives}`：该 MOD 部署的 patch 文件。两个 MOD 带有同一资源时，后加载者生效。 |
| `library` | `Func<List<Dictionary<string, object>>>` | 库中所有 MOD，每项为 `{name, path, enabled, settings}`；`settings` 为其 Lua 写给 HD2 Mod Setting GUI 的设置列表名。可能需要读取 patch 文件，请在后台线程调用。 |
| `stage` | `string` | 游戏所在盘上的一个文件夹（`<游戏目录>\hd2qd_stage`），`ModSource` 返回的文件夹可放在其中，管理器便能以硬链接部署；未设置游戏目录时为 `null`（0.23.0 起）。 |
| `for_session` | `bool` | 仅 `PrepareDeploy` 中提供：见上文。 |

仅窗口中提供：

| 键 | 类型 | 含义 |
|---|---|---|
| `tab` | `Func<string, FrameworkElement, Action, Dictionary<string, object>>` | 管理器窗口中的一个标签页，创建后立即显示：参数为标题、内容，以及标签关闭后管理器调用一次的回调。返回 `show` 和 `close`，均为 `Action`。Quick Deploy 0.25.0 起提供，之前没有此键。见[标签页或窗口](#标签页或窗口)。 |
| `window` | `Func<string, FrameworkElement, Window>` | 使用管理器外框的窗口，参数为标题和内容。供没有 `tab` 的管理器使用。 |
| `ask` | `Func<string, string, bool>` | 管理器的询问对话框：正文和操作按钮的文字；选择该操作时返回 `true`。 |
| `tell` | `Action<string>` | 管理器的消息对话框。 |
| `foot` | `Action<string, string>` | 在管理器状态栏显示一行：文字和颜色。 |
| `refresh` | `Action` | 管理器重新读取状态并重绘插件页。 |

管理器的应用程序资源中带有其样式和颜色，面板或窗口可通过 `Application.Current.TryFindResource`
使用：样式 `Ghost`、`Primary`；画刷 `Ink`、`Muted`、`Yellow`、`Blue`、`Grid`、`Ground700`、
`Ground900`。

## 标签页或窗口

自 Quick Deploy 0.25.0 起，窗口类插件以管理器窗口中的标签页打开，与浏览器相同：管理器本身是第一个
标签，每个打开的插件各占一个标签。插件通过 `host["tab"]` 请求标签页。不使用它的插件照常工作：
仍像以前一样用 `host["window"]`（或自建的窗口）打开独立窗口，不显示为标签。

```csharp
static Action showTab;   // 插件的标签页，打开期间有效

public static void Open(Window owner, Dictionary<string, object> host)
{
    if (showTab != null) { showTab(); return; }       // 再次打开：切换到已有的标签
    var lang = Words.Lang(host);
    FrameworkElement content = MakeContent(host);      // 插件自己的界面内容
    if (host.TryGetValue("tab", out var t) && t is Func<string, FrameworkElement, Action, Dictionary<string, object>> tab)
    {
        var handle = tab(Title(lang), content, () => showTab = null);
        showTab = handle.TryGetValue("show", out var show) ? show as Action : null;
        return;
    }
    // 0.25.0 之前的管理器：打开独立窗口
    ((Func<string, FrameworkElement, Window>)host["window"])(Title(lang), content).Show();
}
```

| 项目 | 说明 |
|---|---|
| 标签 | 标签上显示插件的标题和图标（`app.ico`；`Icon` 返回图标时用该图标）。标签页占据标签栏以下的整个窗口；显示插件标签时，管理器的标题栏和状态栏隐藏。 |
| 关闭 | 点击标签上的 ×、用鼠标中键点击标签或按 Ctrl+W。随后管理器调用插件传入的回调一次：停止计时器、写入未保存的内容、释放文件和快捷键。程序在标签打开时退出，也会调用该回调。Esc 不会关闭标签。 |
| 返回值 | `show` 切换到该标签；窗口在通知区域时一并显示。`close` 关闭该标签，与点击 × 相同。用同一个内容再次调用 `tab`，只会切换到已有的标签，不会新建。 |
| 没有自己的窗口 | 标签页中的内容不属于插件的任何窗口：不要关闭或隐藏窗口。对话框的所有者请用 `Window.GetWindow(content)`。原本放在窗口中的内容，须先从窗口中移出（`window.Content = null`）。 |
| 快捷键 | 显示插件标签时，Ctrl+W、Ctrl+Tab 和 Ctrl+Shift+Tab 由管理器处理。 |
| 启动时打开 | 管理器的设置“启动时恢复上次的标签”打开时，程序关闭时标签仍打开的插件，会在下次启动时再次收到 `Open` 调用。因此 `Open` 不能依赖玩家的点击。 |

## 在游戏中呼出

Quick Deploy 0.26.0 起，window 类插件可以像 HD2 Mod Setting GUI 一样在游戏运行时呼出：插件声明
`OverlayKey`，其余由管理器完成。

```csharp
public const string OverlayKey = "page down";   // "" ：玩家设置之前没有按键
```

| 项目 | 说明 |
|---|---|
| 按键 | 用 `RegisterHotKey` 注册，仅在 `helldivers2.exe` 运行时占用，其余时间留给其他程序。不向游戏进程注入任何内容。 |
| 按下时 | 管理器调用 `Open`（与卡片上的按钮相同），再把标签页或插件自己的窗口放到游戏画面上方，置顶并接收键盘输入。再按一次收起，键盘输入交还游戏。游戏需使用无边框窗口模式。 |
| 玩家设置 | 插件卡片上显示按键，玩家可在此更改或清除。插件提供的值只是默认值。 |
| 两个插件同一按键 | 先注册的插件生效，后一个插件的卡片上会说明。按键被其他程序占用时，卡片上也会说明。 |
| 不要 | 自行注册按键或安装键盘钩子：同一按键会被注册两次，反作弊软件也可能拦截钩子。 |
| 按键名称 | 字母和数字（`"a"`、`"5"`）、`"f1"` 至 `"f24"`、`"numpad 0"` 至 `"numpad 9"`、`"page up"`、`"page down"`、`"home"`、`"end"`、`"insert"`、`"delete"`、方向键（`"up"` 等）、`"backtick"`、`"minus"`、`"equal"` 及其他标点的英文名称；修饰键 `ctrl+`、`alt+`、`shift+`。不支持鼠标按键。 |

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
- 希望玩家在管理器的插件商店中找到你的插件，请将它登记到社区列表（[`community.json`](../community.json)）：
  条件（GitHub 上公开源码、许可证符合要求、每个版本都是 release）和登记方法见
  [社区插件](../README.md#社区插件)。任何插件也都可以通过“添加插件…”从文件添加。
