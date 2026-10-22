# Ryoma Crimson v2.0.0 / 越前龙马 · 绯红球拍指针

以用户提供图片中的红框球拍为参考重新绘制的 Windows 指针方案。
共 17 个角色：15 个静态 CUR、2 个动态 ANI；各含 32 / 48 / 64 / 96 px，透明背景。

## 使用

1. 将整个文件夹解压到准备长期保留的位置。
2. 双击 `register.cmd`，或在 PowerShell 运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\register-scheme.ps1`。
3. 在打开的“鼠标属性 → 指针 → 方案”中选择 **Ryoma Crimson v2.0.0**，点击“应用”。

注册脚本只添加当前用户的方案并打开设置，无需管理员权限。应用后不要移动文件夹。
也可在鼠标属性中手动浏览 `cursors` 目录中的文件。卸载时先切换其他方案，
再运行 `unregister-scheme.ps1`，最后删除文件夹。

## 本次设计

- 配色：绯红 #E62D43、象牙白 #FFF4DF、石墨黑 #24252B、荧光黄绿 #D9F348。
- 球拍：参考图的椭圆拍头、红色拍框、浅色网线、黑色握柄；小尺寸简化线床避免糊成一片。
- 文本、缩放等功能线条：96 单位母版中主线 6，32 px 实际主线约 2 px；与旧方案主线 1.15 相比明显加粗，配深浅双层边线。
- 网球：后台运行直径约 13.2–14.1 母版单位，32 px 资源中约 4.4–4.7 px，约为旧后台网球直径的 2.3 倍。
- 后台运行：球拍固定，球在线床范围内从触网位置升起、到顶点、再落回；接触时轻微压缩并出现触网圈，阴影随高度变化。
- 忙碌：球拍固定，大网球在线床循环弹跳，拍头右上方三点轮替点亮；每点亮 8 帧，即 0.4 秒。
- 两个动画均为 24 帧、20 fps、1.2 秒一循环，热点固定，不随网球移动。
- 正常选择等球拍角色的热点在拍头顶部白点；文本、准星、缩放与移动在中心。详见 manifest.json。

## 预览与验证

- `preview/index.html`：离线预览，含两种背景、暂停、原尺寸图、角色切换及热点点击试用。
- `preview/overview.png`：完整设计总览。
- `preview/working-bounce.gif`：后台运行动画演示。
- `preview/busy-bounce.gif`：忙碌状态的线床弹跳与三点轮替动画演示。
- `preview/native-animation-frames.png`：由 Windows 实际绘制的 ANI 帧。
- `preview/native-working.gif`：Windows 实际绘制的后台运行动画，含浅深背景。
- `preview/native-busy.gif`：Windows 实际绘制的忙碌弹跳与三点动画，含浅深背景。
- `validation.json`：Windows 加载、热点、透明边界、动画帧及固定拍柄检查结果。

构建：Python + Pillow、Node.js + sharp。设置 NODE_EXE 和 NODE_PATH 后运行 `python src/build.py`。
`src/design.py` 是矢量几何及配色，`src/svg` 保存全部母版与动画帧。

验证时使用 Windows LoadImageW / DrawIconEx 加载并绘制资源，不切换系统当前指针。
尚未在用户桌面实际应用方案；系统具体显示尺寸取决于指针大小与 DPI 设置。
Windows 根据指针大小设置选择并缩放资源时，热点取整可能与源文件坐标相差 1 px。
参考图保存在 reference/ryoma-reference.png；这是参考图启发的自制方案。

## 版本与许可

当前版本为 v2.0.0。v1.0.0 使用拍喉环绕忙碌动画，v2.0.0 使用线床弹跳与三点轮替。
两个版本使用不同方案名，可在 Windows 鼠标属性中切换。

原创内容采用 MIT License；参考图片及第三方角色权益除外，详见同目录 LICENSE 和 NOTICE.md。
