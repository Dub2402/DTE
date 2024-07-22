from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import CheckPythonMinimalVersion, Clear
from dublib.Methods.Filesystem import MakeRootDirectories
from telebot import types
from dublib.TelebotUtils import UsersManager
import telebot
from datetime import datetime, date
from time import sleep

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)

# Создание папок в корневой директории.
MakeRootDirectories(["Data/Users"])
# Очистка консоли.
Clear()

Settings = ReadJSON("Settings.json")
Bot = telebot.TeleBot(Settings["token"])
Manager = UsersManager("Data/Users")

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
	# Авторизация пользователя.
	User = Manager.auth(Message.from_user)
	try:
		User.get_property("events")
	except KeyError:
		User.set_property("events", [])
	Bot.send_message(Message.chat.id, "Добро пожаловать!\nЯ-бот, помогающий запоминать события и указывать сколько до них осталось.\nВведите команду /create - для создания нового события или команду /list для просмотра всех ваших событий.")

@Bot.message_handler(commands=["create"])
def ProcessCommandCreate(Message: types.Message):
	# Авторизация пользователя.
	User = Manager.auth(Message.from_user)
	Bot.send_message(Message.chat.id, "Введите дату события в формате гггг-мм-дд.")
	User.set_expected_type("date")

@Bot.message_handler(commands=["list"])
def ProcessCommandStart(Message: types.Message):
	# Авторизация пользователя.
	User = Manager.auth(Message.from_user)
	for i in range(len(User.get_property("events"))):
		for Event in User.get_property("events")[i].keys():
			remains = Calculator(User.get_property("events")[i][Event])
			Bot.send_message(Message.chat.id, f"До события {Event} осталось {remains} дней.")
			sleep(0.15)

@Bot.message_handler(content_types=["text"])
def ProcessCommandText(Message: types.Message):
	# Авторизация пользователя.
	User = Manager.auth(Message.from_user)
	for _ in range(0, 1):
		if User.expected_type == "date":
			if is_valid_date(Message.text) == True: 
				Date = Message.text
				User.set_temp_property("tempdate", Date)
				Bot.send_message(Message.chat.id, "Введите имя события.")
				User.set_expected_type("name")
				break

			else: Bot.send_message(Message.chat.id, "Вы ввели дату не соответствующую формату. Повторите попытку.")
		if User.expected_type == "name":
			Name = Message.text
			User.set_expected_type(None)
			Events = User.get_property("events")
			Events.append({Name: User.get_property("tempdate")})
			User.set_property("events", Events)
			remains = Calculator(User.get_property("tempdate"))
			User.clear_temp_properties()
			Bot.send_message(Message.chat.id, text = f"Ваше событие *{Name}* создано и до него осталось {remains} дней\.", parse_mode = "MarkdownV2")

def is_valid_date(date_str):
	try:
		datetime.fromisoformat(date_str)
		return True
	except ValueError:
		return False

def Calculator(event):
	today = date.today()
	remains = (date.fromisoformat(event) - today).days
	if remains <0: remains = f"{str(remains)}"
	return remains

Bot.polling(none_stop = True)
