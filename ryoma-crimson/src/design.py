"""Deterministic, editable artwork inspired by the user's red racket reference."""
import math
import json
from pathlib import Path

VERSION_INFO = json.loads((Path(__file__).resolve().parents[1]/'version.json').read_text(encoding='utf-8'))
VERSION = VERSION_INFO['version']
SCHEME_NAME = VERSION_INFO['scheme_name']

SIZES = (32, 48, 64, 96)
FRAMES = 24
JIF = 3
ROLES = [
    ('normal', '正常选择', 'Arrow'), ('help', '帮助选择', 'Help'),
    ('working', '后台运行', 'AppStarting'), ('busy', '忙碌', 'Wait'),
    ('precision', '精确选择', 'Crosshair'), ('text', '文本选择', 'IBeam'),
    ('handwriting', '手写', 'NWPen'), ('unavailable', '不可用', 'No'),
    ('resize-ns', '垂直调整', 'SizeNS'), ('resize-ew', '水平调整', 'SizeWE'),
    ('resize-nwse', '对角调整 ↖↘', 'SizeNWSE'),
    ('resize-nesw', '对角调整 ↗↙', 'SizeNESW'),
    ('move', '移动', 'SizeAll'), ('alternate', '备用选择', 'UpArrow'),
    ('link', '链接选择', 'Hand'), ('location', '位置选择', 'Pin'),
    ('person', '人员选择', 'Person'),
]
PALETTE = {'crimson': '#E62D43', 'ivory': '#FFF4DF',
           'graphite': '#24252B', 'lime': '#D9F348'}
HEAD = 'M48 5 C37 5 31 15 31 28 C31 41 38 51 48 51 C58 51 65 41 65 28 C65 15 59 5 48 5 Z'
DEFS = f'''<defs>
 <linearGradient id="frame" x1="0" y1="0" x2="1" y2=".8">
  <stop stop-color="#FF6973"/><stop offset=".25" stop-color="#E62D43"/>
  <stop offset=".65" stop-color="#B5112C"/><stop offset="1" stop-color="#F34855"/>
 </linearGradient>
 <linearGradient id="grip"><stop stop-color="#17181D"/><stop offset=".5" stop-color="#414148"/><stop offset="1" stop-color="#191A20"/></linearGradient>
 <radialGradient id="ball" cx=".3" cy=".24" r=".8"><stop stop-color="#F9FFAA"/><stop offset=".5" stop-color="#D9F348"/><stop offset="1" stop-color="#9EBD20"/></radialGradient>
 <clipPath id="bed"><path d="{HEAD}"/></clipPath>
 </defs>'''


def outline(body, weight=6):
    # At 32 px the colored core is 2 px, with dark and light contrast rails.
    attrs = 'fill="none" stroke-linejoin="round" stroke-linecap="round"'
    return ''.join(f'<g {attrs} stroke="{color}" stroke-width="{width}">{body}</g>'
                   for color, width in [('#FFF4DF', weight+3.6),
                                        ('#24252B', weight+1.8),
                                        ('#E62D43', weight)])


def racket(size):
    nx, ny = (7, 9) if size <= 32 else ((10, 12) if size <= 48 else (14, 17))
    strings = ''.join(f'<path d="M{32+i*32/(nx-1):.3f} 5 V52"/>' for i in range(nx))
    strings += ''.join(f'<path d="M29 {7+i*42/(ny-1):.3f} H67"/>' for i in range(ny))
    throat = 'M36 46 Q44 58 45.8 68 H50.2 Q52 58 60 46'
    return f'''<g transform="rotate(-38 48 48)">
      <path d="{throat}" fill="none" stroke="#FFF4DF" stroke-width="5.2" stroke-linejoin="round"/>
      <path d="{throat}" fill="none" stroke="#24252B" stroke-width="4"/>
      <path d="{throat}" fill="none" stroke="url(#frame)" stroke-width="2.7"/>
      <g clip-path="url(#bed)" fill="none">
       <g stroke="#303139" stroke-width="{1.05 if size<=48 else .85}" opacity=".8">{strings}</g>
       <g stroke="#FFF4DF" stroke-width="{.65 if size<=48 else .48}" opacity=".96">{strings}</g>
      </g>
      <path d="{HEAD}" fill="none" stroke="#FFF4DF" stroke-width="5.2"/>
      <path d="{HEAD}" fill="none" stroke="#24252B" stroke-width="4.2"/>
      <path d="{HEAD}" fill="none" stroke="url(#frame)" stroke-width="2.9"/>
      <path d="M35 14 Q40 6 48 6.5" fill="none" stroke="#FFB1AA" stroke-width=".65"/>
      <path d="M32.6 30 L34 37 M63.4 30 L62 37" stroke="#FFF4DF" stroke-width="1.2"/>
      <path d="M45 66 H51 V71 H45 Z" fill="#E62D43" stroke="#FFF4DF" stroke-width=".8"/>
      <path d="M44.9 70 H51.1 L51.5 86 L52.1 90 Q48 91.7 43.9 90 L44.5 86 Z" fill="url(#grip)" stroke="#FFF4DF" stroke-width="1"/>
      <path d="M45 73 L51.1 75 M44.9 77 L51.2 79 M44.8 81 L51.3 83 M44.7 85 L51.5 87" stroke="#919095" stroke-width=".7"/>
      <path d="M44.5 89.5 Q48 90.8 51.5 89.5" stroke="#E62D43" stroke-width="1.5" fill="none"/>
      <circle cx="48" cy="4.8" r="1.2" fill="#FFFDF4"/>
    </g>'''


def bounce_state(frame):
    t = frame / FRAMES
    height = math.sin(math.pi*t)  # contact → apex → contact, repeats seamlessly
    return {'x': 48 + 1.3*math.sin(2*math.pi*t),
            'y': 40.5 - 22*height, 'height': height,
            'radius': 6.6 + .45*height,
            'sx': 1 + .14*max(0, 1-height*6),
            'sy': 1 - .17*max(0, 1-height*6)}


def ball(frame, busy=False):
    p = bounce_state(frame)
    r = p['radius'] * (1.05 if busy else 1)
    x, y, h = p['x'], p['y'], p['height']
    # Shadow remains on the bed. Ball moves toward/away from it in screen space.
    shadow = f'<ellipse cx="48" cy="42" rx="{6.2-2.7*h:.3f}" ry="{1.6-.6*h:.3f}" fill="#24252B" opacity="{.52-.29*h:.3f}"/>'
    rings = ''
    if h < .28:
        rings = f'<ellipse cx="48" cy="42" rx="{8+4*h:.3f}" ry="{3+1.5*h:.3f}" fill="none" stroke="#D9F348" stroke-width=".9" opacity="{.7*(1-h/.28):.3f}"/>'
    return f'''<g transform="rotate(-38 48 48)">{shadow}{rings}
     <g transform="translate({x:.4f} {y:.4f}) scale({p['sx']:.4f} {p['sy']:.4f})">
      <circle r="{r+.7:.4f}" fill="#FFF4DF"/>
      <circle r="{r:.4f}" fill="url(#ball)" stroke="#4F611C" stroke-width=".7"/>
      <g transform="rotate({frame*15})" fill="none" stroke="#FFFFE3" stroke-width="1.05" stroke-linecap="round">
       <path d="M{-r*.62:.4f} {-r*.76:.4f} Q{r*.42:.4f} 0 {-r*.62:.4f} {r*.76:.4f} M{r*.62:.4f} {-r*.76:.4f} Q{-r*.42:.4f} 0 {r*.62:.4f} {r*.76:.4f}"/>
      </g>
      <circle cx="{-r*.3:.3f}" cy="{-r*.4:.3f}" r="{r*.15:.3f}" fill="#FCFFD3" opacity=".7"/>
     </g></g>'''


def badge(role):
    body = {
        'help': '<path d="M73 27 C73 19 86 19 86 27 C86 32 79 32 79 38 M79 45 V46"/>',
        'unavailable': '<circle cx="78" cy="44" r="10"/><path d="M71 37 L85 51"/>',
        'link': '<path d="M73 51 V32 C73 28 78 28 78 32 V40 Q84 36 84 43 Q90 40 90 47 L88 58 Q86 64 77 61 L69 51 Q66 45 71 47 Z" fill="#E62D43"/>',
        'location': '<path d="M78 57 Q64 42 70 36 Q79 28 87 38 Q91 45 78 57 Z" fill="#E62D43"/><circle cx="78" cy="40" r="2.5" fill="#FFF4DF" stroke="none"/>',
        'person': '<circle cx="79" cy="34" r="5" fill="#E62D43"/><path d="M69 55 Q69 43 79 43 Q89 43 89 55 Z" fill="#E62D43"/>',
    }.get(role, '')
    return '<g transform="translate(-3 0)">'+outline(body, 2.6)+'</g>' if body else ''


def arrow_body(angle):
    return f'<g transform="rotate({angle} 48 48)"><path d="M48 16 V80 M37 28 L48 16 L59 28 M37 68 L48 80 L59 68"/></g>'


def icon(role, size=96, frame=0):
    center = False
    if role in ('normal', 'help', 'working', 'busy', 'unavailable', 'link', 'location', 'person'):
        base = racket(size)
        if role == 'busy':
            base += ball(frame, busy=True)
            # Three phases of 8 frames: each dot stays lit for 0.4 s at 20 fps.
            base += ''.join(f'<circle cx="{69+j*8}" cy="19" r="2.3" fill="{("#D9F348" if (frame//8)%3==j else "#67666B")}" stroke="#FFF4DF" stroke-width=".6"/>' for j in range(3))
        elif role == 'working':
            base += ball(frame)
        else:
            base += badge(role)
    elif role == 'text':
        center = True
        base = outline('<path d="M48 17 V79 M35 17 H61 M35 79 H61"/>', 6)
        base += '<path d="M43 40 H53 M43 48 H53 M43 56 H53" stroke="#FFF4DF" stroke-width="1.6"/>'
    elif role == 'precision':
        center = True
        base = outline('<path d="M48 13 V34 M48 62 V83 M13 48 H34 M62 48 H83"/><circle cx="48" cy="48" r="12"/>', 5)
        base += '<circle cx="48" cy="48" r="2.3" fill="#D9F348"/>'
    elif role.startswith('resize-'):
        center = True
        angle = {'resize-ns':0, 'resize-ew':90, 'resize-nwse':-45, 'resize-nesw':45}[role]
        base = outline(arrow_body(angle), 6)
        base += '<circle cx="48" cy="48" r="4.8" fill="#D9F348" stroke="#24252B" stroke-width="1.3"/>'
    elif role == 'move':
        center = True
        base = outline(arrow_body(0)+arrow_body(90), 5.4)
        base += '<circle cx="48" cy="48" r="5.2" fill="#D9F348" stroke="#24252B" stroke-width="1.3"/>'
    elif role == 'alternate':
        base = outline('<path d="M48 16 L33 35 H42 V79 H54 V35 H63 Z" fill="#E62D43"/>', 2)
    elif role == 'handwriting':
        base = '<g transform="rotate(38 48 48)">'+outline('<path d="M43 16 H53 V72 L48 84 L43 72 Z" fill="#E62D43"/><path d="M43 72 H53"/>', 2.3)+'<path d="M46 25 V66" stroke="#FFF4DF" stroke-width="1.5"/><path d="M46 78 L48 83 L50 78" fill="#24252B"/></g>'
    else:
        raise ValueError(role)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">{DEFS}{base}</svg>'
    if center:
        hot = (48, 48)
    elif role == 'alternate':
        hot = (48, 15.7)
    elif role == 'handwriting':
        hot = (48-math.sin(math.radians(38))*36, 48+math.cos(math.radians(38))*36)
    else:
        hot = (48-math.sin(math.radians(38))*43.2, 48-math.cos(math.radians(38))*43.2)
    return svg, tuple(round(p*size/96) for p in hot)
