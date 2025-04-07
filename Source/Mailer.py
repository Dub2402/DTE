from Source.Functions import FormatDays, Calculator, Skinwalker, _

from dublib.TelebotUtils import UsersManager
from dublib.Methods.Filesystem import ReadJSON
from dublib.Polyglot import Markdown

import os
import logging
import dateparser
from datetime import datetime, timedelta
from telebot import TeleBot

class Mailer:

	def __CheckFormatRemained(self, event: dict) -> bool:
		if "Format" in event.keys() and event["Format"] == "Passed":return False
		return True
	
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
	
	def __CheckReminderPeriod(self, event: dict) -> bool:
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

	def __GetUsersID(self) -> list[int]:
		Files = os.listdir("Data/Users")
		Files = list(filter(lambda List: List.endswith(".json"), Files))
		UsersID = list()

		for File in Files:
			ID = int(File.replace(".json", ""))
			UsersID.append(ID)

		return UsersID

	def __init__(self, bot: TeleBot, Manager: UsersManager, language: str):
		self.__Bot = bot
		self.__Manager = Manager
		self.__language = language

	def Start(self):
		UsersID = self.__GetUsersID()

		for ID in UsersID:
			MessagesDaily: dict = {}
			MessagesOnce: dict = {}
			MessagesToday: dict = {}
			DailyEvents = []
			OnceEvents = []
			TodayEvents = []
			Data = ReadJSON(f"Data/Users/{ID}.json")
			logging.info(f"Начата рассылка: {ID} ")

			if "events" in Data["data"].keys():
				for EventID in Data["data"]["events"].keys():
					Event: dict = Data["data"]["events"][EventID]

					if self.__CheckFormatRemained(Event):
				
						if Event["ReminderFormat"] == "EveryDay" and not self.__CheckTodayDate(Event):
							DailyEvents.append(Event)
							MessagesDaily[ID] = {"Events": DailyEvents}
							
						if self.__CheckTodayDate(Event):
							TodayEvents.append(Event)
							MessagesToday[ID] = {"Events": TodayEvents}

						if Event["ReminderFormat"] == "OnceDay" and self.__CheckReminderPeriod(Event) and not self.__CheckTodayDate(Event):
							OnceEvents.append(Event)
							MessagesOnce[ID] = {"Events": OnceEvents}

		
			print(MessagesDaily)
			print(MessagesOnce)
			print(MessagesToday)
			self.send(MessagesDaily, MessagesOnce, MessagesToday)

	
	def send(self, MessagesDaily: dict, MessagesOnce: dict, MessagesToday: dict):

		for ID in MessagesDaily.keys():
			Reminders = list()
			User = self.__Manager.get_user(ID)

			for i in range(len(MessagesDaily[ID]["Events"])):
				Name = Markdown(str(MessagesDaily[ID]["Events"][i]["Name"])).escaped_text
				Remain = Calculator(MessagesDaily[ID]["Events"][i]["Date"])
				if Remain < 0:
					skinwalker = Skinwalker(MessagesDaily[ID]["Events"][i]["Date"])
					Remain = Calculator(skinwalker)
				Days = FormatDays(Remain, self.__language)
				Reminders.append(_("*%s* наступит через %s %s\\!") % (Name, Remain, Days))
			
			base = ""
			for i in range(len(Reminders)):

				if len(base + Reminders[i]) < 2000: base += Reminders[i] + "\n\n" 
				
				if len(base + Reminders[i]) >= 2000 or i == len(Reminders) - 1:

					try:
						self.__Bot.send_message(ID, base, parse_mode="MarkdownV2")
						logging.info(f"Отправлены ежедневные напоминания {ID}: {Name}")
						User.set_chat_forbidden(False)
					except Exception as E: 
						logging.info(f"{E}, {ID}")
						User.set_chat_forbidden(True)

		for ID in MessagesOnce.keys():
			User = self.__Manager.get_user(ID)

			for i in range(len(MessagesOnce[ID]["Events"])):
				Name = Markdown(str(MessagesOnce[ID]["Events"][i]["Name"])).escaped_text
				Reminder = Markdown(str(MessagesOnce[ID]["Events"][i]["Reminder"])).escaped_text
				days = FormatDays(int(MessagesOnce[ID]["Events"][i]["Reminder"]), self.__language)
				try:
					self.__Bot.send_message(
					ID, 
					_("🔔 *НАПОМИНАНИЕ\\!* 🔔\n\nДо события *%s* осталось %s %s\\!\n\nХорошего вам дня\\!") % (Name, Reminder, days),
					parse_mode = "MarkdownV2"
					)
					logging.info(f"Отправленно разовое напоминание {ID}: {Name}")
					User.set_chat_forbidden(False)

				except Exception as E: 
					logging.info(f"{E}, {ID}")
					User.set_chat_forbidden(True)
			
		for ID in MessagesToday.keys():
			User = self.__Manager.get_user(ID)

			for i in range(len(MessagesToday[ID]["Events"])):

				Name = Markdown(str(MessagesToday[ID]["Events"][i]["Name"])).escaped_text
				try:
					self.__Bot.send_message(
							ID, 
							_("🔔 *НАПОМИНАНИЕ\\!* 🔔\n\nСегодня ваше событие *%s*\\!\n\nНе забудьте\\!\\)") % Name,
							parse_mode = "MarkdownV2"
						)
					logging.info(f"Отправленно сегодняшнее напоминание {ID}: {Name}")
					User.set_chat_forbidden(False)

				except Exception as E: 
					logging.info(f"{E}, {ID}")
					User.set_chat_forbidden(True)