from dublib.Methods.Filesystem import ReadJSON
from dublib.Engine.GetText import _

from datetime import date, datetime
import dateparser
import gettext

Settings = ReadJSON("Settings.json")
Language = Settings["language"]

def CheckValidDate(Date: str)-> bool:
	"""Проверка правильности введённой даты."""

	try:
		dateparser.parse(Date, settings ={'DATE_ORDER': 'DMY','STRICT_PARSING': True}).date()
		return True
	except:
		return False
	
def GetValidTime(Time: str)-> datetime.time:
	"""Получение форматированного времени введённого пользователем."""

	return str(dateparser.parse(Time).time().strftime(format = "%H:%M"))

def GetFreeID(Events: dict) -> int:
	""" Получение свободного ID события."""
	
	Increment = list()
	for key in Events.keys(): Increment.append(int(key))
	Increment.sort()
	FreeID = 1
	if Increment: FreeID = max(Increment) + 1

	return FreeID

def Calculator(Date: str) -> int:
	"""Количество дней между датами. Значения могут быть как отрицательные, так и положительные."""

	today = date.today()
	remains = (dateparser.parse(Date, settings={'DATE_ORDER': 'DMY'}).date() - today).days
	
	return remains

def FormatDays(remains: int, language : str) -> str:
	"""
	Отформатировать в зависимости от количества дней слово "день".
	"""

	if language == "en":
		days = "days"
		if remains in [1]: days = "day"	

	else:
		days = "дней"
		if remains in [11, 12, 13, 113, 213, 313]: pass
		elif str(remains).endswith("1") and remains not in [11, 12, 13]: days = "день"
		elif str(remains).endswith("2") or str(remains).endswith("3") or str(remains).endswith("4") and remains not in [11, 12, 13, 113, 213, 313]: days = "дня"
			
	return days

def Skinwalker(Date: str) -> str:
	"""Получение новой даты, в текущем или следующем году."""

	yearnew = int(date.today().year) + 1 
	day = dateparser.parse(Date, settings={'DATE_ORDER': 'DMY'}).day
	month = dateparser.parse(Date, settings={'DATE_ORDER': 'DMY'}).month
	newevent = str(day) + "." + str(month) + "." + str(yearnew)
	remains = Calculator(newevent)
	if remains > 364:
		yearnew = int(date.today().year)
		newevent = str(day) + "." + str(month) + "." + str(yearnew)

	return newevent

def LimitationOnceReminders(date: str) -> int:
	skinwalker = Skinwalker(date) 
	remains = Calculator(skinwalker)

	return remains