# USAGE
# python detect_shapes.py --image shapes_and_colors.png

# import the necessary packages
import argparse
import imutils
import cv2
import numpy

#Initiates the program by loading in the template images

def init():
	path = "/home/hk7/catkin_ws/src/shape_detection_matching/scripts"
	template1 = cv2.GaussianBlur(cv2.cvtColor(cv2.imread(path+"/templ_3.png"), cv2.COLOR_BGR2GRAY), (3, 3), 0)
	template2 = cv2.GaussianBlur(cv2.cvtColor(cv2.imread(path+"/templ_4.png"), cv2.COLOR_BGR2GRAY), (1, 1), 0)
	template3 = cv2.GaussianBlur(cv2.cvtColor(cv2.imread(path+"/templ_5.png"), cv2.COLOR_BGR2GRAY), (1, 1), 0)
	template4 = cv2.GaussianBlur(cv2.cvtColor(cv2.imread(path+"/templ_6.png"), cv2.COLOR_BGR2GRAY), (1, 1), 0)
	templates = [template1,template2,template3,template4]
	return templates

##Imports and transforms the image to be analyzed
def load(image):

    # construct the argument parse and parse the arguments
    #ap = argparse.ArgumentParser()
    #ap.add_argument("-i", "--image", required=True,
    #help="path to the input image")
    #args = vars(ap.parse_args())

    # load the image and resize it to a smaller factor so that
    # the shapes can be approximated better
    #image = cv2.imread(args["image"])

    resized = imutils.resize(image, width=300) # imutils only use width for resize where cv2.resize use both height n width
    ratio = image.shape[0] / float(resized.shape[0])

    # convert the resized image to grayscale, blur it slightly,
    # and threshold it
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blurred, 58, 255, cv2.THRESH_BINARY)[1]
    height = thresh.shape[0]
    width = thresh.shape[1]
    #Blocks out the top and the bottom of the image.
    #cv2.rectangle(thresh, (0, 0), (300, 70), (255, 255, 255), -1)
    #cv2.rectangle(thresh, (0, 190), (300, 223), (255, 255, 255), -1)
    thresh = thresh[90:90+height, 0:width]
    height = thresh.shape[0]
    thresh = thresh[0:height-30, 0:width]
    #Inverts the image.
    thresh = cv2.bitwise_not(thresh)
    ## IMAGE AFTER THRESHOLD
    #cv2.imshow("Image", thresh)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return (thresh,ratio,image)

##Searches for target in the imported image
def search(thresh,templates,ratio,image):
    found = False
    identifier = False
    n = 0
    threshold = 0.86
    candidates = []
    height = image.shape[1]
    width = image.shape[0]

    for templ in templates:
        n = n+1
        for sque in numpy.linspace(0.55,1,4)[::-1]:
            w1 = templ.shape[0]
            h1 = templ.shape[1]
            squeezed = cv2.resize(templ,((sque*w1).astype("int"), h1), interpolation = cv2.INTER_AREA)
            for scale in numpy.linspace(0.7,2.5,8)[::-1]:
                # resize the image according to the scale, and keep track
                # of the ratio of the resizing
                scaled = imutils.resize(squeezed, width = int(squeezed.shape[1] * scale))
                res = cv2.matchTemplate(thresh,scaled,cv2.TM_CCOEFF_NORMED)
                w = scaled.shape[0]
                h = scaled.shape[1]
                if res.max()>=threshold:
                    #print("Shape Match!",res.max())
                    result = numpy.where(res == numpy.amax(res))
                    if len(result[0])>1:
                        result = (result[0][0],result[1][0])
                    cX = int((result[1]+w/2) * ratio)
                    cY = int(((result[0]+h/2)+90) * ratio)
                    if 	(cX>width) or (cY>height):
                        #print("Does not fit in frame")
                        continue
                    color1 = (image[cX, cY]).astype(int)
                    color2 = (image[cX+3, cY+3]).astype(int)
                    color3 = (image[cX-3, cY-3]).astype(int)
                    color4 = (image[cX+3, cY-3]).astype(int)
                    color5 = (image[cX-3, cY+3]).astype(int)
                    ## Checks that color is even around detected point
                    #print(abs(color1))
                    #print(abs(color3))
                    if (abs(color1-color2)<3).all() & (abs(color1-color3)<3).all() & (abs(color1-color4)<3).all() & (abs(color1-color5)<3).all():
                        #print("Similar color")
						pass
                    else:
                        #print("Not similar color")
                        continue

                    ## Checks that the detected area is not Black/Super dark.
                    if (abs(color1)>120).all():
                        pass
                        #print("Brightness OK")
                    else:
                        #print("Brightness TO DARK")
                        continue
                    if n == 1:
                        identifier = "Triangle"
                    if n == 2:
                        idetifier = "Square"
                    if n == 3:
                        identifier = "Pentagon"
                    if n == 4:
                        identifier = "Hexagon"

                    candidates.append([cX, cY, res.max(),identifier])
                    found = True

    if found == False:
        return (False,False,False)
    if found == True:
        max = 0
        #print(candidates)
        for candidate in candidates:
            if candidate[2]>max:
                cX = candidate[0]
                cY = candidate[1]
                identifier = candidate[3]
		cX = int(cX)
		cY = int(cY)
        return(cX,cY,identifier)


##Draws a circle on the identified target
def draw(x,y,image):
    #print("Target has x-pos:", x)
    #print("Target has y-pos:", y)
    image = cv2.circle(image, (x,y), 10, (0, 255, 0), 2)
    return image

if __name__ == "__main__":
	templates = init()
	image = cv2.imread("16.png")
	(thresh,ratio,image) = load(image)

	(x,y,identifier) = search(thresh,templates,ratio,image)
	if (x,y, identifier) != (False,False,False):
		image = draw(x,y,image)
	    #cv2.imshow("Image", image)
        #cv2.waitKey(0)
