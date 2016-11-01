import picamera
from SimpleCV import*

def get_camera_image():
	with picamera.PiCamera() as camera:
		camera.resolution = (1024,768)
		camera.awb_mode = 'off'
		camera.capture('tmp.jpg')
	return Image('tmp.jpg')
