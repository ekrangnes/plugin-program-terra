#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
# Author: Espen Krangnes

import os, sys, subprocess
import xbmcaddon, xbmcgui, xbmc
import tdtool, debug, urllib, urllib2, webbrowser

# self.devices	0:ID		1:name		2:actVal	3:type		4:controlID		5:newVal
MAX_DEVICES = 32
TELLSTICK_DIM = 16
settings = xbmcaddon.Addon(id='plugin.program.terra')	

def terraLocalInit():
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
			id = "dev"+str(i-1)+"ID"
			name = "dev"+str(i-1)+"Name"
			val = "dev"+str(i-1)+"Val"
			type = "dev"+str(i-1)+"Type"
			settings.setSetting(id, cols[0])
			settings.setSetting(name, cols[1])
			settings.setSetting(val, cols[2].rstrip('\n'))
			if "DIMMED" in settings.getSetting(val):
				settings.setSetting(type, "dimmer")
				settings.setSetting(val, "500")
			else:
				settings.setSetting(type, "switch")
		else:
			xbmc.log("Telldus device overflow:" + str(devices[i]) )


def terraLocalUpdate():
	i = 0
	devices = []
	devices = tdtool.listDevices_local()
	for i in range(len(devices)):
		if (i == 0):
			pass
		elif (i<MAX_DEVICES):
			cols = devices[i].split('\t')
			val = "dev"+str(i-1)+"Val"
			settings.setSetting(val, cols[2].rstrip('\n'))


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
			id = "dev"+str(i-1)+"ID"
			name = "dev"+str(i-1)+"Name"
			val = "dev"+str(i-1)+"Val"
			type = "dev"+str(i-1)+"Type"
			settings.setSetting(id, cols[0])
			settings.setSetting(name, cols[1])
			if cols[2].find('DIMMED') >= 0:
				settings.setSetting(type, "dimmer")
				settings.setSetting(val, "500")
			else:
				settings.setSetting(val, cols[2].rstrip('\n'))
				settings.setSetting(type, "switch")
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


def telldusLiveUpdate():
	pass


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
	try:
		os.remove(xbmc.translatePath('special://profile') + 'tdtool.conf')
	except OSError:
		debug.log("tdtool.conf does not exist")
	dialog = xbmcgui.Dialog()
	dialog.ok("Reset Telldus Live!", "Telldus Live! authentication has successfully been reset.")


def terraDummyInit():
	settings.setSetting("dev0ID", "0781235")
	settings.setSetting("dev0Name", "alpha")
	settings.setSetting("dev0Val", "off")
	settings.setSetting("dev0Type", "switch")
	settings.setSetting("dev1ID", "1532")
	settings.setSetting("dev1Name", "bravo")
	settings.setSetting("dev1Val", "125")
	settings.setSetting("dev1Type", "dimmer")
	settings.setSetting("dev2ID", "24145")
	settings.setSetting("dev2Name", "charlie")
	settings.setSetting("dev2Val", "on")
	settings.setSetting("dev2Type", "switch")
	settings.setSetting("dev3ID", "39692")
	settings.setSetting("dev3Name", "delta")
	settings.setSetting("dev3Val", "off")
	settings.setSetting("dev3Type", "switch")
	settings.setSetting("dev4ID", "40921")
	settings.setSetting("dev4Name", "echo")
	settings.setSetting("dev4Val", "750")
	settings.setSetting("dev4Type", "dimmer")
	settings.setSetting("dev5ID", "593321")
	settings.setSetting("dev5Name", "foxtrot")
	settings.setSetting("dev5Val", "500")
	settings.setSetting("dev5Type", "dimmer")
	settings.setSetting("dev6ID", "691893")
	settings.setSetting("dev6Name", "golf")
	settings.setSetting("dev6Val", "on")
	settings.setSetting("dev6Type", "switch")
	settings.setSetting("dev7ID", "75232")
	settings.setSetting("dev7Name", "hotel")
	settings.setSetting("dev7Val", "750")
	settings.setSetting("dev7Type", "dimmer")
	settings.setSetting("dev8ID", "844145")
	settings.setSetting("dev8Name", "india")
	settings.setSetting("dev8Val", "750")
	settings.setSetting("dev8Type", "dimmer")
	settings.setSetting("dev9ID", "9163")
	settings.setSetting("dev9Name", "juliet")
	settings.setSetting("dev9Val", "750")
	settings.setSetting("dev9Type", "dimmer")
	settings.setSetting("dev10ID", "012023")
	settings.setSetting("dev10Name", "kilo")
	settings.setSetting("dev10Val", "off")
	settings.setSetting("dev10Type", "switch")
	settings.setSetting("dev11ID", "198")
	settings.setSetting("dev11Name", "lima")
	settings.setSetting("dev11Val", "off")
	settings.setSetting("dev11Type", "switch")
	settings.setSetting("dev12ID", "265974")
	settings.setSetting("dev12Name", "mike")
	settings.setSetting("dev12Val", "on")
	settings.setSetting("dev12Type", "switch")
	settings.setSetting("deviceCount", str(13))


#def terraTimeTest():
#	pass

	
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
		terraLocalInit()
	elif sys.argv[1] == "TELLDUS_DUMMY_INIT":
		terraDummyInit()
#	elif sys.argv[1] == "TERRA_TIME_TEST":
#		terraTimeTest()
	else:
		pass
