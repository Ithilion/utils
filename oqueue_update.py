import os
import re
import requests
import shutil
import tempfile
import zipfile

oqueue_tmp = os.path.join(tempfile.gettempdir(), "oqueue_update.tmp.zip")
wow_path = "C:\Program Files (x86)\World of Warcraft"
oqueue_path = os.path.join(wow_path, "Interface", "Addons", "oqueue")
addons_path = os.path.join(wow_path, "Interface", "Addons")

s = requests.session()
r = s.get("http://solidice.com/addons/wow/oqueue")
reg_nonce = re.compile("<input type='hidden' name='nonce' value='(.*?)'>")
nonce = reg_nonce.search(r.text).group(1)
payload = {"id": "30", "nonce": nonce}
r = s.get("http://solidice.com/files/serve.php", params = payload)
with open(oqueue_tmp, "wb") as f:
	f.write(r.content)

if os.path.isdir(oqueue_path):
	shutil.rmtree(oqueue_path)

with open(oqueue_tmp, "rb") as f:
	z = zipfile.ZipFile(f)
	z.extractall(addons_path)

os.remove(oqueue_tmp)
