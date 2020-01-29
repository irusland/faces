import cv2
import numpy as np

img = cv2.imread(
    '/Users/irusland/Desktop/UrFU/python/faces/src_test/eye.png', 0)
gimg = img
_, gimg = cv2.threshold(gimg, 40, 255, cv2.THRESH_BINARY)
gimg = cv2.erode(gimg, None, iterations=1)
gimg = cv2.dilate(gimg, None, iterations=9)
gimg = cv2.medianBlur(gimg, 5)

detector_params = cv2.SimpleBlobDetector_Params()
detector_params.filterByArea = True
detector_params.maxArea = 1500
detector = cv2.SimpleBlobDetector_create(detector_params)
keypoints = detector.detect(gimg)
print(keypoints)
cv2.imshow('parsed', gimg)
cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
cv2.drawKeypoints(cimg, keypoints, cimg, (0, 255, 0),
                  cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imshow('img', img)
cv2.imshow('final', cimg)
cv2.waitKey(0)

circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 2, 100)

if circles is None:
    print('No cir')
    exit(0)
circles = np.uint16(np.around(circles))
for i in circles[0, :]:
    # draw the outer circle
    cv2.circle(gimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
    # draw the center of the circle
    cv2.circle(gimg, (i[0], i[1]), 2, (0, 0, 255), 3)

print(circles)
cv2.imshow('detected circles', gimg)
cv2.waitKey(0)
cv2.destroyAllWindows()
