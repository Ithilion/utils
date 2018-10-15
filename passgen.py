import argparse
import secrets

import pyperclip

parser = argparse.ArgumentParser(description="A cryptographically secure (i think) password generator")
parser.add_argument("-l", type = int, choices = list(range(8,257)), default = 16, metavar="", help = "length of the generated password; valid range is 8-256; default is 16")
parser.add_argument("-n", type = int, default = 1, help = "number of generated passwords")
parser.add_argument("-t", choices = ["an", "noalt", "full"], default = "an", metavar="", help = "type of generated characters; valid input is 'an' (alphanumeric), 'noalt' (all printable ASCII characters except space, ` and ~) or 'full' (all printable ASCII characters except space); default is 'an'")
args = parser.parse_args()

if args.t == "an":
	passrange = list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123))
elif args.t == "noalt":
	passrange = list(range(33, 96)) + list(range(97, 126))
elif args.t == "full":
	passrange = list(range(33, 127))

finalpass = ""
newline = ""
for i in range(args.n):
	temppass = ""
	for i in range(args.l):
		temppass += chr(secrets.choice(passrange))
	finalpass += newline + temppass
	newline = "\n"

pyperclip.copy(finalpass)
print(f'password {finalpass} copied to clipboard')
