#!/usr/bin/env python
import rospy
import imutils
import cv2
import numpy as np
from cv_bridge import CvBridge
from detect_shapes_matching import init, load, search, draw
from sensor_msgs.msg import Image
from apriltag_ros.msg import geometricpixels
from std_msgs.msg import String

image_pub = rospy.Publisher("/shape/image",Image, queue_size = 10)
xy_pub = rospy.Publisher("/shape/coordinates", geometricpixels, queue_size = 10)
templates = None

def node_init():
	global templates

	# subscribed Topic
	subscriber = rospy.Subscriber("/raspicam_node/image",Image, callback,  queue_size = 10)
	templates = init()


def callback(ros_data):
	global templates
	#### direct conversion to CV2 ####
	bridge = CvBridge()
	image = bridge.imgmsg_to_cv2(ros_data, desired_encoding='passthrough')

	(thresh,ratio,image) = load(image)

	(x,y,identifier) = search(thresh,templates,ratio,image)

	if (x,y,identifier) != (False,False,False):
		geo_pixels = geometricpixels()
		geo_pixels.geometric_x = x
		geo_pixels.geometric_y = y
		xy_pub.publish(geo_pixels)
		image = draw(x,y,image)

    # Publish new image
	image_ros = bridge.cv2_to_imgmsg(image, encoding="passthrough")

	image_pub.publish(image_ros)

    	#self.subscriber.unregister()

def main():
	node_init()
	rospy.init_node('shape_node', anonymous=False)
	try:
		rospy.spin()
	except KeyboardInterrupt:
		print "Shutting down ROS Image feature detector module"
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()
