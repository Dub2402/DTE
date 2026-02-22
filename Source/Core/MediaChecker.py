from .Enums import MediaPath

from dublib.CLI.TextStyler import FastStyler

from pathlib import Path
import os

def check_media():
	is_validated = True

	for element in MediaPath:

		if os.path.exists(element.value):
			print(FastStyler(f"File \"{element.value}\" exists.").colorize.green)

		else:
			LANG = os.environ["DTE_LANG"]
			element_name = Path(element.value).stem

			if element_name.endswith(f"_{LANG}"):
				print(FastStyler(f"File \"{element.value}\" not found.").colorize.red)
				is_validated = False

			else:
				print(FastStyler(f"File \"{element.value}\" not found [optional].").colorize.yellow)

	if not is_validated: exit(-1)