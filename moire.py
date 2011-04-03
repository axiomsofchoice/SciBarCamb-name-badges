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

"""

import Image, ImageSequence, ImageChops, ImageDraw
import itertools

def buildGridAndMasks(numframes, xsize, ysize):
    """ This helper function builds a grid viewer image and a collection of
        frame mask images to be applied to the """
    
    # First we build the grid
    grid = Image.new("RGB", (xsize, ysize), (256,256,256))
    maskDraw = ImageDraw.Draw(grid, "RGB")
    
    # Draw the lines of the grid
    for i in range(xsize / numframes):
        maskDraw.rectangle([ (i*numframes, 0), 
                            (i*numframes + (resultNumFrames-2), ysize)],
                            fill=(0,0,0))
    del maskDraw
    
    # Next we make the masks, along the same principles, but shift
    # the position by one for each frame
    masks = []
    
    for fi in range(numframes):
        mask = Image.new("RGBA", (xsize, ysize), (0,0,0,0))
        maskDraw = ImageDraw.Draw(mask, "RGBA")
        
        # Draw the lines of the mask
        for i in range(xsize / numframes):
            maskDraw.rectangle([ (i*numframes - fi, 0), 
                            (i*numframes - fi + (resultNumFrames-2), ysize) ],
                            fill=(0,0,0,256))
        del maskDraw
        
        masks.append(mask)
    
    return (grid, masks)
    
def main():
    
    # When present get options from the command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:w:o:", 
                      ["height=", "width=", "output="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(-1)
    
    # This gives the number of frames in the final animation
    resultNumFrames = 8
    
    # Get the animation file and determine it's size
    animations = { "vortex": Image.open("Vortex-street-animation.gif"),
                    "sn2": Image.open("SN2.gif"),
                    "dna": Image.open("ADN_animation.gif"),
                    "mitosis": Image.open("mitosis.gif") }
                    "drift": Image.open("Pangea_animation_03.gif"),
    
    for (n, a) in animations.iteritems():
        print "%s has %s\n" % (n, a.info)
    
    im = animations["vortex"]
    (xsize, ysize) = im.size
    
    # Extract every resultNumFrames of the frames of the animation
    rawSourceFrames = [frame.convert("RGB") for frame in ImageSequence.Iterator(im)]
    sourceFrames = [frame.copy() for frame in rawSourceFrames[:resultNumFrames]]
    
    for (frame,i) in zip(sourceFrames, range(len(sourceFrames))):
        frame.save("frame"+str(i)+".PNG")
    
    (grid,masks) = buildGridAndMasks(resultNumFrames, xsize, ysize)
    
    blankcanvas = Image.new("RGB", (xsize, ysize), (0,0,0))
    
    # We will accumulate the results to a new image, rather than using the
    # original animate gif
    intermediates = map(lambda (image1, image2) : Image.composite(blankcanvas, image1, image2),
            zip(sourceFrames, masks) )
    # Save the intermediates (for debugging)
    map( lambda (a,b) : a.save("foo-"+str(b)+".png"), zip (intermediates, range(len(intermediates))))
    compositeIm = reduce( lambda img1, img2 : ImageChops.add(img1, img2), intermediates)
    
    # Save the grid image and final composite image
    grid.save("grid-1.PNG", dpi=(175, 175))
    compositeIm.save("moire-1.PNG", dpi=(175, 175))

if __name__ == "__main__" :
    main()
