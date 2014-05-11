#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
# Author: Espen Krangnes

import xbmc, xbmcaddon
import subprocess,os
import tdtool, debug

if os.name == 'nt':
	info = subprocess.STARTUPINFO()
	info.dwFlags = 1
	info.wShowWindow = 0

TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_DIM = 16

settings = xbmcaddon.Addon(id='plugin.program.terra')

def telldusApply(telldusStatus):
	for i in range(int(settings.getSetting("deviceCount"))):
		if (settings.getSetting("automation_"+telldusStatus+"_ID"+str(i)) == "true"):
			if (settings.getSetting("type"+str(i)) == "SWITCH"):
				if (settings.getSetting("automation_"+telldusStatus+"_switch_ID"+str(i)) == "true"):
					tdtool.doDevice(settings.getSetting("telldusSource"), settings.getSetting('ID'+str(i)), TELLSTICK_TURNON,255)
				else:
					tdtool.doDevice(settings.getSetting("telldusSource"), settings.getSetting('ID'+str(i)), TELLSTICK_TURNOFF,0)
			else:
				val = int(float( settings.getSetting("automation_"+telldusStatus+"_dimmer_ID"+str(i))))
				tdtool.doDevice(settings.getSetting("telldusSource"), settings.getSetting('ID'+str(i)), TELLSTICK_DIM, val)

class MyPlayer(xbmc.Player) :
		def __init__ (self):
			xbmc.Player.__init__(self)
		
		def onPlayBackStarted(self): # PLAY
			if (xbmc.Player().isPlayingVideo()): 
				telldusApply("playing")
		
		def onPlayBackEnded(self): # ENDED
			if (VIDEO == 1):
				telldusApply("stopped")
		
		def onPlayBackStopped(self): # STOPPED
			if (VIDEO == 1):
				telldusApply("stopped")
		
		def onPlayBackPaused(self): # PAUSED
			if (xbmc.Player().isPlayingVideo()):
				telldusApply("paused")
		
		def onPlayBackResumed(self): # RESUMED (play)
			if (xbmc.Player().isPlayingVideo()):
				telldusApply("playing")
		
player=MyPlayer()

while (not xbmc.abortRequested):
	while(1):
		if xbmc.Player().isPlayingVideo():
			VIDEO = 1	
		else:
			VIDEO = 0
		
		xbmc.sleep(3000)