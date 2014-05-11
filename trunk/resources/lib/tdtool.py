#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Telldus Technologies
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys, os, subprocess
import oauth, getopt, httplib, urllib, json
from configobj import ConfigObj
import xbmc, xbmcgui, xbmcaddon
import debug

settings = xbmcaddon.Addon(id='plugin.program.terra')
PUBLIC_KEY = settings.getSetting("public_key")
PRIVATE_KEY = settings.getSetting("private_key")
USERNAME = settings.getSetting("username")
PASSWORD = settings.getSetting("password")
TELLDUS_EXE = settings.getSetting("telldusExe")

if os.name == 'nt':
	info = subprocess.STARTUPINFO()
	info.dwFlags = 1
	info.wShowWindow = 0
	
if sys.platform == 'darwin':
	TELLDUS_EXE.replace(" ", "\\ ")
elif sys.platform == 'linux2':
	pass
elif sys.platform == 'windows':
	pass

TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_BELL = 4
TELLSTICK_DIM = 16
TELLSTICK_UP = 128
TELLSTICK_DOWN = 256

SUPPORTED_METHODS = TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_DIM | TELLSTICK_UP | TELLSTICK_DOWN;

def runCmd(cmd):
	debug.log("runCmd("+ cmd +")")
	if sys.platform == 'darwin':
		return os.system(cmd)
	else:
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, error = p.communicate()
		return output

def doDevice(source, deviceId, methodId, methodValue=0):
	debug.log("doDevice(" + source +", "+ str(deviceId) +", "+ str(methodId) +", "+ str(methodValue)+")")
	if (source == "Telldus Live!"):
		doMethod(deviceId, methodId, methodValue)
	elif (source == "Local tdtool"):
		doMethod_local(deviceId, methodId, methodValue)
	else:
		pass

def listDevices_local():
	debug.log("listDevices_local()")
	devices = []
	output = runCmd(TELLDUS_EXE + " --list ")
	devices = output.splitlines()
	devices.pop(len(devices)-1)
	devices[0] = str(len(devices)-1)
	for i in range(len(devices)):
		xbmc.log(str(i) +": "+ str(devices[i]))
	return devices

def doMethod_local(deviceId, methodId, methodValue = 0):
	debug.log("doMethod_local("+ str(deviceId) +", "+ str(methodId) +", "+ str(methodValue) +")")
	if (methodId == TELLSTICK_TURNON):
		runCmd(TELLDUS_EXE + " --on " + deviceId)
	elif (methodId == TELLSTICK_TURNOFF):
		runCmd(TELLDUS_EXE + " --off " + deviceId)
	elif (methodId == TELLSTICK_DIM):
		runCmd(TELLDUS_EXE + " --dimlevel " + str(methodValue) + " --dim " + deviceId)
	return "success"

def listDevices():
	debug.log("listDevices()")
	devices = []
	response = doRequest('devices/list', {'supportedMethods': SUPPORTED_METHODS})
	devices.append(str(len(response['device'])));
	for device in response['device']:
		if (device['state'] == TELLSTICK_TURNON):
			state = 'ON'
		elif (device['state'] == TELLSTICK_TURNOFF):
			state = 'OFF'
		elif (device['state'] == TELLSTICK_DIM):
			state = "DIMMED"
		elif (device['state'] == TELLSTICK_UP):
			state = "UP"
		elif (device['state'] == TELLSTICK_DOWN):
			state = "DOWN"
		else:
			state = 'Unknown state'
		devices.append("%s\t%s\t%s" % (device['id'], device['name'], state));	
	return devices

def doMethod(deviceId, methodId, methodValue = 0):
	debug.log("doMethod("+ str(deviceId) +", "+ str(methodId) +", "+ str(methodValue) +")")
	response = doRequest('device/info', {'id': deviceId})	
	if (methodId == TELLSTICK_TURNON):
		method = 'on'
	elif (methodId == TELLSTICK_TURNOFF):
		method = 'off'
	elif (methodId == TELLSTICK_BELL):
		method = 'bell'
	elif (methodId == TELLSTICK_UP):
		method = 'up'
	elif (methodId == TELLSTICK_DOWN):
		method = 'down'
	if ('error' in response):
		name = ''
		retString = response['error']
	else:
		name = response['name']
		response = doRequest('device/command', {'id': deviceId, 'method': methodId, 'value': methodValue})
		if ('error' in response):
			retString = response['error']
		else:
			retString = response['status']
	if (methodId in (TELLSTICK_TURNON, TELLSTICK_TURNOFF)):
		return "Turning %s device %s, %s - %s" % ( method, deviceId, name, retString)
	elif (methodId in (TELLSTICK_BELL, TELLSTICK_UP, TELLSTICK_DOWN)):
		return "Sending %s to: %s %s - %s" % (method, deviceId, name, retString)
	elif (methodId == TELLSTICK_DIM):
		return "Dimming device: %s %s to %s - %s" % (deviceId, name, methodValue, retString)


def doRequest(method, params):
	debug.log("doRequest("+ str(method) +", "+ str(params) +")")
	global config
	consumer = oauth.OAuthConsumer(PUBLIC_KEY, PRIVATE_KEY)
	token = oauth.OAuthToken(config['token'], config['tokenSecret'])
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method='GET', http_url="http://api.telldus.com/json/" + method, parameters=params)
	oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
	headers = oauth_request.to_header()
	headers['Content-Type'] = 'application/x-www-form-urlencoded'
	conn = httplib.HTTPConnection("api.telldus.com:80")
	conn.request('GET', "/json/" + method + "?" + urllib.urlencode(params, True).replace('+', '%20'), headers=headers)
	response = conn.getresponse()
	return json.load(response)

def requestToken():
	debug.log("requestToken()")
	global config
	consumer = oauth.OAuthConsumer(PUBLIC_KEY, PRIVATE_KEY)
	request = oauth.OAuthRequest.from_consumer_and_token(consumer, http_url='http://api.telldus.com/oauth/requestToken')
	request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, None)
	conn = httplib.HTTPConnection('api.telldus.com:80')
	conn.request(request.http_method, '/oauth/requestToken', headers=request.to_header())
	resp = conn.getresponse().read()
	token = oauth.OAuthToken.from_string(resp)
	config['requestToken'] = str(token.key)
	config['requestTokenSecret'] = str(token.secret)
	saveConfig()
	return str(token.key)

def getAccessToken():
	debug.log("getAccessToken()")
	global config
	consumer = oauth.OAuthConsumer(PUBLIC_KEY, PRIVATE_KEY)
	token = oauth.OAuthToken(config['requestToken'], config['requestTokenSecret'])
	request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method='GET', http_url='http://api.telldus.com/oauth/accessToken')
	request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
	conn = httplib.HTTPConnection('api.telldus.com:80')
	conn.request(request.http_method, request.to_url(), headers=request.to_header())
	resp = conn.getresponse()
	if resp.status != 200:
		message('Error retreiving access token',str(resp.read()))
		return
	token = oauth.OAuthToken.from_string(resp.read())
	config['requestToken'] = None
	config['requestTokenSecret'] = None
	config['token'] = str(token.key)
	config['tokenSecret'] = str(token.secret)
	saveConfig()
	
def saveConfig():
	debug.log("saveConfig()")
	config.write()

def message(header,body):
	debug.log("message("+ header +", "+ body +")")
	dialog = xbmcgui.Dialog()
	dialog.ok(header,body)

config = ConfigObj(xbmc.translatePath('special://profile') + 'tdtool.conf')