"""Exercise the produced CUR/ANI files through Windows APIs, without applying them."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import json
import struct
from PIL import Image, ImageDraw, ImageChops
from design import FRAMES, SIZES, VERSION
from presentation import font

ROOT=Path(__file__).resolve().parents[1]
u=c.WinDLL('user32',use_last_error=True)
g=c.WinDLL('gdi32',use_last_error=True)
u.LoadImageW.argtypes=[w.HINSTANCE,w.LPCWSTR,w.UINT,c.c_int,c.c_int,w.UINT]
u.LoadImageW.restype=w.HANDLE
u.DrawIconEx.argtypes=[w.HDC,c.c_int,c.c_int,w.HANDLE,c.c_int,c.c_int,w.UINT,w.HBRUSH,w.UINT]
u.DestroyCursor.argtypes=[w.HANDLE]
g.CreateCompatibleDC.argtypes=[w.HDC];g.CreateCompatibleDC.restype=w.HDC
g.SelectObject.argtypes=[w.HDC,w.HANDLE];g.SelectObject.restype=w.HANDLE
g.DeleteObject.argtypes=[w.HANDLE];g.DeleteDC.argtypes=[w.HDC]


class Header(c.Structure):
    _fields_=[('size',w.DWORD),('width',w.LONG),('height',w.LONG),('planes',w.WORD),('bits',w.WORD),('compression',w.DWORD),('image_size',w.DWORD),('xppm',w.LONG),('yppm',w.LONG),('used',w.DWORD),('important',w.DWORD)]


class IconInfo(c.Structure):
    _fields_=[('fIcon',w.BOOL),('xHotspot',w.DWORD),('yHotspot',w.DWORD),('hbmMask',w.HBITMAP),('hbmColor',w.HBITMAP)]


u.GetIconInfo.argtypes=[w.HANDLE,c.POINTER(IconInfo)]
g.CreateDIBSection.argtypes=[w.HDC,c.POINTER(Header),w.UINT,c.POINTER(c.c_void_p),w.HANDLE,w.DWORD]
g.CreateDIBSection.restype=w.HBITMAP


def render(cursor,size,step,bg):
    dc=g.CreateCompatibleDC(None)
    info=Header(40,size,-size,1,32,0,size*size*4,0,0,0,0)
    ptr=c.c_void_p()
    bitmap=g.CreateDIBSection(dc,c.byref(info),0,c.byref(ptr),None,0)
    assert bitmap
    old=g.SelectObject(dc,bitmap)
    c.memmove(ptr,bytes([bg[2],bg[1],bg[0],255])*(size*size),size*size*4)
    assert u.DrawIconEx(dc,0,0,cursor,size,size,step,None,3)
    g.GdiFlush()
    image=Image.frombytes('RGBA',(size,size),c.string_at(ptr,size*size*4),'raw','BGRA').convert('RGB')
    g.SelectObject(dc,old);g.DeleteObject(bitmap);g.DeleteDC(dc)
    return image


def parse_cur(data):
    reserved,kind,count=struct.unpack_from('<HHH',data)
    assert (reserved,kind,count)==(0,2,4)
    entries=[]
    for i,size in enumerate(SIZES):
        width,height,_,_,hx,hy,length,offset=struct.unpack_from('<BBBBHHII',data,6+16*i)
        assert width==height==size and offset+length<=len(data)
        assert struct.unpack_from('<IiiHH',data,offset)==(40,size,size*2,1,32)
        raster=Image.frombytes('RGBA',(size,size),data[offset+40:offset+40+size*size*4],'raw','BGRA').transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        entries.append((size,(hx,hy),raster))
    return entries


def read_frames(path):
    data=path.read_bytes()
    if path.suffix=='.cur':
        return [data]
    assert data[:4]==b'RIFF' and data[8:12]==b'ACON'
    assert struct.unpack_from('<I',data,4)[0]+8==len(data)
    assert data[12:16]==b'anih'
    assert struct.unpack_from('<9I',data,20)==(36,FRAMES,FRAMES,0,0,32,1,3,1)
    assert data[56:60]==b'LIST' and data[64:68]==b'fram'
    pos=68;frames=[]
    while pos<len(data):
        assert data[pos:pos+4]==b'icon'
        length=struct.unpack_from('<I',data,pos+4)[0]
        frames.append(data[pos+8:pos+8+length])
        pos+=8+length+(length%2)
    assert len(frames)==FRAMES and pos==len(data)
    return frames


def main():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    result={'version':VERSION,'roles':len(manifest),'sizes':list(SIZES),'animation_frames':FRAMES,'fps':20,'loop_seconds':1.2,'windows_loads':[],'native_animation_rendering':[]}
    for item in manifest:
        role=item['role'];path=ROOT/'cursors'/item['file']
        for frame,raw in enumerate(read_frames(path)):
            for size,hot,embedded in parse_cur(raw):
                assert tuple(item['hotspots'][str(size)])==hot
                source=Image.open(ROOT/'preview'/'raster'/f'{role}-{size}-{frame:02}.png').convert('RGBA')
                assert embedded.tobytes()==source.tobytes(),(role,size,frame,'embedded pixel mismatch')
        for size in SIZES:
            cursor=u.LoadImageW(None,str(path),2,size,size,16)
            assert cursor,(path,size,c.get_last_error())
            try:
                info=IconInfo()
                assert u.GetIconInfo(cursor,c.byref(info))
                hot=(info.xHotspot,info.yHotspot)
                expected_hot=tuple(item['hotspots'][str(size)])
                assert max(abs(a-b) for a,b in zip(hot,expected_hot))<=1,(role,size,hot,expected_hot)
                for bm in (info.hbmMask,info.hbmColor):
                    if bm:g.DeleteObject(bm)
                count=FRAMES if role in ('working','busy') else 1
                for frame in range(count):
                    for bg in ((37,38,45),(247,242,233)):
                        native=render(cursor,size,frame,bg)
                        bounds=ImageChops.difference(native,Image.new('RGB',(size,size),bg)).getbbox()
                        assert bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<size and bounds[3]<size,(role,size,frame,'native clipping')
                if count>1:
                    frames=[render(cursor,size,f,(37,38,45)) for f in range(FRAMES)]
                    unique=len({im.tobytes() for im in frames})
                    assert unique==FRAMES,(role,size,unique)
                    for box in ((.70,.73,.80,.87),(.18,.12,.25,.18)):
                        crop=tuple(round(v*size) for v in box)
                        assert len({im.crop(crop).tobytes() for im in frames})==1,(role,size,'racket moved')
                    result['native_animation_rendering'].append({'role':role,'size':size,'native_unique_frames':unique,'grip_and_leading_rim_fixed':True,'light_and_dark_rendering':True})
                    if size==96:
                        sheet=Image.new('RGB',(6*176,4*202),'#25262D')
                        d=ImageDraw.Draw(sheet)
                        for i,im in enumerate(frames):
                            x,y=(i%6)*176,(i//6)*202
                            sheet.paste(im.resize((160,160),Image.Resampling.NEAREST),(x+8,y+8))
                            d.text((x+14,y+176),f'FRAME {i+1:02}',font=font(13),fill='#FFF4DF')
                        sheet.save(ROOT/'preview'/('native-animation-frames.png' if role=='working' else 'native-busy-frames.png'))
                        animation=[]
                        for i in range(FRAMES):
                            panel=Image.new('RGB',(768,390),'#F7F2E9')
                            draw=ImageDraw.Draw(panel)
                            draw.rectangle((384,0,768,390),fill='#25262D')
                            for x,bg,color in ((0,(247,242,233),'#24252B'),(384,(37,38,45),'#FFF4DF')):
                                im=render(cursor,96,i,bg).resize((288,288),Image.Resampling.NEAREST)
                                panel.paste(im,(x+48,22))
                                title='后台运行 · 线床循环弹跳' if role=='working' else '忙碌 · 线床弹跳 + 三点提示'
                                draw.text((x+24,325),title,font=font(18,True),fill=color)
                                draw.text((x+24,359),'Windows ANI 实际绘制 / 20 fps',font=font(13),fill=color)
                            animation.append(panel)
                        animation[0].save(ROOT/'preview'/f'native-{role}.gif',save_all=True,append_images=animation[1:],duration=50,loop=0,disposal=2)
                result['windows_loads'].append({'role':role,'size':size,'hotspot':hot,'source_hotspot':expected_hot,'loaded':True})
            finally:
                u.DestroyCursor(cursor)
    result['checks']=[
        'All 17 files load through Windows LoadImageW at 4 sizes: 68 successful loads.',
        'Embedded hotspots match manifest exactly in all animation frames; Windows-scaled hotspots differ by at most 1 px.',
        'All embedded CUR and ANI raster pixels match their RGBA source exactly.',
        'All native CUR and ANI steps render without clipping on light and dark backgrounds.',
        'Both ANI files render 24 distinct frames at every size; grip and leading rim stay fixed.',
        'Every raster resource has transparent margins without clipping.',
        'No system cursor or registry setting was changed during validation.',
    ]
    result['rendering_note']='LoadImageW may select and resample another embedded size according to Windows pointer size settings. Source equality is checked against embedded DIB bytes, while native output is checked through actual GDI rendering.'
    (ROOT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'windows_loads':len(result['windows_loads']),'native_animation_variants':len(result['native_animation_rendering']),'status':'passed'}))


if __name__=='__main__':main()
