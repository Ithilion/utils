# TODO:
# multiple algorithms at the same time
# default algorithm (setting)
# files and folders together
# add to/remove from sendto or contextmenu shellex
# GUI ?

import argparse
import hashlib
import os
import sys
from zlib import crc32

chunk_size = 4096

parser = argparse.ArgumentParser(description = "File hash calculator")
parser.add_argument("objects", help = "files to calculate the hash of", nargs="+")
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
		if algorithm.lower() == "crc32":
			crc = 0
			for chunk in iter(lambda: f.read(chunk_size), b""):
				crc = crc32(chunk, crc)
			print(object_path)
			print("crc32:", format(crc, "08X"))
		else:
			new_hash = hashlib.new(algorithm)
			for chunk in iter(lambda: f.read(chunk_size), b""):
				new_hash.update(chunk)
			print(object_path)
			print("{:s}:".format(algorithm.lower()), new_hash.hexdigest().upper())

# for directory in os.walk("D:\test"):
# 	root, _, files = directory
# 	for filename in files:
# 		path = os.path.join(root, filename)
# 		with open(path, "rb") as f:
# 			print(format(crc32(f.read()), "X"))

# 'DSA'
# 'DSA-SHA'
# 'dsaEncryption'
# 'dsaWithSHA'
# 'ecdsa-with-SHA1'
# 'md4'
# 'MD4'
# 'MD5'
# 'md5'
# 'ripemd160'
# 'RIPEMD160'
# 'sha'
# 'SHA'
# 'sha1'
# 'SHA1'
# 'SHA224'
# 'sha224'
# 'SHA256'
# 'sha256'
# 'SHA384'
# 'sha384'
# 'sha512'
# 'SHA512'
# 'whirlpool'

# 'sha256'
# 'sha384'
# 'sha1'
# 'sha512'
# 'sha224'
# 'md5'
