import argparse
import datetime
import locale
import os
import shutil
import zipfile

import xlrd

import ssl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

_default_block = object()

class MyAdapter(HTTPAdapter):
	def init_poolmanager(self, connections, maxsize, block=_default_block):
		pool_kw = dict()
		if block is _default_block:
			try: from requests.adapters import DEFAULT_POOLBLOCK
			except ImportError: pass
			else: pool_kw['block'] = DEFAULT_POOLBLOCK
		self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, ssl_version=ssl.PROTOCOL_TLSv1, **pool_kw)

import requests

s = requests.Session()
s.mount('https://', MyAdapter())

locale.setlocale(locale.LC_ALL, 'ita_ita')

parser = argparse.ArgumentParser(description = "Telecom Italia coverage files checker")
parser.add_argument("--atm", action="store_true", help = "download ADSL ATM files")
parser.add_argument("--eth", action="store_true", help = "download ADSL Ethernet files")
parser.add_argument("--olt", action="store_true", help = "download NGA OLT files")
parser.add_argument("--onu", action="store_true", help = "download NGA ONU files")
parser.add_argument("--all", action="store_true", help = "download all files")
parser.add_argument("search", help = "string to search in the files")
args = parser.parse_args()

atm_planned = "https://www.wholesale.telecomitalia.com/sitepub/SFTP/58_Coperture_Bitstream_e_EASY_IP_ADSL/Copertura pianificata Adsl su DSLAM ATM da Centrale e da Armadio.zip"
atm_active = "https://www.wholesale.telecomitalia.com/sitepub/SFTP/58_Coperture_Bitstream_e_EASY_IP_ADSL/ADSL attiva su DSLAM ATM da Centrale e da Armadio.zip"
eth_planned = "https://www.wholesale.telecomitalia.com/sitepub/SFTP/58_Coperture_Bitstream_e_EASY_IP_ADSL/Copertura pianificata ADSL su DSLAM ETHERNET da Centrale e da Armadio.zip"
eth_active = "https://www.wholesale.telecomitalia.com/sitepub/SFTP/58_Coperture_Bitstream_e_EASY_IP_ADSL/ADSL attiva su DSLAM ETHERNET da Centrale e da Armadio.zip"
olt_planned = "https://www.wholesale.telecomitalia.com/sitepub/SFTP/59_Coperture_Bitstream_NGA_e_VULA/Centrali NGA pianificate.zip"
olt_active = "https://www.wholesale.telecomitalia.com/sitepub/SFTP/59_Coperture_Bitstream_NGA_e_VULA/Centrali NGA attive.zip"
onu_planned = "https://www.wholesale.telecomitalia.com/sitepub/SFTP/59_Coperture_Bitstream_NGA_e_VULA/Copertura pianificata FTTCab.zip"
onu_active = "https://www.wholesale.telecomitalia.com/sitepub/SFTP/59_Coperture_Bitstream_NGA_e_VULA/Copertura attiva FTTCab.zip"

status_date_dict = {
	atm_planned: 10,
	atm_active: 10,
	eth_planned: 13,
	eth_active: 13,
	olt_planned: 15,
	olt_active: 15,
	onu_planned: 19,
	onu_active: 23,
}

atm = [atm_planned, atm_active]
eth = [eth_planned, eth_active]
olt = [olt_planned, olt_active]
onu = [onu_planned, onu_active]

files = []
if args.all:
	files = files + atm + eth + olt + onu
else:
	if args.atm:
		files = files + atm
	if args.eth:
		files = files + eth
	if args.olt:
		files = files + olt
	if args.onu:
		files = files + onu

temp_dir = "coverage_temp"
os.makedirs(temp_dir, exist_ok=True)

try:
	for file in files:
		downloaded = s.get(file)
		zipped_path = os.path.join(temp_dir, file.split("/")[-1])

		with open(zipped_path, "wb") as f:
			f.write(downloaded.content)

		with zipfile.ZipFile(zipped_path, "r") as zipped:
			xml_file_name = zipped.namelist()[0]
			zipped.extractall(temp_dir)

		print(xml_file_name)

		xml_file_path = os.path.join(temp_dir, xml_file_name)
		with xlrd.open_workbook(xml_file_path) as xml_file:
			for sheet in xml_file.sheets():
				for row_index in range(sheet.nrows):
					for column_index in range(sheet.ncols):
						if args.search.lower() in str(sheet.cell_value(row_index, column_index)).lower():
							cell_list = sheet.row_values(row_index)
							status_date = cell_list[status_date_dict[file]]
							if isinstance(status_date, float):
								status_date_tuple = xlrd.xldate_as_tuple(status_date, 0)
								status_date_date = datetime.date(year=status_date_tuple[0], month=status_date_tuple[1], day=status_date_tuple[2])
								cell_list[status_date_dict[file]] = status_date_date.strftime("%b-%y")
							print(cell_list)

		print("")
except Exception:
	print("Something went wrong")
finally:
	input("Press enter key...")
	shutil.rmtree(temp_dir)
