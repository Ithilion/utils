import os
import re
import requests
import shutil
import sys
import tempfile
import zipfile

# TODO: get wow_path from registry

oqueue_tmp = os.path.join(tempfile.gettempdir(), "oqueue_update.tmp.zip")
wow_path = "C:\Program Files (x86)\World of Warcraft"
oqueue_path = os.path.join(wow_path, "Interface", "Addons", "oqueue")
addons_path = os.path.join(wow_path, "Interface", "Addons")
error_message = "Something went wrong while fetching oQUeue... exiting."

print("Fetching oQueue...")
s = requests.session()

r = s.get("http://solidice.com/downloads/world-of-warcraft/oqueue")
if not r:
	print(error_message)
	sys.exit()

token = re.search('http://solidice.com/downloads/world-of-warcraft/oqueue/download\?_token=(.*?)"', r.text)
if not token:
	print(error_message)
	sys.exit()
token = token.group(1)

payload = {"_token": token}
r = s.get("http://solidice.com/download/world-of-warcraft/oqueue", params = payload)
if not r:
	print(error_message)
	sys.exit()

with open(oqueue_tmp, "wb") as f:
	f.write(r.content)

if os.path.isdir(oqueue_path):
	print("Previous installation detected, removing it...")
	shutil.rmtree(oqueue_path)

print("Extracting...")
with open(oqueue_tmp, "rb") as f:
	z = zipfile.ZipFile(f)
	z.extractall(addons_path)

print("Cleaning up...")
os.remove(oqueue_tmp)
