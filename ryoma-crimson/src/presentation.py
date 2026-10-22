"""Offline previews, registration scripts, and human-readable documentation."""
import json
from PIL import Image, ImageDraw, ImageFont
from design import ROLES, FRAMES, PALETTE, VERSION, SCHEME_NAME, icon


def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc', size)


def paste_icon(board, root, role, xy, pixels, frame=0, native=False):
    source = root/'preview'/'raster'/f'{role}-{pixels}-{frame:02}.png' if native else root/'preview'/f'{role}.png'
    im = Image.open(source).convert('RGBA')
    if not native:
        im = im.resize((pixels, pixels), Image.Resampling.LANCZOS)
    board.paste(im, xy, im)


def previews(root):
    board = Image.new('RGB', (1600, 1580), '#F7F2E9')
    d = ImageDraw.Draw(board)
    d.rectangle((0,0,1600,10), fill='#E62D43')
    d.text((56,35), 'RYOMA / CRIMSON', font=font(43, True), fill='#24252B')
    d.text((58,99), f'越前龙马 · 绯红球拍指针 / v{VERSION}', font=font(23), fill='#6E6867')
    for j,(name,color) in enumerate(PALETTE.items()):
        x = 939+j*151
        d.rounded_rectangle((x,46,x+26,72), 6, fill=color, outline='#C7BDB4')
        d.text((x,84), color, font=font(14), fill='#6E6867')
    # Three clear promises, visually demonstrated rather than only described.
    for j in range(3):
        x=56+j*500
        d.rounded_rectangle((x,158,x+480,420), 18, fill='#25262D' if j==1 else '#FFFCF6', outline='#DDD4CA')
    paste_icon(board,root,'normal',(72,168),190)
    d.text((276,202),'01 / 红框黑柄',font=font(22,True),fill='#24252B')
    d.text((276,245),'椭圆拍头',font=font(19),fill='#6E6867')
    d.text((276,278),'象牙白线床',font=font(19),fill='#6E6867')
    d.text((276,311),'石墨黑握柄',font=font(19),fill='#6E6867')
    paste_icon(board,root,'working',(570,166),192,frame=7,native=True)
    d.text((776,202),'02 / 线床弹跳',font=font(22,True),fill='#FFF4DF')
    d.text((776,245),'大号荧光网球',font=font(19),fill='#C7C3BB')
    d.text((776,278),'24 帧循环 · 20 fps',font=font(18),fill='#C7C3BB')
    d.text((776,311),'触网压缩 / 升起 / 回落',font=font(16),fill='#C7C3BB')
    paste_icon(board,root,'text',(1072,175),112)
    paste_icon(board,root,'resize-nwse',(1190,175),112)
    d.text((1083,309),'03 / 功能线条加粗',font=font(22,True),fill='#24252B')
    d.text((1083,352),'32 px 下彩色主线约 2 px',font=font(18),fill='#6E6867')
    d.text((58,453),'完整方案 / 17 个 Windows 指针角色',font=font(22,True),fill='#24252B')
    for i,(role,label,_) in enumerate(ROLES):
        x,y = 56+(i%5)*300, 505+(i//5)*242
        d.rounded_rectangle((x,y,x+280,y+222), 14, fill='#FFFCF6', outline='#DDD4CA')
        paste_icon(board,root,role,(x+16,y+7),108)
        # A dark chip alongside a light one exposes contrast at actual cursor sizes.
        d.rounded_rectangle((x+142,y+12,x+266,y+113), 9, fill='#25262D')
        paste_icon(board,root,role,(x+151,y+30),32,native=True)
        paste_icon(board,root,role,(x+201,y+25),48,native=True)
        d.text((x+18,y+125),label,font=font(19,True),fill='#24252B')
        d.text((x+18,y+158),role.upper(),font=font(13),fill='#9A5559')
        d.text((x+18,y+189),'放大示意  /  原尺寸 32 · 48',font=font(13),fill='#827976')
    d.text((661,1305),'CUR + ANI',font=font(35,True),fill='#E62D43')
    d.text((661,1364),'32 / 48 / 64 / 96 px',font=font(23),fill='#24252B')
    d.text((661,1405),'透明背景 · 固定热点 · 浅深背景适配',font=font(18),fill='#6E6867')
    d.line((56,1500,1540,1500), fill='#D3C9BF', width=1)
    d.text((58,1525),'红框 / 象牙白 / 石墨黑 / 荧光网球',font=font(18),fill='#6E6867')
    d.text((1090,1525),f'WINDOWS CURSORS / v{VERSION}',font=font(16),fill='#9A5559')
    board.save(root/'preview'/'overview.png')
    # Same frames as ANI, displayed simultaneously on light and dark backgrounds.
    for role,title in [('working','后台运行 · 网球在线床上循环弹跳'),('busy','忙碌 · 线床弹跳 + 三点轮替提示')]:
        gif=[]
        sprite=Image.new('RGBA',(192*FRAMES,192))
        for frame in range(FRAMES):
            im=Image.open(root/'preview'/'raster'/f'{role}-192-{frame:02}.png')
            sprite.paste(im,(frame*192,0))
            panel=Image.new('RGB',(960,460),'#F7F2E9')
            pd=ImageDraw.Draw(panel)
            pd.rectangle((480,0,960,460),fill='#25262D')
            large=im.resize((320,320),Image.Resampling.LANCZOS)
            for x,color in [(0,'#24252B'),(480,'#FFF4DF')]:
                panel.paste(large,(x+80,32),large)
                pd.text((x+30,370),title,font=font(18,True),fill=color)
                pd.text((x+30,410),'24 帧 / 20 fps / 1.2 秒循环',font=font(16),fill=color)
            gif.append(panel)
        gif[0].save(root/'preview'/f'{role}-bounce.gif',save_all=True,append_images=gif[1:],duration=50,loop=0,disposal=2)
        sprite.save(root/'preview'/f'{role}-sprite.png')


def documentation(root):
    files = [f'{r}.ani' if r in ('busy','working') else f'{r}.cur' for r,_,_ in ROLES]
    ps = '''# Register only; apply from Mouse Properties when you choose.
$ErrorActionPreference = 'Stop'
$scheme = 'Ryoma Crimson'
$cursorDir = Join-Path $PSScriptRoot 'cursors'
$files = @(
FILES
)
$paths = @($files | ForEach-Object { Join-Path $cursorDir $_ })
foreach ($cursorPath in $paths) {
    if (-not (Test-Path -LiteralPath $cursorPath)) { throw "Missing cursor: $cursorPath" }
}
$key = 'HKCU:\\Control Panel\\Cursors\\Schemes'
New-Item -Path $key -Force | Out-Null
New-ItemProperty -Path $key -Name $scheme -Value ($paths -join ',') -PropertyType String -Force | Out-Null
Write-Host 'Registered Ryoma Crimson. Select it in Mouse Properties > Pointers, then Apply.'
Start-Process control.exe -ArgumentList 'main.cpl,,1'
'''.replace('FILES','\n'.join(f"    '{f}'" for f in files))
    ps=ps.replace('Ryoma Crimson',SCHEME_NAME)
    (root/'register-scheme.ps1').write_text(ps,encoding='utf-8-sig')
    (root/'unregister-scheme.ps1').write_text(f"# Switch to a different scheme before unregistering.\nRemove-ItemProperty -Path 'HKCU:\\Control Panel\\Cursors\\Schemes' -Name '{SCHEME_NAME}' -ErrorAction SilentlyContinue\n",encoding='utf-8-sig')
    (root/'register.cmd').write_text('@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0register-scheme.ps1"\r\npause\r\n',encoding='ascii',newline='')
    readme='''# Ryoma Crimson / 越前龙马 · 绯红球拍指针

以用户提供图片中的红框球拍为参考重新绘制的 Windows 指针方案。
共 17 个角色：15 个静态 CUR、2 个动态 ANI；各含 32 / 48 / 64 / 96 px，透明背景。

## 使用

1. 将整个文件夹解压到准备长期保留的位置。
2. 双击 `register.cmd`，或在 PowerShell 运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\register-scheme.ps1`。
3. 在打开的“鼠标属性 → 指针 → 方案”中选择 **Ryoma Crimson**，点击“应用”。

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
'''
    readme=readme.replace('Ryoma Crimson',SCHEME_NAME)
    readme+=f'\n## 版本与许可\n\n当前版本为 v{VERSION}。v1.0.0 使用拍喉环绕忙碌动画，v2.0.0 使用线床弹跳与三点轮替。\n两个版本使用不同方案名，可在 Windows 鼠标属性中切换。\n\n原创内容采用 MIT License；参考图片及第三方角色权益除外，详见同目录 LICENSE 和 NOTICE.md。\n'
    (root/'README.md').write_text(readme,encoding='utf-8')
    cards=[]
    for role,label,_ in ROLES:
        hx,hy=icon(role,64)[1]
        stage=f'<div class="anim {role}" role="img" aria-label="{label}动画"></div>' if role in ('busy','working') else f'<img src="{role}.png" width="144" height="144" alt="{label}">'
        natives=''.join(f'<img src="raster/{role}-{s}-00.png" width="{s}" height="{s}" alt="{s}像素">' for s in (32,48,64))
        cards.append(f'<article><div class="stage">{stage}</div><h3>{label}</h3><small>{role.upper()}</small><div class="native">{natives}</div><button data-role="{role}" data-label="{label}" data-x="{hx}" data-y="{hy}">试用此指针</button></article>')
    html=(root/'src'/'preview-template.html').read_text(encoding='utf-8')
    html=html.replace('<!-- CARDS -->',''.join(cards)).replace('/* HOTSPOTS */',json.dumps({r:icon(r,64)[1] for r,_,_ in ROLES})).replace('<!-- VERSION -->',VERSION)
    (root/'preview'/'index.html').write_text(html,encoding='utf-8')
