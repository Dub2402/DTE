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

	def SayHello(self, ID: int, Call: str):
		Call = Markdown(Call).escaped_text
		self.__Bot.send_message(
				ID, 
				f"Приветствую, {Call}!"
				)

	def send(self, ID: int, event: dict, Every: bool, Today: bool):
		Name = Markdown(str(event["Name"])).escaped_text
		if Today:
			self.__Bot.send_message(
				ID, 
				f"🔔 *НАПОМИНАНИЕ\\!* 🔔\n\nСегодня ваше событие *{Name}*\\!\n\nХорошего вам дня\\!",
				parse_mode = "MarkdownV2"
			)

		else:
			Reminder = Markdown(str(event["Reminder"])).escaped_text
			days = FormatDays(int(event["Reminder"]))
			self.__Bot.send_message(
				ID, 
				f"🔔 *НАПОМИНАНИЕ\\!* 🔔\n\nДо события *{Name}* осталось {Reminder} {days}\\!\n\nХорошего вам дня\\!",
				parse_mode = "MarkdownV2"
			)

	def send_long_messages(self, Messages):

		for ID in Messages.keys():
			Reminders = list()
			Call = Markdown(str(Messages[ID]["Call"])).escaped_text
			for i in range(len(Messages[ID]["Events"])):
				
				Name = Markdown(str(Messages[ID]["Events"][i]["Name"])).escaped_text
				
				Remain = Calculator(Messages[ID]["Events"][i]["Date"])	
				if Remain < 0 and "Format" in Messages[ID]["Events"][i].keys():
					if Messages[ID]["Events"][i]["Format"] == "Remained":
						skinwalker = Skinwalker(Messages[ID]["Events"][i]["Date"])
						Remain = Calculator(skinwalker)
						Days = FormatDays(Remain)


				Days = FormatDays(Remain)
				Reminders.append(f"*{Name}* наступит через {Remain} {Days}\\!")

			base = f"Приветствую, {Call}\\!\n\n"
			end = f"_Хорошего тебе дня\\!\\)_"
			for i in range(len(Reminders)):

				if len(base + Reminders[i] + end) < 2000: base += Reminders[i] + "\n\n" 
				
				if len(base + Reminders[i] + end) >= 2000 or i == len(Reminders) - 1:
					self.__Bot.send_message(ID, base + end, parse_mode="MarkdownV2")
					base = ""

	def StartRemindering(self):
		Messages: dict = {}
		CountID = 0
		try:
			UsersID = self.__GetUsersID()

			for ID in UsersID:
				Data = ReadJSON(f"Data/Users/{ID}.json")
				IsHello = False
				Events = []

				if "events" in Data["data"].keys():
					
					for EventID in Data["data"]["events"].keys():
						
						Event: dict = Data["data"]["events"][EventID]
						Call = Data["data"]["call"]

						if self.__CheckTodayRemind(Event) and self.__CheckTodayDate(Event):
							
							try:
								if not IsHello:
									self.SayHello(ID, Call)
									IsHello = True
							
									self.send(ID, Event, Every=False, Today=True)
								
							except Exception as ExceptionData: pass

						if "ReminderFormat" in Event.keys() and self.__CheckFormatRemained(Event):
							if not self.__CheckTodayDate(Event) and Event["ReminderFormat"] == "EveryDay":
								CountID +=1
								Events.append(Event)
								if not IsHello:
									Messages[ID] = {"Call": Call}
									IsHello = True	
								Messages[ID].update({"Events": Events})
								# 	self.send(ID, Event, Every=True, Today= False)
								
								# except Exception as ExceptionData: pass
						
						if self.__CheckRemind(Event) and self.__CheckRemindDate(Event):
							try:
								if not IsHello:
									self.SayHello(ID, Call)
									IsHello = True

								self.send(ID, Event, Today=False, Every=False)

							except Exception as ExceptionData: pass

		except Exception as ExceptionData: logging.error(str(ExceptionData))
		try:
			self.send_long_messages(Messages)

		except Exception as ExceptionData: logging.error(str(ExceptionData))