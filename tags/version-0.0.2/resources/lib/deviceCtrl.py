#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
# Author: Espen Krangnes

import os, sys, subprocess
import xbmcaddon, xbmc
import tdtool, webbrowser

# self.devices	0:ID		1:name		2:actVal	3:type		4:controlID		5:newVal
MAX_DEVICES = 8
TELLSTICK_DIM = 16
settings = xbmcaddon.Addon(id='plugin.program.terra')	

def telldusLocalInit():
	i = 0
	deviceCount = 0
	devices = []
	devices = tdtool.listDevices_local()
	for i in range(len(devices)):
		if (i == 0):
			deviceCount=int(devices[i])
			settings.setSetting("deviceCount", str(deviceCount))
		elif (i<MAX_DEVICES):
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
		else:
			xbmc.log("Telldus device overflow:" + str(devices[i]) )


def telldusLiveInit():
	i = 0
	deviceCount = 0
	devices = []
	devices = tdtool.listDevices()
	for i in range(len(devices)):
		if (i == 0):
			deviceCount=int(devices[i])
			settings.setSetting("deviceCount", str(deviceCount))
		elif (i<MAX_DEVICES):
			cols = devices[i].split('\t')
			id = "ID"+str(i-1)
			name = "name"+str(i-1)
			val = "val"+str(i-1)
			type = "type"+str(i-1)
			settings.setSetting(id, cols[0])
			settings.setSetting(name, cols[1])
			if cols[2].find('DIMMED') >= 0:
				settings.setSetting(type, "DIMMER")
				settings.setSetting(val, "500")
			else:
				settings.setSetting(val, cols[2].rstrip('\n'))
				settings.setSetting(type, "SWITCH")
		else:
			xbmc.log("Telldus device overflow:" + str(devices[i]) )
	
	
	for i in range(deviceCount):
		id = "ID"+str(i)
		val = "val"+str(i)
		type = "type"+str(i)
		if "SWITCH" in settings.getSetting(type):
			if "ON" in settings.getSetting(val):
				j = "255"
			else:
				j = "0"
			output = tdtool.doMethod(settings.getSetting(id), TELLSTICK_DIM, j)
			if "success" in output:
				settings.setSetting(type, "DIMMER")
				settings.setSetting(val, j)

def telldusLiveAuthenticate():
	key = tdtool.requestToken()
	settings.setSetting("telldus_live_authenticated", "true")
	webbrowser.open("http://api.telldus.com/oauth/authorize?oauth_token=" + key)

def telldusLiveConfirm():
	tdtool.getAccessToken()
	settings.setSetting("telldus_live_confirmed", "true")

def telldusLiveReset():
	settings.setSetting("telldus_live_authenticated", "false")
	settings.setSetting("telldus_live_confirmed", "false")

if len(sys.argv)>1:
	if sys.argv[1] == "TELLDUS_LIVE_AUTHENTICATE":
		telldusLiveAuthenticate()
	elif sys.argv[1] == "TELLDUS_LIVE_CONFIRM":
		telldusLiveConfirm()
	elif sys.argv[1] == "TELLDUS_LIVE_RESET":
		telldusLiveReset()	
	elif sys.argv[1] == "TELLDUS_LIVE_INIT":
		telldusLiveInit()
	elif sys.argv[1] == "TELLDUS_LOCAL_INIT":
		telldusLocalInit()
	else:
		pass
