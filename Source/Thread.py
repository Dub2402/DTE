import os
from .Instruments import FormatDays, Skinwalker
from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import Clear
from dublib.Polyglot import Markdown
from telebot import TeleBot
import dateparser
from datetime import datetime, timedelta

Clear()

class Reminder:

	def __GetUsersID(self) -> list[int]:
		# Получение списка файлов в директории.
		Files = os.listdir("Data/Users")
		# Фильтрация только файлов формата JSON.
		Files = list(filter(lambda List: List.endswith(".json"), Files))
		# Список ID пользователей.
		UsersID = list()

		# Для каждого файла.
		for File in Files:
			# Получение ID пользователя.
			ID = int(File.replace(".json", ""))
			# Добавление ID в список.
			UsersID.append(ID)

		return UsersID

	def __CheckRemind(self, event: dict) -> bool:
		if "Format" in event.keys() and event["Format"] == "Passed": return False
		if not "Reminder" in event.keys(): return False
		return True
	
	def __CheckTodayRemind(self, event: dict) -> bool:
		if "Format" in event.keys() and event["Format"] == "Passed": return False
		return True

	def __CheckRemindDate(self, event: dict) -> bool:
		EventDate = dateparser.parse(event["Date"], settings={'DATE_ORDER': 'DMY'})
		CurrentDate = datetime.now().date()
		Day = EventDate.day
		Month = EventDate.month
		Year = CurrentDate.year
		CurrentYearEventDate = datetime(Year, Month, Day)
		if CurrentYearEventDate.date() < datetime.now().date(): CurrentYearEventDate = datetime(Year + 1, Month, Day)
		Period = timedelta(days = int(event["Reminder"]))
		RemindDate = CurrentYearEventDate - Period
		if CurrentDate == RemindDate.date(): return True

		return False
	
	def __CheckTodayDate(self, event: dict) -> bool:
		EventDate = dateparser.parse(event["Date"], settings={'DATE_ORDER': 'DMY'})
		CurrentDate = datetime.now().date()
		Day = EventDate.day
		Month = EventDate.month
		Year = CurrentDate.year
		CurrentYearEventDate = datetime(Year, Month, Day)
		if CurrentYearEventDate.date() < datetime.now().date(): CurrentYearEventDate = datetime(Year + 1, Month, Day)
		if CurrentDate == CurrentYearEventDate.date(): return True

		return False

	def __init__(self, bot: TeleBot):

		self.__Bot = bot

	def send(self, ID: int, name: str, event: dict, Today: bool):
		Call = Markdown(name).escaped_text
		Name = Markdown(str(event["Name"])).escaped_text
		
		if Today:
			self.__Bot.send_message(
				ID, 
				f"🔔 *НАПОМИНАНИЕ\\!* 🔔\n\n{Call}, приветствую\\!\nСегодня ваше событие *{Name}*\\!\n\nХорошего вам дня\\!",
				parse_mode = "MarkdownV2"
			)
		else:
			Reminder = Markdown(str(event["Reminder"])).escaped_text
			days = FormatDays(int(event["Reminder"]))
			self.__Bot.send_message(
				ID, 
				f"🔔 *НАПОМИНАНИЕ\\!* 🔔\n\n{Call}, приветствую\\!\nДо события *{Name}* осталось {Reminder} {days}\\!\n\nХорошего вам дня\\!",
				parse_mode = "MarkdownV2"
			)

	def start(self):
		UsersID = self.__GetUsersID()
		
		for ID in UsersID:
			Data = ReadJSON(f"Data/Users/{ID}.json")

			if "events" in Data["data"].keys():
				for EventID in Data["data"]["events"].keys():
					Event = Data["data"]["events"][EventID]
					Name = Data["data"]["call"]
					
					if self.__CheckRemind(Event) and self.__CheckRemindDate(Event): self.send(ID, Name, Event, False)

	def startdefault(self):
		UsersID = self.__GetUsersID()
		
		for ID in UsersID:
			Data = ReadJSON(f"Data/Users/{ID}.json")

			if "events" in Data["data"].keys():
				for EventID in Data["data"]["events"].keys():
					Event: dict = Data["data"]["events"][EventID]
					Name = Data["data"]["call"]
					
					if self.__CheckTodayRemind(Event) and self.__CheckTodayDate(Event): self.send(ID, Name, Event, True)
		