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


settings = xbmcaddon.Addon(id='plugin.program.terra')

while (not xbmc.abortRequested):
	while(1):
		if xbmc.Player().isPlayingVideo():
			VIDEO = 1	
		else:
			VIDEO = 0
		
		#check every 5 mins
		xbmc.sleep(300000)