import argparse
import subprocess
import time

def start_process():
	startupinfo = subprocess.STARTUPINFO()
	startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	process = subprocess.Popen(args.commandline.split(), startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

	return process

parser = argparse.ArgumentParser(description = "Keep process alive and hide console window")
parser.add_argument("commandline", help = "process command line")
args = parser.parse_args()

process = start_process()

while True:
	if process.poll() is not None:
		process = start_process()
	time.sleep(15)
