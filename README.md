# Ryoma Crimson · 越前龙马绯红球拍指针

以红框球拍为主体的 Windows 鼠标指针方案。绯红、象牙白、石墨黑与荧光黄绿配色，文本和缩放线条加粗。

**当前版本：v2.0.0 · 17 种状态 · 15 CUR + 2 ANI · 32 / 48 / 64 / 96 px**

## 选择版本

| 版本 | 忙碌状态 | 后台运行 | Windows 方案名称 | 下载 |
| --- | --- | --- | --- | --- |
| [v2.0.0](https://github.com/feisays/ryoma-crimson-cursors/tree/v2.0.0)（当前） | 线床弹跳 + 三点轮替提示 | 线床弹跳 | `Ryoma Crimson v2.0.0` | [完整指针包](Ryoma-Crimson-v2.0.0-Windows.zip?raw=true) |
| [v1.0.0](https://github.com/feisays/ryoma-crimson-cursors/tree/v1.0.0) | 拍喉环绕旋转 | 线床弹跳 | `Ryoma Crimson` | [第一版原始包](https://github.com/feisays/ryoma-crimson-cursors/raw/refs/tags/v1.0.0/Ryoma-Crimson-Windows.zip) |

两个版本可同时注册，在“鼠标属性 → 指针 → 方案”中切换。请将两个 ZIP 分别解压到独立的固定目录。
第一版原始包保持不变；第二版使用独立文件名。历史变更见 [CHANGELOG.md](CHANGELOG.md)，版本与文件校验信息见 [versions.json](versions.json)。

![第二版完整方案总览](overview.png)

## 第二版动画

忙碌状态采用最初设计：球拍固定，网球在线床循环升起、回落，触网时轻微压缩，阴影随高度变化。
拍头右上方三个状态点依次亮起，每点持续约 **0.4 秒**。

![第二版忙碌：线床弹跳与三点轮替](busy-bounce.gif)

后台运行继续使用线床弹跳。

![后台运行：线床弹跳](working-bounce.gif)

两套动画均为 **24 帧、20 fps、1.2 秒循环**，热点保持固定。

## 安装和切换

1. 下载选定版本 ZIP，解压到长期保留的位置。
2. 进入解压后的 `ryoma-crimson` 文件夹，双击 `register.cmd`。
3. 在“鼠标属性 → 指针 → 方案”中选择对应版本，然后“应用”。

脚本只注册当前用户的方案并打开设置，无需管理员权限。应用后请保留文件所在目录。
卸载某个版本前，先切换至另一方案，再运行该版本的 `unregister-scheme.ps1`。

## 源码与构建

第二版源码、指针和离线预览已展开保存在 [ryoma-crimson/](ryoma-crimson/)，完整 ZIP 也包含相同内容。
第一版的原始源码保存在 `v1.0.0` 标签下的 ZIP 中。

版本信息源文件为 [ryoma-crimson/version.json](ryoma-crimson/version.json)；根目录 `VERSION`、`package.json` 和 `versions.json` 记录仓库版本及下载信息。

需要 Windows、Python 3.10+、Node.js，以及 Windows 自带的微软雅黑字体：

```powershell
python -m pip install -r requirements.txt
npm install
python ryoma-crimson/src/build.py
```

如需指定其他 Node.js 路径，可设置 `NODE_EXE` 和 `NODE_PATH`。
离线预览入口为 `ryoma-crimson/preview/index.html`，可暂停动画、切换背景并检查热点。

## 验证

每次发布检查四种尺寸的 Windows 原生加载、热点、透明边界、内嵌像素一致性和 ANI 的 24 帧绘制。
第二版另检查三点的 8 帧轮替，以及除忙碌状态外的 16 个指针文件与第一版逐字节一致。
记录见 [validation.json](ryoma-crimson/validation.json) 和 [version-validation.json](version-validation.json)。验证不会修改系统当前指针或注册表。

Windows 可能根据指针大小和 DPI 设置缩放资源。Word 等应用自行提供的专用指针也可能保持其原有外观。

## 某台显示器上指针颜色变淡

如果桌面和多个应用都出现“松开鼠标时颜色淡、按住时正常”，而另一台电脑正常，可能与 Windows／显卡的指针合成或显示器色彩处理有关，不能仅凭这一现象确定是 HDR。先在出现问题的电脑上排查，无需调整整套指针的配色。

源码目录提供可恢复的兼容性试验：在 PowerShell 中运行 `ryoma-crimson/cursor-color-workaround.ps1`，开启最短指针轨迹（值为 2），然后比较松开、按住和移动鼠标时的颜色。这可能缓解部分电脑的显示问题，但需实际观察确认，也可能带来可见拖影。

如果颜色恢复但拖影明显，可运行 `ryoma-crimson/cursor-color-workaround.ps1 -NoTrail` 试用参数 `-1`，这是未公开支持的无拖尾兼容用法。[NVIDIA 指针褪色的复现记录](https://github.com/kamusmg/nvidia-bright-cursor-fix)报告它可绕开异常的硬件指针绘制路径。效果需在本机确认；软件指针的响应可能受画面刷新影响。脚本不会安装常驻程序，也不会更改指针文件。

脚本首次运行会在同目录备份当前用户的原设置，再次运行不会覆盖备份。运行 `ryoma-crimson/cursor-color-workaround.ps1 -Restore` 恢复，或用 `-Status` 查询。该设置作用于当前用户的所有鼠标指针；只在受影响的电脑上使用，不随指针方案自动启用。微软的 [SystemParametersInfoW 文档](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow)说明了指针轨迹参数。

如果重启后再次变淡，可能是注册表仍保存 `-1`，但 Windows 登录时未将这个特殊值加载到运行时；`-Status` 显示的就是运行时读数。运行 `ryoma-crimson/cursor-color-logon.ps1` 可立即应用修复，并为当前用户创建登录任务，在登录 15 秒后无窗口重新应用一次，无需常驻进程。任务使用当前用户的普通权限，不保存密码。启用期间请保留脚本所在目录。

用 `ryoma-crimson/cursor-color-logon.ps1 -Status` 查看任务；用 `-Remove` 仅移除自动应用。运行原脚本的 `-Restore` 会先移除登录任务，再恢复备份的指针设置。

## 开源许可

原创内容在作者有权授权的范围内采用 [MIT License](LICENSE)。参考图片、第三方角色及商标权益不在授权范围内，详见 [NOTICE.md](NOTICE.md)。分发时请保留许可证和第三方权益说明。
