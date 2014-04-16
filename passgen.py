import random
import argparse
import os
from tkinter import Tk

parser = argparse.ArgumentParser(description="A cryptographically (i think) secure password generator")
parser.add_argument("-n", type = int, choices = list(range(8,257)), default = 16, help = "number of generated charaters; valid range is 8-256; default is 16", metavar="")
parser.add_argument("-t", choices = ["an", "noalt", "full"], default = "noalt", help = "type of generated characters; valid input is 'an' (alphanumeric), 'noalt' (all printable ASCII characters except space, '`' and '~') or 'full' (all printable ASCII characters except space); default is 'noalt'", metavar="")
args = parser.parse_args()

if args.t == "an":
	passrange = list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123))
elif args.t == "noalt":
	passrange = list(range(33, 96)) + list(range(97, 126))
elif args.t == "full":
	passrange = list(range(33, 127))

muhpass = ''
for i in range(args.n):
	muhpass += chr(random.SystemRandom().choice(passrange))

r = Tk()
r.withdraw()
r.clipboard_clear()
r.clipboard_append(muhpass)
r.destroy()

print("copied password to clipboard")
