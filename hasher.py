# TODO:
# multiple algorithms at the same time
# default algorithm (setting)
# files and folders together
# add to/remove from sendto or contextmenu shellex
# GUI ?

# for directory in os.walk("D:\test"):
# 	root, _, files = directory
# 	for filename in files:
# 		path = os.path.join(root, filename)
# 		with open(path, "rb") as f:
# 			print(format(crc32(f.read()), "X"))

import argparse
import hashlib
import os
import sys
from zlib import crc32

def progress_bar(current, total):
	progress = current / total
	if progress > 1:
		progress = 1
	print("\r[{:50s}] {:.1f}%".format('█' * int(progress * 50), progress * 100), end="")

chunk_size = 8192

parser = argparse.ArgumentParser(description = "File hash calculator")
parser.add_argument("-n", "--notruncate", action='store_true', help = "don't truncate paths to 79 characters")
parser.add_argument("objects", nargs="+", help = "files to calculate the hash of")
args = parser.parse_args()

supported_algorithms = list(hashlib.algorithms_available) + ["crc32"]
print_supported_algorithms = sorted(set([algorithm.lower() for algorithm in supported_algorithms]))
print("Choose from these algorithms:", ", ".join(print_supported_algorithms))

algorithm_input = input("--> ")
try:
	algorithm = algorithm_input.split()[0]
except IndexError:
	print("You didn't insert anything...")
	sys.exit()

position = [supported_algorithms[i] for i, x in enumerate(supported_algorithms) if x.lower() == algorithm.lower()]
if position:
	algorithm = position[0]
else:
	print("Unrecognized algorithm")
	sys.exit()

for object_path in args.objects:
	with open(object_path, "rb") as f:
		size = os.fstat(f.fileno()).st_size
		print(object_path) if len(object_path) <= 79 or args.notruncate else print("..." + object_path[-76:])
		if algorithm.lower() == "crc32":
			crc = 0
			for i, chunk in enumerate(iter(lambda: f.read(chunk_size), b""), start=1):
				crc = crc32(chunk, crc)
				if i == 1 or not i % 10 or i * chunk_size > size:
					progress_bar(i * chunk_size, size)
			print("\r{:s}\rcrc32: {:08X}".format(" " * 59, crc))
		else:
			new_hash = hashlib.new(algorithm)
			for i, chunk in enumerate(iter(lambda: f.read(chunk_size), b""), start=1):
				new_hash.update(chunk)
				if i == 1 or not i % 10 or i * chunk_size > size:
					progress_bar(i * chunk_size, size)
			print("\r{:s}\r{:s}:".format(" " * 59, algorithm.lower()), new_hash.hexdigest().upper())
