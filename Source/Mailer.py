from Source.Functions import FormatDays, Calculator, Skinwalker
from Source.Timezoner import CorrectUserTime, Replacing_timezone
from Source.Bot_Addition import DeleteEvent

from dublib.TelebotUtils import UsersManager
from dublib.Methods.Filesystem import ReadJSON
from dublib.Engine.GetText import _

import os
import logging
import dateparser
from datetime import datetime, timedelta, timezone
from telebot import TeleBot

class Mailer:

	def __CheckFormatRemained(self, event: dict) -> bool:
		"""Проверка отслеживается ли событие в будущем."""

		if "Format" in event.keys() and event["Format"] == "Passed": return False
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

	def Start(self, objectsdirs: list[str]):
		"""
		Добавление событий в рассылку:
			MessagesDaily
			MessagesToday
			MessagesOnceDefault
			MessagesOnce

		"""

		UsersID = self.__GetUsersID()

		for ID in UsersID:

			MessagesDaily: dict = {}
			MessagesTodaywithTime: dict = {}
			MessagesTodayDefault: dict = {}
			MessagesOnce: dict = {}
			
			DailyEvents = []
			TodayEventsTime = []
			TodayEventsDefault = []
			OnceEvents = []

			Data = ReadJSON(f"Data/Users/{ID}.json")
			logging.info(f"Начата рассылка: {ID} ")

			if "events" in Data["data"].keys():
				for EventID in Data["data"]["events"].keys():
					Event: dict = Data["data"]["events"][EventID]
					User = self.__Manager.get_user(ID)

					if self.__CheckFormatRemained(Event):
						
						if "MessagesDaily" in objectsdirs:
							if Event["ReminderFormat"] == "EveryDay" and not self.__CheckTodayDate(Event):
								DailyEvents.append(Event)
								MessagesDaily[ID] = {"Events": DailyEvents}

						if "MessagesTodaywithTime" in objectsdirs and Event["Time"] != None: 
							Delta = Replacing_timezone(self.__Manager.get_user(ID))
							if self.__CheckTodayDate(Event) and CorrectUserTime(Event["Time"], Delta) == datetime.now(timezone.utc).replace(microsecond=0):
								TodayEventsTime.append(Event)
								MessagesTodaywithTime[ID] = {"Events": TodayEventsTime}
								DeleteEvent(User, EventID)

						if "MessagesTodayDefault" in objectsdirs: 
							if self.__CheckTodayDate(Event) and Event["Time"] == None:
								TodayEventsDefault.append(Event)
								MessagesTodayDefault[ID] = {"Events": TodayEventsDefault}

						if "MessagesOnce" in objectsdirs and Event["Time"] != None:
							Delta = Replacing_timezone(self.__Manager.get_user(ID))
							if Event["ReminderFormat"] == "OnceDay" and self.__CheckReminderPeriod(Event) and not self.__CheckTodayDate(Event) and CorrectUserTime(Event["Time"], Delta) == datetime.now(timezone.utc).replace(microsecond=0):
								OnceEvents.append(Event)
								MessagesOnce[ID] = {"Events": OnceEvents}
								DeleteEvent(User, EventID)

				self.send(MessagesDaily, MessagesTodaywithTime, MessagesTodayDefault, MessagesOnce)

	def send(self, MessagesDaily: dict = None, MessagesTodaywithTime: dict = None, MessagesTodayDefault: dict = None, MessagesOnce: dict = None ):
		if MessagesDaily:
			for ID in MessagesDaily.keys():
				Reminders = list()
				User = self.__Manager.get_user(ID)

				for i in range(len(MessagesDaily[ID]["Events"])):
					Name = MessagesDaily[ID]["Events"][i]["Name"]
					Remain = Calculator(MessagesDaily[ID]["Events"][i]["Date"])
					if Remain < 0:
						skinwalker = Skinwalker(MessagesDaily[ID]["Events"][i]["Date"])
						Remain = Calculator(skinwalker)
					Days = FormatDays(Remain, self.__language)
					Reminders.append(_("<b>%s</b> наступит через %s %s!") % (Name, Remain, Days))
				
				base = ""
				for i in range(len(Reminders)):

					if len(base + Reminders[i]) < 2000: base += Reminders[i] + "\n\n" 
					
					if len(base + Reminders[i]) >= 2000 or i == len(Reminders) - 1:

						try:
							self.__Bot.send_message(ID, base, parse_mode = "HTML")
							logging.info(f"Отправлены ежедневные напоминания {ID}: {Name}")
							User.set_chat_forbidden(False)
						except Exception as E: 
							logging.info(f"{E}, {ID}")
							User.set_chat_forbidden(True)

		if MessagesTodaywithTime:
			for ID in MessagesTodaywithTime.keys():
				User = self.__Manager.get_user(ID)

				for i in range(len(MessagesTodaywithTime[ID]["Events"])):

					Name = MessagesTodaywithTime[ID]["Events"][i]["Name"]
					try:
						self.__Bot.send_message(
								ID, 
								_("🔔 <b>НАПОМИНАНИЕ!</b> 🔔\n\nСегодня ваше событие <b>%s</b>!\n\nНе забудьте!)") % Name,
								parse_mode = "HTML"
							)
						
						logging.info(f"Отправленно сегодняшнее напоминание (время, выбранное пользователем) {ID}: {Name}")
						User.set_chat_forbidden(False)

					except Exception as E: 
						logging.info(f"{E}, {ID}")
						User.set_chat_forbidden(True)

		if MessagesTodayDefault:
			for ID in MessagesTodayDefault.keys():
				User = self.__Manager.get_user(ID)

				for i in range(len(MessagesTodayDefault[ID]["Events"])):

					Name = MessagesTodayDefault[ID]["Events"][i]["Name"]
					try:
						self.__Bot.send_message(
								ID, 
								_("🔔 <b>НАПОМИНАНИЕ!</b> 🔔\n\nСегодня ваше событие <b>%s</b>!\n\nНе забудьте!)") % Name,
								parse_mode = "HTML"
							)
						
						logging.info(f"Отправленно сегодняшнее напоминание (время по умолчанию) {ID}: {Name}")
						User.set_chat_forbidden(False)

					except Exception as E: 
						logging.info(f"{E}, {ID}")
						User.set_chat_forbidden(True)

		if MessagesOnce:
			for ID in MessagesOnce.keys():
				User = self.__Manager.get_user(ID)
				for i in range(len(MessagesOnce[ID]["Events"])):
					Name = MessagesOnce[ID]["Events"][i]["Name"]
					Reminder = MessagesOnce[ID]["Events"][i]["Reminder"]
					days = FormatDays(int(MessagesOnce[ID]["Events"][i]["Reminder"]), self.__language)
					try:
						self.__Bot.send_message(
						ID, 
						_("🔔 <b>НАПОМИНАНИЕ!</b> 🔔\n\nДо события <b>%s</b> осталось %s %s!\n\nХорошего вам дня!") % (Name, Reminder, days),
						parse_mode = "HTML"
						)

						logging.info(f"Отправленно разовое напоминание {ID}: {Name}")
						User.set_chat_forbidden(False)

					except Exception as E: 
						logging.info(f"{E}, {ID}")
						User.set_chat_forbidden(True)