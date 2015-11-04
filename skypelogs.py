# TODO:
# conversation displayname in filename
# body_xml cleansing
# don't access tuples directly (e.g. mgs[0])
# with statement for sqlite connection
# other Messages types ?
# continuous monitoring ?

import argparse
import os
import re
import sys
import sqlite3
from datetime import datetime
from html import unescape

parser = argparse.ArgumentParser(description = "Skype logs dumper")
parser.add_argument("-u", "--user", help = "use this Skype user's main.db")
parser.add_argument("-p", "--path", help = "path to specific main.db (or ortherwise named)")
parser.add_argument("-d", "--directory", help = "logs will be stored in a subdirectory (\"logs\") of this directory; if not provided, current active directory will be used")
args = parser.parse_args()

if args.user and args.path:
	print("Use only one main.db source")
	sys.exit()
elif args.user:
	if sys.platform.startswith("win32"):
		main_db_path = os.path.join(os.getenv('APPDATA'), "Skype", args.user, "main.db")
	elif sys.platform.startswith("linux"):
		main_db_path = os.path.join("~", ".Skype", args.user, "main.db")
	else:
		print("Unsupported OS")
		sys.exit()
	if not os.path.isfile(main_db_path):
		print("The main.db file could not be found")
		sys.exit()
elif args.path:
	main_db_path = args.path
	if not os.path.isfile(main_db_path):
		print("The main.db file could not be found")
		sys.exit()
else:
	print("You have to specify a main.db source")
	sys.exit()

logs_folder = "logs"
if args.directory:
	if not os.path.exists(args.directory):
		print("The folder does not exist")
		sys.exit()
	logs_folder = os.path.join(args.directory, "logs")
os.makedirs(logs_folder, exist_ok=True)

print("main.db path: {:s}".format(main_db_path))
print("output path: {:s}".format(logs_folder))
print("")

conn = sqlite3.connect(main_db_path)

c1 = conn.cursor()
c1.execute("SELECT id, identity FROM Conversations ORDER BY id;")

for conv in c1.fetchall():
	c2 = conn.cursor()
	c2.execute("SELECT timestamp, remote_id, from_dispname, author, body_xml FROM Messages WHERE type = 61 and convo_id = {:d} ORDER BY timestamp, id;".format(conv[0]))

	rowlist = c2.fetchall()
	if rowlist:
		file_path = os.path.join(logs_folder, "{:s}.txt".format(conv[1].replace(":", "_").replace("/", "_")))
		open(file_path, "a").close()
		with open(file_path, "r+", encoding="utf-8") as f:
			for line in f:
				pass
			try:
				line = line.strip("\n")
				r = re.match("(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) (\d+) \[.+\]\[(.+)\]\t(.*)", line)
				time = int(datetime.strptime(r.group(1), '%Y/%m/%d %H:%M:%S').timestamp())
				remote_id = int(r.group(2))
				author = r.group(3)
				body_xml = r.group(4)

				found = -1
				for i, msg in enumerate(rowlist):
					if msg[1] == remote_id and msg[3] == author and time - 100 <= msg[0] <= time + 100:
						found = i
						break
				if found != -1 and found + 1 != len(rowlist):
					print("Updating conv: {:s}".format(conv[1]))
					f.write("".join(["{:s} {:d} [{:s}][{:s}]\t{:s}\n".format(datetime.fromtimestamp(msg[0]).strftime('%Y/%m/%d %H:%M:%S'), msg[1], msg[2], msg[3], unescape(msg[4].replace("\n", "\t").replace("\r", ""))) for msg in rowlist[found + 1:]]))
				if found != -1 and found + 1 == len(rowlist):
					print("Nothing to update for conv: {:s}".format(conv[1]))
				if found == -1:
					print("Could not find a suitable starting row for conv: {:s}, appending every new message".format(conv[1]))
					f.write("".join(["{:s} {:d} [{:s}][{:s}]\t{:s}\n".format(datetime.fromtimestamp(msg[0]).strftime('%Y/%m/%d %H:%M:%S'), msg[1], msg[2], msg[3], unescape(msg[4].replace("\n", "\t").replace("\r", ""))) for msg in rowlist]))
			except NameError:
				print("Initial population for conv: {:s}".format(conv[1]))
				f.write("".join(["{:s} {:d} [{:s}][{:s}]\t{:s}\n".format(datetime.fromtimestamp(msg[0]).strftime('%Y/%m/%d %H:%M:%S'), msg[1], msg[2], msg[3], unescape(msg[4].replace("\n", "\t").replace("\r", ""))) for msg in rowlist]))
