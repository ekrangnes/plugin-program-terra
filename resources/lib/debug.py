#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
# Author: Espen Krangnes

import os, subprocess
import xbmc, xbmcaddon

if os.name == 'nt':
	info = subprocess.STARTUPINFO()
	info.dwFlags = 1
	info.wShowWindow = 0

settings = xbmcaddon.Addon(id='plugin.program.terra')

def log(s):
	if (settings.getSetting("telldusDebug") == "true" ):
		xbmc.log("plugin.program.terraStick - " + s)
