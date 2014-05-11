#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
# Author: Espen Krangnes

import os, sys
import xbmcaddon, xbmc, xbmcgui
import xlogger, tdtool, debug
from threading import Thread

# self.devices	0:ID		1:name		2:actVal	3:type		4:controlID		5:newVal
MAX_DEVICES = 8
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
settings = xbmcaddon.Addon(id='plugin.program.terra')
__img_path__   = xbmc.translatePath( os.path.join( __addonpath__, 'resources', 'skins', 'Default', 'media') )

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

# create a global logger object and set the preamble
tw = xlogger.inst
tw.setPreamble ('[telldusinfo]')

#this is the class for creating and populating the window 
class TelldusInfoWindow(xbmcgui.WindowXMLDialog): 

	def __init__(self, *args, **kwargs):
		tw.log('script already running, aborting subsequent run attempts', 'standard')


	def onInit(self):
		debug.log("onInit()")
		if (int(settings.getSetting("deviceCount")) == 0):
			self.message("No devices found", "Please configure the addon first.")
		self.getDevices()
		self.printControls()
		self.applyNavigation()

		
	def onAction(self, action):
		debug.log("onAction("+ str(action) +")")
		if (action == ACTION_MOVE_RIGHT or action == ACTION_MOVE_LEFT):
			if ( self.devices[self.curLine][3] == "DIMMER" ):
				val = int(self.devices[self.curLine][5])
				if(action == ACTION_MOVE_RIGHT):
					if ( int(val) >= 1000 ):
						val = 0 
					else:
						val +=STEP_SIZE
				if(action == ACTION_MOVE_LEFT):
					if ( int(val) <= 0 ):
						val = 1000
					else:
						val -=STEP_SIZE
				self.devices[self.curLine][5] = str(val)
				self.getControl(210+self.curLine).setImage(__img_path__+'/'+str(val)+'_active.png')
			elif ( self.devices[self.curLine][3] == "SWITCH" ):
				if ( self.devices[self.curLine][5] == "ON" ):
					self.getControl(210+self.curLine).setImage(__img_path__+'/off_active.png')
					self.devices[self.curLine][5] = "OFF"
				else:
					self.getControl(210+self.curLine).setImage(__img_path__+'/on_active.png')
					self.devices[self.curLine][5] = "ON"
		elif (action == ACTION_MOVE_UP):
			if (self.curLine > 0):
				self.curLine -= 1
				self.getControl(210+self.curLine+1).setImage(__img_path__+'/'+self.devices[self.curLine+1][2]+'.png')
				self.getControl(210+self.curLine).setImage(__img_path__+'/'+self.devices[self.curLine][2]+'_active.png')
				self.devices[self.curLine][5] = self.devices[self.curLine][2]
				self.selector.setPosition(89, (self.curLine*75)+99)
		elif (action == ACTION_MOVE_DOWN):
			if (self.curLine < MAX_DEVICES):
				self.curLine += 1
				self.getControl(210+self.curLine-1).setImage(__img_path__+'/'+self.devices[self.curLine-1][2]+'.png')
				self.getControl(210+self.curLine).setImage(__img_path__+'/'+self.devices[self.curLine][2]+'_active.png')
				self.devices[self.curLine][5] = self.devices[self.curLine][2]
				self.selector.setPosition(89, (self.curLine*75)+99)
		elif (action == ACTION_PREVIOUS_MENU or action == ACTION_BACK or action == ACTION_HOME):
			global __windowopen__
			self.storeDevices()
			__windowopen__ = False
			self.close()


	def onClick(self, controlId):
		debug.log("onAction("+ str(controlId) +")")
		for i in range(0,self.deviceCount):		
			if ( str(controlId) == self.devices[i][4]):
				self.devices[i][2] = self.devices[i][5]
				break
		if (self.devices[i][3] == "SWITCH"):
			if (self.devices[self.curLine][2] == "ON"):
				tdtool.doDevice(settings.getSetting("telldusSource"), self.devices[i][0], TELLSTICK_TURNON, 255)
			else:
				tdtool.doDevice(settings.getSetting("telldusSource"), self.devices[i][0], TELLSTICK_TURNOFF, 100)
		elif (self.devices[i][3] == "DIMMER"):
			tdtool.doDevice(settings.getSetting("telldusSource"), self.devices[i][0], TELLSTICK_DIM, int(round((int(self.devices[i][2])*255)/1000)))

			
	def onFocus(self, controlId):
		debug.log("onAction("+ str(controlId) +")")


	def applyNavigation(self):
		debug.log("applyNavigation()")
		self.curLine = 0
		self.setFocus(self.buttons[self.curLine])		
		if ( self.devices[self.curLine][3] == "SWITCH" ):
			if ( self.devices[self.curLine][2] == "ON" ):
				self.getControl(210+self.curLine).setImage(__img_path__+'/on_active.png')
			else:
				self.getControl(210+self.curLine).setImage(__img_path__+'/off_active.png')
		elif ( self.devices[self.curLine][3] == "DIMMER" ):
			self.getControl(210+self.curLine).setImage(__img_path__+'/'+self.devices[self.curLine][2]+'_active.png')
		for i in range(0,self.deviceCount-1):
			self.buttons[i].controlDown(self.buttons[(i+1)%10])
			self.buttons[(i+1)%10].controlUp(self.buttons[i])


	def printControls(self):
		debug.log("printControls()")
		self.labels = []
		self.buttons = []
		self.selector = xbmcgui.ControlImage(89, 99, 16, 32, __img_path__+'/selector.png')
		self.addControl(self.selector)
		for i in range(0,self.deviceCount):
			self.labels.append(xbmcgui.ControlLabel(120, 78+(i*75), 400, 69, self.devices[i][1] ,alignment=4, font='font14', textColor='0xFFFFFFFF'))
			self.addControl(self.labels[i])
			if ( self.devices[i][3] == "SWITCH" ):
				self.buttons.append(xbmcgui.ControlButton(34, 104+(i*75), 32, 32,'','',''))
			else:
				self.buttons.append(xbmcgui.ControlButton(34, 104+(i*75), 32, 32,'','',''))
			self.addControl(self.buttons[i])
			self.devices[i][4] = str(self.buttons[i].getId())
			if ( self.devices[i][3] == "SWITCH" ):
				if ( self.devices[i][2] == "ON" ):
					self.getControl(210+i).setImage(__img_path__+'/on.png')
				else:
					self.getControl(210+i).setImage(__img_path__+'/off.png')
			elif ( self.devices[i][3] == "DIMMER" ):
				self.getControl(210+i).setImage(__img_path__+'/'+self.devices[i][2]+'.png')
			self.devices[i][5] = self.devices[i][2]


	def logDeviceStatus(self):
		debug.log("logDeviceStatus()")	
		if ( self.deviceCount == 0):
			xbmc.log("-> no devices registered")
		else:
			for i in range(self.deviceCount):
				xbmc.log("-> "+self.devices[i][0])
				xbmc.log("-> "+self.devices[i][1])
				xbmc.log("-> "+self.devices[i][2])
				xbmc.log("-> "+self.devices[i][3])
				xbmc.log("-> "+str(self.devices[i][4]))
				xbmc.log("-> "+str(self.devices[i][5]))
				xbmc.log(" ")


	def getDevices(self):
		debug.log("getDevices()")	
		self.deviceCount = int(settings.getSetting("deviceCount"))				
		self.devices = [[0 for x in xrange(6)] for x in xrange(self.deviceCount)] 
		for i in range(self.deviceCount):
			id = "ID"+str(i)
			name = "name"+str(i)
			val = "val"+str(i)
			type = "type"+str(i)
			self.devices[i][0] = settings.getSetting(id)
			self.devices[i][1] = settings.getSetting(name)
			self.devices[i][2] = settings.getSetting(val)
			self.devices[i][3] = settings.getSetting(type)
			self.devices[i][5] = self.devices[i][2]
			
			if ( self.devices[i][3] == "SWITCH" ):	
					if ( isNumber(self.devices[i][2]) == True ):
						if ( int(self.devices[i][2]) >= (1000/2) ):
							self.devices[i][2] = "ON"
							settings.setSetting("ON", self.devices[i][2])
						else:
							self.devices[i][2] = "OFF"
							settings.setSetting("OFF", self.devices[i][2])
					elif (self.devices[i][2] == '' ):
						self.devices[i][2] = "OFF"
						settings.setSetting("OFF", self.devices[i][2])
							
			if ( self.devices[i][3] == "DIMMER" ):	
				if ( self.devices[i][2] == "ON" ):
					self.devices[i][2] = "1000"
					settings.setSetting("1000", self.devices[i][2])
				elif ( self.devices[i][2] == "OFF" ):
					self.devices[i][2] = "0"
					settings.setSetting("0", self.devices[i][2])


	def storeDevices(self):
		debug.log("storeDevices()")	
		for i in range(self.deviceCount):
			id = "ID"+str(i)
			name = "name"+str(i)
			val = "val"+str(i)
			type = "type"+str(i)
			settings.setSetting(id, str(self.devices[i][0]) )
			settings.setSetting(name, str(self.devices[i][1]) )
			settings.setSetting(val, str(self.devices[i][2]) )
			settings.setSetting(type, str(self.devices[i][3]) )


	def initDevices(self):
		debug.log("initDevices()")	
		i = 0
		self.deviceCount = 0
		self.devices = []
		devices = tdtool.listDevices()
		for i in range(len(devices)):
			if (i == 0):
				self.deviceCount=int(devices[i])
				settings.setSetting("deviceCount", str(self.deviceCount))
				self.devices = [[0 for x in xrange(6)] for x in xrange(self.deviceCount)] 
			else:
				cols = devices[i].split('\t')
				id = "ID"+str(i-1)
				name = "name"+str(i-1)
				val = "val"+str(i-1)
				type = "type"+str(i-1)
				settings.setSetting(id, cols[0])
				settings.setSetting(name, cols[1])
				settings.setSetting(val, cols[2].rstrip('\n'))
				if "DIMMED" in settings.getSetting(val):
					settings.setSetting(type, "DIMMER")
					settings.setSetting(val, "500")
				else:
					settings.setSetting(type, "SWITCH")
		for i in range(self.deviceCount):
			id = "ID"+str(i)
			val = "val"+str(i)
			type = "type"+str(i)
			if "SWITCH" in settings.getSetting(type):
				if "ON" in settings.getSetting(val):
					val = "255"
				else:
					val = "0"
				output = tdtool.doMethod(settings.getSetting(id), TELLSTICK_DIM, val)
				if "success" in output:
					settings.setSetting(type, "DIMMER")


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
if ( xbmcgui.Window(winID).getProperty("telldus.running") == "true" ):
	tw.log('script already running, aborting subsequent run attempts', 'standard')
else:
	xbmcgui.Window(winID).setProperty( "telldus.running",  "true" )
	tw.log('attempting to create main script object', 'verbose')
	w = TelldusInfoWindow("telldus.xml", __addonpath__, "Default")
	w.doModal()
	del w
	del tw
	xbmcgui.Window(winID).setProperty( "telldus.running",  "false" )