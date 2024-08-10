#==========================================================================================#
# >>>>> ПОДКЛЮЧЕНИЕ БИБЛИОТЕК И МОДУЛЕЙ <<<<< #
#==========================================================================================#

from Source.Instruments import Calculator, CheckValidDate, GetFreeID, Skinwalker, FormatDays
from Source.InlineKeyboards import InlineKeyboards
from Source.ReplyKeyboard import ReplyKeyboard
from Source.Thread import Reminder

from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import CheckPythonMinimalVersion, Clear
from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.TelebotUtils import UsersManager
from dublib.Polyglot import Markdown
from telebot import types
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
import telebot
import logging

#==========================================================================================#
# >>>>> ЛОГГИРОВАНИЕ <<<<< #
#==========================================================================================#

logging.basicConfig(level=logging.INFO, encoding="utf-8", filename="LOGING.log", filemode="w",
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

#==========================================================================================#
# >>>>> СИСТЕМНЫЕ НАСТРОЙКИ <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 10)
MakeRootDirectories(["Data/Users"])
Clear()

#==========================================================================================#
# >>>>> НАСТРОЙКИ БОТА <<<<< #
#==========================================================================================#

Settings = ReadJSON("Settings.json")
Bot = telebot.TeleBot(Settings["token"])

#==========================================================================================#
# >>>>> СОЗДАНИЕ ОБЪЕКТОВ КЛАССОВ <<<<< #
#==========================================================================================#

Manager = UsersManager("Data/Users")
InlineKeyboardsBox = InlineKeyboards()
ReplyKeyboardBox = ReplyKeyboard()
scheduler = BackgroundScheduler()
reminder = Reminder(Bot)

#==========================================================================================#
# >>>>> НАСТРОЙКИ APSHEDULER <<<<< #
#==========================================================================================#

DefaultReminders = Settings["default_reminders"]
EveryReminders = Settings["every_reminders"]
OnceReminders = Settings["once_reminders"]

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ ЗАДАНИЙ В APSHEDULER <<<<< #
#==========================================================================================#

scheduler.add_job(reminder.StartDefault, 'cron', hour = DefaultReminders["hour"], minute=DefaultReminders["minute"])
scheduler.add_job(reminder.StartEvery, 'cron', hour = EveryReminders["hour"], minute = EveryReminders["minute"])
scheduler.add_job(reminder.StartOnce, 'cron', hour = OnceReminders["hour"], minute=OnceReminders["minute"])
scheduler.start()

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
	User = Manager.auth(Message.from_user)
	User.set_expected_type(None)

	User.set_property("events", {}, False)
	Bot.send_message(
		Message.chat.id, 
		"🎉 Добро пожаловать! 🎉\n\nЯ бот, помогающий запоминать события и узнавать, сколько дней до них осталось."
		)
	User.set_temp_property("emoji", False)

	try:
		call = User.get_property("call")
		Bot.send_message(
			Message.chat.id, 
			f"{call}, мы рады вновь видеть вас! 🤗",
			reply_markup= ReplyKeyboardBox.AddMenu(User)
			)
		
	except KeyError:
		Bot.send_message(
			Message.chat.id, 
			"Давайте познакомимся!\nНапишите свое имя! 🤗"
			)
		User.set_expected_type("call")
	
@Bot.message_handler(content_types = ["text"], regexp = "⚙️ Настройки")
def ProcessTextReminders(Message: types.Message):
	# Авторизация пользователя.
	User = Manager.auth(Message.from_user)
	Bot.send_message(
		Message.chat.id, 
		"Выберите пункт, который вы хотите настроить:", reply_markup= InlineKeyboardsBox.SettingsMenu(User))
		
@Bot.message_handler(content_types = ["text"], regexp = "➕ Новое событие")
def ProcessTextNewEvent(Message: types.Message):
	User = Manager.auth(Message.from_user)

	Bot.send_message(
		Message.chat.id, 
		"Введите, пожалуйста, название события, которое вы ждёте\\! 😉 \n\n",
			parse_mode = "MarkdownV2"
		)
	User.set_expected_type("name")

@Bot.message_handler(content_types = ["text"], regexp = "🗓 Мои события")
def ProcessTextMyEvents(Message: types.Message):
	User = Manager.auth(Message.from_user)

	if not User.get_property("events"):
		Bot.send_message(
			Message.chat.id, 
			"Вы не создали ни одного события 🙄\nНужно это дело исправить\\!\\)",
			parse_mode = "MarkdownV2", 
			reply_markup= InlineKeyboardsBox.AddNewEvent()
			)

	else:
		call = Markdown(str(User.get_property("call"))).escaped_text
		Events = User.get_property("events")
		Bot.send_message(
					Message.chat.id,
					f"Приветствую, {call}\\!",
					parse_mode = "MarkdownV2")
		
		for EventID in Events.keys():
			remains = Calculator(User.get_property("events")[EventID]["Date"])
			name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
			days = FormatDays(remains)

			if remains == 0:
				Bot.send_message(
					Message.chat.id,
					f"Ваше событие *{name}* сегодня\\.",
					parse_mode = "MarkdownV2")

			elif remains > 0:
				remains = Markdown(str(remains)).escaped_text
				Bot.send_message(
					Message.chat.id, f"До события *{name}* осталось {remains} {days}\\!",
					parse_mode = "MarkdownV2"
				)
			else:
				if "Format" in Events[EventID]:
					if Events[EventID]["Format"] == "Passed":
						remains = Markdown(str(abs(remains))).escaped_text
						Bot.send_message(
							Message.chat.id, f"Событие *{name}* было {remains} {days} назад\\!",
							parse_mode = "MarkdownV2"
						)

					if Events[EventID]["Format"] == "Remained":
						newdate = Skinwalker(User.get_property("events")[EventID]["Date"])
						remainsnew = Calculator(newdate)
						days = FormatDays(remainsnew)
						if remainsnew == 0:
							Bot.send_message(
								Message.chat.id,
								f"Ваше событие *{name}* сегодня\\.",
								parse_mode = "MarkdownV2"
								)
						else:
							remainsnew = Markdown(str(remainsnew)).escaped_text
							Bot.send_message(
								Message.chat.id, 
								f"До события *{name}* осталось {remainsnew} {days}\\!",
								parse_mode = "MarkdownV2"
						)
				else:
					remains = Markdown(str(abs(remains))).escaped_text
					Bot.send_message(
						Message.chat.id, f"Событие *{name}* было {remains} {days} назад\\!",
						parse_mode = "MarkdownV2"
					)

				
			sleep(0.1)
	
@Bot.message_handler(content_types = ["text"], regexp = "📢 Поделиться с друзьями")
def ProcessShareWithFriends(Message: types.Message):
	User = Manager.auth(Message.from_user)

	Bot.send_message(
		Message.chat.id, 
		text='@Dnido_bot\n\nЛучший бот для отсчёта дней до события 🥳\nПользуйся на здоровье!)', 
		reply_markup=InlineKeyboardsBox.AddShare()
		)

@Bot.message_handler(content_types=["text"])
def ProcessText(Message: types.Message):
	User = Manager.auth(Message.from_user)

	if User.expected_type == "call":
		User.set_property("call", Message.text)
		User.set_expected_type(None)

		call = Markdown(str(User.get_property("call"))).escaped_text
		if User.get_property("emoji"):
			Bot.send_message(
				Message.chat.id,
				f"Приятно познакомиться, {call}! 😎",
			reply_markup = ReplyKeyboardBox.AddMenu(User)
			)
		else: 
			Bot.send_message(
				Message.chat.id,
				f"Приятно познакомиться, {call}!",
			reply_markup = ReplyKeyboardBox.AddMenu(User)
			)
			User.clear_temp_properties()
			sleep(0.1)

		if not User.get_property("events"):
			Bot.send_message(
			Message.chat.id, 
			text= "Для начала работы с ботом создайте своё первое событие! 🙌",
			reply_markup = InlineKeyboardsBox.AddNewEvent()
			)
		
		return
	
	if User.expected_type == "date":
		name = Markdown(User.get_property("date")).escaped_text
		if CheckValidDate(Message.text) == True:
			Events = User.get_property("events")
			FreeID = str(GetFreeID(Events))
			Events[FreeID] = {"Name": User.get_property("date"), "Date": Message.text, "ReminderFormat": "EveryDay"}
			User.set_expected_type(None)
			User.set_property("events", Events)

			remains = Calculator(User.get_property("events")[FreeID]["Date"])
			name = Markdown(User.get_property("events")[FreeID]["Name"]).escaped_text
			days = FormatDays(remains)
			

			if remains > 0:
				Bot.send_message(
					Message.chat.id,
					text = f"Данные сохранены\\!\n\nДо события *{name}* осталось {remains} {days}\\!\n\nБудем ждать его вместе\\! 💪", 
					parse_mode = "MarkdownV2"
					)
				
			elif remains == 0:
				Bot.send_message(
					Message.chat.id,
					text = f"Данные сохранены\\!\n\nВаше событие *{name}* сегодня\\!\\!\\! 😊", 
					parse_mode = "MarkdownV2"
					)
			else: 
				Bot.send_message(
					Message.chat.id,
					text ="Укажите, какой формат отсчёта вам показывать?",
					reply_markup= InlineKeyboardsBox.ChoiceFormat(User, FreeID)
				)

			User.clear_temp_properties()
			User.set_temp_property("EventsID", FreeID)

		else:
			Bot.send_message(
				Message.chat.id, 
				"Вы ввели не соответствующую формату дату. Повторите попытку."
				)

		return

	if User.expected_type == "name":
		User.set_temp_property("date", Message.text)
		Bot.send_message(
			Message.chat.id,
			"А теперь мне нужна дата вашего события 🤔 \n\n_Пример_\\: 01\\.01\\.2025", 
			parse_mode = "MarkdownV2")

		User.set_expected_type("date")

		return
	
	if User.expected_type == "reminder":
		
		if Message.text.isdigit() and int(Message.text) >= 1 and int(Message.text) <= 366:
			Events: dict = User.get_property("events")
			ReminderDict: dict = {"Reminder": Message.text}
			Events[User.get_property("EventsID")].update(ReminderDict)
			User.set_property("events", Events)
			User.set_expected_type(None)

			Bot.send_message(
				Message.chat.id,
				"Информация принята!🫡 Будем держать руку на пульсе!")
		else:
			Bot.send_message(
				Message.chat.id,
				"Я не совсем понял, что вы от меня хотите.")
		return

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_event"))
def InlineButtonRemoveEvent(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	EventID = Call.data.split("_")[-1]
	Events: dict = User.get_property("events")
	del Events[EventID]
	User.set_property("events", Events)

	Bot.delete_message(Call.message.chat.id, Call.message.id)
	if not User.get_property("events"):
		Bot.delete_message(Call.message.chat.id, User.get_property("ID_DelMessage"))
		User.clear_temp_properties()
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_reminder"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	Delete = 0 
	User = Manager.auth(Call.from_user)
	
	EventID = Call.data.split("_")[-1]
	Events: dict = User.get_property("events")
	try:
		del Events[EventID]["Reminder"]
		del Events[EventID]["ReminderFormat"]
	except:
		del Events[EventID]["ReminderFormat"]
	
	User.set_property("events", Events)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	for EventID in User.get_property("events"):
		if "ReminderFormat" in User.get_property("events")[EventID].keys() and User.get_property("events")[EventID]["ReminderFormat"] != "WithoutReminders": 
			Delete += 1

	if Delete == 0:
		Bot.delete_message(Call.message.chat.id, User.get_property("ID_DelMessage"))
		User.clear_temp_properties()

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("create_event"))
def InlineButtonCreateEvent(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Bot.send_message(
		Call.message.chat.id, 
		"Введите, пожалуйста, название события, которое вы ждёте\\! 😉 \n\n_Например_\\: День рождения",
		parse_mode = "MarkdownV2"
	)
	User.set_expected_type("name")

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("choice_event"))
def InlineButtonChoiceEventToAddReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	CountReminders = 0
	Events = User.get_property("events").copy()
	for EventID in Events.keys():
		if "ReminderFormat" in Events[EventID].keys():
			CountReminders +=1

	if CountReminders < 10:
		EventsID = Call.data.split("_")[-1]
		Events: dict = User.get_property("events")
		Name = Markdown(Events[EventsID]["Name"]).escaped_text
		User.set_temp_property("EventsID", EventsID)

		Bot.send_message(
			Call.message.chat.id,
			f"Выберите тип напоминания:",
			reply_markup= InlineKeyboardsBox.ChoiceFormatReminder(User)
		)
		User.set_expected_type("reminder")

	else: 
		Bot.send_message(
			Call.message.chat.id, 
			"Превышен лимит напоминаний (>10).\nУдалите ненужные напоминания, для создания нового напоминания.")

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("passed_days"))
def InlineButtonPassedDays(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	FreeID = Call.data.split("_")[-1]
	name = Markdown(User.get_property("events")[FreeID]["Name"]).escaped_text
	remains = Calculator(User.get_property("events")[FreeID]["Date"])

	Event: dict = User.get_property("events")
	Format: dict = {"Format": "Passed"}
	Event[FreeID].update(Format)
	User.set_property("events", Event)

	days = FormatDays(remains)

	Bot.send_message(
		Call.message.chat.id,
		text = f"Данные сохранены\\!\n\nВаше событие *{name}* произошло {abs(remains)} {days} назад\\!", 
		parse_mode = "MarkdownV2"
		)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remained_days"))
def InlineButtonRemainedDays(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	FreeID = Call.data.split("_")[-1]
	name = Markdown(User.get_property("events")[FreeID]["Name"]).escaped_text
	newevent = Skinwalker(User.get_property("events")[FreeID]["Date"])
	remains = Calculator(newevent)

	Event: dict = User.get_property("events")
	Format: dict = {"Format": "Remained"}
	Event[FreeID].update(Format)
	User.set_property("events", Event)

	days = FormatDays(remains)
	if remains == 365:
		Bot.send_message(
				Call.message.chat.id,
				text = f"Данные сохранены\\!\n\nВаше событие *{name}* сегодня\\!\\!\\! 😊", 
				parse_mode = "MarkdownV2"
				)
	else:
		Bot.send_message(
			Call.message.chat.id,
			f"Данные сохранены\\!\n\nДо события *{name}* осталось {remains} {days}\\!\n\nБудем ждать его вместе\\! 💪", 
			parse_mode = "MarkdownV2"
			)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Remove_event"))
def ProcessDeleteEvent(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	if not User.get_property("events"):
		Bot.send_message(
			Call.message.chat.id, 
			"Вы не создали ни одного события 🙄\nНужно это дело исправить\\!\\)",
			parse_mode = "MarkdownV2", 
			reply_markup= InlineKeyboardsBox.AddNewEvent()
		)

	else:
		somedict = User.get_property("events").copy()
		DeleteMessage = Bot.send_message(
					Call.message.chat.id,
					f"Ваши события: ")
		
		User.set_temp_property("ID_DelMessage", DeleteMessage.id)
		for EventID in somedict.keys():
			name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
			Bot.send_message(
				Call.message.chat.id,
				f"*{name}*",
				reply_markup = InlineKeyboardsBox.RemoveEvent(EventID),
				parse_mode = "MarkdownV2")
			sleep(0.1)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Create_reminder"))
def ProcessTextNewReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Events = User.get_property("events")
			
	if User.get_property("events"):

		Bot.send_message(
			Call.message.chat.id, 
			"Выберите событие, для которого вы хотите создать напоминание:")
		
		for EventID in Events.keys():
			name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
			if "ReminderFormat" in Events[EventID].keys():
				Bot.send_message(
					Call.message.chat.id,
					f"*{name}*",
					reply_markup = InlineKeyboardsBox.ChoiceEventToChangeReminder(EventID),
					parse_mode = "MarkdownV2")
				sleep(0.1)

			else:	
				Bot.send_message(
					Call.message.chat.id,
					f"*{name}*",
					reply_markup = InlineKeyboardsBox.ChoiceEventToAddReminder(EventID),
					parse_mode = "MarkdownV2")
				sleep(0.1)

	elif not User.get_property("events"):
		Bot.send_message(
			Call.message.chat.id, 
			text= "Для создания напоминания сначала создайте событие!",
			reply_markup = InlineKeyboardsBox.AddNewEvent()
			)
		
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Delete_reminder"))
def ProcessDeleteReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	CountReminder = 0
	somedict = User.get_property("events").copy()

	for EventID in somedict.keys():
		if "ReminderFormat" in User.get_property("events")[EventID].keys() and User.get_property("events")[EventID]["ReminderFormat"] != "WithoutReminders":
			CountReminder += 1
	
	if CountReminder < 1:
		Bot.send_message(
			Call.message.chat.id, 
			"Вы не создали ни одного напоминания."
			)
	else:
		DeleteMessage = Bot.send_message(
					Call.message.chat.id,
					f"Ваши напоминания: ")
		User.set_temp_property("ID_DelMessage", DeleteMessage.id)

		for EventID in somedict.keys():
			Name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
		
			if "ReminderFormat" in somedict[EventID].keys():
				
				if somedict[EventID]["ReminderFormat"] == "EveryDay":
					
					Bot.send_message(
					Call.message.chat.id,
					f"*{Name}*\nУстановлены ежедневные напоминания\\!",
					reply_markup = InlineKeyboardsBox.RemoveReminder(EventID),
					parse_mode = "MarkdownV2")
					
				if somedict[EventID]["ReminderFormat"] == "OnceDay":
					if "Reminder" in somedict[EventID].keys():

						Reminder = Markdown(User.get_property("events")[EventID]["Reminder"]).escaped_text

						Bot.send_message(
							Call.message.chat.id,
							f"*{Name}*\nНапоминание установлено за {Reminder} дней\\!",
							reply_markup = InlineKeyboardsBox.RemoveReminder(EventID),
							parse_mode = "MarkdownV2")
			
			sleep(0.1)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Change"))
def ProcessChangeName(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	User.set_temp_property("emoji", True)
	Bot.send_message(
		Call.message.chat.id,
		"Напишите свое новое имя!")
	User.set_expected_type("call")

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("every_day_reminder"))
def ProcessEveryDayReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Events: dict = User.get_property("events")
	ReminderDict: dict = {"ReminderFormat": "EveryDay"}

	EventID = User.get_property("EventsID")
	Events[EventID].update(ReminderDict)
	User.set_property("events", Events)

	name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
	Bot.send_message(
		Call.message.chat.id,
		f"Ежедневные напоминания для события *{name}* активированы\\!",
		parse_mode = "MarkdownV2"
		)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("once_reminder"))
def ProcessOnceDayReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Events: dict = User.get_property("events")
	ReminderDict: dict = {"ReminderFormat": "OnceDay"}

	EventID = User.get_property("EventsID")
	Events[EventID].update(ReminderDict)
	User.set_property("events", Events)

	Name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
	Bot.send_message(
		Call.message.chat.id,
			f"Укажите, за сколько дней вам напомнить о событии *{Name}*? 🔊\n\n_Пример_\\: 10",
			parse_mode = "MarkdownV2"
		)
	User.set_expected_type("reminder")
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("without_reminders"))
def ProcessWithoutReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Events: dict = User.get_property("events")
	ReminderDict: dict = {"ReminderFormat": "WithoutReminders"}

	EventID = User.get_property("EventsID")
	Events[EventID].update(ReminderDict)
	User.set_property("events", Events)

	Name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
	Bot.send_message(
		Call.message.chat.id,
			f"Для события *{Name}* напоминания отключены\\!\n\nСколько осталось дней вы сможете помотреть по кнопке *Мои события* 🖲",
			parse_mode = "MarkdownV2"
		)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Return"))
def ProcessWithoutReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	
	Bot.answer_callback_query(Call.id)

Bot.infinity_polling()
