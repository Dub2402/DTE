from Source.UI.InlineKeyboards import InlineKeyboard

from dublib.TelebotUtils import UserData
from dublib.TelebotUtils.Master import TeleMaster
from dublib.Engine.GetText import _

import telebot
from telebot import types
from telebot.types import ReactionTypeEmoji

def GetFreeID(Events: dict) -> int:
	""" Получение свободного ID события."""
	
	Increment = list()
	for key in Events.keys(): Increment.append(int(key))
	Increment.sort()
	FreeID = 1
	if Increment: FreeID = max(Increment) + 1

	return FreeID

def MessageWaitingName(Bot: telebot.TeleBot, Message: types.Message, inline_keyboard: InlineKeyboard, User: UserData, text: str, isbutton: bool = True):
	"""
	Отправка сообщения с клавиатурой: 
		текст: 
			Введите, пожалуйста, название события, которое вы так ждёте!
		кнопки: 
			Cпасибо, чуть позже!
	Ожидание ввода имени в файле пользователя.
	"""
	
	if isbutton: button = inline_keyboard.SteakActions(name_button = _("Cпасибо, чуть позже!"), delete = "WaitingName")
	else: button = None
	WaitingName = Bot.send_message(
		chat_id = Message.chat.id, 
		text = text,
		parse_mode = "HTML",
		reply_markup = button
		)
	
	SaveMessageID(User, WaitingName.id, ["WaitingName"])
	FreeID = GetFreeID(User.get_property("events"))
	User.set_property("EventID", str(FreeID))
	User.set_expected_type("name")	

def SendFormatReminders(Bot: telebot.TeleBot, inline_keyboard: InlineKeyboard, Message: types.Message, New_User: bool = False) -> types.Message:
	
	"""
	Отправка сообщения с клавиатурой: 
		текст: 
			Супер! Хотите получить разовое напоминание или отсчитывать дни?)
		кнопки: 
			разовое напоминание
			отсчитывать дни
	"""

	text = _("Супер! Хотите получить разовое напоминание или отсчитывать дни?)") 
	if New_User: 
		text = _("Супер! Хотите получить разовое напоминание или отсчитывать дни?)\n\n<b>Совет:</b> <i>Для своего ДР часто выбирают отсчитывать дни, а вот для ДР других - разовые напоминания 🤭</i>")
		
	DeleteMessageNotification = Bot.send_message(
		Message.chat.id,
		text = text,
		reply_markup = inline_keyboard.ChoiceFormatReminderStart(),
		parse_mode = "HTML"
		)
	return DeleteMessageNotification

def SendChangeFormat(Bot: telebot.TeleBot, Call: types.CallbackQuery, inline_keyboard: InlineKeyboard) -> types.Message:
	"""
	Просим пользователеля поменять формат события, если он хочет включить напоминания.
	"""
	DeleteMessageNotification = Bot.send_message(
		Call.message.chat.id,
		"Для отсчитывания дней до события выберите формат: <b>сколько дней осталось</b>.",
		parse_mode = "HTML",
		reply_markup = inline_keyboard.ChoiceFormat()
		)
	
	Bot.answer_callback_query(Call.id)

	return DeleteMessageNotification

def isEventExist(User: UserData, ID: str) -> bool:
	"""Создано ли событие с заданным ID."""

	return ID in User.get_property("events").keys()

def GetDataEvent(User: UserData):
	
	"""
	Получение словаря всех данных события пользователя из временных свойств. 
		Name: имя события;
		Date: дата;
		Format: отслеживание сколько прошло от даты/сколько осталось до даты;
		ReminderFormat: вид формата напоминаний;
		Reminder: за сколько поставить напоминание для пользователя;
		Time: во сколько напомнить пользователю.
	"""

	Name = None
	Date = None 
	ReminderFormat = None
	Format = None
	Reminder = None 
	Time = None

	if User.has_property("Name"): Name = User.get_property("Name")

	if User.has_property("Date"): Date = User.get_property("Date")

	if User.has_property("Format"): Format = User.get_property("Format")

	if User.has_property("ReminderFormat"): ReminderFormat= User.get_property("ReminderFormat")

	if User.has_property("Reminder"): Reminder = User.get_property("Reminder")

	if User.has_property("Time"): Time = User.get_property("Time")

	Data = {"Name": Name, "Date": Date, "ReminderFormat": ReminderFormat, "Format": Format, "Reminder": Reminder, "Time": Time}

	return Data

def SetDataEvent(User: UserData, Data: dict, FreeID: int):
	""" Добавление события в словарь всех событий пользователя. """

	Events: dict = User.get_property("events")
	Events[str(FreeID)] = Data
	User.set_property("events", Events)
	User.clear_temp_properties()

def DeleteEvent(User: UserData, EventID: int):
	"""Удаление события по ID."""

	Events = User.get_property("events")
	del Events[EventID]
	User.set_property("events", Events)

def SetPropertyEvent(User: UserData, Data: dict, FreeID: int):
	"""Обновление события в словарь всех событий пользователя. """

	Events: dict = User.get_property("events")
	for key, value in Data.items():
		Events[str(FreeID)][key] = value
	User.set_property("events", Events)

def SaveMessageID(User: UserData, ID: int, keys: list[str]):
	"""Добавляет значение ID сообщения.
		User: данные пользователя;
		ID: id сообщения;
		key: ключ для сохранения в пользовательском файле.
	"""

	for key in keys:
		Data = list()
		if User.has_property(key):
			Data: list = User.get_property(key)
		Data.append(ID)
		User.set_property(key, Data)

def DeleteMessageID(User: UserData, Call: types.CallbackQuery, masterbot: TeleMaster, key: str):
	"""Добавляет значение ID сообщения.
		User: данные пользователя;
		Call: экземляр класса types.CallbackQuery;
		Bot: экземпляр класса telebot.TeleBot;
		key: ключ для удаления в пользовательском файле.
	"""

	reversed_messages = reversed(User.get_property(key))
	masterbot.safely_delete_messages(chat_id = Call.message.chat.id, messages = reversed_messages)
	User.remove_property(key)

def SendMessagewithEmoji(Bot: telebot.TeleBot, Call: types.CallbackQuery, inline_keyboard: InlineKeyboard):
	"""
	Отправка сообщения с клавиатурой: 
		текст: 
			И вам спасибо!\nХорошего дня! ))
		кнопка: 
			❤️
	"""

	Bot.send_message(
			Call.message.chat.id,
			_("И вам спасибо!\nХорошего дня! ))"),
			reply_markup = inline_keyboard.SendEmoji("❤️")
		)
	
def PutReaction(Bot: telebot.TeleBot, Call: types.CallbackQuery, Emoji: str):

	"""
	Постановка реакции на сообщение. 
		Emoji: тип эмодзи.
	"""
	Bot.edit_message_reply_markup(
		Call.message.chat.id,
		Call.message.id,
		reply_markup = None
	)

	Bot.set_message_reaction(
			Call.message.chat.id, 
			Call.message.id, 
			[ReactionTypeEmoji(Emoji)]
			)

def SendErrorInput(Bot: telebot.TeleBot, User: UserData, Message: types.Message, expected_type: str, text: str = None):
	if text: text = text
	else: text = _("Я не совсем понял, что вы от меня хотите. Повторите попытку.")
	DeleteMessageNotification = Bot.send_message(
		chat_id = Message.chat.id,
		text = text,
		parse_mode = "HTML")
	SaveMessageID(User, DeleteMessageNotification.id, ["Leavechangenotifications", "MessageNotificationsChange"])
	User.set_expected_type(expected_type)
	