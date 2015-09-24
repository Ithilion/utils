import argparse
import math
import os
import re
import random

from lxml import etree

parser = argparse.ArgumentParser(description = "Converts a .qpf frame list to a .xml Matroska chapters file")
parser.add_argument("inputfile", help = ".qpf file to convert; output file name is the same of input file but with .xml extension (will be overwritten if it already exists)")
parser.add_argument("-z", "--noframezero", action='store_true', help = "do not include frame zero")
parser.add_argument("-l", "--language", default="ita", help = "chapter language in ISO639-2 format (no check against any language list is done); default is 'ita'")
parser.add_argument("-f", "--fps", default="24000/1001", help = "custom fps; use fpsnum(/|:)fpsden notation (e.g. 24/1 or 30000:1001); default is 24000/1001")
args = parser.parse_args()

if len(args.language) != 3:
	print("language is not in ISO639-2 format")
	exit()

fileName, fileExtension = os.path.splitext(args.inputfile)
if fileExtension != ".qpf":
	print("inputfile is not a qpf file")
	exit()

r = re.compile(r"[1-9]\d*(/|:)\d+")
match = r.match(args.fps)
if not match:
	print("invalid --fps input")
	exit()
fpsnum, fpsden = re.split("/|:", match.group())

with open(args.inputfile, "r") as f:
	lines = f.read().splitlines()

	frames = ['0']
	if args.noframezero:
		frames.pop()

	r = re.compile(r"\d+")
	for line in lines:
		match = r.match(line)
		if match:
			frames += [match.group()]

random_ids = random.sample(range(10000,100000), len(frames) + 1)

frametimes = []
for frame in frames:
	hour = minute = second = 0
	ms = math.floor(((1000 * int(fpsden) * int(frame)) / int(fpsnum)) + 0.5)
	while ms >= 3600000:
		ms -= 3600000
		hour += 1
	while ms >= 60000:
		ms -= 60000
		minute += 1
	while ms >= 1000:
		ms -= 1000
		second += 1
	frametimes += [[hour, minute, second, ms]]

Chapters = etree.Element("Chapters")
EditionEntry = etree.SubElement(Chapters, "EditionEntry")
EditionFlagHidden = etree.SubElement(EditionEntry, "EditionFlagHidden")
EditionFlagHidden.text = "0"
EditionFlagDefault = etree.SubElement(EditionEntry, "EditionFlagDefault")
EditionFlagDefault.text = "0"
EditionUID = etree.SubElement(EditionEntry, "EditionUID")
EditionUID.text = str(random_ids[0])

for frame, random_id, frametime in zip(frames, random_ids[1:], frametimes):
	hour, minute, second, ms = frametime

	ChapterAtom = etree.SubElement(EditionEntry, "ChapterAtom")

	ChapterDisplay = etree.SubElement(ChapterAtom, "ChapterDisplay")
	ChapterString = etree.SubElement(ChapterDisplay, "ChapterString")
	ChapterString.text = "Chapter" + frame
	ChapterLanguage = etree.SubElement(ChapterDisplay, "ChapterLanguage")
	ChapterLanguage.text = args.language

	ChapterUID = etree.SubElement(ChapterAtom, "ChapterUID")
	ChapterUID.text = str(random_id)
	ChapterTimeStart = etree.SubElement(ChapterAtom, "ChapterTimeStart")
	ChapterTimeStart.text = "{:02d}:{:02d}:{:02d}.{:03d}000000".format(hour, minute, second, ms)
	ChapterFlagHidden = etree.SubElement(ChapterAtom, "ChapterFlagHidden")
	ChapterFlagHidden.text = "0"
	ChapterFlagEnabled = etree.SubElement(ChapterAtom, "ChapterFlagEnabled")
	ChapterFlagEnabled.text = "1"

with open(fileName + ".xml", "w") as f:
	bytexml = etree.tostring(Chapters, pretty_print = True, xml_declaration = True, encoding = "UTF-8", doctype = "<!DOCTYPE Chapters SYSTEM \"matroskachapters.dtd\">")
	f.write(bytexml.decode("UTF-8"))
