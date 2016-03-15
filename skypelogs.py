# TODO:
# better body_xml cleansing
# don't access tuples directly (e.g. mgs[0])
# with statement for sqlite connection
# other Messages types ?

import argparse
import os
import re
import sys
import sqlite3
from datetime import datetime
from html import unescape

def main():
	parser = argparse.ArgumentParser(description = "Skype logs dumper")
	parser.add_argument("-u", "--user", help = "use this Skype user's main.db")
	parser.add_argument("-p", "--path", help = "path to specific main.db (or otherwise named)")
	parser.add_argument("-d", "--directory", help = "logs will be stored in a subdirectory (\"logs\") of this directory (of current directory if not provided)")
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
				line = None
				for line in f:
					pass
				if line is not None:
					line = line.strip("\n")
					result = match_log_line.match(line)
					time = int(datetime.strptime(result.group(1), '%Y/%m/%d %H:%M:%S').timestamp())
					remote_id = int(result.group(2))
					author = result.group(3)

					found = -1
					for i, msg in enumerate(rowlist):
						if msg[1] == remote_id and msg[3] == author and time - 100 <= msg[0] <= time + 100:
							found = i
							break
					if found != -1 and found + 1 != len(rowlist):
						print("Updating: {:s}".format(conv[1]))
						f.write("".join(["{:s} {:d} [{:s}][{:s}]\t{:s}\n".format(datetime.fromtimestamp(msg[0]).strftime('%Y/%m/%d %H:%M:%S'), msg[1], msg[2], msg[3], cleanse_body_xml(msg[4])) for msg in rowlist[found + 1:]]))
					if found != -1 and found + 1 == len(rowlist):
						print("Up-to-date: {:s}".format(conv[1]))
					if found == -1:
						print("Appending all: {:s}".format(conv[1]))
						f.write("".join(["{:s} {:d} [{:s}][{:s}]\t{:s}\n".format(datetime.fromtimestamp(msg[0]).strftime('%Y/%m/%d %H:%M:%S'), msg[1], msg[2], msg[3], cleanse_body_xml(msg[4])) for msg in rowlist]))
				else:
					print("Initial population: {:s}".format(conv[1]))
					f.write("".join(["{:s} {:d} [{:s}][{:s}]\t{:s}\n".format(datetime.fromtimestamp(msg[0]).strftime('%Y/%m/%d %H:%M:%S'), msg[1], msg[2], msg[3], cleanse_body_xml(msg[4])) for msg in rowlist]))

match_log_line = re.compile("(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) (\d+) \[.+\]\[(.+)\]\t(.*)")
cleanse = [
	re.compile("</?legacyquote>"),
	re.compile("<quote .*?>"),
	re.compile("</quote>"),
	re.compile("<a .*?>"),
	re.compile("</a>"),
	re.compile("<ss .*?>"),
	re.compile("</ss>"),
	re.compile("<b .*?>"),
	re.compile("</>"),
	re.compile("<s .*?>"),
	re.compile("</s>"),
	re.compile("<i .*?>"),
	re.compile("</i>"),
	]

def cleanse_body_xml(body_xml):
	body_xml = unescape(body_xml.replace("\n", "\t").replace("\r", ""))
	for regex in cleanse:
		body_xml = regex.sub("", body_xml)
	return body_xml

if __name__ == "__main__":
	main()
