import argparse
import cv2
import numpy as np

def print_error():
    print("-1")

def print_fire(x, y, w, h):
    print("[%d,%d,%d,%d]" % (x, y, w, h))

def print_no_fire():
    print("0")

#Using romanian notation

#load the image
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
ap.add_argument("-t", "--type", required=False, help="uniform to remove small disturbances, unique to highlight them. Uniform is on by default")
ap.add_argument("-f", "--filter", required=False, help="open to remove false positives, close to remove false negatives, none for nether, none by default")
ap.add_argument("-a", "--all", required=False, help="y to show all images, n to not. n by default")
ap.add_argument("-o", "--output", required=False, help="path for where to save the segmented image")
args = vars(ap.parse_args())

# Arg Strings
image = cv2.imread(args["image"])
sType = str(args["type"])
sFilter = str(args["filter"])
sAll = str(args["all"])
sOutput = str(args["output"])

# ---- Arg error handling ----

#first filter
if (sType == "uniform") or (sType == "None"):
    bUniform = True
elif (sType == "unique"):
    bUniform = False
else:
    #print("Error: " + sType + " is not a valid argument: Please select uniform to remove small disturbances, unique to highlight them")
    print_error()
    exit()

#second filter
if(sFilter == "None") or (sFilter == "none"):
    bSecond_Filter = False;
    bOpen = True
elif (sFilter == "open"):
    bOpen = True
    bSecond_Filter = True;
elif (sFilter == "close"):
    bOpen = False
    bSecond_Filter = True;
else:
    #print("Error: " + sFilter + " is not a valid argument: open to remove false positives, close to remove false negatives, none for nether")
    print_error()
    exit()

#show all images
if (sAll == "y"):
    bAll = True
elif (sAll == "n") or (sAll == "None"):
    bAll = False
else:
    #print("Error: " + sAll + " is not a valid argument: y to show all images, n to not. n by default")
    print_error()
    exit()


#Colour Filtering

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

#hsv is hue sat value

lower_red = np.array([0,120,0]) #0,130,0 filter
upper_red = np.array([10,255,255])

mask = cv2.inRange(hsv, lower_red, upper_red)
res = cv2.bitwise_and(image, image, mask = mask) #both in the frame

kernel = np.ones((5,5), np.uint8)

if (bUniform):
    # Eroding
    image_type = cv2.erode(mask, kernel, iterations=1)
else:
    # Dilating
    image_type = cv2.dilate(mask, kernel, iterations=1)

if(bSecond_Filter):
    if (bOpen):
        image_filtered = cv2.morphologyEx(image_type, cv2.MORPH_OPEN, kernel)  # false positives
    else:
        image_filtered = cv2.morphologyEx(image_type, cv2.MORPH_CLOSE, kernel)  # false negatives

coords = cv2.findNonZero(image_filtered)
if (coords is not None and len(coords) > 1):
    (x, y, w, h) = cv2.boundingRect(coords)

    print_fire(x, y, w, h)

    segmented = image[y:y+h, x:x+w]

    if (sOutput != "None"):
        cv2.imwrite(sOutput, segmented)
else:
    print_no_fire()

if (bAll):
    cv2.imshow('image', image)
    cv2.imshow('res', res)
    cv2.imshow('image_type', image_type)
    cv2.imshow('image_filtered', image_filtered)

    if (segmented is not None):
        cv2.imshow('segmented', segmented)

# determine if there is a fire
if(bSecond_Filter):
    non_zero_post = cv2.countNonZero(image_filtered)
else:
    non_zero_post = cv2.countNonZero(image_type)

# if (non_zero_post > 1):
#     print("FireDetected in " + str(non_zero_post) + " pixels.")
# else:
#     print("No Fire Detected")

cv2.waitKey(0)