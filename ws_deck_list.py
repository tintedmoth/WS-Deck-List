# ---------------------------------------------- #
# Auto-fill deck registration sheet Weiss Schwarz
#
# Original Author: Enrico Salvatore Brancato
# ---------------------------------------------- #

import base64
import io
import json
import logging
import math
import os
import subprocess
import sys
import urllib.request
from zlib import decompress as zdecom

from PIL import Image as pImage
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily, stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import PageTemplate, Frame, NextPageTemplate, SimpleDocTemplate, Paragraph, Image, Table

try:
	import title
except ImportError:
	pass

registerFont(TTFont('MSGothic', 'msgothic.ttc'))
registerFont(TTFont('Calibri', 'calibri.ttf'))
registerFont(TTFont('Calibri-Bold', 'calibrib.ttf'))
registerFont(TTFont('Calibri-Italic', 'calibrii.ttf'))
registerFont(TTFont('Calibri-BoldItalic', 'calibriz.ttf'))

registerFontFamily('Calibri', normal='Calibri', bold='Calibri-Bold', italic='Calibri-Italic', boldItalic='Calibri-BoldItalic')

main_dir = "."
res_dir = "./res"
pic_dir = "./pic"
deck_dir = "./deck"
sheet_dir = "./sheet"
if not os.path.exists(res_dir):
	os.makedirs(res_dir)
if not os.path.exists(pic_dir):
	os.makedirs(pic_dir)
if not os.path.exists(deck_dir):
	os.makedirs(deck_dir)
if not os.path.exists(sheet_dir):
	os.makedirs(sheet_dir)

with open(f"{res_dir}/log", "w", encoding='utf8') as log_file:
	pass
logging.basicConfig(filename=f"{res_dir}/log", level=logging.DEBUG)

'''
to add
- different directory
- option to change directory
- import deck list
- multiple set in title series
- edit cards added before confirmation
- other option in confirmation
'''


class Sheet:
	blank = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAACxMAAAsTAQCanBgAAAAHdElNRQfiARcUDBdTv5fYAAAAC0lEQVQI12N4ywAAAd0A7sU5uXsAAAAASUVORK5CYII="
	fontname = "Helvetica"
	fontjap = "MSGothic"
	fontsize = 11
	regsheet = ["ws-registration-consent-2018_ver.pdf", "ws-registration-consent-2018_v1.pdf", "Deck-Registration-WS-w-consent-2018v2.pdf"]
	oldregsheet = "Deck-Registration-WS-w-consent-2.pdf"
	data_name = "data.db"
	title_name = "title.txt"
	reg_name = "ws-registration-consent-2018_ver.pdf"
	pdf_name = ""
	pdf_done = False
	zip = 'I2UHBG58pJ'

	cdata = {}
	tdata = {}
	sets = []

	cards = 0
	climax = 0
	names = {}
	deck_name = ""
	deck_name_o = ""
	series_title = ""
	player_name = ""
	location = ""
	date = ""
	guardian = ""
	code = 0
	title = ""
	card_data = {}
	deck_list = []
	deck_list_edited = []
	qty = {}
	card_error = []
	card_error_qty = []
	zodiac = ("Ari", "Gem", "Leo", "Sgr", "Tau", "Vir", "Ang", "Bra", "Cob", "Hot", "Mid", "Rac")
	end_rariry = ("SSP", "JSP", "PPR", "SR", "RRR", "XR", "SWR", "SP", "μR", "SBR", "FBR", "BNP", "SEC", "OFR")
	ssp = ("SSP", "JSP", "PPR")
	special = ("S", "R", "X", "P", "J")
	sp_pr = ("SP", "PR", "μR")
	te_pe = ("TE", "PE")
	t_p = ("T", "P")
	jplayable = ("55", "56", "57", "58", "59", "60","P02")
	variant = "abcdefghi"
	n = 0
	other = ["E", "y", "y", "y", "y"]
	e = ("P4/EN-S01-E", "LL/EN-W01-E")
	exbox = 0
	exbox_list = ("/SE", "/WE")
	set_id = ["/WS","/S","/EN-S","/MIR","/W","/TBS","/PSP"]
	lang = ""
	d = 0
	characters = ("\\", "/", ":", "*", "?", '"', "<", ">", "|")
	aonly = False
	auto_set = False

	def __init__(self):
		if not os.path.exists(f"{pic_dir}/blank.png"):
			with open(f"{pic_dir}/blank.png", 'wb') as img:
				img.write(base64.b64decode(self.blank))

		if os.path.exists(f"{res_dir}/{self.data_name}"):
			print(f"\nDatabase file location: '{res_dir}/{self.data_name}'")

		if any(os.path.exists(f"{res_dir}/{pdf}") for pdf in self.regsheet) or os.path.exists(f"{res_dir}/{self.oldregsheet}"):
			print(f"\nDeck Registration Sheet location: {res_dir}")
			for reg in self.regsheet + [self.oldregsheet]:
				if os.path.exists(f"{res_dir}/{reg}"):
					self.reg_name = reg

			self.import_database()
			self.eng_jap()
		else:
			print(f'The file "{self.reg_name}" is missing.')
			print("This file may have a different name based on the version")

	def import_database(self):
		self.other[4] = "n"

		if not os.path.exists(f"{res_dir}/{self.data_name}"):
			for file in os.listdir(res_dir):
				if file.endswith(".txt") or file.endswith(".html"):
					if file in self.regsheet + [self.data_name, self.title_name]:
						continue
					txt = open(f"{res_dir}/{file}", "r", encoding="utf8")
					for line in txt.readlines():
						if "Downloaded from HeartOfTheCards.com" in line:
							self.add_file_to_data(file)
							break
					txt.close()
		else:
			with open(f"{res_dir}/{self.data_name}", "r", encoding="utf8") as read_file:
				if self.data_name.startswith("c"):
					self.cdata = self.json_unzip(json.load(read_file))
				else:
					self.cdata = json.load(read_file)

		self.tdata = {}
		if os.path.exists(f"{res_dir}/{self.title_name}"):
			with open(f"{res_dir}/{self.title_name}","r",encoding="utf8") as title_file:
				for tt in title_file.readlines():
					var = tt.replace("\n","").split("\t")
					self.tdata[var[0]] = var[1].replace(","," ").split()

	def add_file_to_data(self, file_name):
		skip = [["translation", "downloaded", "reprint", "repost", "======"],
		        ["Card No.:", "Color:", "Side:", "Level:", "Cost:", "Power:", "Soul:", "Traits:", "Trait 1:", "Trait 2:", "Triggers:", "Flavor:", "TEXT:"],
		        ["legal", "tournament"],
		        ["", "\t", " "]]

		card = ""
		eng = ""
		jap = ""
		e = True
		j = True
		f = True

		for line in open(f"{res_dir}/{file_name}", "r", encoding="utf8").readlines():
			if "\n" in line and ".\n" not in line:
				var = line.replace("\n", "")
			else:
				var = line

			if var.startswith("<"):
				continue

			if var.startswith(" "):
				var = var[1:]

			if any(z in var.lower() for z in skip[0]):
				if "======" in var:
					e = True
					j = True
					f = True
					jap = ""
				continue

			if any(blank in var and len(var) <= 1 for blank in skip[3]):
				continue

			if any(z in var for z in skip[1]):
				if "Card No.:" in var:
					e = False
					j = False
					var = var.replace("Card No.:", "")
					var = var.replace("Rarity:", "")
					var = var.split()

					card = var[0]

					self.cdata[var[0]] = {}
					self.cdata[var[0]]["id"] = str(var[0])

					try:
						self.cdata[var[0]]["rarity"] = str(var[1])
					except IndexError:
						if "promo" in file_name.lower():
							self.cdata[var[0]]["rarity"] = "PR"
						else:
							self.cdata[var[0]]["rarity"] = ""
					self.cdata[var[0]]["name"] = str(eng)
					self.cdata[var[0]]["jap"] = str(jap)
					self.cdata[var[0]]["img"] = var[0].lower().replace("/", "_").replace("-", "_")

					if var[0].split("-")[0] + "-" not in self.sets:
						self.sets.append(var[0].split("-")[0] + "-")

				elif "Color:" in var:
					var = var.replace("Color:", "")
					var = var.replace("Side:", "")
					var = var.split()

					self.cdata[card]["colour"] = var[0]
					self.cdata[card]["side"] = var[1]
					self.cdata[card]["type"] = var[2]

				elif "Level:" in var:
					var = var.replace("Level:", "")
					var = var.replace("Cost:", "")
					var = var.replace("Power:", "")
					var = var.replace("Soul:", "")
					var = var.split()

					self.cdata[card]["level"] = var[0]
					self.cdata[card]["cost"] = var[1]
					self.cdata[card]["power"] = var[2]
					self.cdata[card]["soul"] = var[3]

				elif "Trait 1:" in var:
					var = var.replace("Trait 1:", "")
					var = var.replace("Trait 2:", "")
					var = var.split()

					jt = []
					et = []
					temp = ""

					if len(var) == 4:
						jt.append(var[0])
						jt.append(var[2])
						et.append(var[1])
						et.append(var[3])
					else:
						for y in var:
							if all(ord(char) < 128 for char in y):
								if "none" in y.lower():
									jt.append(y)
									et.append(y)

								elif "(" in temp and "(" not in y and ")" not in y:
									temp += y + " "
								elif len(jt) < 2 and "(" not in y and ")" not in y:
									jt.append(y)
								elif "(" in y and ")" in y:
									et.append(y)
								elif ")" in y:
									temp += y
									et.append(temp)
									temp = ""
								elif "(" in y:
									temp += y + " "

								else:
									temp = y
							else:
								jt.append(y)

					self.cdata[card]["trait"] = []
					self.cdata[card]["traitj"] = []
					for tr in et:
						if "none" in tr.lower():
							continue
						self.cdata[card]["trait"].append(tr.replace("(", "").replace(")", ""))

					for trj in jt:
						if "none" in trj.lower():
							continue
						elif "―" in trj.lower():
							continue
						self.cdata[card]["traitj"].append(trj.replace("(", "").replace(")", ""))

				elif "Traits:" in var:
					var = var.replace("Traits:", "").replace(",", "").replace("()", "").replace("\xe2\x80\x90", "")
					var = var.split()

					temp = []
					temp1 = ""
					br = False
					for item in var:
						if "(" in item:
							br = True
						if br and ")" not in item:
							temp1 += f"{item} "
						elif br and ")" in item:
							temp1 += item
							br = False
							temp.append(temp1)
							temp1 = ""
						else:
							temp.append(item)
					var = temp

					self.cdata[card]["trait"] = []
					self.cdata[card]["traitj"] = []
					if len(var) >= 2:
						for i in range(int(len(var) / 2)):
							tr = var[i * 2 + 1]
							trj = var[i * 2]
							if tr.count("(") >= 2:
								tr = tr[1:-1]
							else:
								tr = tr.replace("(", "").replace(")", "")
							self.cdata[card]["trait"].append(tr)
							self.cdata[card]["traitj"].append(trj.replace("(", "").replace(")", ""))
					else:
						self.cdata[card]["trait"] = []
						self.cdata[card]["traitj"] = []

				elif "Triggers:" in var:
					var = var.replace("Triggers: ", "")

					if "2" in var:
						var = var.replace("2", "Soul")
					elif "None" in var:
						var = ""
					var = var.split()

					self.cdata[card]["trigger"] = []

					for y in var:
						self.cdata[card]["trigger"].append(y.lower())

				elif "Flavor:" in var:
					var = var.replace("Flavor:", "")

					if var[0] == " ":
						var = var[1:]
					if "-- None --" in var:
						var = ""
					elif "none" in var.lower():
						var = ""

					self.cdata[card]["flavour"] = var

				elif "TEXT:" in var:
					f = False
					var = var.replace("TEXT:", "")
					if var[0] == " ":
						var = var[1:]

					self.cdata[card]["text"] = [f"{self.replace_text(var)}"]

			else:
				var = var.replace("\n", "")
				if e:
					eng = str(var)
					e = False
					if '"' in eng:
						tname = eng.replace('"', "“", 1)
						tname = tname.replace('"', "”", 1)
						self.names[eng] = str(tname)
						eng = str(tname)
				elif j:
					jap = str(var)
					j = False
				elif f:
					self.cdata[card]["flavour"] = self.cdata[card]["flavour"] + " " + var

				else:
					var = self.replace_text(var)

					n = len(self.cdata[card]["text"])
					if (var[0] == "[" and "[standby" not in var.lower()) or var[0] == "(":
						self.cdata[card]["text"].append(var)
					else:
						self.cdata[card]["text"][n - 1] = self.cdata[card]["text"][n - 1] + " " + var

	def replace_text(self, var):
		var = var.replace("[C]", "[CONT]")
		var = var.replace("[A]", "[AUTO]")
		var = var.replace("[S]", "[ACT]")
		var = var.replace("\n", "")

		if "-- None --" in var:
			var = ""
		elif var == "-":
			var = ""

		for inx in range(var.count("::") // 2):
			var = var.replace("::", "«", 1)
			var = var.replace("::", "»", 1)

		return var

	def json_unzip(self, j, insist=True):
		try:
			assert (j[self.zip])
			assert (set(j.keys()) == {self.zip})
		except:
			if insist:
				raise RuntimeError("JSON not in the expected format {" + str(self.zip) + ": zipstring}")
			else:
				return j

		try:
			j = zdecom(base64.b64decode(j[self.zip]))
		except:
			raise RuntimeError("Could not decode/unzip the contents")

		try:
			j = json.loads(j)
		except:
			raise RuntimeError("Could interpret the unzipped contents")

		return j

	def eng_jap(self):
		if not os.path.exists(f"{res_dir}/{self.data_name}"):
			self.other[0] = "J"
			self.start()
		else:
			print("\nWhat language are you playing?\tENG/JAP or E/J")
			lang = input(" >\t")

			if lang == "q" or lang == "quit":
				sys.exit()
			elif lang == "r" or lang == "reset":
				self.eng_jap()
			elif lang.upper() == "ENG" or lang.upper() == "E":
				self.other[0] = "E"
				self.start()
			elif lang.upper() == "JAP" or lang.upper() == "J":
				self.other[0] = "J"
				self.start()
			else:
				print("\nInput Error\n")
				self.eng_jap()

	def check_lang(self):
		if self.other[0].upper() == "E":
			if self.title.upper() in self.e:
				self.lang = ""
			else:
				self.lang = "E"
		elif self.other[0].upper() == "J":
			self.lang = ""
		else:
			pass

	def start(self):
		self.clear()
		self.pdf_done = False

		self.check_extrabox()
		self.add_cards()
		self.n = -1
		self.restart()

	def clear(self):
		self.deck_list = []
		self.deck_list_edited = []
		self.qty = {}
		self.climax = 0
		self.cards = 0

	def restart(self):
		if self.pdf_done:
			if self.other[0] == "J":
				end = input("\nInput 'o' or 'open' to open file.\nInput 't' or 'translation' to open translation file\nInput 'q' or press ENTER to quit.\nInput 'r' or 'reset' to restart:\n >\t")
			else:
				end = input("\nInput 'o' or 'open' to open file.\nInput 't' or 'translation' to open translation file\nInput 'q' or press ENTER to quit.\nInput 'r' or 'reset' to restart:\n >\t")
		else:
			end = input("\nInput 'q' or press ENTER to quit.\nInput 'r' or 'reset' to restart.\n >\t")

		self.n += 1

		if self.n >= 5:
			sys.exit()
		elif end.lower() == "r" or end.lower() == "reset":
			self.clear()
			self.pdf_done = False
			self.eng_jap()
		elif end.lower() == "q" or end.lower() == "quit" or end.lower() == "":
			sys.exit()
		elif self.pdf_done and (end.lower() == "o" or end.lower() == "open"):
			if sys.platform == 'linux2':
				subprocess.call(["xdg-open", self.pdf_name])
			else:
				os.startfile(self.pdf_name)
			self.restart()
		elif self.pdf_done and (end.lower() == "t" or end.lower() == "translation"):
			if sys.platform == 'linux2':
				subprocess.call(["xdg-open", self.pdf_name[:-4] + "_translation.pdf"])
			else:
				os.startfile(self.pdf_name.replace(".pdf", "") + "_translation.pdf")
			self.restart()
		else:
			self.restart()

	def add_card_instruction(self):
		print("\nAdd card using the format 'code' 'quantity': e.g. FS/S36-E001 3\nTo end input 'e' or 'end'.")
		if os.path.exists(f"{res_dir}/{self.data_name}") and self.auto_set:
			print("To change the sets input 'c' or 'change'.")
		print("To check the current deck list input 'l' or 'list'.\n")
		self.n += 1

	def add_cards(self):
		text = True
		self.add_card_instruction()

		while text:
			line = input(" >\t")
			line = line.replace("\t", " ")

			if self.n % 10 == 0:
				self.add_card_instruction()
			elif line.lower() == "q" or line.lower() == "quit":
				sys.exit()
			elif line.lower() == "":
				self.n += 1
			elif line.lower() == "r" or line.lower() == "reset":
				self.start()
			elif line.lower() == "e" or line.lower() == "end":
				text = False
				self.check_list("t")
			elif line.lower() == "l" or line.lower() == "list":
				self.n = 0
				self.check_list()
			elif len(line.split()) == 1:
				print("\nMissing second input.\n")
				self.n += 1
			elif not line.lower() == "":
				var = line.split()
				if len(var)>2:
					if any(st in var[0] for st in self.set_id) and "-" in var[0]:
						try:
							int(var[1])
							if var[-1] == "p":
								var = var[:3]
							else:
								var = var[:2]
						except AttributeError:
							pass

				if len(var) % 2 == 0 or var[-1] == "p":
					if "Woo" in var[0]:
						var[0] = var[0].split("-")[0] + "-" + var[0].split("-")[1]
					else:
						if len(var[0].split("-")) > 2:
							var[0] = var[0].split("-")[0] + "-" + var[0].split("-")[1] + "-" + var[0].split("-")[2]
						else:
							var[0] = var[0].split("-")[0] + "-" + var[0].split("-")[1]

					if len(var) == 2 or (len(var) == 3 and var[2] == "p"):
						try:
							if len(var) == 3 and var[2] == "p":
								self.cdata[var[0]]["parallel"] = True
							else:
								self.cdata[var[0]]["parallel"] = False
						except KeyError:
							print(var)

						if var[0] in self.cdata and var[0] in self.deck_list and var[1].isdigit():
							if self.cdata[var[0]]["type"] == "Climax":
								self.cards -= int(self.qty[var[0]])
								self.climax -= int(self.qty[var[0]])

								self.qty[var[0]] = var[1]

								self.climax += int(var[1])
								self.cards += int(var[1])
							else:
								self.cards -= int(self.qty[var[0]])
								self.qty[var[0]] = var[1]
								self.cards += int(var[1])
						elif var[0] in self.cdata and var[1].isdigit():
							self.deck_list.append(var[0])
							self.qty[var[0]] = var[1]
							self.cards += int(var[1])
							if self.cdata[var[0]]["type"] == "Climax":
								self.climax += int(var[1])
						elif var[0] in self.cdata and var[1].isdigit():
							self.deck_list.append(var[0])
							self.qty[var[0]] = var[1]
							self.cards += int(var[1])
							if self.cdata[var[0]]["type"] == "Climax":
								self.climax += int(var[1])
						elif var[0] in self.cdata and not var[1].isdigit():
							self.card_error_qty.append(var[0])
						else:
							self.card_error.append(var[0])

					else:
						print("\nMultiple cards input failed\n")
						self.n += 1
						continue

					if len(self.card_error) > 0 or len(self.card_error_qty) > 0:
						print("\nInput Error.")
						for x in range(len(self.card_error)):
							print(f"{self.card_error[x]} does not exist in database\n")
						for y in range(len(self.card_error_qty)):
							print(f"Quantity error in {self.card_error_qty[y]}\n")
						self.card_error_qty = []
						self.card_error = []
				elif len(var) % 2 != 0:
					print("\nMultiple cards input failed or odd number of input\n")
					self.n += 1
			else:
				print("\nInput Error\n")
				self.n += 1

	def check_extrabox(self, cset=""):
		if any(x in cset for x in self.exbox_list):
			self.exbox = 1
		else:
			pass

	def change_set(self):
		print(f"\nSelect and input a different set.\tCurrent: {self.card_data['sets'][self.other[0]][self.title.upper()][self.code]}")

		for x in range(len(self.card_data["sets"][self.other[0]][self.title.upper()])):
			print(f"\t{x}\t{self.card_data['sets'][self.other[0]][self.title.upper()][x]}")

		code = input("\n >\t")

		if code.isdigit():
			self.code = int(code)
			self.check_extrabox()
			self.add_cards()
		elif code.lower() == "q" or code.lower() == "quit":
			sys.exit()
		elif code.lower() == "r" or code.lower() == "reset":
			self.start()
		elif code.lower() == "":
			self.change_set()
		elif code.lower() == "e" or code.lower() == "end":
			self.check_list("t")
		elif code.lower() == "l" or code.lower() == "list":
			self.check_list()
			self.n = 10
			self.add_cards()
		else:
			self.change_set()

	def check_list(self, test="n"):
		print("\nPrinting Deck list on screen:")
		print("-" * 50)

		self.deck_list = sorted(self.deck_list)

		self.deck_list = sorted(self.deck_list, key=lambda x: self.cdata[x]["level"])

		for x in range(len(self.deck_list)):
			print("\tx%s\t%s\tLv %s\t%s" % (self.qty[self.deck_list[x]], self.deck_list[x], self.cdata[self.deck_list[x]]["level"],self.cdata[self.deck_list[x]]["name"]))

		print("-" * 50)
		print(f"Total cards: {self.cards}\tClimax: {self.climax}")

		if test == "t":
			if self.cards > 50:
				print("Too many cards in deck. Cards to remove %s" % (self.cards - 50))
				self.change_card()
			elif self.cards < 50:
				print("Missing cards in deck. Card to add %s" % (50 - self.cards))
				self.change_card()
			if self.climax > 8:
				print("Too many Climax cards in deck. Climax cards to remove %s" % (self.climax - 8))
				self.change_card()
			self.confirm()

	def print_list_title(self):
		print(self.card_data["title"])
		for title in sorted(self.card_data["title"][self.other[0]]):
			print("%s\t%s" % (title, self.card_data["title"][self.other[0]][title].encode("ascii", "ignore")))

	def option(self):
		pass

	def change_card(self):
		pass

	def add_player_name(self):
		if self.other[2] == "y":
			reply = input("\nAdd/Change Player Name?\tY/N\nCurrent:\t%s\n >\t" % self.player_name)
			if reply.lower() == "q" or reply.lower() == "quit":
				sys.exit()
			elif reply.lower() == "y" or reply.lower() == "yes":
				self.player_name = input("\nType Player Name:\n >\t")
				self.add_deck_name()
			elif reply.lower() == "n" or reply.lower() == "no":
				self.add_deck_name()
			elif reply.lower() == "nn" or reply.lower() == "nono":
				pass
			elif reply.lower() == "r" or reply.lower() == "reset":
				self.add_player_name()
			elif reply.lower() == "b" or reply.lower() == "back":
				self.confirm()
			else:
				print("\nInput Error\n")
				self.add_player_name()
		else:
			pass

	def add_deck_name(self):
		if self.other[1] == "y":
			reply = input("\nAdd/Change Deck Name?\tY/N\nCurrent:\t%s\n >\t" % self.deck_name)
			if reply.lower() == "q" or reply.lower() == "quit":
				sys.exit()
			elif reply.lower() == "y" or reply.lower() == "yes":
				self.deck_name = input("\nType Deck Name:\n >\t")
				self.deck_name_o = self.deck_name
				self.add_date()
			elif reply.lower() == "n" or reply.lower() == "no":
				self.add_date()
			elif reply.lower() == "nn" or reply.lower() == "nono":
				pass
			elif reply.lower() == "r" or reply.lower() == "reset":
				self.add_deck_name()
			elif reply.lower() == "b" or reply.lower() == "back":
				self.add_player_name()
			else:
				print("\nInput Error\n")
				self.add_deck_name()
		else:
			pass

	def add_series_title(self):
		if self.other[4] == "y":
			reply = input("\nAdd/Change Series Title?\tY/N\n >\t")
			if reply.lower() == "q" or reply.lower() == "quit":
				sys.exit()
			elif reply.lower() == "y" or reply.lower() == "yes":
				self.series_title = input("\nType Series Title:\n >\t")
			elif reply.lower() == "n" or reply.lower() == "no":
				pass
			elif reply.lower() == "r" or reply.lower() == "reset":
				self.add_series_title()
			elif reply.lower() == "b" or reply.lower() == "back":
				self.add_deck_name()
			else:
				print("\nInput Error\n")
				self.add_series_title()
		else:
			pass

	def add_date(self):
		if self.other[3] == "y":
			reply = input("\nAdd/Change different Date?\tY/N\nCurrent:\t%s\n >\t" % self.date)
			if reply.lower() == "q" or reply.lower() == "quit":
				sys.exit()
			elif reply.lower() == "y" or reply.lower() == "yes":
				self.date = input("\nType Date:\n >\t")
				self.add_location()
			elif reply.lower() == "n" or reply.lower() == "no":
				self.add_location()
			elif reply.lower() == "nn" or reply.lower() == "nono":
				pass
			elif reply.lower() == "r" or reply.lower() == "reset":
				self.add_date()
			elif reply.lower() == "b" or reply.lower() == "back":
				self.add_deck_name()
			else:
				print("\nInput Error\n")
				self.add_date()
		else:
			pass

	def add_location(self):
		if self.other[3] == "y":
			reply = input("\nAdd/Change Location?\tY/N\nCurrent:\t%s\n >\t" % self.location)
			if reply.lower() == "q" or reply.lower() == "quit":
				sys.exit()
			elif reply.lower() == "y" or reply.lower() == "yes":
				self.location = input("\nType Location:\n >\t")
				self.add_guardian()
			elif reply.lower() == "n" or reply.lower() == "no":
				self.add_guardian()
			elif reply.lower() == "nn" or reply.lower() == "nono":
				pass
			elif reply.lower() == "r" or reply.lower() == "reset":
				self.add_location()
			elif reply.lower() == "b" or reply.lower() == "back":
				self.add_date()
			else:
				print("\nInput Error\n")
				self.add_location()
		else:
			pass

	def add_guardian(self):
		if self.other[3] == "y":
			reply = input(f"\nAdd/Change Guardian Name?\tY/N\nCurrent:\t{self.guardian}\n >\t")
			if reply.lower() == "q" or reply.lower() == "quit":
				sys.exit()
			elif reply.lower() == "y" or reply.lower() == "yes":
				self.guardian = input("\nType Guardian Name:\n >\t")
			elif reply.lower() == "n" or reply.lower() == "no":
				pass
			elif reply.lower() == "r" or reply.lower() == "reset":
				self.add_guardian()
			elif reply.lower() == "b" or reply.lower() == "back":
				self.add_location()
			else:
				print("\nInput Error\n")
				self.add_guardian()
		else:
			pass

	def confirm(self):
		approve = input("\nIs the deck list correct?\tY/N\n >\t")
		if approve.lower() == "q" or approve.lower() == "quit":
			sys.exit()
		elif approve.lower() == "r" or approve.lower() == "reset":
			self.start()
		elif approve.lower() == "y" or approve.lower() == "yes":
			self.add_player_name()
			print("\nAdding deck list to registration sheet...")
			if any(os.path.exists(f"{res_dir}/{pdf}") and pdf != self.oldregsheet for pdf in self.regsheet):
				self.fill_form_pdf(f"{res_dir}/{self.reg_name}")
				if self.other[0] == "J":
					self.fill_form_pdf(f"{res_dir}/{self.reg_name}", eng=True)
					print("\nCreating translation sheet of deck...")
					self.translation()
			else:
				try:
					self.create_pdf()
					print(f"\nDone adding to registration sheet.\nCreating file '{self.pdf_name}'.")
					if self.other[0] == "J":
						self.create_pdf(eng=True)
						print("\nCreating translation sheet of deck...")
						self.translation()
				except IOError:
					print(f"The file {self.pdf_name} is already opened. Close the file then retry.")

		elif approve.lower() == "n" or approve.lower() == "no":
			self.change_card()
		elif approve.lower() == "r" or approve.lower() == "reset":
			self.confirm()
		elif approve.lower() == "b" or approve.lower() == "back":
			self.add_cards()
		else:
			self.confirm()

	def fill_form_pdf(self, pdfpath, eng=False):
		with open(pdfpath, 'rb') as f:
			pdf = PdfFileReader(f, strict=False)
			if "/AcroForm" in pdf.trailer["/Root"]:
				pdf.trailer["/Root"]["/AcroForm"].update({NameObject("/NeedAppearances"): BooleanObject(True)})

			form = {}
			title = ""
			initial = ""
			if eng and self.other[0] == "J":
				name = "name"
			elif self.other[0] == "J":
				name = "jap"
			else:
				name = "name"

			for key in self.tdata.keys():
				if all(card.split("/")[0] in self.tdata[key] for card in self.deck_list):
					initial = self.tdata[key][0].split("/")[0].lower()
					title = key

			form["Title"] = title
			form["Deck Name"] = self.deck_name_o
			form["Player Name"] = self.player_name
			form["Location"] = self.location
			form["undefined_3"] = self.date
			if self.guardian != "" and self.guardian != self.player_name:
				form[u"undefined_1"] = self.guardian
			else:
				form[u"undefined_1"] = self.player_name

			x = 1
			y = 1
			z = 1
			for inx in range(len(self.deck_list)):
				card = self.cdata[self.deck_list[inx]]

				if card["type"] == "Character":
					form[u"Qty%s" % x] = self.qty[self.deck_list[inx]]
					form[u"No%s" % x] = self.deck_list[inx]
					form[u"Lvl%s" % x] = card["level"]
					try:
						form[u"Row%s" % x] = card[name]
					except KeyError:
						form[u"Row%s" % x] = card["name"]
					x += 1

				elif card["type"] == "Event":
					form[u"Row%s_2" % y] = self.qty[self.deck_list[inx]]
					form[u"Row%s_3" % y] = self.deck_list[inx]
					form[u"Row%s_4" % y] = card["level"]
					try:
						form[u"Row%s_5" % y] = card[name]
					except KeyError:
						form[u"Row%s_5" % y] = card["name"]
					y += 1

				elif card["type"] == "Climax":
					form[u"Cx Row%s" % z] = self.qty[self.deck_list[inx]]
					form[u"Cx No Row%s" % z] = self.deck_list[inx]
					try:
						form[u"ex_%s" % z] = card[name]
					except KeyError:
						form[u"ex_%s" % z] = card["name"]
					z += 1

			pdf_write = PdfFileWriter()
			self.set_need_appearances_writer(pdf_write)
			if "/AcroForm" in pdf_write._root_object:
				pdf_write._root_object["/AcroForm"].update({NameObject("/NeedAppearances"): BooleanObject(True)})

			pdf_write.appendPagesFromReader(pdf)

			if self.deck_name != "":
				for y in range(len(self.characters)):
					if self.characters[y] in self.deck_name:
						self.deck_name = self.deck_name.replace(self.characters[y], "")
				print("Removed special characters in file name")
				if eng:
					pdf_out = open(self.deck_name + "_eng.pdf", "wb")
				else:
					pdf_out = open(self.deck_name + ".pdf", "wb")
				self.pdf_name = self.deck_name + ".pdf"
			else:
				word = initial
				try:
					self.pdf_name = word + "_deck" + str(self.d) + ".pdf"
					if eng:
						pdf_out = open(self.pdf_name[:-4] + "_eng.pdf", "wb")
					else:
						pdf_out = open(self.pdf_name, "wb")

				except IOError:
					self.d += 1
					self.pdf_name = word + "_deck" + str(self.d) + ".pdf"
					if eng:
						pdf_out = open(self.pdf_name[:-4] + "_eng.pdf", "wb")
					else:
						pdf_out = open(self.pdf_name, "wb")

			pdf_write.updatePageFormFieldValues(pdf_write.getPage(0), form)
			pdf_write.write(pdf_out)
			pdf_out.close()
			self.pdf_done = True


	def set_need_appearances_writer(self, writer):
		# See 12.7.2 and 7.7.2 for more inimgtypeion: http://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
		try:
			catalog = writer._root_object
			# get the AcroForm tree
			if "/AcroForm" not in catalog:
				writer._root_object.update({NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

			need_appearances = NameObject("/NeedAppearances")
			writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
			return writer

		except Exception as e:
			print('set_need_appearances_writer() catch : ', repr(e))
			return writer

	def create_pdf(self, eng=False):
		packet = io.BytesIO()

		canvas = Canvas(packet)
		canvas.setLineWidth(.3)
		canvas.setFont(self.fontname, self.fontsize)

		x = 0
		y = 0
		z = 0

		canvas.setFont(self.fontname, 9.5)

		title = ""
		initial = ""
		if eng:
			name = "name"
		else:
			name = "jap"

		if not os.path.exists(f"{res_dir}/{self.title_name}"):
			for key in self.tdata.keys():
				if all(card.split("/")[0] in self.tdata[key] for card in self.deck_list):
					initial = self.tdata[key][0].split("/")[0].lower()
					title = key
		else:
			title = self.card_data["title"][self.other[0]][self.title.upper()]

		canvas.drawString(35.592 + (248.041 - 35.592 - stringWidth(title, self.fontname, 9.5)) / 2, 727.36, title)

		canvas.drawString(248.041 + (558.534 - 248.041 - stringWidth(self.deck_name_o, self.fontname, 9.5)) / 2, 727.36, self.deck_name_o)

		canvas.setFont(self.fontname, self.fontsize)

		canvas.drawString(120.452 + (558.534 - 120.452 - stringWidth(self.player_name, self.fontname, self.fontsize)) / 2, 755.75, self.player_name)

		for inx in range(len(self.deck_list)):
			if "data.db" not in os.listdir("./"):
				card = self.cdata[self.deck_list[inx]]
			else:
				card = self.card_data[self.deck_list[inx]]

			if card["type"] == "Character":
				canvas.drawString(58, 656.5 - 17.52 * x, self.qty[self.deck_list[inx]])
				canvas.drawString(193.34, 656.5 - 17.52 * x, str(card["level"]))

				if self.other[0] == "J":
					canvas.setFont(self.fontjap, self.fontsize)
				canvas.drawString(232, 656.5 - 17.52 * x, card[name])
				if self.other[0] == "J":
					canvas.setFont(self.fontname, self.fontsize)

				if len(self.deck_list[inx]) >= 13:
					canvas.setFont(self.fontname, self.fontsize * 14 / len(self.deck_list[inx]))

				canvas.drawString(91, 656.5 - 17.52 * x, self.deck_list[inx])
				canvas.setFont(self.fontname, self.fontsize)
				x += 1

			elif card["type"] == "Event":
				canvas.drawString(58, 205.66 - 17.520 * y, self.qty[self.deck_list[inx]])
				canvas.drawString(193.34, 205.66 - 17.520 * y, card["level"])

				if self.other[0] == "J":
					canvas.setFont(self.fontjap, self.fontsize)
				canvas.drawString(232, 205.66 - 17.520 * y, card[name])
				if self.other[0] == "J":
					canvas.setFont(self.fontname, self.fontsize)

				if len(self.deck_list[inx]) >= 12:
					canvas.setFont(self.fontname, self.fontsize * 13 / len(self.deck_list[inx]))

				canvas.drawString(91, 205.66 - 17.520 * y, self.deck_list[inx])
				canvas.setFont(self.fontname, self.fontsize)
				y += 1

			elif card["type"] == "Climax":
				canvas.drawString(58, 122.23 - 17.520 * z, self.qty[self.deck_list[inx]])

				if self.other[0] == "J":
					canvas.setFont(self.fontjap, self.fontsize)
				canvas.drawString(232, 122.23 - 17.520 * z, card[name])
				if self.other[0] == "J":
					canvas.setFont(self.fontname, self.fontsize)

				if len(self.deck_list[inx]) >= 12:
					canvas.setFont(self.fontname, self.fontsize * 14 / len(self.deck_list[inx]))

				canvas.drawString(91, 122.23 - 17.520 * z, self.deck_list[inx])
				canvas.setFont(self.fontname, self.fontsize)
				z += 1

		canvas.save()

		packet.seek(0)
		pdf_deck = PdfFileReader(packet)

		pdf_file = open(self.reg_name, "rb")

		pdf_read = PdfFileReader(pdf_file)
		pdf_write = PdfFileWriter()

		try:
			page = pdf_read.getPage(0)
			page1 = pdf_read.getPage(1)
			page.mergePage(pdf_deck.getPage(0))
			pdf_write.addPage(page)
			pdf_write.addPage(page1)
		except IndexError:
			page = pdf_read.getPage(0)
			page.mergePage(pdf_deck.getPage(0))
			pdf_write.addPage(page)

		if self.deck_name != "":
			for y in range(len(self.characters)):
				if self.characters[y] in self.deck_name:
					self.deck_name = self.deck_name.replace(self.characters[y], "")
			print("Removed special characters in file name")
			if eng:
				pdf_out = open(self.deck_name + "_eng.pdf", "wb")
			else:
				pdf_out = open(self.deck_name + ".pdf", "wb")
			self.pdf_name = self.deck_name + ".pdf"
		else:
			if "data.db" not in os.listdir("./"):
				word = initial
			else:
				word = self.title

			try:
				self.pdf_name = word + "_deck" + str(self.d) + ".pdf"
				if eng:
					pdf_out = open(self.pdf_name[:-4] + "_eng.pdf", "wb")
				else:
					pdf_out = open(self.pdf_name, "wb")

			except IOError:
				self.d += 1
				self.pdf_name = word + "_deck" + str(self.d) + ".pdf"
				if eng:
					pdf_out = open(self.pdf_name[:-4] + "_eng.pdf", "wb")
				else:
					pdf_out = open(self.pdf_name, "wb")

		pdf_write.write(pdf_out)
		pdf_out.close()
		pdf_file.close()
		self.pdf_done = True

	def translation(self):
		url = "http://www.heartofthecards.com/images/cards/ws/"
		imgtype = ".gif"
		pdir = f"{pic_dir}/"

		if not os.path.exists(pdir):
			try:
				os.makedirs(pdir)
			except Exception as e:
				pdir = f"{main_dir}/"

		for card in self.deck_list:
			var = card
			for end in self.end_rariry:
				if card.endswith(end):
					var = card.replace(end, "")

			for end in self.special:
				if var.endswith(end):
					var = card[:-1]

			for letter in self.variant:
				if letter == "a" and var.split("-")[1][2:].lower() not in self.cdata:
					self.aonly = True
				if not self.aonly and letter in var.split("-")[1][2:].lower():
					var = var.split("-")[0] + "-" + var.split("-")[1][:2].lower() + var.split("-")[1][2:].lower().replace(letter, "")

			if var.endswith("SS"):
				var = var + "P"

			if var not in self.deck_list_edited:
				self.deck_list_edited.append(var)

		for card in self.deck_list_edited:
			card_down = card.lower().replace("/", "_").replace("-", "_")
			print(card_down)
			if os.path.exists(f"{pdir}{card_down}.png") or os.path.exists(f"{pdir}{card_down}.gif"):
				continue
			else:
				try:
					print(url + card.lower().replace("/", "-") + imgtype)
					urllib.request.urlretrieve(url + card.upper().replace("/", "-") + imgtype, pdir + card_down + imgtype)
					temp = pImage.open(pdir + card_down + imgtype)
					temp.close()
					self.cdata[card]["img"] = card_down + imgtype
				except IOError:
					try:
						print(url + card.lower().replace("/", "-") + imgtype)
						urllib.request.urlretrieve(url + card.lower().replace("/", "-") + imgtype, pdir + card_down + imgtype)
						temp = pImage.open(pdir + card.lower().replace("/", "_").replace("-", "_") + imgtype)
						temp.close()
						self.cdata[card]["img"] = card_down + imgtype
					except IOError:
						os.remove(pdir + card.lower().replace("/", "_").replace("-", "_") + imgtype)
						imgtype = ".png"
						try:
							# print(url + card.lower().replace("/", "-") + imgtype)
							urllib.request.urlretrieve(url + card.lower().replace("/", "-") + imgtype, pdir + card_down + imgtype)
							temp = pImage.open(pdir + card_down + imgtype)
							temp.close()
							self.cdata[card]["img"] = card_down + imgtype
						except IOError:
							try:
								# print(url + self.cdata[card]["img"].lower())
								urllib.request.urlretrieve(url + self.cdata[card]["img"].lower().replace("_","-"), pdir + card_down + imgtype)
								temp = pImage.open(pdir + card_down + imgtype)
								temp.close()
								self.cdata[card]["img"] = card_down + imgtype
							except IOError:
								try:
									if "SR" in self.cdata[card]["rarity"] or "RRR" in self.cdata[card]["rarity"]:
										ims = card[:-1]
									else:
										ims = card
									ims = f"{ims.lower().replace('/','-')}{self.cdata[card]['rarity'].lower()}{imgtype}"
									# print(url + ims)
									urllib.request.urlretrieve(url + ims, pdir + card_down + imgtype)
									temp = pImage.open(pdir + card_down + imgtype)
									temp.close()
									self.cdata[card]["img"] = card_down + imgtype
								except IOError:
									os.remove(pdir + card.lower().replace("/", "_").replace("-", "_") + imgtype)
									print(f"Could not download {card} image")
									self.cdata[card]["img"] = "blank.png"

			if "J" in card.split("-")[0] and "P" not in card.split("-")[1] and not any(num in card for num in self.jplayable) and not "J/" in card:
				card0 = card + "J"
			elif card.endswith("SS"):
				card0 = card + "P"
			else:
				card0 = card

			if self.cdata[card0]["type"] == "Climax":
				try:
					img = pImage.open(pdir + card_down + imgtype)
					img.rotate(-90, expand=True).save(pdir + card_down + imgtype)
				except FileNotFoundError:
					pass
		self.translation_pdf(pdir)

	def translation_pdf(self, pdir):
		def bunko(ind):
			return ind.split("-")[1]

		promo_end = True
		margin = 12.5
		font_size = 8
		font_name = "Calibri"
		max_string = 47  # 47
		nspacer = 3
		spacer = "&nbsp;" * nspacer
		keywords = ["ENCORE", "ASSIST", "BOND", "BACKUP", "GREAT PERFORMANCE", "BODYGUARD", "ALARM", "BRAINSTORM", "CONCENTRATE", "CHANGE", "MEMORY", "EXPERIENCE", "SHIFT", "ACCELERATE", "RESONANCE", "RECOLLECTION"]
		ability = {"[C]": "[CONT]", "[A]": "[AUTO]", "[S]": "[ACT]"}

		doc = SimpleDocTemplate(self.pdf_name.replace(".pdf", "") + "_translation.pdf", rightMargin=margin, leftMargin=margin, topMargin=margin, bottomMargin=margin)
		styleSheet = getSampleStyleSheet()

		frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width / 2 + 0, doc.height, id='col1')
		frame2 = Frame(doc.leftMargin + doc.width / 2 - 0, doc.bottomMargin, doc.width / 2 + 0, doc.height, id='col2')

		elements = [NextPageTemplate('TwoCol')]

		self.deck_list_edited = sorted(self.deck_list_edited)
		temp = sorted(self.deck_list_edited)
		if promo_end:
			for card in self.deck_list_edited:
				if "-P" in card or "PR" in card:
					temp1 = temp.remove(card)
					temp.append(card)
			self.deck_list_edited = temp

		if any("w62" in ind.lower() or "w65" in ind.lower() for ind in self.deck_list_edited):
			self.deck_list_edited = sorted(self.deck_list_edited, key=bunko)

		c = 1
		for card in self.deck_list_edited:
			if "J" in card.split("-")[0] and "P" not in card.split("-")[1] and not any(num in card for num in self.jplayable) and not "J/" in card:
				card0 = card + "J"
			else:
				if card == "MK/SJ01-056r":
					card0 = card[:-1] + "Rb"
				elif "cgs/ws01-p11" in card.lower():
					card0 = "CGS/WS01-P11a"
				elif card == "CGS/WS01-p04":
					continue
				elif card.endswith("SS"):
					card0 = card + "P"
				else:
					card0 = card
			print(card0)
			row = 1

			if c % 11 == 0:
				elements.append(NextPageTemplate('TwoCol'))
				c = 1

			try:
				# if "P4/S08-096" in card:
				# 	self.cdata[card]["img"] = "p4_s08_096.gif"
				# if "P3/S01-057" in card:
				# 	self.cdata[card]["img"] = "p3_s01_057.gif"
				pic = Image(pdir + self.cdata[card]["img"])
				print(pdir + self.cdata[card]["img"])
			except FileNotFoundError:
				pic = Image(base64.b64decode(self.blank))
				print("2")
			pic.drawHeight = 120  # 126
			pic.drawWidth = 87  # 90
			trigger = ""

			for tt in sorted(self.cdata[card0]["trigger"], reverse=True):
				if tt == "":
					continue
				trigger = "%s%s %s" % (tt[0].upper(), tt[1:], trigger)
			if len(self.cdata[card0]["trigger"]) == 0:
				trigger = "No "
			elif len(self.cdata[card0]["trigger"]) == 1 and self.cdata[card0]["trigger"][0] == "":
				trigger = "No "

			if not os.path.exists(f"{res_dir}/{self.data_name}"):
				text1 = f"<b>{card}:</b> {self.cdata[card0]['eng']}<br/>"
			else:
				text1 = f"<b>{card}:</b> {self.cdata[card0]['name']}<br/>"

			if self.cdata[card0]["type"] == "Climax":
				text2 = "%s %s %s<br/>" % (self.cdata[card0]["colour"], self.cdata[card0]["rarity"], self.cdata[card0]["type"])
				text3 = ""
			else:
				text2 = "%s/%s %s %s %s%s%s Trigger<br/>" % (self.cdata[card0]["level"], self.cdata[card0]["cost"], self.cdata[card0]["colour"], self.cdata[card0]["rarity"], self.cdata[card0]["type"], spacer, trigger)

				if self.cdata[card0]["type"] == "Character":

					def word(cdata, n1, n2, s=False, n=False):
						s1 = "&nbsp;" * n1
						s2 = "&nbsp;" * n2
						ss1 = " " * n1
						ss2 = " " * n2

						if not os.path.exists(f"{res_dir}/{self.data_name}"):
							if not n:
								if s:
									text0 = "Power: " + str(cdata[card0]["power"]) + s1 + 'Soul: ' + str(cdata[card0]["soul"]) + "<br/>"
									for tr in range(len(cdata[card0]["trait"])):
										if tr == 0:
											text0 += cdata[card0]["trait"][tr].replace("(", "&laquo;").replace(")", "&raquo;")
										else:
											text0 += s1 + cdata[card0]["trait"][tr].replace("(", "&laquo;").replace(")", "&raquo;")
									text0 += "<br/>"
								else:
									text0 = "Power: " + str(cdata[card0]["power"]) + s1 + 'Soul: ' + str(cdata[card0]["soul"]) + s2
									for tr in range(len(cdata[card0]["trait"])):
										if tr == 0:
											text0 += cdata[card0]["trait"][tr].replace("(", "&laquo;").replace(")", "&raquo;")
										else:
											text0 += s1 + cdata[card0]["trait"][tr].replace("(", "&laquo;").replace(")", "&raquo;")
									text0 += "<br/>"
							else:
								if n1 == 0 and n2 == 0:
									text0 = "Power: " + str(cdata[card0]["power"]) + ss1 + 'Soul: ' + str(cdata[card0]["soul"]) + s1
									for tr in range(len(cdata[card0]["trait"])):
										if tr == 0:
											text0 += cdata[card0]["trait"][tr].replace("(", "<").replace(")", ">")
										else:
											text0 += "<br/>" + cdata[card0]["trait"][tr].replace("(", "<").replace(")", ">")
								else:
									text0 = "Power: " + str(cdata[card0]["power"]) + ss1 + 'Soul: ' + str(cdata[card0]["soul"]) + ss2
									for tr in range(len(cdata[card0]["trait"])):
										if tr == 0:
											text0 += cdata[card0]["trait"][tr].replace("(", "<").replace(")", ">")
										else:
											text0 += ss1 + cdata[card0]["trait"][tr].replace("(", "<").replace(")", ">")
						else:
							if not n:
								text0 = "Power: " + str(cdata[card0]["power"]) + s1 + 'Soul: ' + str(
										cdata[card0]["soul"])
								if s:
									text0 = text0 + "<br/>"
								else:
									text0 = text0 + s2
								for trait in cdata[card0]["trait"]:
									text0 = text0 + s1 + trait
								text0 = text0 + "<br/>"
							else:
								text0 = "Power: " + str(cdata[card0]["power"]) + ss1 + 'Soul: ' + str(
										cdata[card0]["soul"])
								if n1 == 0 and n2 == 0:
									text0 = text0 + s1
									for tr in range(len(cdata[card0]["trait"])):
										if tr == 0:
											text0 += cdata[card0]["trait"][tr]
										else:
											text0 += "<br/>" + cdata[card0]["trait"][tr]
								else:
									if len(cdata[card0]["trait"]) > 1:
										text0 = text0 + ss2
										for tr in range(len(cdata[card0]["trait"])):
											if tr == 0:
												text0 += cdata[card0]["trait"][tr]
											else:
												text0 += ss1 + cdata[card0]["trait"][tr]
									else:
										text0 = text0 + ss2
										for tr in range(len(cdata[card0]["trait"])):
											text0 += cdata[card0]["trait"][tr]

						return text0

					row -= 1
					text3 = word(self.cdata, nspacer, nspacer)
					textn = word(self.cdata, nspacer, nspacer, n=True)

					if len(textn) > max_string:
						for x in range(nspacer):
							for y in range(nspacer - 1):
								if len(textn) <= max_string:
									break
								z = y
								if x == nspacer - 1:
									z = 0
								text3 = word(self.cdata, nspacer - z - x, nspacer - x)
								textn = word(self.cdata, nspacer - z - x, nspacer - x, n=True)

					if len(textn) > max_string:
						text3 = word(self.cdata, nspacer, nspacer, s=True)

					if "&nbsp;&nbsp;&nbsp;&laquo;No" in text3:
						text3 = text3.replace("&nbsp;&nbsp;&nbsp;&laquo;No", "")

				else:
					text3 = ""

			text4 = ""
			for text in self.cdata[card0]["text"]:
				def replace_text(sl, nr, n=False):
					text = sl
					row = nr

					for pre in ability:
						if pre in text:
							text = text.replace(pre, ability[pre])

					text = text.replace("\n", "<br/>")

					if not n:
						if "[Counter] BACKUP" in text:
							bold = text.split("[")[2][:-1].replace("Counter] ", "")
							text = text.replace(bold, "<b>" + bold + "</b>")

						for word in keywords:
							if word in text:
								text = text.replace(word, "<b>" + word + "</b>")

						text = text.replace(" ::", " &laquo;").replace(":: ", "&raquo; ").replace("::,", "&raquo; ").replace("::.", "&raquo; ")
						text = text.replace("\n", "<br/>")

						return text

					elif n:
						for s in text.split("<br/>"):
							text = text.replace("::", "_").replace("\'", "_")
							row += int(math.ceil(len(s) / float(max_string)))

						return row

				text = replace_text(text, row)
				row = replace_text(text, row, n=True)

				if text.endswith("<br/>"):
					text4 = text4 + text
				else:
					text4 = text4 + text + "<br/>"

			if row >= 0:
				for x in range(6 - row):
					text4 += "<br/>"

			text4 = f"<font size='{font_size}' face='{font_name}'>{text4}</font>"
			text = f"<font size='{font_size}' face='{font_name}'>{text1}{text2}{text3}</font>"

			data = [[pic, Paragraph(text, styleSheet['Normal'])], ["", Paragraph(text4, styleSheet["Normal"])]]

			table = Table(data,
			              style=[
				              ('LINEABOVE', (0, 0), (-1, 0), 0.1, colors.black),
				              ('LINEBELOW', (0, 1), (-1, 1), 0.1, colors.black),
				              ('LINEABOVE', (1, 1), (1, 1), 0.1, colors.black), ('SPAN', (0, 0), (0, 1)),
				              ('VALIGN', (1, 0), (1, -1), 'TOP'), ('VALIGN', (0, 0), (0, -1), 'CENTER'),
				              ('ALIGN', (0, 0), (-1, -1), 'CENTER')
			              ])

			table._argW[0] = pic.drawWidth + 4

			c += 1
			elements.append(table)

		doc.addPageTemplates(PageTemplate(id='TwoCol', frames=[frame1, frame2]))
		doc.build(elements)


if __name__ in '__main__':
	Sheet()

# Original Author: Enrico Salvatore Brancato
