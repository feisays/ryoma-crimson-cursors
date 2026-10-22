"""Build the standalone Ryoma Crimson Windows cursor collection."""
from pathlib import Path
from PIL import Image
import json
import os
import struct
import subprocess
import sys
import zipfile
from design import SIZES, FRAMES, JIF, ROLES, PALETTE, VERSION, SCHEME_NAME, icon
from presentation import previews, documentation
ROOT = Path(__file__).resolve().parents[1]


def cur_bytes(images, hotspots):
    payloads = []
    for im in images:
        im = im.convert('RGBA')
        w,h = im.size
        stride = ((w+31)//32)*4
        mask = bytearray(stride*h)
        for y in range(h):
            for x in range(w):
                if im.getpixel((x,y))[3] == 0:
                    mask[(h-1-y)*stride+x//8] |= 0x80 >> (x%8)
        # CUR file pixels use straight BGRA; Windows premultiplies when loading.
        bgra = im.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes('raw','BGRA')
        dib = struct.pack('<IiiHHIIiiII',40,w,h*2,1,32,0,len(bgra)+len(mask),0,0,0,0)
        payloads.append(dib + bgra + mask)
    offset = 6+16*len(images)
    out = struct.pack('<HHH',0,2,len(images))
    for im,hot,payload in zip(images,hotspots,payloads):
        out += struct.pack('<BBBBHHII',*im.size,0,0,*hot,len(payload),offset)
        offset += len(payload)
    return out + b''.join(payloads)


def chunk(tag,data):
    return tag + struct.pack('<I',len(data)) + data + (b'\0' if len(data)%2 else b'')


def ani_bytes(frames):
    anih = struct.pack('<9I',36,len(frames),len(frames),0,0,32,1,JIF,1)
    body = b'ACON' + chunk(b'anih',anih)
    body += chunk(b'LIST',b'fram'+b''.join(chunk(b'icon',f) for f in frames))
    return b'RIFF'+struct.pack('<I',len(body))+body


def main():
    raster=ROOT/'preview'/'raster'
    vector=ROOT/'src'/'svg'
    for directory in (raster, vector, ROOT/'cursors'):
        directory.mkdir(parents=True,exist_ok=True)
    jobs=[]
    manifest=[]
    for role,label,reg in ROLES:
        count=FRAMES if role in ('busy','working') else 1
        hotspots={}
        for frame in range(count):
            (vector/f'{role}-{frame:02}.svg').write_text(icon(role,96,frame)[0],encoding='utf-8')
            for size in SIZES:
                svg,hot=icon(role,size,frame)
                hotspots[str(size)]=hot
                jobs.append({'svg':svg,'size':size,'output':str(raster/f'{role}-{size}-{frame:02}.png')})
        jobs.append({'svg':icon(role,96)[0],'size':320,'output':str(ROOT/'preview'/f'{role}.png')})
        manifest.append({'role':role,'label':label,'windows_role':reg,'file':f'{role}.ani' if count>1 else f'{role}.cur','hotspots':hotspots})
    for role in ('busy','working'):
        for frame in range(FRAMES):
            jobs.append({'svg':icon(role,96,frame)[0],'size':192,'output':str(raster/f'{role}-192-{frame:02}.png')})
    jobs_file=ROOT/'src'/'render-jobs.json'
    jobs_file.write_text(json.dumps(jobs),encoding='utf-8')
    subprocess.run([os.environ.get('NODE_EXE','node'),str(ROOT/'src'/'render.cjs'),str(jobs_file)],check=True)
    jobs_file.unlink()
    for item in manifest:
        role=item['role']
        count=FRAMES if role in ('busy','working') else 1
        frames=[]
        for frame in range(count):
            images=[Image.open(raster/f'{role}-{s}-{frame:02}.png') for s in SIZES]
            for im,size in zip(images,SIZES):
                bounds=im.getbbox()
                assert bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<size and bounds[3]<size,(role,size,frame,bounds)
            frames.append(cur_bytes(images,[item['hotspots'][str(s)] for s in SIZES]))
        (ROOT/'cursors'/item['file']).write_bytes(ani_bytes(frames) if count>1 else frames[0])
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'theme.json').write_text(json.dumps({'name':SCHEME_NAME,'version':VERSION,'palette':PALETTE,'sizes':SIZES,'fps':20,'loop_seconds':1.2,'frames':FRAMES,'animation':{'working':'string-bed bounce','busy':'string-bed bounce with three cycling dots'},'status_dot_seconds':.4,'line_core_at_32_px':2,'ball_diameter_at_32_px':[4.4,4.7]},ensure_ascii=False,indent=2),encoding='utf-8')
    previews(ROOT)
    documentation(ROOT)
    subprocess.run([sys.executable,str(ROOT/'src'/'verify_native.py')],check=True)
    package=ROOT.parent/f'Ryoma-Crimson-v{VERSION}-Windows.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and not {'__pycache__'}.intersection(p.relative_to(ROOT).parts):
                z.write(p,Path(ROOT.name)/p.relative_to(ROOT))
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
    print(json.dumps({'package':str(package),'roles':len(manifest),'zip_bytes':package.stat().st_size},ensure_ascii=False))

if __name__=='__main__':
    main()
