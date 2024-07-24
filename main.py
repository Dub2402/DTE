from Source.Instruments import Calculator, CheckValidDate, GetFreeID
from Source.InlineKeyboards import InlineKeyboards
from Source.ReplyKeyboard import ReplyKeyboard

from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import CheckPythonMinimalVersion, Clear
from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.TelebotUtils import UsersManager
from dublib.Polyglot import Markdown
from telebot import types
from time import sleep

import telebot

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)

# Создание папок в корневой директории.
MakeRootDirectories(["Data/Users"])
# Очистка консоли.
Clear()

Settings = ReadJSON("Settings.json")
Bot = telebot.TeleBot(Settings["token"])

Manager = UsersManager("Data/Users")
InlineKeyboardsBox = InlineKeyboards()
ReplyKeyboardBox = ReplyKeyboard()

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
	User = Manager.auth(Message.from_user)

	try:
		User.get_property("events")
	except KeyError:
		User.set_property("events", {})
	Bot.send_message(
		Message.chat.id, 
		"Добро пожаловать!\n\nЯ бот, помогающий запоминать события и указывать, сколько дней до них осталось."
		)
	sleep(0.5)
	Bot.send_message(
		Message.chat.id, 
		"Давайте познакомимся!\n\nНапишите свое имя! 🤗")
	User.set_expected_type("call")
	
@Bot.message_handler(content_types = ["text"], regexp = "Новое событие")
def ProcessTextNewEvent(Message: types.Message):
	User = Manager.auth(Message.from_user)

	Bot.send_message(
		Message.chat.id, 
		"Введите, пожалуйста, название события, которое вы так с нетерпением ждёте\\! 😉 \n\n_Например_\\: День рождения",
			parse_mode = "MarkdownV2"
		)
	User.set_expected_type("name")

@Bot.message_handler(content_types = ["text"], regexp = "Мои события")
def ProcessTextMyEvents(Message: types.Message):
	# Авторизация пользователя.
	User = Manager.auth(Message.from_user)

	if not User.get_property("events"):
		Bot.send_message(
			Message.chat.id, 
			"Вы не создали ни одного события 🙄\nНужно это дело исправить\\!\\)\n\nИспользуйте кнопку *Новое событие*\\.",
			parse_mode = "MarkdownV2"
			)

	else:
		somedict = User.get_property("events").copy()
		for EventID in somedict.keys():
			remains = Calculator(User.get_property("events")[EventID]["Date"])
			name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
			days = "дней"

			if abs(remains) in [11, 12, 13]: pass
			elif str(remains).endswith("1"): days = "день"
			elif str(remains).endswith("2") or str(remains).endswith("3") or str(remains).endswith("4"): days = "дня"

			if remains == 0:
				Bot.send_message(
					Message.chat.id,
					f"Ваше событие *{name}* сегодня\\.",
					reply_markup = InlineKeyboardsBox.RemoveEvent(EventID),
					parse_mode = "MarkdownV2")

			elif remains > 0:
				remains = Markdown(str(remains)).escaped_text
				call = Markdown(str(User.get_property("call"))).escaped_text
				Bot.send_message(
					Message.chat.id, f"{call}, до события *{name}* осталось {remains} {days}\\!\n\nДождёмся\\!\\!\\!",
					reply_markup = InlineKeyboardsBox.RemoveEvent(EventID),
					parse_mode = "MarkdownV2"
				)
			else:
				remains = Markdown(str(abs(remains))).escaped_text
				call = Markdown(str(User.get_property("call"))).escaped_text
				Bot.send_message(
					Message.chat.id, f"{call}, событие *{name}* было {remains} {days} назад\\!",
					reply_markup = InlineKeyboardsBox.RemoveEvent(EventID),
					parse_mode = "MarkdownV2"
				)
			sleep(0.15)
		
@Bot.message_handler(content_types = ["text"], regexp = "Поделиться с друзьями")
def ProcessShareWithFriends(Message: types.Message):
	User = Manager.auth(Message.from_user)

	Bot.send_message(
		Message.chat.id, 
		text='Лучший бот для отсчитывания дней до праздника 🥳\n\n@SleepFox789_TestBot\n\nПользуйся на здоровье!)', 
		reply_markup=InlineKeyboardsBox.AddShare()
		)

	User.set_expected_type("name")

@Bot.message_handler(content_types=["text"])
def ProcessText(Message: types.Message):
	User = Manager.auth(Message.from_user)
	if User.expected_type == "call":
		User.set_property("call", Message.text)

		Bot.send_message(
		Message.chat.id,
		"Для начала работы с ботом нажмите на любую кнопку.",
		reply_markup = ReplyKeyboardBox.AddMenu(User)
		)
		return
	
	if User.expected_type == "date":
		name = Markdown(User.get_property("date")).escaped_text
		if CheckValidDate(Message.text) == True:
			Date = Message.text
			Events = User.get_property("events")
			FreeID = str(GetFreeID(Events))
			Events[FreeID] = {"Name": User.get_property("date"), "Date": Date}
			User.set_property("events", Events)
			remains = Calculator(User.get_property("events")[FreeID]["Date"])
			if remains > 0:
				Bot.send_message(
					Message.chat.id,
					text = f"Данные сохранены\\! Теперь будем ждать ваше событие *{name}* вместе\\! 😊", 
					parse_mode = "MarkdownV2"
					)
			elif remains == 0:
				Bot.send_message(
					Message.chat.id,
					text = f"Данные сохранены\\! Ваше событие *{name}* сегодня\\!\\!\\! 😊", 
					parse_mode = "MarkdownV2"
					)
			else: 
				Bot.send_message(
					Message.chat.id,
					text = f"Данные сохранены\\! Ваше событие *{name}* уже произошло\\! 😊", 
					parse_mode = "MarkdownV2"
					)
			User.clear_temp_properties()
			User.set_expected_type(None)

		else:
			Bot.send_message(
				Message.chat.id, 
				"Вы ввели не соответствующую формату дату. Повторите попытку."
				)

		return

	elif User.expected_type == "name":
		Name = Message.text
		User.set_temp_property("date", Name)
		Bot.send_message(
			Message.chat.id,
			"А теперь мне нужна дата вашего события 🤔 \n\nПример\\: 01\\.01\\.2025", 
			parse_mode = "MarkdownV2")

		User.set_expected_type("date")

		return

# Обработка Inline-кнопки: удаление задачи.
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_event"))
def InlineButton(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	
	EventsID = Call.data.split("_")[-1]
	Events: dict = User.get_property("events")
	print(Events)
	del Events[EventsID]

	User.set_property("events", Events)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	
	# Ответ на запрос.
	Bot.answer_callback_query(Call.id)

Bot.polling(none_stop = True)
