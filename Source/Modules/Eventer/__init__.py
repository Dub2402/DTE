from .ReminderStructs import ReminderData, ReminderTime
from Source.Core.Enums import PropertiesUser

from typing import Any, TYPE_CHECKING
from datetime import date as datetime_date
import enum
import os

import dateparser

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

class EventTypes(enum.Enum):
	passed = "passed"
	remained = "remained"
	today = "today"

class Event:
	"""Событие."""

	@property
	def id(self) -> int:
		"""ID события."""

		return self.__id
	
	@property
	def is_temp(self) -> bool:
		"""Состояние: является ли событие не до конца созданным."""

		return bool(self.__data.get("is_temp"))
	
	@property
	def name(self) -> str | None:
		"""Название события."""

		return self.__data["name"]
	
	@property
	def date(self) -> datetime_date | None:
		"""Дата события."""

		return self.__date

	@property
	def counter_type(self) -> EventTypes | None:
		"""Тип события."""

		return EventTypes(self.__data["counter_type"]) if self.__data.get("counter_type") else None

	@property
	def reminder(self) -> ReminderData | None:
		"""Данные дополнительного напоминания."""

		return self.__reminder_data
	
	@property
	def notifications(self) -> bool:
		"""Состояние: включены ли уведомления."""
	
		return self.__data["notifications"]

	@property
	def is_date_passed(self) -> bool: 
		"""Состояние: прошла ли эта дата."""
		
		return datetime_date.today() > self.date
	
	@property
	def is_date_passed_this_year(self) -> bool: 
		"""Состояние: прошла ли эта дата в этом году."""
		
		return datetime_date.today() > self.date.replace(year = datetime_date.today().year)

	def __parse_reminder_data(self, data: dict[str, int | str]) -> ReminderData | None:
		"""
		Парсит словарь данных дополнительного напоминания.

		:param data: Данные напоминания.
		:type data: dict[str, int  |  str]
		:return: Объектное представление или `None` при отсутствии.
		:rtype: ReminderData | None
		"""

		if not data: return
		reminder_time = data["time"].split(":")

		return ReminderData(data["days"], ReminderTime(int(reminder_time[0]), int(reminder_time[1])))

	def __init__(self, eventer: "Eventer", id: int, data: dict[str, Any] | None = None, is_temp: bool = True):
		"""
		Событие.

		:param eventer: Обработчик событий.
		:type eventer: Eventer
		:param id: ID события.
		:type id: int
		:param data: Словарное представление данных события.
		:type data: dict[str, Any]
		:param is_temp: Указывает, вляется ли событие временным.
		:type is_temp: bool
		"""

		self.__eventer = eventer
		self.__id = id
		self.__data = data or {
			"name": None,
			"date": None,
			"counter_type": None,
			"notifications": False, 
			"reminder": None
		}
		if is_temp: self.__data["is_temp"] = True
		
		self.__date = dateparser.parse(self.__data["date"], settings = {"DATE_ORDER": "DMY", "STRICT_PARSING": True}).date() if self.__data["date"] else None
		self.__reminder_data = self.__parse_reminder_data(self.__data["reminder"])

	def calculate_date_difference(self) -> int:
		"""
		Разница в днях между датой события и указанной датой.

		:return: Разница в датах.
		:rtype: int
		"""

		event_date = self.date

		if self.counter_type == EventTypes.remained and self.is_date_passed:
			year = datetime_date.today().year + 1 if self.is_date_passed_this_year else datetime_date.today().year
			event_date = event_date.replace(year = year)

		delta = event_date - datetime_date.today()

		return abs(delta.days)
		
	def formating_word_day(self, difference: int) -> str:
		"""
		Согласовывает слово "день" по падежу, числу и языку.

		:param difference: Разница во времени между датами (в днях).
		:type difference: int
		:return: Результирующее слово.
		:rtype: str
		"""

		match os.environ["DTE_LANG"]:

			case "en":
				days = "day" if difference in (1,) else "days"

			case _:
				days = "дней"
				if difference in (11, 12, 13, 113, 213, 313): return days
				elif str(difference).endswith("1"): days = "день"
				elif str(difference).endswith("2") or str(difference).endswith("3") or str(difference).endswith("4"): days = "дня"
				
		return days

	def save(self):
		"""Сохраняет данные события, если оно помещено в обработчик."""

		if self.__id in self.__eventer.events_id: self.__eventer.save()

	def set_name(self, name: str | datetime_date):
		"""
		Задаёт имя события.

		:param date: Дата события.
		:type date: str | datetime_date
		"""

		self.__data["name"] = name
		self.save()

	def set_date(self, date: str | datetime_date):
		"""
		Задаёт дату события.

		:param date: Дата события.
		:type date: str | datetime_date
		"""

		if type(date) == str: date = dateparser.parse(date, settings = {"DATE_ORDER": "DMY", "STRICT_PARSING": True}).date()
		self.__date = date
		self.__data["date"] = date.strftime("%d-%m-%Y")
		self.save()

	def set_counter_type(self, counter_type: EventTypes):
		"""
		Задаёт тип события.

		:param type: Тип события.
		:type type: EventTypes 
		"""

		self.__data["counter_type"] = counter_type.value
		self.save()

	def set_reminder(self, reminder: ReminderData | None):
		"""
		Задаёт данные напоминания.

		:param reminder: Данные о напоминании.
		:type reminder: ReminderData | None
		"""

		self.__reminder_data = reminder
		self.__data["reminder"] = reminder.to_dict() if reminder else None
		self.save()

	def switching_notifications(self, switch: bool):
		"""
		Переключает уведомления.

		:param switch: Переклюатель.
		:type switch: bool
		"""

		self.__data["notifications"] = switch
		self.save()

	def to_dict(self) -> dict[str, dict | str]:
		"""
		Возвращает словарное представление данных события.

		:return: Данные события.
		:rtype: dict[str, dict | str]
		"""

		Buffer = self.__data.copy()
		if self.is_temp: Buffer["is_temp"] = True

		return Buffer

	def untemp(self):
		"""Выводит событие из временного режима."""

		del self.__data["is_temp"]
		self.__user.set_property(PropertiesUser.working_event_id.value, None)
		self.save()

class Eventer:
	"""Обработчик событий."""

	@property
	def events(self) -> tuple[Event]:
		"""
		Набор событий пользователя.

		:return: Набор событий пользователя.
		:rtype: tuple[Event]
		"""

		return tuple(self.__events.values())
	
	@property
	def events_id(self) -> tuple[int]:
		"""Набор ID событий."""

		return tuple(self.__events.keys())

	@property
	def temp_event(self) -> Event | None:
		"""Временное событие."""

		for current_event in self.__events.values():
			if current_event.is_temp: return current_event

	@property
	def working_event(self) -> Event | None:
		"""Событие с которым сейчас идёт работа."""

		working_event_id = self.__user.get_property(PropertiesUser.working_event_id.value)

		return self.__events[working_event_id]

	def __get_free_id(self) -> int:
		"""
		Возвращает свободный ID события.

		:return: Свободный ID события.
		:rtype: int
		"""

		events_ids = self.__events.keys()

		return max(events_ids) + 1 if events_ids else 1

	def __parse_events(self) -> dict[int, Event]:
		"""
		Преобразует словарь событий в словарь объектов.

		:return: Словарь событий.
		:rtype: dict[int, Event]
		"""

		buffer = dict()
		events_dict: dict[str, dict] = self.__user.get_property("events")

		for id in events_dict.keys():
			integer_id = int(id)
			buffer[integer_id] = (Event(self, integer_id, events_dict[id], is_temp = False))

		return buffer

	def __init__(self, user: "UserData"):
		"""
		Обработчик событий.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__user = user

		self.__events: dict[int, Event] = self.__parse_events()

	def __getitem__(self, id: int) -> Event:
		"""
		Возвращает событие с переданным ID.

		:param id: ID события.
		:type id: int
		:return: Событие.
		:rtype: Event
		:raise KeyError: Выбрасывается при отсутствии события с указанным ID.
		"""

		return self.__events[id]

	def create_event(self) -> Event:
		"""
		Создаёт новое событие.

		:return: Новое событие.
		:rtype: Event
		"""

		free_id = self.__get_free_id()

		new_event = Event(self, free_id)
		if new_event.id in self.__events.keys(): raise IndexError("Event with same ID already exists.")
		self.__events[new_event.id] = new_event

		self.__user.set_property(PropertiesUser.working_event_id.value, free_id)

		return new_event

	def is_exists(self, id: int) -> bool:
		"""
		Проверяет, существует ли событие с переданным ID.

		:param id: ID события.
		:type id: int
		:return: Возвращает `True`, если событие существует.
		:rtype: bool
		"""

		return id in self.__events
	
	def remove_event(self, id: int):
		"""
		Удаляет событие.

		:param id: ID события.
		:type id: int
		"""

		del self.__events[id]
		self.save()

	def save(self):

		"""Сохраняет события в данные пользователя."""

		buffer: dict[str, dict] = dict()
		for id, current_event in self.__events.items(): buffer[str(id)] = current_event.to_dict()
		self.__user.set_property("events", buffer)
