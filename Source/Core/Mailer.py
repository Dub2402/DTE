from Source.Modules.Eventer import EventTypes, Eventer, Event
from Source.Core.Enums import RemindersTypes

from dublib.TelebotUtils import UsersManager
from dublib.Engine.GetText import _

from datetime import datetime, timedelta, time
from typing import Any
import logging
import random

from apscheduler.events import EVENT_JOB_MISSED, JobExecutionEvent
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot

class Mailer:

	def randomize_time_notification(self):
		"""Выбирает рандомное время c заданными параметрами."""

		return time(random.randint(*self.__reminder_range["hours"]), random.randint(*self.__reminder_range["minutes"]))

	def _listener_missed_jobs(self, event: JobExecutionEvent):
		job = self.__scheduler.get_job(event.job_id)

	def __init__(self, bot: TeleBot, manager: UsersManager, scheduler: BackgroundScheduler, settings: dict[str, Any]):

		self.__bot = bot
		self.__manager = manager
		self.__scheduler = scheduler
		self.__reminder_range = settings["reminder_range"]
		self.__default_reminder_today = settings["default_reminder_today"]
		self.__language = settings["language"]

		self.__scheduler.add_listener(self._listener_missed_jobs, EVENT_JOB_MISSED)

	def handler_notifications(self):
		"""Обработчик напоминаний."""
		now = datetime.now()

		for user in self.__manager.users:
			logging.info(f"Начало постановки задач для отправления напоминаний для пользователя {user.id}")
			eventer = Eventer(user)
			everyday_groups = {}

			for event in eventer.events:
				logging.info(f"Пользователь {user.id}.\n Событие {event.name}, дата - {event.date}.\n {event.counter_type, event.notifications, event.reminder}")
				if event.is_temp: continue

				if event.is_day_today:
					reminder_time = event.reminder.time.to_time() if event.reminder else time(*self.__default_reminder_today) 
					run_date = datetime.combine(now.date(), reminder_time)
					reminder_type = RemindersTypes.today
					self.__scheduler.add_job(self.send, "date", run_date = run_date, name = str(event.id), args = (user, event, reminder_type))
					logging.info(f"Обработка напоминаний для пользователя {user.id}")
				else:
                                        
					if event.notifications:
						
						if event.reminder: run_date = datetime.combine(now.date(), event.reminder.time.to_time()) 
						else: run_date = datetime.combine(now.date(), self.randomize_time_notification()) 

						if run_date not in everyday_groups: everyday_groups[run_date] = []

						everyday_groups[run_date].append(event)
						reminder_type = RemindersTypes.everyday
					
					else:
					
						if event.reminder:

							date_event_in_future = event.date.replace(year = now.year + 1) if event.is_date_passed_this_year else event.date
							reminder_type = RemindersTypes.once
							reminder_date = date_event_in_future - timedelta(days = event.reminder.days_before_event)
							run_date = datetime.combine(reminder_date, event.reminder.time.to_time())
							self.__scheduler.add_job(self.send, "date", run_date = run_date, name = str(event.id), args = (user, event, reminder_type))

			for scheduled_time, events_list in everyday_groups.items():

				job_name = f"{user.id}_everyday_{scheduled_time.strftime('%H%M%S')}"
				self.__scheduler.add_job(self.send, "date", run_date=scheduled_time, name=job_name, args=(user, events_list, RemindersTypes.everyday))

	def preparation_text(self, events: list[Event] | Event, reminder_type: RemindersTypes) -> str:
		"""
		Подготовка текста напоминания.

		:param event: Событие.
		:type event: Event
		:param reminder_type: Тип напоминания.
		:type reminder_type: RemindersTypes
		:return: Текст отправляемого напоминания.
		:rtype: str
		"""

		if not isinstance(events, list): events = [events]
		
		preparation_texts = {
			RemindersTypes.today: "🔔 <b>НАПОМИНАНИЕ!</b> 🔔\n\nСегодня ваше событие <b>$name</b>!\n\nНе забудьте!)",
			RemindersTypes.everyday: {
				EventTypes.passed: _("Cобытие <b>$name</b> было $remains $days!"),
				EventTypes.remained: _("<b>$name</b> наступит через $remains $days!")
			}, 
			RemindersTypes.once: _("🔔 <b>НАПОМИНАНИЕ!</b> 🔔\n\nДо события <b>$name</b> осталось $remains $days!\n\nХорошего вам дня!")
		}
		
		ready_messages = []

		for event in events:

			template = preparation_texts[reminder_type]
			if isinstance(template, dict): template = template[event.counter_type]

			replaces = {
				"$name": event.name
				}
		
			if "$remains" in template or "$days" in template:
				difference = event.calculate_date_difference()
				replaces["$remains"] = str(difference)
				replaces["$days"] = event.formating_word_day(difference, self.__language)

			for key, value in replaces.items(): template = template.replace(key, value)
			ready_messages.append(template)

		return ("\n\n").join(ready_messages)
	
	def send(self, user: UsersManager, event: Event, reminder_type: RemindersTypes):

		"""
		Отправляет сообщение с напоминаниями.

		:param user: Данные пользователя.
		:type user: UsersManager
		:param event: Событие.
		:type event: Event
		:param reminder_type: Тип напоминания.
		:type reminder_type: RemindersTypes
		"""

		text = self.preparation_text(event, reminder_type)

		try:
			self.__bot.send_message(user, text, parse_mode = "HTML")
			logging.info(f"Отправленно разовое напоминание {user.id}: {event.name}")
			user.set_chat_forbidden(False)
		except Exception as E: 
			logging.info(f"{E}, {user.id}: {event.name}")
			user.set_chat_forbidden(True)