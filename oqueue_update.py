import os
import re
import requests
import shutil
import sys
import tempfile
import winreg
import zipfile

def critical_error(error_message):
	input(error_message)
	sys.exit()

def main():
	try:
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\Blizzard Entertainment\World of Warcraft", access = winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
		wow_path = winreg.QueryValueEx(key, "InstallPath")[0]
	except WindowsError:
		critical_error("Could not locate World of Warcraft folder... press ENTER to exit")

	oqueue_tmp = os.path.join(tempfile.gettempdir(), "oqueue_update.tmp.zip")
	oqueue_path = os.path.join(wow_path, "Interface", "Addons", "oqueue")
	addons_path = os.path.join(wow_path, "Interface", "Addons")

	print("Fetching oQueue...")
	s = requests.session()

	r = s.get("http://solidice.com/downloads/world-of-warcraft/oqueue")
	if not r:
		critical_error("Something went wrong while fetching oQueue...  press ENTER to exit")

	token = re.search('http://solidice.com/downloads/world-of-warcraft/oqueue/download\?_token=(.*?)"', r.text)
	if not token:
		critical_error("Something went wrong while fetching oQueue...  press ENTER to exit")
	token = token.group(1)

	payload = {"_token": token}
	r = s.get("http://solidice.com/download/world-of-warcraft/oqueue", params = payload)
	if not r:
		critical_error("Something went wrong while fetching oQueue...  press ENTER to exit")

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

	input("All done, press ENTER to exit")

if __name__ == "__main__":
	main()
