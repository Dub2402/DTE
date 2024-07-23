from Source.Instruments import Calculator, CheckValidDate, GetFreeID
from Source.InlineKeyboard import InlineKeyboard

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
InlineKeyboardsBox = InlineKeyboard()

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
	User = Manager.auth(Message.from_user)

	try:
		User.get_property("events")
	except KeyError:
		User.set_property("events", {})

	Bot.send_message(Message.chat.id, "Добро пожаловать!\n\nЯ бот, помогающий запоминать события и указывать, сколько дней до них осталось.\n\nВведите команду /create для создания нового события или команду /list для просмотра всех ваших событий.")

@Bot.message_handler(commands=["create"])
def ProcessCommandCreate(Message: types.Message):
	User = Manager.auth(Message.from_user)

	Bot.send_message(Message.chat.id, "Введите, пожалуйста, название события, которое вы так с нетерпением ждёте 😉")
	User.set_expected_type("name")

@Bot.message_handler(commands=["list"])
def ProcessCommandList(Message: types.Message):
	# Авторизация пользователя.
	User = Manager.auth(Message.from_user)

	if not User.get_property("events"):
		Bot.send_message(Message.chat.id, "Вы не создали ни одного события.\nИспользуйте команду /create.")

	else:

		for EventID in User.get_property("events").keys():
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

			else:
				remains = Markdown(str(remains)).escaped_text
				Bot.send_message(
					Message.chat.id, f"До события *{name}* осталось {remains} {days}\\.",
					reply_markup = InlineKeyboardsBox.RemoveEvent(EventID),
					parse_mode = "MarkdownV2"
				)
			sleep(0.15)
		

@Bot.message_handler(content_types=["text"])
def ProcessText(Message: types.Message):
	User = Manager.auth(Message.from_user)
	
	if User.expected_type == "date":
		name = Markdown(User.get_property("date")).escaped_text
		if CheckValidDate(Message.text) == True:
			Date = Message.text
			Events = User.get_property("events")
			FreeID = GetFreeID(Events)
			Events[FreeID] = {"Name": User.get_property("date"), "Date": Date}
			User.set_property("events", Events)
			Bot.send_message(
				Message.chat.id,
				text = f"Данные сохранены\\! Теперь будем ждать ваше событие *{name}* вместе\\! 😊", 
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
		Bot.send_message(Message.chat.id, "А теперь мне нужна дата вашего события. \n\nФормат даты: ГГГГ-ММ-ДД")

		User.set_expected_type("date")

		return

# Обработка Inline-кнопки: удаление задачи.
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_event"))
def InlineButton(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	
	EventsID = Call.data.split("_")[-1]
	Events: dict = User.get_property("events")
	del Events[EventsID]

	User.set_property("events", Events)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	
	# Ответ на запрос.
	Bot.answer_callback_query(Call.id)

Bot.polling(none_stop = True)
