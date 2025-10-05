from Source.Events import Additional

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

def LimitationOnceReminders(date: str) -> int:
	skinwalker = Additional.Skinwalker(date) 
	remains = Additional.Calculator(skinwalker)

	return remains