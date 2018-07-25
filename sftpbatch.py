import argparse
import csv
import logging
import os
import tempfile

import paramiko

def progress_bar(current, total):
	try:
		progress = current / total
	except ZeroDivisionError:
		progress = 1
	print("\r[{0:50s}] {1:.1f}%".format('█' * int(progress * 50), progress * 100), end="")

parser = argparse.ArgumentParser(description = "Very simple SFTP batch uploader")
parser.add_argument("hostname", help = "the host to connect to")
parser.add_argument("username", help = "the user to connect as")
parser.add_argument("localfile", help = "path to local file")
parser.add_argument("remotefile", help = "path to remote file")
parser.add_argument("--noblock", action = "store_true", help = "don't ask for input at the end of the script")
args = parser.parse_args()

logging_dir = os.path.join(os.getenv("APPDATA"), "backup")
os.makedirs(logging_dir, exist_ok=True)
if args.noblock:
	logging.basicConfig(filename=os.path.join(logging_dir, "sftpbatch.log"), format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
else:
	logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

temp_file_name = "sftpbatch_tmp.txt"
temp_file = os.path.join(tempfile.gettempdir(), temp_file_name)
known_hosts_dir = os.path.join(os.path.expanduser('~'), ".ssh")
known_hosts_file = os.path.join(known_hosts_dir, "known_hosts")

running = os.path.exists(temp_file)

with open(temp_file, "a", newline='') as f:
	writer = csv.writer(f)
	writer.writerow([args.hostname, args.username, args.localfile, args.remotefile])
	logging.info("added: {:s} {:s} {:s} {:s}".format(args.hostname, args.username, args.localfile, args.remotefile))

if not running:
	while True:
		with open(temp_file, "r", newline='') as f:
			reader = csv.reader(f)
			try:
				firstline = next(reader)
			except StopIteration:
				break

		hostname_port, username, localfile, remotefile = firstline

		try:
			hostname, port = hostname_port.split(":")
		except ValueError:
			hostname = hostname_port
			port = 22

		logging.info("processing: {:s} {:s} {:s} {:s}".format(hostname_port, username, localfile, remotefile))

		client = paramiko.client.SSHClient()
		os.makedirs(known_hosts_dir, exist_ok=True)
		open(known_hosts_file, "a").close()
		client.load_host_keys(known_hosts_file)
		client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
		try:
			client.connect(hostname, port=int(port), username=username)
			sftp = client.open_sftp()
			if not args.noblock:
				sftp.put(localfile, remotefile, progress_bar)
				print("")
			else:
				sftp.put(localfile, remotefile)
			sftp.close()
		except Exception as e:
			logging.exception("Something went wrong while processing current upload")
		finally:
			client.close()

		with open(temp_file, "r") as f:
			data = f.read().splitlines(True)
		with open(temp_file, "w") as f:
			f.writelines(data[1:])
	os.remove(temp_file)

if not args.noblock:
	input("\nPress enter key...")
