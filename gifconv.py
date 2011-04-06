from PIL import Image, ImageSequence
import sys, os

#im = Image.open("animations\\Copy-of-SN2-2.gif")
im = Image.open("animations\\DNA-large.gif")
original_duration = im.info['duration']

def removeTrans(img):
    """Ensure all transparent pixels are non-transparent"""
    img = img.convert("RGBA")
    
    bkg = Image.new("RGBA", img.size, (0,0,0,0))
    
    #datas = img.getdata()
    #newData = list()
    
    #for item in datas:
    #  if item[3] == 0:
    #    newData.append((255, 255, 255, 0))
    #  else:
    #    newData.append(item)

    #img.putdata(newData)
    
    bkg.paste(img)
    return bkg.copy()


frames = [removeTrans(frame.copy()) for frame in ImageSequence.Iterator(im)]    
#frames.reverse()

from images2gif import writeGif
writeGif("animations\\reverse_1.gif" , frames, duration=original_duration/1000.0, dither=0)

