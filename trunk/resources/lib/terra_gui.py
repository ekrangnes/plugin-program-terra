#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
# Author: Espen Krangnes

import os, sys
import xbmcaddon, xbmc, xbmcgui
import xlogger, tdtool, debug, deviceCtrl
from threading import Thread

# self.devices	0:ID		1:name		2:actVal	3:type		4:newVal
STEP_SIZE = 125

TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_DIM = 16

### get addon info and set globals
__addon__      = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__author__       = __addon__.getAddonInfo('author')
__version__      = __addon__.getAddonInfo('version')
__addonpath__    = __addon__.getAddonInfo('path')
__addondir__     = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__addonicon__    = xbmc.translatePath('%s/icon.png' % __addonpath__ ).decode("utf-8")
__localize__     = __addon__.getLocalizedString
__img_path__   = xbmc.translatePath( os.path.join( __addonpath__, 'resources', 'skins', 'Default', 'media') )
settings = xbmcaddon.Addon(id='plugin.program.terra')

#global used to tell the worker thread the status of the window
__windowopen__   = True
winID = 10000

# capture a couple of actions to close the window or change icon upon actions
ACTION_PREVIOUS_MENU = 10
ACTION_BACK = 92
ACTION_HOME = 159
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_SELECT_ITEM = 7

# create a global logger object and set the preamble
tw = xlogger.inst
tw.setPreamble ('[terrainfo]')

#this is the class for creating and populating the window 
class TerraInfoWindow(xbmcgui.WindowXMLDialog): 

	def __init__(self, *args, **kwargs):
		tw.log('script already running, aborting subsequent run attempts', 'standard')


	def onInit(self):
		debug.log("onInit()")
		if (int(settings.getSetting("deviceCount")) == 0):
			self.message("No devices found", "Please configure the addon first.")
			self.close()
		else:
			self.getDevices()
			self.printControls()

	def applyValue(self, ID, type, val):
		debug.log("applyValue("+str(val)+", "+str(ID)+", "+str(type)+", "+str(val)+")")
		if (type == "switch"):
			if (val == "OFF"):
				tdtool.doDevice(settings.getSetting("telldusSource"), ID, TELLSTICK_TURNOFF, 255)
			else:
				tdtool.doDevice(settings.getSetting("telldusSource"), ID, TELLSTICK_TURNON, 
				0)
		elif (type == "dimmer"):
			tdtool.doDevice(settings.getSetting("telldusSource"), ID, TELLSTICK_DIM, int(round((int(val)*255)/1000)))


	def onAction(self, action):
		debug.log("onAction("+ str(action) +")")

		if (action == ACTION_MOVE_UP or action == ACTION_MOVE_DOWN):
			if ( self.devices[self.curSel][3] == "dimmer" ):
				val = int(self.devices[self.curSel][4])
				if(action == ACTION_MOVE_UP):
					if ( int(val) != 1000 ):
						val += STEP_SIZE
				if(action == ACTION_MOVE_DOWN):
					if ( int(val) != 0 ):
						val -= STEP_SIZE
				self.devices[self.curSel][4] = str(val)
				self.buttons[4].setImage(__img_path__+'/'+str(val)+'_active.png')
			elif ( self.devices[self.curSel][3] == "switch" ):
				if ( self.devices[self.curSel][4] == "ON" ):
					self.buttons[4].setImage(__img_path__+'/off_active.png')
					self.devices[self.curSel][4] = "OFF"
				else:
					self.buttons[4].setImage(__img_path__+'/on_active.png')
					self.devices[self.curSel][4] = "ON"
			if (settings.getSetting("quickMode") == "true"):
				self.applyValue(self.devices[self.curSel][0], self.devices[self.curSel][3],  self.devices[self.curSel][4] )
				self.devices[self.curSel][2] = self.devices[self.curSel][4]


		elif (action == ACTION_MOVE_RIGHT):
			self.carusel("right")

		elif (action == ACTION_MOVE_LEFT):
			self.carusel("left")

		elif (action == ACTION_SELECT_ITEM):
			if (settings.getSetting("quickMode") == "false"):
				self.applyValue(self.devices[self.curSel][0], self.devices[self.curSel][3],  self.devices[self.curSel][4] )
				self.devices[self.curSel][2] = self.devices[self.curSel][4]
				self.printStatus()

		elif (action == ACTION_PREVIOUS_MENU or action == ACTION_BACK or action == ACTION_HOME):
			global __windowopen__
			__windowopen__ = False
			self.close()


#	def onClick(self, controlId):
#		debug.log("onAction("+ str(controlId) +")")


	def getDevices(self):
		self.deviceCount = int(settings.getSetting("deviceCount"))
		self.devices = [[0 for x in xrange(5)] for x in xrange(self.deviceCount)]
		for i in xrange(self.deviceCount):
			# self.devices	0:ID		1:name		2:actVal	3:type		4:newVal
			self.devices[i][0]=settings.getSetting("dev"+str(i)+"ID")
			self.devices[i][1]=settings.getSetting("dev"+str(i)+"Name")
			self.devices[i][2]=settings.getSetting("dev"+str(i)+"Val")
			self.devices[i][3]=settings.getSetting("dev"+str(i)+"Type")

			#check if devices have updated values applied outside addon
			if (settings.getSetting("telldusSource") == "Local tdtool"):
				deviceCtrl.terraLocalUpdate()
			#elif (settings.getSetting("telldusSource") == "Telldus Live!"):
			#	deviceCtrl.telldusLiveUpdate()

			#fiddling with settings if the device has changed type with a non updated value
			if (self.devices[i][3] == "switch"):
				if isNumber(self.devices[i][2]):
					self.devices[i][2] = "ON"
			if (self.devices[i][3] == "dimmer"):
				if self.devices[i][2] == "OFF":
					self.devices[i][2] = "0"
				elif self.devices[i][2] == "OFF":
					self.devices[i][2] = "1000"

			# set the right current value
			self.devices[i][4]=self.devices[i][2]


	def printControls(self):
		self.labels = []
		self.buttons = []
		self.selector = []
		
		if self.deviceCount < 7:
			self.range=self.deviceCount
		else:
			self.range = 7
		
		if self.deviceCount==1 or self.deviceCount==2:
			self.offset = 3
			self.curSel = 0
		elif self.deviceCount==3 or self.deviceCount==4:
			self.offset = 2
			self.curSel = 1
		elif self.deviceCount==5 or self.deviceCount==6:
			self.offset = 1
			self.curSel = 2
		else:
			self.offset= 0
			self.curSel = 3 

		# initialize empty controls and labels
		for i in xrange(9):
			if i == 0:
				self.labels.append(xbmcgui.ControlLabel(-110,265, 300, 50, '' ,alignment=0, font='font14', textColor='0xFFFFFFFF',disabledColor='0xFFFF3300',angle=45))
				self.addControl(self.labels[i])
				self.buttons.append(xbmcgui.ControlImage(-70, 300, 100, 100,''))
				self.addControl(self.buttons[i])
			else:
				self.labels.append(xbmcgui.ControlLabel(90+((i-1)*180),265, 300, 50, '' ,alignment=0, font='font14', textColor='0xFFFFFFFF',disabledColor='0xFFFF3300',angle=45))
				self.addControl(self.labels[i])
				self.buttons.append(xbmcgui.ControlImage(50+((i-1)*180), 300, 100, 100,''))
				self.addControl(self.buttons[i])

		# populate initial controls and labels
		for i in range(self.range):
			self.labels[i+1+self.offset].setLabel(str(self.devices[i][1]))
			self.buttons[i+1+self.offset].setImage(__img_path__+'/'+str(self.devices[i][2])+'.png')
		self.buttons[4].setImage(__img_path__+'/'+str(self.devices[self.curSel][2])+'_active.png')

		# add selector
		self.selector.append(xbmcgui.ControlImage(580, 390, 100, 20,''))
		self.addControl(self.selector[0])


	def printStatus(self):
			xbmc.log("--> deviceCount:" + str(self.deviceCount) + " curSel:" + str(self.curSel) + " offset:" + str(self.offset) +" range:" + str(self.range) )
			for i in xrange(0, self.deviceCount):
				# self.devices	0:ID		1:name		2:actVal	3:type		4:newVal
				xbmc.log("--> dev" + str(i) + " - name: " +str(self.devices[i][1]) + ", type: " + str(self.devices[i][3]) + ", ID: " + str(self.devices[i][0]) + ", value: " + str(self.devices[i][2]) ) 


	def findAvailableGuiObject(self):
		for i in xrange(0, 10):
			if 210+i not in [row[0] for row in self.guiLink]:
				return 210+i

	
	def carusel(self, direction):
		
		# set the right actual value
		self.devices[self.curSel][4] = self.devices[self.curSel][2]

		# clear all objects if not at the bookends
		if (self.curSel!=0 and direction=="left") or (self.curSel!=(self.deviceCount-1) and direction=="right"):
			for i in xrange(1,8):
				self.labels[i].setLabel('')
				self.buttons[i].setImage('')
		
		# move left
		if (direction == "left" and self.curSel>=1):
			# move the sticks on the left
			if self.curSel == 3 or self.curSel == 2 or self.curSel == 1:
				self.offset += 1	
			# adjust the range
			if self.curSel<4 and self.deviceCount>4:
				self.range -= 1
			if (self.deviceCount-self.curSel)<4 and self.deviceCount>4:
				self.range += 1
			# move the carusel
			self.curSel -= 1
				
		# move	right
		elif (direction == "right" and self.curSel<(self.deviceCount-1)):
			# move the sticks on the left
			if self.curSel == 2 or self.curSel == 1 or self.curSel == 0:
				self.offset -= 1
			# adjust the range
			if self.curSel<3 and self.deviceCount>4:
				self.range += 1
			if (self.deviceCount-self.curSel)<5 and self.deviceCount>4:
				self.range -= 1
			# move the carusel
			self.curSel += 1

		# print labels and controls
		for i in range(self.range):
			self.labels[self.offset+i+1].setLabel(str(self.devices[self.curSel+i-(3-self.offset)][1]))
			self.buttons[self.offset+i+1].setImage(__img_path__+'/'+str(self.devices[self.curSel+i-(3-self.offset)][2])+'.png')
		#set active
		self.buttons[4].setImage(__img_path__+'/'+str(self.devices[self.curSel][2])+'_active.png')

	
	def onFocus(self, controlId):
		debug.log("onFocus("+ str(controlId) +")")


	def message(self,title, message):
		debug.log("message("+ title +", "+ message +")")	
		dialog = xbmcgui.Dialog()
		dialog.ok(title,message)


def isNumber(s):
	debug.log("isNumber("+ s +")")	
	try:
		float(s)
		return True
	except ValueError:
		return False
			
#custom plarform setting modifications		
if sys.platform == 'darwin':
	__img_path__.replace(" ", "\\ ")
elif sys.platform == 'linux2':
	pass
elif sys.platform == 'windows':
	pass

#run the script
if ( xbmcgui.Window(winID).getProperty("terra.running") == "true" ):
	tw.log('script already running, aborting subsequent run attempts', 'standard')
else:
	xbmcgui.Window(winID).setProperty( "terra.running",  "true" )
	tw.log('attempting to create main script object', 'verbose')
	w = TerraInfoWindow("terra.xml", __addonpath__, "Default")
	w.doModal()
	del w
	del tw
	xbmcgui.Window(winID).setProperty( "terra.running",  "false" )