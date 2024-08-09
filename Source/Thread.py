from .Instruments import FormatDays, Calculator, Skinwalker

import os
import dateparser
from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import Clear
from dublib.Polyglot import Markdown
from telebot import TeleBot
from datetime import datetime, timedelta

import logging
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

	def __CheckFormatRemained(self, event: dict) -> bool:
		if "Format" in event.keys() and event["Format"] == "Passed": return False
		return True
	
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

	def send(self, ID: int, Call: str, event: dict, Every: bool, Today: bool):
		Call = Markdown(Call).escaped_text
		Name = Markdown(str(event["Name"])).escaped_text
		
		if Every:
			remain = Calculator(event["Date"])
			if remain > 0:
				remain = Markdown(str(remain)).escaped_text
				days = FormatDays(remain)
				self.__Bot.send_message(
				ID, 
				f"До события *{Name}* осталось {remain} {days}\\!",
				parse_mode = "MarkdownV2"
				)
				return
			if remain < 0 and "Format" in event.keys():
				if event["Format"] == "Remained":
					skinwalker = Skinwalker(event["Date"])
					remain = Calculator(skinwalker)
					days = FormatDays(remain)
					self.__Bot.send_message(
						ID, 
						f"До события *{Name}* осталось {remain} {days}\\!",
						parse_mode = "MarkdownV2"
						)

		elif Today:
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

	def StartOnce(self):
		logging.info("Разовые напоминания.")
		try:
			UsersID = self.__GetUsersID()
			
			for ID in UsersID:
				Data = ReadJSON(f"Data/Users/{ID}.json")

				if "events" in Data["data"].keys():
					for EventID in Data["data"]["events"].keys():
						Event = Data["data"]["events"][EventID]
						Name = Data["data"]["call"]
						
						if self.__CheckRemind(Event) and self.__CheckRemindDate(Event):
							self.send(ID, Name, Event, Today=False, Every=False)
		except Exception as ExceptionData: logging.error(str(ExceptionData))

	def StartEvery(self):
		logging.info("Ежедневные напоминания.")
		
		try:
			UsersID = self.__GetUsersID()
			for ID in UsersID:
				Data = ReadJSON(f"Data/Users/{ID}.json")

				if "events" in Data["data"].keys():
					for EventID in Data["data"]["events"].keys():
						Event: dict = Data["data"]["events"][EventID]
						Call = Data["data"]["call"]
						if "ReminderFormat" in Event.keys() and self.__CheckFormatRemained(Event):
							if not self.__CheckTodayDate(Event) and Event["ReminderFormat"] == "EveryDay":
								self.send(ID, Call, Event, Every=True, Today= False)

		except Exception as ExceptionData: logging.error(str(ExceptionData))
		
	def StartDefault(self):
		logging.info("Напоминания по умолчанию.")
		try:
			UsersID = self.__GetUsersID()
			for ID in UsersID:
				Data = ReadJSON(f"Data/Users/{ID}.json")

				if "events" in Data["data"].keys():
					for EventID in Data["data"]["events"].keys():
						Event: dict = Data["data"]["events"][EventID]
						Call = Data["data"]["call"]
						
						if self.__CheckTodayRemind(Event) and self.__CheckTodayDate(Event):
							self.send(ID, Call, Event, Every=False, Today=True)
							
		except Exception as ExceptionData: logging.error(str(ExceptionData))