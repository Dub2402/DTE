from dublib.Methods.Filesystem import ReadJSON
from dublib.TelebotUtils import UserData

from datetime import date
import dateparser
import gettext
import telebot
from telebot import types

Settings = ReadJSON("Settings.json")
Language = Settings["language"]

_ = gettext.gettext
try: _ = gettext.translation("DTE", "locales", languages = [Language]).gettext
except FileNotFoundError: pass

def CheckValidDate(Date: str)-> bool:
	try:
		dateparser.parse(Date, settings={'DATE_ORDER': 'DMY','STRICT_PARSING': True}).date()
		return True
	except:
		return False
	
def GetFreeID(Events: dict) -> int:
	Increment = list()
	for key in Events.keys(): Increment.append(int(key))
	Increment.sort()
	FreeID = 1
	if Increment: FreeID = max(Increment) + 1

	return FreeID

def Calculator(event: str) -> int:
	today = date.today()
	remains = (dateparser.parse(event, settings={'DATE_ORDER': 'DMY'}).date() - today).days
	
	return remains

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


def DeleteMessageNotificationsDeactivate(User: UserData, Call: types.CallbackQuery, Bot: telebot.TeleBot):
	if User.has_property("MessageNotificationsDeactivate"):
		try:
			MessageNotifications = User.get_property("MessageNotificationsDeactivate")
			for MessageNotification in MessageNotifications:
				Bot.delete_message(Call.message.chat.id, MessageNotification)
		except: print("Ошибка удаления сообщения.")
		if User.has_property("ID_DelMessage"):
			try:
				ID_DelMessage = User.get_property("ID_DelMessage")
				Bot.delete_message(Call.message.chat.id, ID_DelMessage)
			except: print("Ошибка удаления сообщения ID_DelMessage.")

def DeleteMessageNotificationsChange(User: UserData, Call: types.CallbackQuery, Bot: telebot.TeleBot):
	if User.has_property("MessageNotificationsChange"):
		print(Call.message.chat.id)
		try:
			MessageNotifications = User.get_property("MessageNotificationsChange")
			for MessageNotification in MessageNotifications:
				Bot.delete_message(Call.message.chat.id, MessageNotification)
		except: print("Ошибка удаления сообщения.")