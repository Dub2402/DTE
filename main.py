#==========================================================================================#
# >>>>> ПОДКЛЮЧЕНИЕ БИБЛИОТЕК И МОДУЛЕЙ <<<<< #
#==========================================================================================#

from Source.Functions import Calculator, CheckValidDate, GetFreeID, Skinwalker, FormatDays, _
from Source.InlineKeyboards import InlineKeyboards
from Source.ReplyKeyboard import ReplyKeyboard
from Source.Thread import Reminder
from Source.AdminPanel import Panel

from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import CheckPythonMinimalVersion, Clear
from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.TelebotUtils.Cache import TeleCache
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
reminder = Reminder(Bot, Manager, Settings["language"])
AdminPanel = Panel()

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ ЗАДАНИЙ В APSHEDULER <<<<< #
#==========================================================================================#

scheduler.add_job(reminder.StartRemindering, 'cron', hour = Settings["start_remindering"].split(":")[0], minute = Settings["start_remindering"].split(":")[1])
scheduler.add_job(reminder.ContinueRemindering, 'cron', hour = Settings["continue_remindering"].split(":")[0], minute = Settings["continue_remindering"].split(":")[1])
scheduler.start()

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ ИЗОБРАЖЕНИЯ В КЭШ <<<<< #
#==========================================================================================#

# Инициализация менеджера кэша.
Cacher = TeleCache()
# Установка данных для выгрузки медиафайлов.
Cacher.set_options(Settings["token"], Settings["chat_id"])

# Получение структуры данных кэшированного файла.
try:
	File = Cacher.get_cached_file(Settings["share_image_path"], type = types.InputMediaPhoto)
	# Получение ID кэшированного файла.
	FileID = Cacher[Settings["share_image_path"]]
except Exception:
	pass

#==========================================================================================#
# >>>>> ПАНЕЛЬ АДМИНИСТИРОВАНИЯ <<<<< #
#==========================================================================================#

AdminPanel.decorators.commands(Bot, Manager, Settings["password"])

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
	User = Manager.auth(Message.from_user)
	User.set_expected_type(None)
	try:
		File = Cacher.get_cached_file(Settings["start_jpg"], type = types.InputMediaPhoto)
		# Получение ID кэшированного файла.
		StartID = Cacher[Settings["start_jpg"]]
	except Exception:
		pass

	User.set_property("events", {}, False)
	try:
		Bot.send_photo(
			Message.chat.id, 
			photo = StartID,
			caption = _("🎉 *Добро пожаловать\\!* 🎉\n\nЯ бот, помогающий запоминать события и узнавать, сколько дней до них осталось\\."),
			parse_mode= "MarkdownV2"
		)
	except: 
		Bot.send_message(
			Message.chat.id, 
			text = _("🎉 *Добро пожаловать\\!* 🎉\n\nЯ бот, помогающий запоминать события и узнавать, сколько дней до них осталось\\."),
			parse_mode= "MarkdownV2"
		)
		
	User.set_temp_property("emoji", False)

	try:
		call = User.get_property("call")
		Bot.send_message(
			Message.chat.id, 
			call + _(", мы рады вас видеть снова! 🤗"),
			reply_markup= ReplyKeyboardBox.AddMenu(User)
			)
		
	except KeyError:
		Bot.send_message(
			Message.chat.id, 
			_("Давайте познакомимся!\nНапишите свое имя! 🤗")
			)
		User.set_expected_type("call")
	
AdminPanel.decorators.reply_keyboards(Bot, Manager)

@Bot.message_handler(content_types = ["text"], regexp = _("⚙️ Настройки"))
def ProcessTextReminders(Message: types.Message):
	User = Manager.auth(Message.from_user)
	Bot.send_message(
		Message.chat.id, 
		_("Выберите пункт, который вы хотите настроить:"), reply_markup = InlineKeyboardsBox.SettingsMenu(User))
		
@Bot.message_handler(content_types = ["text"], regexp = _("➕ Новое событие"))
def ProcessTextNewEvent(Message: types.Message):
	User = Manager.auth(Message.from_user)

	Bot.send_message(
		Message.chat.id, 
		_("Введите, пожалуйста, название события, которое вы так ждёте\\! 😉 \n\n"),
			parse_mode = "MarkdownV2"
		)
	User.set_expected_type("name")

@Bot.message_handler(content_types = ["text"], regexp = _("🗓 Мои события"))
def ProcessTextMyEvents(Message: types.Message):
	User = Manager.auth(Message.from_user)
	DeleteMessages = list()

	if not User.get_property("events"):
		Bot.send_message(
			Message.chat.id, 
			_("Вы не создали ни одного события 🙄\nНужно это дело исправить\\!\\)"),
			parse_mode = "MarkdownV2", 
			reply_markup= InlineKeyboardsBox.AddNewEvent()
			)

	else:
		call = Markdown(str(User.get_property("call"))).escaped_text
		Events = User.get_property("events").copy()
		DeleteMessage = Bot.send_message(
					Message.chat.id,
					_("Приветствую, %s\\!") % call, 
					parse_mode = "MarkdownV2")
		
		DeleteMessages.append(DeleteMessage.id)
		
		for EventID in Events.keys():
			remains = Calculator(User.get_property("events")[EventID]["Date"])
			name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
			days = FormatDays(remains, Settings["language"])

			if remains == 0:
				Bot.send_message(
					Message.chat.id,
					_("Ваше событие *%s* сегодня\\.") % name,
					parse_mode = "MarkdownV2",
					reply_markup = InlineKeyboardsBox.RemoveEvent(EventID))

			elif remains > 0:
				remains = Markdown(str(remains)).escaped_text
				Bot.send_message(
					Message.chat.id,
					_("*%s* наступит через %s %s\\!") % (name, remains, days),
					parse_mode = "MarkdownV2",
					reply_markup = InlineKeyboardsBox.RemoveEvent(EventID))
				
			else:
				if "Format" in Events[EventID]:
					if Events[EventID]["Format"] == "Passed":
						remains = Markdown(str(abs(remains))).escaped_text
						Bot.send_message(
							Message.chat.id,
							_("Событие *%s* было %s %s назад\\!") % (name, remains, days),
							parse_mode = "MarkdownV2",
							reply_markup = InlineKeyboardsBox.RemoveEvent(EventID))

					if Events[EventID]["Format"] == "Remained":
						newdate = Skinwalker(User.get_property("events")[EventID]["Date"])
						remainsnew = Calculator(newdate)
						days = FormatDays(remainsnew, Settings["language"])
						if remainsnew == 0:
							Bot.send_message(
								Message.chat.id,
								_("Ваше событие *%s* сегодня\\.") % name,
								parse_mode = "MarkdownV2",
								reply_markup = InlineKeyboardsBox.RemoveEvent(EventID))
							
						else:
							remainsnew = Markdown(str(remainsnew)).escaped_text
							Bot.send_message(
								Message.chat.id, 
								_("*%s* наступит через %s %s\\!") % (name, remainsnew, days),
								parse_mode = "MarkdownV2",
								reply_markup = InlineKeyboardsBox.RemoveEvent(EventID))
							
				else:
					remains = Markdown(str(abs(remains))).escaped_text
					Bot.send_message(
						Message.chat.id, 
						_("Событие *%s* было %s %s назад\\!") % (name, remains, days),
						parse_mode = "MarkdownV2",
						reply_markup = InlineKeyboardsBox.RemoveEvent(EventID))
					
			sleep(0.1)
		DeleteMessage = Bot.send_message(
						Message.chat.id,
						_("Хорошего тебе дня\\!\\)"),
						parse_mode = "MarkdownV2"
						)
		
		DeleteMessages.append(DeleteMessage.id)
		User.set_temp_property("ID_DelMessage", DeleteMessages)
	
@Bot.message_handler(content_types = ["text"], regexp = _("📢 Поделиться с друзьями"))
def ProcessShareWithFriends(Message: types.Message):
	User = Manager.auth(Message.from_user)
	try:
		Bot.send_photo(
			Message.chat.id, 
			photo = FileID,
			caption = _("@Dnido_bot\n@Dnido_bot\n@Dnido_bot\n\nПросто <b>Т-т-топовый</b> бот для отсчёта дней до событий 🥳\n\n<b><i>Пользуйся и делись с друзьями!</i></b>"), 
			reply_markup = InlineKeyboardsBox.AddShare(),
			parse_mode = "HTML" 
			)
	except: 
		Bot.send_message(
			Message.chat.id,
			_("@namebot"),
			reply_markup = InlineKeyboardsBox.AddShare()
			
			)

@Bot.message_handler(content_types=["text"])
def ProcessText(Message: types.Message):
	User = Manager.auth(Message.from_user)

	if AdminPanel.procedures.text(Bot, User, Message): return

	if User.expected_type == "call":
		User.set_property("call", Message.text)
		User.set_expected_type(None)

		call = User.get_property("call")
		if User.get_property("emoji"):
			Bot.send_message(
				Message.chat.id,
				_("Приятно познакомиться, %s! 😎") % call,
			reply_markup = ReplyKeyboardBox.AddMenu(User), 
			
			)
		else: 
			Bot.send_message(
				Message.chat.id,
				_("Приятно познакомиться, %s!") % call,
			reply_markup = ReplyKeyboardBox.AddMenu(User)
			)
			User.clear_temp_properties()
			sleep(0.1)

		if not User.get_property("events"):
			Bot.send_message(
			Message.chat.id, 
			text = _("Для начала работы с ботом создайте своё первое событие! 🙌"),
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
			days = FormatDays(remains, Settings["language"])
			
			if remains > 0:
				Bot.send_message(
					Message.chat.id,
					text = _("Данные сохранены\\!\n\nДо события *%s* осталось %s %s\\!\n\nБудем ждать его вместе\\! 💪") % (name, remains, days), 
					parse_mode = "MarkdownV2",
					reply_markup= InlineKeyboardsBox.ChoiceReminderForNewEvent(FreeID)
					)
				
			elif remains == 0:
				Bot.send_message(
					Message.chat.id,
					text = _("Данные сохранены\\!\n\nВаше событие *%s* сегодня\\!\\!\\! 😊") % name, 
					parse_mode = "MarkdownV2",
					reply_markup= InlineKeyboardsBox.ChoiceReminderForNewEvent(FreeID)
					)
			else: 
				Bot.send_message(
					Message.chat.id,
					text = _("Укажите, какой формат отсчёта вам показывать?"),
					reply_markup= InlineKeyboardsBox.ChoiceFormat(User, FreeID)
				)

			User.clear_temp_properties()
			User.set_temp_property("EventsID", FreeID)

		else:
			Bot.send_message(
				Message.chat.id, 
				_("Вы ввели не соответствующую формату дату. Повторите попытку.")
				)

		return

	if User.expected_type == "name":
		User.set_temp_property("date", Message.text)
		Bot.send_message(
			Message.chat.id,
			_("А теперь мне нужна дата вашего события 🤔 \n\n_Пример_\\: 01\\.01\\.2000"), 
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

			Name = User.get_property("events")[User.get_property("EventsID")]["Name"]
			Reminder = User.get_property("events")[User.get_property("EventsID")]["Reminder"]
			days = FormatDays(Reminder, Settings["language"])
			Bot.send_message(
				Message.chat.id,
				_("✅ Информация принята!\n\nЗа <b>$reminder $days</b> мы вам напомним о событии <b>$name</b>!").replace("$reminder", str(Reminder)).replace("$name", Name).replace("$days", days),
				parse_mode = "HTML"
			)
			
		else:
			Bot.send_message(
				Message.chat.id,
				_("Я не совсем понял, что вы от меня хотите."))
		return

AdminPanel.decorators.inline_keyboards(Bot, Manager)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_event"))
def InlineButtonRemoveEvent(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	EventID = Call.data.split("_")[-1]
	Events: dict = User.get_property("events")
	del Events[EventID]
	User.set_property("events", Events)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	if not User.get_property("events"):
		for ID in User.get_property("ID_DelMessage"):
			Bot.delete_message(Call.message.chat.id, ID)
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
		_("Введите, пожалуйста, название события, которое вы так ждёте\\! 😉 \n\n_Например_\\: День рождения"),
		parse_mode = "MarkdownV2"
	)
	User.set_expected_type("name")

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("choice_event"))
def InlineButtonChoiceEventToAddReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	if Call.data.count("_") == 2:
		EventsID = Call.data.split("_")[-1]
		Bot.send_message(
			Call.message.chat.id,
			_("Выберите тип напоминания:"),
			reply_markup = InlineKeyboardsBox.ChoiceFormatReminderChange(User)
		)
	else: 
		EventsID = Call.data.split("_")[-2]
		Bot.send_message(
			Call.message.chat.id,
			_("Выберите тип напоминания:"),
			reply_markup = InlineKeyboardsBox.ChoiceFormatReminderNew(User)
		)
	
	User.set_temp_property("EventsID", EventsID)
	User.set_expected_type("reminder")

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("passed_days"))
def InlineButtonPassedDays(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	FreeID = Call.data.split("_")[-1]
	name = Markdown(User.get_property("events")[FreeID]["Name"]).escaped_text
	remains = Calculator(User.get_property("events")[FreeID]["Date"])

	Event: dict = User.get_property("events")
	Format: dict = {"Format": "Passed"}
	ReminderFormat: dict = {"ReminderFormat": "WithoutReminders"}
	Event[FreeID].update(Format)
	Event[FreeID].update(ReminderFormat)
	User.set_property("events", Event)

	days = FormatDays(remains, Settings["language"])

	Bot.send_message(
		Call.message.chat.id,
		text = _("Данные сохранены\\!\n\nВаше событие *%s* произошло %s %s назад\\!") % (name, abs(remains), days), 
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

	days = FormatDays(remains, Settings["language"])
	if remains == 365:
		Bot.send_message(
				Call.message.chat.id,
				text = _("Данные сохранены\\!\n\nВаше событие *%s* сегодня\\!\\!\\! 😊") % name, 
				parse_mode = "MarkdownV2",
				reply_markup= InlineKeyboardsBox.ChoiceReminderForNewEvent(FreeID)
				)
	else:
		Bot.send_message(
			Call.message.chat.id,
			_("Данные сохранены\\!\n\nДо события *%s* осталось %s %s\\!\n\nБудем ждать его вместе\\! 💪")  % (name, remains, days), 
			parse_mode = "MarkdownV2", 
			reply_markup= InlineKeyboardsBox.ChoiceReminderForNewEvent(FreeID)
			)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Change_reminder"))
def ProcessTextNewReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	somedict = User.get_property("events").copy()
			
	if User.get_property("events"):

		Bot.send_message(
			Call.message.chat.id, 
			_("Выберите событие, для которого вы хотели бы изменить напоминание:"))
		
		for EventID in somedict.keys():
			Name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
			if "ReminderFormat" in somedict[EventID].keys():
				
				if somedict[EventID]["ReminderFormat"] == "EveryDay":
					if "Format" not in somedict[EventID].keys() or "Format" in somedict[EventID].keys() and somedict[EventID]["Format"] == "Remained":
						Bot.send_message(
						Call.message.chat.id,
						_("*%s*\nУстановлены ежедневные напоминания\\!") % Name,
						reply_markup = InlineKeyboardsBox.ChoiceEventToChangeReminder(EventID),
						parse_mode = "MarkdownV2")
					
				if somedict[EventID]["ReminderFormat"] == "OnceDay":
					if "Reminder" in somedict[EventID].keys():

						Reminder = Markdown(User.get_property("events")[EventID]["Reminder"]).escaped_text
						days = FormatDays(Reminder, Settings["language"])
						Bot.send_message(
							Call.message.chat.id,
							_("*%s*\nНапоминание установлено за %s %s\\!") % (Name, Reminder, days),
							reply_markup = InlineKeyboardsBox.ChoiceEventToChangeReminder(EventID),
							parse_mode = "MarkdownV2")
			
			sleep(0.1)

	elif not User.get_property("events"):
		Bot.send_message(
			Call.message.chat.id, 
			text = _("Чтобы изменить напоминание, сначала создайте событие!"),
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
			_("Чтобы отключить напоминания, сначала создайте событие!"),
			reply_markup = InlineKeyboardsBox.AddNewEvent()
			)
	else:
		DeleteMessage = Bot.send_message(
					Call.message.chat.id,
					_("Ваши напоминания:"))
		User.set_temp_property("ID_DelMessage", DeleteMessage.id)

		for EventID in somedict.keys():
			Name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
		
			if "ReminderFormat" in somedict[EventID].keys():
				
				if somedict[EventID]["ReminderFormat"] == "EveryDay":
					if "Format" not in somedict[EventID].keys() or "Format" in somedict[EventID].keys() and somedict[EventID]["Format"] == "Remained":
						Bot.send_message(
						Call.message.chat.id,
						_("*%s*\nУстановлены ежедневные напоминания\\!") % Name,
						reply_markup = InlineKeyboardsBox.RemoveReminder(EventID),
						parse_mode = "MarkdownV2")
					
				if somedict[EventID]["ReminderFormat"] == "OnceDay":
					if "Reminder" in somedict[EventID].keys():

						Reminder = Markdown(User.get_property("events")[EventID]["Reminder"]).escaped_text
						days = FormatDays(Reminder, Settings["language"])
						Bot.send_message(
							Call.message.chat.id,
							_("*%s*\nНапоминание установлено за %s %s\\!") % (Name, Reminder, days),
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
		_("Напишите свое новое имя!"))
	User.set_expected_type("call")

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Info"))
def ProcessInfo(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Bot.send_message(
		Call.message.chat.id,
		text = _("@Dnido_bot предназначен для запоминания событий и отслеживания, сколько дней до них осталось.\n\n1) По умолчанию, если вы создаёте событие, то будут активированы <b>ежедневные напоминания</b> 🔔. Вы их сможете отключить в любой момент, нажав на \"Отключить напоминание\" в настройках. Само событие останется.\n\n2) Даже если вы уберете напоминания, то не переживайте, в день события мы вам всё равно о нём напомним! В покое точно не оставим! 🤓 Также вы можете установить <b>разовое напоминание</b>, например, за 10 дней 📆.\n\n<b><i>Пользуйтесь, и не забывайте делиться с друзьями!</i></b>"),
		parse_mode= "HTML",
		reply_markup= InlineKeyboardsBox.OK()
	)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("every_day_reminder"))
def ProcessEveryDayReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	
	Events: dict = User.get_property("events")
	ReminderDict: dict = {"ReminderFormat": "EveryDay", "Format": "Remained"}

	EventID = User.get_property("EventsID")
	Events[EventID].update(ReminderDict)
	User.set_property("events", Events)

	name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
	Bot.send_message(
		Call.message.chat.id,
		_("Для события *%s* ежедневные напоминания включены\\!") % name,
		parse_mode = "MarkdownV2"
		)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("once_reminder"))
def ProcessOnceDayReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	Events: dict = User.get_property("events")
	ReminderDict: dict = {"ReminderFormat": "OnceDay", "Format": "Remained"}

	EventID = User.get_property("EventsID")
	Events[EventID].update(ReminderDict)
	User.set_property("events", Events)

	Name = Markdown(User.get_property("events")[EventID]["Name"]).escaped_text
	Bot.send_message(
		Call.message.chat.id,
			_("Укажите, за сколько дней вам напомнить о событии *%s*? 🔊\n\n_Пример_\\: 10") % Name,
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
			_("Для события *%s* напоминания отключены\\!\n\nНо не переживайте\\! День в день мы вас все равно о нём уведомим\\! 🛎") % Name,
			parse_mode = "MarkdownV2"
		)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Return"))
def ProcessWithoutReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("OK"))
def ProcessWithoutOK(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	Bot.delete_message(Call.message.chat.id, Call.message.id)
	
	Bot.answer_callback_query(Call.id)
	
@Bot.message_handler(content_types = ["audio", "document", "video"])
def File(Message: types.Message):
	User = Manager.auth(Message.from_user)
	AdminPanel.procedures.files(Bot, User, Message)

AdminPanel.decorators.photo(Bot, Manager)

Bot.infinity_polling()
