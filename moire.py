"""
This script generates the grid composite image necessary for the animation

For details on PIL: http://www.pythonware.com/library/pil/handbook/index.htm
Note that we're not using the alpha channel here, just the standard RGB

Some good source images
http://upload.wikimedia.org/wikipedia/commons/b/b4/Vortex-street-animation.gif
http://www.bluffton.edu/~bergerd/classes/cem221/sn-e/SN2.gif
http://upload.wikimedia.org/wikipedia/commons/8/81/ADN_animation.gif
http://www.sci.sdsu.edu/multimedia/mitosis/mitosis.gif
http://i306.photobucket.com/albums/nn247/quantum_flux/Animations/Evolution%20and%20Cosmology/Pangea_animation_03.gif
http://www.umass.edu/molvis/tutorials/dna/an_dna.gif

"""

import os, sys, getopt
import Image, ImageSequence, ImageChops, ImageDraw
import itertools
import random
from collections import deque

def permutegrill(sd, numframes, oldimg, dupheight):
    """Applies a low-level pseudo-random pixel shifts to rows of pixels in the
    image
    """
    
    (xpixels, ypixels) = oldimg.size
    
    # get data from old image (as you already did)
    data = list(oldimg.getdata())
    assert len(data) == (xpixels * ypixels)
    
    # The permutated image data will be accumulated here
    datanew = []
    
    # create empty new image of appropriate format
    newimg = oldimg
    
    # Reseeding each time should ensure that the same seed results in the same
    # permutation
    random.seed(sd)
    
    # Return a random shift between 0 and 7 pixels, duplicating that for dupheight
    # rows
    shiftamounts = []
    for i in range(ypixels/dupheight):
        shiftamounts.extend([random.randrange(0, 100, 1) % numframes] * dupheight)
    
    for (rownum,shiftamount) in zip(range(0,(xpixels * ypixels),xpixels), shiftamounts[:ypixels]):
        
        # Obtain the original row of data
        originalrow = deque(data[rownum:(rownum+xpixels)])
        
        # Perform the actual shift
        originalrow.rotate(shiftamount)
        
        assert len(list(originalrow)) == xpixels
        datanew.extend(list(originalrow))
    
    assert len(datanew) == (xpixels * ypixels)
    
    # insert saved data into the image
    newimg.putdata(datanew)
    
    return newimg
    

def buildGridAndMasks(numframes, xsize, ysize, permutationNo, dupheight):
    """ This helper function builds a grid viewer image and a collection of
        frame mask images to be applied to the """
    
    # First we build the grid
    grid = Image.new("RGB", (xsize, ysize), (256,256,256))
    maskDraw = ImageDraw.Draw(grid, "RGB")
    
    # Draw the lines of the grid
    for i in range(xsize / numframes):
        maskDraw.rectangle([ (i*numframes, 0), 
                            (i*numframes + (numframes-2), ysize)],
                            fill=(0,0,0))
    del maskDraw
    completeMask = permutegrill(permutationNo,numframes,grid,dupheight).copy()
    
    # Next we make the masks, along the same principles, but shift
    # the position by one for each frame
    masks = []
    
    for fi in range(numframes):
        mask = Image.new("RGBA", (xsize, ysize), (0,0,0,0))
        maskDraw = ImageDraw.Draw(mask, "RGBA")
        
        # Draw the lines of the mask
        for i in range(xsize / numframes):
            maskDraw.rectangle([ (i*numframes - fi, 0), 
                            (i*numframes - fi + (numframes-2), ysize) ],
                            fill=(0,0,0,256))
        del maskDraw
        
        masks.append(permutegrill(permutationNo,numframes,mask,dupheight).copy())
    
    return (completeMask, masks)

def get100images(attendeeList, animations, anidir):
    """Runs the moire algorithm to get 100 images, 50 composites and 50 grids,
    using the given list of attendees
    """
    # TODO: run through the various permutations
    for a in attendeeList:
        myImg = animations[0]['file'].copy()
        myImg.save("%s.PNG" % (os.path.join(anidir, a["Attendee #"])))

def main():
    
    # When present get options from the command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:w:o:f:", 
                      ["height=", "width=", "output=", "frames="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(-1)
    
    # This gives the number of frames required in the final animation
    # (if the original doesn't have exactly this many it will be truncated/padded as appropriate)
    resultNumFrames = 8
    # Place to output resulting image files
    outdir = "composites"
    # Directory where animation source files are held
    anidir = "animations"
    # Default size for the resulting composite image and grill
    # (image will be fit, centred into this)
    (qrcodeWidth, qrcodeHeight) = (500, 500)
    # The height for the random grill strip
    dupheight = 8
    
    for o, a in opts:
        if o in ("-h", "--height"):
            qrcodeHeight = a
        elif o in ("-w", "--width"):
            qrcodeWidth = a
        elif o in ("-o", "--output"):
            outdir = a
        elif o in ("-f", "--frames"):
            resultNumFrames = a
        else:
            assert False, "unhandled option"
    
    
    for (n, a) in animations.iteritems():
        print "%s has %s\n" % (n, a.info)
    
    im = animations["vortex"]
    (xsize, ysize) = im.size
    
    # Extract every resultNumFrames of the frames of the animation
    rawSourceFrames = [frame.convert("RGB") for frame in ImageSequence.Iterator(im)]
    sourceFrames = [frame.copy() for frame in rawSourceFrames[:resultNumFrames]]
    
    for (frame,i) in zip(sourceFrames, range(len(sourceFrames))):
        frame.save(os.path.join(outdir,"frame"+str(i)+".PNG"))
    
    # TODO: update this each time
    permutationNo = 1
    
    (grid,masks) = buildGridAndMasks(resultNumFrames, xsize, ysize, permutationNo, dupheight)
    
    blankcanvas = Image.new("RGB", (xsize, ysize), (0,0,0))
    
    # We will accumulate the results to a new image, rather than using the
    # original animate gif
    intermediates = map(lambda (image1, image2) : Image.composite(blankcanvas, image1, image2),
            zip(sourceFrames, masks) )
    # Save the intermediates (for debugging)
    map( lambda (a,b) : a.save(os.path.join(outdir,"foo-"+str(b)+".png")), zip (intermediates, range(len(intermediates))))
    compositeIm = reduce( lambda img1, img2 : ImageChops.add(img1, img2), intermediates)
    
    # Save the grid image and final composite image
    grid.save(os.path.join(outdir,"grid-1.PNG"), dpi=(175, 175))
    compositeIm.save(os.path.join(outdir,"moire-1.PNG"), dpi=(175, 175))

if __name__ == "__main__" :
    main()
