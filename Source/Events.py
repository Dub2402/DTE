from .Users import User as MainUserData
from .Bot_Addition import SaveMessageID
from Source.UI.InlineKeyboards import InlineKeyboard

from dublib.TelebotUtils import UserData
from dublib.Engine.GetText import _

from datetime import date
from time import sleep
import dateparser

from telebot import TeleBot, types

class Additional():
	"""Вспомогательный класс, отвещающий за дополнительные функции событий."""

	def Calculator(Date: str) -> int:
		"""Количество дней между датами. Значения могут быть как отрицательные, так и положительные.

		:param Date: Дата события.
		:type Date: str
		:return: Разница между датами.
		:rtype: int
		"""

		today = date.today()
		remains = (dateparser.parse(Date, settings = {'DATE_ORDER': 'DMY'}).date() - today).days
		
		return remains
	
	def FormatDays(remains: int, language : str) -> str:
		"""Отформатировать в зависимости от количества дней слово "день".
		
		:param remains: Разница между текущим днём и днём события.
		:type remains: int
		:param language: Код языка.
		:type language: str
		:return: Окончание слова "день".
		:rtype: str
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
		remains = Additional.Calculator(newevent)
		if remains > 364:
			yearnew = int(date.today().year)
			newevent = str(day) + "." + str(month) + "." + str(yearnew)

		return newevent

class InlineTemplates:
	"""Набор inline keyboards."""

	def AddNewEvent() -> types.InlineKeyboardMarkup:
		"""Кнопка создать событие.

		:return: inline keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Создать событие"), callback_data = "create_event")]])
	
	def RemoveEvent(EventID: int) -> types.InlineKeyboardMarkup:
		"""Кнопка удаление события.

		:param EventID: ID удаляемого события.
		:type EventID: int
		:return: inline keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Удалить"), callback_data = f"remove_event_{EventID}")]])

class Sender:
	"""Отправщик сообщений."""

	def __init__(self, user: UserData, bot: TeleBot):
		"""Инициализация необходимых данных для отправки сообщений связанных с событиями."""

		self.__user = user
		self.__bot = bot

	def no_events(self):
		"""Отправка сообщения о том, что нет событий."""

		self.__bot.send_message(
			self.__user.id, 
			_("Вы не создали ни одного события 🙄\nНужно это дело исправить!)"),
			parse_mode = "HTML", 
			reply_markup = InlineTemplates.AddNewEvent()
			)
		
	def hello_call(self, call: str):
		"""Отправка сообщения c приветствием.

		:param call: Обращение к пользователю.
		:type call: str
		"""

		DeleteMessage = self.__bot.send_message(
			self.__user.id, 
			_("Приветствую, %s!") % call, 
			parse_mode = "HTML"
			)
		SaveMessageID(self.__user, DeleteMessage.id, ["MessagesMyEvents"])

	def remains(self, type_remains: str, number_event: int, EventID: int, name: str, remains: int = 0, days: str = "", ):
		"""Отправка сообщения о том, что событие сегодня.

		:param name: Имя события.
		:type name: str
		:param EventID: ID события.
		:type EventID: int
		"""

		texts = {
			"null": "$number_event) " + _("Ваше событие <b>$name</b> сегодня."),
			"after": "$number_event) " + _("<b>$name</b> наступит через $remains $days!"),
			"before": "$number_event) " + _("Событие <b>$name</b> было $remains $days назад!")
		}

		Replaces = {
			"$name": name,
			"$remains": str(remains),
			"$days": days,
			"$number_event": str(number_event)
		}

		final_text: str = texts[type_remains]

		for start_replace in Replaces.keys(): final_text = final_text.replace(start_replace, Replaces[start_replace])
		
		DeleteMessage = self.__bot.send_message(
			chat_id = self.__user.id,
			text = final_text,
			parse_mode = "HTML",
			reply_markup = InlineTemplates.RemoveEvent(EventID))
			
		SaveMessageID(self.__user, DeleteMessage.id, ["MessagesMyEvents"])

class EventsData:
	"""Основной класс, отвечающий за события."""

	@property
	def events(self) -> dict:
		"""Данные о всех событиях."""

		return self.__user.get_property("events")
	
	def __init__(self, user: UserData):
		"""Инициализация данных необходимых для модуля событий."""
		
		self.__user = user

	def property_event(self, property: str, ID: str):
		"""Получение свойства события по ID."""

		return self.events[ID][property]

class Core:
	"""Класс, отвечающий за основной функционал бота."""

	@property
	def user(self):
		"""Данные пользователя."""

		return self.__user
	
	@property
	def bot(self):
		"""Telegram bot."""

		return self.__bot
	
	@property
	def data(self):
		"""Объект, отвечающий за события пользователя."""

		return self.__data

	@property
	def sender(self):
		"""Объект, отвечающий за события пользователя."""

		return self.__sender

	def __init__(self, user: UserData, bot: TeleBot, Settings: dict):
		"""Инициализация модуля событий."""
		
		self.__user = user
		self.__bot = bot
		self.__Settings = Settings

		self.__data = EventsData(self.user)
		self.__sender = Sender(self.user, self.bot)

	def my_events(self):
		"""Функционал, при нажатии кнопки "Мои события"."""

		if not self.data.events: self.sender.no_events()
		else: 
			events = self.data.events.copy()
			self.sender.hello_call(MainUserData(self.user).call)
			number_event = 1

			for EventID in events.keys():

				remains = Additional.Calculator(self.data.property_event("Date", EventID))
				name = self.data.property_event("Name", EventID)
				days = Additional.FormatDays(remains, self.__Settings["language"])

				if remains == 0: self.sender.remains(type_remains = "null", number_event = number_event, EventID = EventID, name = name)

				elif remains > 0: self.sender.remains(type_remains = "after", number_event = number_event, EventID = EventID, name = name, remains = remains, days = days)

				else:
					if self.data.property_event("Format", EventID) == "Passed":
						remains = str(abs(remains))
						self.sender.remains(type_remains = "before", number_event = number_event, EventID = EventID, name = name, remains = remains, days = days)

					elif self.data.property_event("Format", EventID) == "Remained":
						newdate = Additional.Skinwalker(self.data.property_event("Date", EventID))
						remainsnew = Additional.Calculator(newdate)
						daysnew = Additional.FormatDays(remainsnew, self.__Settings["language"])

						if remainsnew == 0: self.sender.remains(type_remains = "null", number_event = number_event, EventID = EventID, name = name)
							
						else: self.sender.remains(type_remains = "after", number_event = number_event, EventID = EventID, name = name, remains = remainsnew, days = daysnew)

				number_event += 1 		
				sleep(0.1)

			DeleteMessage = self.bot.send_message(
							self.user.id,
							_("Хорошего вам дня!)"),
							reply_markup = InlineKeyboard.SendEmoji("❤️", "events")
							)
			SaveMessageID(self.user, DeleteMessage.id, ["MessagesMyEvents"])

	# def disable_notifications(self):
	# 	"""Функционал, при нажатии кнопки "Отключить напоминания"."""

