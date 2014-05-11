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

class MyPlayer(xbmc.Player) :
		def __init__ (self):
			xbmc.Player.__init__(self)
		
		def onPlayBackStarted(self): # PLAY
			if (xbmc.Player().isPlayingVideo()): 
				xbmc.log("playing")
		
		def onPlayBackEnded(self): # ENDED
			if (VIDEO == 1):
				xbmc.log("stopped")
		
		def onPlayBackStopped(self): # STOPPED
			if (VIDEO == 1):
				xbmc.log("stopped")
		
		def onPlayBackPaused(self): # PAUSED
			if (xbmc.Player().isPlayingVideo()):
				xbmc.log("paused")
		
		def onPlayBackResumed(self): # RESUMED (play)
			if (xbmc.Player().isPlayingVideo()):
				xbmc.log("playing")
		
player=MyPlayer()

while (not xbmc.abortRequested):
	while(1):
		if xbmc.Player().isPlayingVideo():
			VIDEO = 1	
		else:
			VIDEO = 0
		
		xbmc.sleep(3000)