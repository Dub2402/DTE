from datetime import date
import dateparser
import gettext

_ = gettext.gettext
try: _ = gettext.translation("DTE", "locales", languages = ["en"]).gettext
except FileNotFoundError: pass

def CheckValidDate(Date: str)-> bool:
	try:
		dateparser.parse(Date, settings={'DATE_ORDER': 'DMY'}).date()
		return True
	except:
		return False
	
def Skinwalker(event: str) -> str:

	yearnew = int(date.today().year) + 1 
	day = dateparser.parse(event, settings={'DATE_ORDER': 'DMY'}).day
	month = dateparser.parse(event, settings={'DATE_ORDER': 'DMY'}).month
	newevent = str(day) + "." + str(month) + "." + str(yearnew)
	remains = Calculator(newevent)
	if remains > 364:
		yearnew = int(date.today().year)
		newevent = str(day) + "." + str(month) + "." + str(yearnew)

	return newevent

def Calculator(event: str) -> int:
	today = date.today()
	remains = (dateparser.parse(event, settings={'DATE_ORDER': 'DMY'}).date() - today).days
	
	return remains

def GetFreeID(Events: dict) -> int:
	Increment = list()
	for key in Events.keys(): Increment.append(int(key))
	Increment.sort()
	FreeID = 1
	if Increment: FreeID = max(Increment) + 1

	return FreeID

def FormatDays(remains: int, language : str) -> str:
	if language == "en":
		days = "days"
	
		if remains in [1]: days = "day"	

	else:
		days = "дней"
		
		if remains in [11, 12, 13]: pass
		elif str(remains).endswith("1") and remains not in [11, 12, 13]: days = "день"
		elif str(remains).endswith("2") or str(remains).endswith("3") or str(remains).endswith("4") and remains not in [11, 12, 13]: days = "дня"
			
	return days
