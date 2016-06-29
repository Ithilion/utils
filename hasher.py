import argparse
import hashlib
import io
import os
import sys
from zlib import crc32

def progress_bar(current, total):
	progress = current / total
	if progress > 1:
		progress = 1
	print("\r[{:50s}] {:.1f}%".format('█' * int(progress * 50), progress * 100), end="")

def worker(file, is_bytes):
	with io.BytesIO(file) if is_bytes else open(file, "rb") as f:
		f.seek(0, os.SEEK_END)
		size = f.tell()
		f.seek(0, os.SEEK_SET)
		if algorithm.lower() == "crc32":
			crc = 0
			for i, chunk in enumerate(iter(lambda: f.read(chunk_size), b""), start=1):
				crc = crc32(chunk, crc)
				if i == 1 or not i % 10 or i * chunk_size > size:
					progress_bar(i * chunk_size, size)
			crc_text = "{:08X}".format(crc)
			print("\r{:s}\rcrc32: {:s}".format(" " * 59, crc_text), end="")
			return crc_text
		else:
			new_hash = hashlib.new(algorithm)
			for i, chunk in enumerate(iter(lambda: f.read(chunk_size), b""), start=1):
				new_hash.update(chunk)
				if i == 1 or not i % 10 or i * chunk_size > size:
					progress_bar(i * chunk_size, size)
			new_hash_text = new_hash.hexdigest().upper()
			print("\r{:s}\r{:s}: {:s}".format(" " * 59, algorithm.lower(), new_hash_text), end="")
			return new_hash_text

supported_algorithms = list(hashlib.algorithms_available) + ["crc32"]
print_supported_algorithms = sorted(set([algorithm.lower() for algorithm in supported_algorithms]))

parser = argparse.ArgumentParser(description = "File hash calculator")
parser.add_argument("-a", choices=print_supported_algorithms, default="sha1", metavar="", dest="algorithm", help="hash algorithm to use; available choices: " + ", ".join(print_supported_algorithms) + "; default is 'sha1'.")
parser.add_argument("-n", "--notruncate", action='store_true', help = "don't truncate paths to 79 characters")
parser.add_argument("-p", "--path", action='store_true', help = "include path in listing")
parser.add_argument("items", nargs="+", help = "files to calculate the hash of")
args = parser.parse_args()

chunk_size = 8192

position = [supported_algorithms[i] for i, x in enumerate(supported_algorithms) if x.lower() == args.algorithm.lower()]
if position:
	algorithm = position[0]
else:
	print("Unrecognized algorithm")
	sys.exit()

for item_path in args.items:
	item_text = item_path if args.path else os.path.basename(item_path)
	print(item_text) if len(item_text) <= 79 or args.notruncate else print("..." + item_text[-76:])
	if os.path.isdir(item_path):
		files_hashes = []
		for path, directory, file in os.walk(item_path):
			for f in file:
				files_hashes.append(worker(os.path.join(path, f), False))
		worker("".join(sorted(files_hashes)).encode("utf-8"), True)
		print("")
	else:
		worker(item_path, False)
		print("")

input("\nPress enter key...")
