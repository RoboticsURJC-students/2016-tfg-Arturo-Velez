from sensors import sensor
from gui import colorFilterWidget as CFW
import cv2
import numpy as np

class MyAlgorithm():
	def __init__(self, sensor):
		self.sensor = sensor
		self.CFW = CFW
	
				
      
	def execute(self):
		input_image = self.sensor.getImage()
		imgcentery = 130.0
		imgcenterx = 145.0
		zrefmax = 450.0
		zrefmin = 350.0
		zref = 400.0
		
		
		def chkImg(img):
			Al = len(img)
			An = len(img[0])
			blancos = 0
			for i in range(Al):
				for j in range(An):
					if (img[i][j] != 0):
						blancos = blancos + 1
			
			return blancos
			
		def isDark(img):
			wh = chkImg(img)
			
			return (wh < 31)
			
		def setHeight(img):
			
			blancos = chkImg(img)
			
			if (blancos < zrefmin):
				return ((float(blancos)-zref)/zref)
			elif (blancos > zrefmax):
				return ((float(blancos)-zref)/zref)
			elif (blancos == zref ):
				return 0

		if input_image != None:
			#self.sensor.setColorImage(input_image)
			
			hsv = cv2.cvtColor(input_image, cv2.COLOR_BGR2HSV)

            
			lower = np.array([50,140,50])
			upper = np.array([120,255,255])

	    
			mask = cv2.inRange(hsv, lower, upper)
			maskshow = mask.copy()
			res = cv2.bitwise_and(input_image,input_image, mask= mask)

			
			res = cv2.cvtColor(res, cv2.COLOR_HSV2RGB)
			
			if isDark(mask):
				vz = 1
				self.sensor.sendCMDVel(0, 0, vz, 0, 0, 0)
			else:
				contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
				cnt = contours[0]
				M = cv2.moments(cnt)
				centroid_x = int(M['m10']/M['m00'])
				centroid_y = int(M['m01']/M['m00'])
				res_b, res_g, res_r = cv2.split(res)
				res_r[centroid_y][centroid_x] = 255
				res_r[centroid_y+1][centroid_x] = 255
				res_r[centroid_y-1][centroid_x] = 255
				res_r[centroid_y][centroid_x+1] = 255
				res_r[centroid_y][centroid_x-1] = 255
				res = cv2.merge([res_r, res_g, res_b])
				
			
				vx = (imgcenterx-float(centroid_x))/imgcenterx
				vy = (imgcentery-float(centroid_y))/imgcentery
				vz = setHeight(mask)
				if (vz == None):
					vz = 0
					
				print(vz)
				
				self.sensor.sendCMDVel(vx, vy, vz, 0, 0, 0)
			
			
		
		if res != None:
			
			self.sensor.setColorImage(res)
			
		
		
		if maskshow != None:
			self.sensor.setThresoldImage(maskshow)

