from dublib.Engine.GetText import GetText
from Source.Functions import CheckValidDate, GetValidTime, LimitationOnceReminders
from Source.Bot_Addition import *
from Source.TeleBotAdminPanel import Panel
from Source.UI.InlineKeyboards import InlineKeyboard
from Source.UI.ReplyKeyboard import ReplyKeyboard
from Source.Mailer import Mailer
from Source.Modules.Mode import Modes, Data as DataModes
from Source.Events import Core as CoreEvents, Additional, EventsData

from Source.Modules.Timezoner import TimezonerInlineKeyboards, TimezonerDecorators, CorrectUserTime, Replacing_timezone
import Source.AdminPanelExtensions
import Source.AdditionalColumns

from dublib.Methods.Filesystem import ReadJSON
from dublib.Methods.System import CheckPythonMinimalVersion, Clear
from dublib.TelebotUtils import UsersManager
from dublib.TelebotUtils.Cache import TeleCache
from dublib.TelebotUtils.Master import TeleMaster

import telebot
import logging
from telebot import types
from time import sleep
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler

CheckPythonMinimalVersion(3, 10)
Clear()

logging.basicConfig(level=logging.INFO, encoding="utf-8", filename="LOGING.log", filemode="w",
	format='%(asctime)s - %(levelname)s - %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S')

logging.getLogger("pyTelegramBotAPI").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

Settings = ReadJSON("Settings.json")

GetText.initialize("DTE", Settings["language"], "locales")
_ = GetText.gettext

Bot = telebot.TeleBot(Settings["token"])
telemaster = TeleMaster(Settings["token"])
Manager = UsersManager("Data/Users")
reply_keyboard = ReplyKeyboard()
AdminPanel = Panel()
Cacher = TeleCache()
modes = Modes(Manager, Bot)

Cacher.set_bot(Bot)
Cacher.set_chat_id(Settings["chat_id"])
scheduler = BackgroundScheduler()

mailer = Mailer(Bot, Manager, Settings["language"])

scheduler.add_job(mailer.Start, 'cron', hour = Settings["start_remindering"].split(":")[0], minute = Settings["start_remindering"].split(":")[1], args = [["MessagesDaily", "MessagesTodayDefault"]])
scheduler.add_job(mailer.Start, 'cron', hour = '*', minute = '*', args = [["MessagesOnce", "MessagesTodaywithTime"]])
scheduler.start()

AdminPanel.decorators.commands(Bot, Manager, Settings["password"])

Manager.clear_temp_properties()

@Bot.message_handler(commands = ["start"])
def ProcessCommandStart(Message: types.Message):
	""" 
	Создание в пользовательском файле "New_User", если пользователь первый раз нажал /start.
		Отправка приветственного сообщения.
	"""

	if not Manager.is_user_exists(Message.from_user.id):
		User = Manager.auth(Message.from_user)
		User.set_property("New_User", True)

	User = Manager.auth(Message.from_user)
	User.set_property("events", {}, False)
	User.set_property("emoji", False)
	User.set_expected_type(None)
	
	try:
		StartID = Cacher.get_real_cached_file(Settings["start_jpg"], types.InputMediaPhoto)
		Bot.send_photo(
			Message.chat.id, 
			photo = StartID.file_id,
			caption = _("<b>ДОБРО ПОЖАЛОВАТЬ!</b>\n\nЯ бот, помогающий запоминать события и узнавать, сколько дней до них осталось."),
			parse_mode = "HTML"
		)
	except Exception as E: print(f"Проблема с кэшированием файла, при отправке сообщения. Проверьте файл Settings.json {E}")
		
	if User.has_property("call"):
		call = User.get_property("call")
		Bot.send_message(
			Message.chat.id, 
			call + _(", мы рады тебя видеть снова! 🤗"),
			reply_markup = reply_keyboard.AddMenu()
			)
	else:
		Bot.send_message(
			Message.chat.id, 
			_("Давайте познакомимся!\nНапишите свое имя! 🤗")
			)
		User.set_expected_type("call")

AdminPanel.decorators.reply_keyboards(Bot, Manager)

@Bot.message_handler(commands = ["infa"])
def ProcessInfa(Message: types.Message):

	User = Manager.auth(Message.from_user)
	Text = (_("@Dnido_bot предназначен для запоминания событий, отслеживания дней, а также установки различных напоминаний!\n"),
	_("<b>Здесь вы можете:</b>\n- Отсчитывать дни ДО события"),
	_("- Отсчитывать дни ПОСЛЕ события"),
	_("- Ставить напоминания о событии день в день в определенное время"),
	_("- Ставить напоминание о событии день в день без определенного времени (по умолчанию в 7 утра)"),
	_("- Ставить напоминание о событии за несколько дней до события в определенное время\n"),
	_("На каждое событие вы можете изменить тип напоминания в любой момент)\n"),
	_("<b><i>Пользуйтесь, и не забывайте делиться с друзьями!</i></b>")
	)
	MessageInfo = Bot.send_message(
		Message.chat.id,
		text = "\n".join(Text),
		parse_mode = "HTML",
		reply_markup = InlineKeyboard.SteakActions(name_button = _("Ясненько"), delete = "MessageInfo")
	)
	User.set_temp_property("MessageInfo", MessageInfo.id)

@Bot.message_handler(content_types = ["text"], regexp = "✏️ "+ _("Новое событие"))
def ProcessTextNewEvent(Message: types.Message):
	"""Отправка сообщения об ожидании ввода названия события."""

	User = Manager.auth(Message.from_user)
	text = _("Введите, пожалуйста, название события, которое вы так ждёте!")
	MessageWaitingName(Bot, Message, InlineKeyboard, User, text)

@Bot.message_handler(content_types = ["text"], regexp = _("🛎 Настройка напоминаний"))
def ProcessSettingsReminders(Message: types.Message):
	User = Manager.auth(Message.from_user)
	
	MessageSettings = Bot.send_message(
		Message.chat.id, 
		_("Выберите пункт, который вы хотите настроить:"),
		reply_markup = InlineKeyboard.SettingsMenu())

	SaveMessageID(User, MessageSettings.id, ["MessageSettings"])
	
@Bot.message_handler(content_types = ["text"], regexp = "📜 " + _(" Мои события"))
def ProcessTextMyEvents(Message: types.Message):
	User = Manager.auth(Message.from_user)
	
	CoreEvents(User, Bot, Settings).my_events()

@Bot.message_handler(content_types = ["text"], regexp = _("👄 Поделиться с друзьями"))
def ProcessShareWithFriends(Message: types.Message):
	User = Manager.auth(Message.from_user)
	try:
		ShareID = Cacher.get_real_cached_file(Settings["share_image_path"], types.InputMediaPhoto)
		Bot.send_photo(
			Message.chat.id, 
			photo = ShareID.file_id,
			caption = _("@Dnido_bot\n@Dnido_bot\n@Dnido_bot\n\nПросто <b>Т-т-топовый</b> бот для отсчёта дней до событий 🥳\n\n<b><i>Пользуйся и делись с друзьями!</i></b>"), 
			reply_markup = InlineKeyboard.AddShare(),
			parse_mode = "HTML" 
			)
	except Exception as E: print(f"Проблема с кэшированием файла share_image: {E}")

@Bot.message_handler(content_types = ["text"])
def ProcessText(Message: types.Message):
	User = Manager.auth(Message.from_user)
	if AdminPanel.procedures.text(Bot, Manager, Message): return

	if User.expected_type == "call":
		SaveMessageID(User, Message.id, ["Changename"])
		User.set_property("call", Message.text)
		User.set_expected_type(None)

		Changename = Bot.send_message(
			Message.chat.id,
			_("Приятно познакомиться, %s!") % Message.text,
			reply_markup = reply_keyboard.AddMenu()
			)
		SaveMessageID(User, Changename.id, ["Changename"])
		Changename = Bot.send_message(
			Message.chat.id,
			_("Укажите, пожалуйста, ваш пол. Это для лучшей адаптации бота под вас:"),
			reply_markup = InlineKeyboard.ChoiceGender()
			)
		SaveMessageID(User, Changename.id, ["Changename"])
		
		return
	
	if User.expected_type == "name":
		User.set_temp_property("Name", Message.text)

		Bot.send_message(
			Message.chat.id,
			_("А теперь мне нужна дата вашего события 🤔 \n\n<i>Пример: 01.01.2000</i>"), 
			parse_mode = "HTML")
		User.set_expected_type("date")

		return
	
	if User.expected_type == "date":
		if CheckValidDate(Message.text) == True:
			User.set_temp_property("Date", Message.text)
			remains = Additional.Calculator(Message.text)
			User.set_expected_type(None)
			User.set_temp_property("Format", "Remained")
			New_User = False
			if User.has_property("New_User"): 
				New_User = True
				User.remove_property("New_User")
			DeleteMessageNotification = SendFormatReminders(Bot, InlineKeyboard, Message, New_User)
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
		else:
			Bot.send_message(
				Message.chat.id, 
				_("Вы ввели не соответствующую формату дату. Повторите попытку.")
				)
		return
	
	if User.expected_type == "reminder&time":
		FreeID = User.get_property("EventID")
		SaveMessageID(User, Message.id, ["MessageNotificationsChange", "TextUserreminder&time" ])
		User.set_temp_property("ReminderFormat", "OnceDay")
		Modificated_message = Message.text.replace(":", "").replace(" ", "")
		Reminder_piece = Message.text.split(" ")[0].lstrip("0")
		if not Reminder_piece: 
			SendErrorInput(Bot = Bot, User = User, Message = Message, expected_type = "reminder&time")
			return
		Time_piece = Message.text.split(" ")[-1]
		
		try:
			if User.has_property("Name"): Name = User.get_property("Name")
			else: 
				Name = EventsData(User).property_event("Name", FreeID)

			if User.has_property("Date"): remains = LimitationOnceReminders(User.get_property("Date"))
			else: remains = LimitationOnceReminders(EventsData(User).property_event("Date", FreeID))

			Days_Reminder_piece = Additional.FormatDays(int(Reminder_piece), Settings["language"])
			Days_Remains = Additional.FormatDays(remains, Settings["language"])

			if Modificated_message.isdigit() and int(Reminder_piece) >= 1 and int(Reminder_piece) <= remains and Time_piece.count(":") == 1:
				if len(Time_piece) >= 3 and len(Time_piece) <= 5:
					Time = GetValidTime(Time_piece)
					
					if int(Reminder_piece) == remains: 
						Delta = Replacing_timezone(User)
						UserTime = CorrectUserTime(Time, Delta)

						if UserTime <= datetime.now(timezone.utc).replace(microsecond=0): 
							type_mistake = _("Ой-ой, а время напоминания <b>$Time_piece</b> для события <b>$Name</b> прошло...\nК сожалению, я не смогу отправиться в прошлое и предупредить вас 😔").replace("$Name", Name).replace("$Time_piece", Time_piece)
							SendErrorInput(Bot = Bot, User = User, Message = Message, expected_type = "reminder&time", text = type_mistake)
							return
					
					if not User.has_property("Name"): 
						Data = {"Reminder": Reminder_piece, "ReminderFormat": "OnceDay", "Time": Time}
						SetPropertyEvent(User, Data, FreeID)

					else: 
						User.set_temp_property("ReminderFormat", "OnceDay")
						User.set_temp_property("Reminder", Reminder_piece)
						User.set_temp_property("Time", Time)
						Data = GetDataEvent(User)
						SetDataEvent(User, Data, FreeID)

					if User.has_property("Oncereminders_button"):
						if User.get_property("Oncereminders_button") == "start": button = InlineKeyboard.Saving(["notSave", "Save"], _("Спасибо!"))
						if User.get_property("Oncereminders_button") == "new": button = InlineKeyboard.SteakActions(name_button = _("Спасибо!"), delete = "MessageNotificationsChange", update = "OnceDay")
						if User.get_property("Oncereminders_button") == "change": button = InlineKeyboard.SteakActions(name_button = _("Спасибо!"), delete = "MessageNotificationsChange", update = "AllReminders")

						DeleteMessageNotification = Bot.send_message(
							Message.chat.id, 
							_("✅ Данные сохранены!\n\nМы вам напомним о событии <b>$Name</b> в <b>$Time</b> за <b>$Reminder $Days</b>!").replace("$Name", Name).replace("$Time", Time).replace("$Reminder", Reminder_piece).replace("$Days", Days_Reminder_piece),
							parse_mode = "HTML",
							reply_markup = button
							)
						SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])

				else: SendErrorInput(Bot = Bot, User = User, Message = Message, expected_type = "reminder&time")
			else: 
				type_mistake = "Ой-ой, а до вашего события <b>$Name</b> осталось всего <b>$remains</b> $Days_Remains...\nК сожалению, я не смогу отправиться в прошлое на <b>$Reminder_piece</b> $Days_Reminder_piece назад и предупредить вас 😔".replace("$Reminder_piece", Reminder_piece).replace("$Name", Name).replace("$remains", str(remains)).replace("$Days_Reminder_piece", Days_Reminder_piece).replace("$Days_Remains", Days_Remains)
				SendErrorInput(Bot = Bot, User = User, Message = Message, expected_type = "reminder&time", text = type_mistake)

		except ZeroDivisionError:
			SendErrorInput(Bot = Bot, User = User, Message = Message, expected_type = "reminder&time")
		return
	
	if User.expected_type == "time":
		button = InlineKeyboard.SteakActions(name_button = _("Спасибо!"), delete = "MessageNotificationsChange", update = "OnceDay")
		SaveMessageID(User, Message.id, ["MessageNotificationsChange"])
		TimeModificated = Message.text.replace(":", "").replace(" ", "")
		if TimeModificated.isdigit() and Message.text.count(":") == 1 and len(Message.text) >= 3 and len(Message.text) <= 5:
			try:
				Time = GetValidTime(Message.text)
				FreeID = User.get_property("EventID")

				if User.has_property("Date"): remains = LimitationOnceReminders(User.get_property("Date"))
				else: remains = LimitationOnceReminders(EventsData(User).property_event("Date", FreeID))

				if User.has_property("Name"): User.get_property("Name")
				else: Name = EventsData(User).property_event("Name", FreeID)
				
				if remains == 0: 
					Delta = Replacing_timezone(User)
					UserTime = CorrectUserTime(Time, Delta)

					if UserTime <= datetime.now(timezone.utc).replace(microsecond=0): 
						type_mistake = _("Ой-ой, а время напоминания <b>$Time_piece</b> для события <b>$Name</b> прошло...\nК сожалению, я не смогу отправиться в прошлое и предупредить вас 😔").replace("$Name", Name).replace("$Time_piece", Time)
						SendErrorInput(Bot = Bot, User = User, Message = Message, expected_type = "time", text = type_mistake)
						return

				if not User.has_property("Name"): 
					Data = {"Reminder": "0", "ReminderFormat": "OnceDay", "Time": Time}
					SetPropertyEvent(User, Data, FreeID)

				else: 
					User.set_temp_property("Reminder", "0")
					User.set_temp_property("ReminderFormat", "OnceDay")
					User.set_temp_property("Time", Message.text)
					Data = GetDataEvent(User)
					SetDataEvent(User, Data, FreeID)

				Name = EventsData(User).property_event("Name", FreeID)

				if User.has_property("Oncereminders_button"):
						if User.get_property("Oncereminders_button") == "start": button = InlineKeyboard.Saving(["Save"], _("Спасибо"))
						if User.get_property("Oncereminders_button") == "new": button = InlineKeyboard.SteakActions(name_button = _("Спасибо!"), delete = "MessageNotificationsChange", update = "OnceDay")
						if User.get_property("Oncereminders_button") == "change": button = InlineKeyboard.SteakActions(name_button = _("Спасибо!"), delete = "MessageNotificationsChange", update = "AllReminders")

				DeleteMessageNotification = Bot.send_message(
					Message.chat.id, 
					_("✅ Данные сохранены!\n\nМы вам напомним о событии <b>$Name</b> в <b>$Time день в день!</b>").replace("$Name", Name).replace("$Time", Time),
					parse_mode = "HTML",
					reply_markup = button
				)
				SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
			except ZeroDivisionError: SendErrorInput(Bot = Bot, User = User, Message = Message, expected_type = "time")
		else:
			SendErrorInput(Bot = Bot, User = User, Message = Message, expected_type = "time")
		return

AdminPanel.decorators.inline_keyboards(Bot, Manager)
modes.decorators.inline_keyboards()

TimezonerDecorators(Bot, Manager, InlineKeyboard)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Gender"))
def InlineButtonsChoiceGender(Call: types.CallbackQuery):
	"""
	Задаём пол пользователя.
	Отправка сообщения пользователю с запросом часового пояса.
	"""

	User = Manager.auth(Call.from_user)
	Gender = Call.data.split("_")[-1]
	User.set_property("Gender", Gender)

	User.set_expected_type("timezone")
	Call_user = User.get_property("call")
	if User.has_property("emoji") and User.get_property("emoji"):
		if User.has_property("Gender") and User.get_property("Gender") == "man": Gender_text = _("Наш мужчина")
		else: Gender_text = _("Наша женщина")
	
		Changename =  Bot.send_message(
		chat_id = Call.message.chat.id,
		text = _("Спасибо большое! $gender_text, $name!)").replace("$gender_text", Gender_text).replace("$name", Call_user),
		parse_mode = "HTML",
		reply_markup = InlineKeyboard.SendEmoji("🤗")
	)
		SaveMessageID(User, Changename.id, ["Changename"])
	else:
		Bot.delete_message(Call.message.chat.id, Call.message.id)		
		Bot.send_message(
			chat_id = Call.message.chat.id,
			text = _("Спасибо большое!\n\nА теперь нам нужен ваш часовой пояс. Сколько сейчас времени у вас на телефоне? 🕐"),
			parse_mode = "HTML",
			reply_markup = TimezonerInlineKeyboards().timezone_first_page()
		)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Format"))
def InlineButtonsFormatDays(Call: types.CallbackQuery):
	"""
	Задаём формат события (Remained/Passed).
	Отправка сообщения пользователю с видом напоминаний (разовое/отсчитывать дни).
	"""

	User = Manager.auth(Call.from_user)
	EventID = User.get_property("EventID")
	Format = Call.data.split("_")[-1]

	if isEventExist(User, EventID): 
		Name = EventsData(User).property_event("Name", EventID)
		Date = EventsData(User).property_event("Date", EventID)
		SetPropertyEvent(User, {"Format": Format}, EventID)
	else: 
		Name = User.get_property("Name")
		Date = User.get_property("Date")
		Data = GetDataEvent(User)
		SetDataEvent(User, Data, EventID)
	
	if Format == "Remained":
		skinwalker = Additional.Skinwalker(Date)
		remains = str(Additional.Calculator(skinwalker))
		days = Additional.FormatDays(remains, Settings["language"])
		if DataModes(User).type == None: reply_markup = InlineKeyboard.SettingsNotifications(EventID, Send = "SendMessagewithEmoji", new_user = True)
		else: reply_markup = InlineKeyboard.SettingsNotifications(EventID, Send = "SendMessagewithEmoji")
		DeleteMessageNotification = Bot.send_message(
			chat_id = Call.message.chat.id,
			text = _("Данные сохранены!\n\nДо события <b>$Name</b> осталось $remains $days!\n\nБудем ждать его вместе с <u>ежедневными напоминаниями!</u> 🛎").replace("$Name", Name).replace("$remains", remains).replace("$days" ,days),
			reply_markup = reply_markup,
			parse_mode = "HTML"
		)
		SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])

	if Format == "Passed":

		remains = str(abs(Additional.Calculator(Date)))
		days = Additional.FormatDays(remains, Settings["language"])
		DeleteMessageNotification = Bot.send_message(
			chat_id = Call.message.chat.id,
			text = _("Данные сохранены!\n\nВаше событие <b>$Name</b> произошло $remains $days назад!").replace("$Name", Name).replace("$remains", remains).replace("$days", days),
			parse_mode = "HTML"
		)
		SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("AnotherDay"))
def InlineButtonAnotherDay(Call: types.CallbackQuery):
	"""
	Отправка сообщения для выбора дня и времени разовых напоминаний.
	"""
	
	User = Manager.auth(Call.from_user)
	if User.has_property("Name"): Name = User.get_property("Name")
	else:
		FreeID = User.get_property("EventID")
		Name = EventsData(User).property_event("Name", FreeID)
	DeleteMessageNotification = Bot.send_message(
		Call.message.chat.id,
		_("Укажите, за сколько дней и в какое время вам напомнить о событии <b>$Name</b>? 🔊\n\n<i>Пример: 10 18:30 (означает за 10 дней и в 18:30)</i>").replace("$Name", Name),
		parse_mode = "HTML"
	)

	User.set_expected_type("reminder&time")
	SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Save"))
def InlineButtonsSave(Call: types.CallbackQuery):
	"""
	Сохранение или исправление событий (разовое за n-ное количество дней до события), а также постановка реакции на сообщение (разовое за день до события).
	Удаление временных данных в пользовательском файле.
	"""

	User = Manager.auth(Call.from_user)
	Saving = Call.data.split("_")[1]
	
	if Saving.startswith("yes"):
		if Saving == "yes":
			SendMessagewithEmoji(Bot, Call, InlineKeyboard)
		
		else:
			Reaction = Saving.replace("yes","")
			PutReaction(Bot, Call, Reaction)

		User.clear_temp_properties()
		User.set_expected_type(None)
	else: 
		# ? Нужно ли при нажатии на исправить удалять что-либо, и назначать User.set_expected_type(None) ???????
		Delete = Call.data.split("_")[2]
		Bot.delete_message(Call.message.chat.id, Call.message.id)
		DeleteMessageID(User, Call, telemaster, "TextUserreminder&time")
		if Delete:
			DeleteMessageID(User, Call, telemaster, Delete)
			User.set_expected_type(None)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("create_event"))
def InlineButtonCreateEvent(Call: types.CallbackQuery):
	"""Отправка сообщения об ожидании ввода названия события."""

	User = Manager.auth(Call.from_user)
	text = _("Введите, пожалуйста, название события, которое вы так ждёте! 😉 \n\n<i>Например: День рождения</i>")
	MessageWaitingName(Bot, Call.message, InlineKeyboard, User, text, isbutton = False)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_event"))
def InlineButtonRemoveEvent(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	EventID = Call.data.split("_")[-1]
	DeleteEvent(User, EventID)
	DeleteMessageID(User, Call, telemaster, "MessagesMyEvents")

	if User.get_property("events"): CoreEvents(User, Bot, Settings).my_events()

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Delete_reminder"))
def ProcessDeleteReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	CountReminder = 0
	somedict: dict = User.get_property("events").copy()

	if User.get_property("events"):

		for EventID in somedict.keys():
			if User.get_property("events")[EventID]["ReminderFormat"] != "WithoutReminders":
				CountReminder += 1
		
		if CountReminder < 1:
			DeleteMessageNotification = Bot.send_message(
				Call.message.chat.id, 
				_("У вас все напоминания уже отключены!")
				)
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsDeactivate"])
		else:
			DeleteMessageNotification = Bot.send_message(
						Call.message.chat.id,
						_("ВАШИ НАПОМИНАНИЯ:"))
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsDeactivate"])

			number_event = 1
			for EventID in somedict.keys():
				Name = EventsData(User).property_event("Name", EventID)
			
				if somedict[EventID]["ReminderFormat"] == "EveryDay":
					DeleteMessageNotification = Bot.send_message(
					Call.message.chat.id,
					f"{number_event}) " + _("<b>%s</b>\nУстановлены ежедневные напоминания!") % Name,
					reply_markup = InlineKeyboard.ChoiceEventToRemoveReminder(EventID),
					parse_mode = "HTML")
					SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsDeactivate"])
					number_event += 1 
					
				if somedict[EventID]["ReminderFormat"] == "OnceDay":
					Reminder = EventsData(User).property_event("Reminder", EventID)
					Time = EventsData(User).property_event("Time", EventID)
					days = Additional.FormatDays(int(Reminder), Settings["language"])
					if Reminder == "0": text = f"{number_event}) " + _("<b>$Name</b>\nНапоминание установлено на $Time день в день!").replace("$Name", Name).replace("$Time", Time)
					else: text = f"{number_event}) " + _("<b>$Name</b>\nНапоминание установлено на $Time за $Reminder $days!").replace("$Name", Name).replace("$Time", Time).replace("$Reminder", Reminder).replace("$days", days)
					DeleteMessageNotification = Bot.send_message(
						Call.message.chat.id,
						text = text,
						reply_markup = InlineKeyboard.ChoiceEventToRemoveReminder(EventID),
						parse_mode = "HTML")
					SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsDeactivate"])
					number_event += 1 
				sleep(0.1)			
	else:
		DeleteMessageNotification = Bot.send_message(
				Call.message.chat.id, 
				_("Чтобы отключить напоминания, сначала создайте событие!"),
				reply_markup = InlineKeyboard.AddNewEvent()
				)
		SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsDeactivate"])
	
	DeleteMessageNotification = Bot.send_message(
		Call.message.chat.id,
		_("<b>Для выхода</b> в предыдущее меню нажмите \"Назад\":"),
		reply_markup = InlineKeyboard.SteakActions(name_button = _("🔙 Назад"), delete = "MessageNotificationsDeactivate"),
		parse_mode = "HTML"
		)
	
	SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsDeactivate"])

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_reminder"))
def InlineButtonRemoveReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	
	EventID = Call.data.split("_")[-1]
	Data = {"Reminder": None, "ReminderFormat": "WithoutReminders", "Time": None}
	SetPropertyEvent(User, Data, EventID)

	Bot.delete_message(Call.message.chat.id, Call.message.id)

	Delete = 0

	for EventID in User.get_property("events"):
		if User.get_property("events")[EventID]["ReminderFormat"] != "WithoutReminders": 
			Delete += 1

	if Delete == 0:
		DeleteMessageID(User, Call, telemaster, "MessageNotificationsDeactivate")

	DeleteMessageID(User, Call, telemaster, "MessageNotificationsDeactivate")
	ProcessDeleteReminder(Call = Call)

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Change_reminder"))
def ProcessChange_reminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	CountRemained = 0
	somedict: dict = User.get_property("events").copy()

	if User.get_property("events"):
		for EventID in somedict.keys():
			if somedict[EventID]["Format"] == "Remained":
				CountRemained += 1 
		if CountRemained >= 1:
			DeleteMessageNotification = Bot.send_message(
				Call.message.chat.id, 
				_("ВАШИ СОБЫТИЯ:"))
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
			
			number_event = 1
			for EventID in somedict.keys():
				Name = EventsData(User).property_event("Name", EventID)
				
				if somedict[EventID]["ReminderFormat"] == "EveryDay":
					DeleteMessageNotification = Bot.send_message(
					Call.message.chat.id,
					f"{number_event}) " + _("<b>%s</b>\nУстановлены ежедневные напоминания!") % Name,
					reply_markup = InlineKeyboard.ChoiceEventToChangeReminder(EventID),
					parse_mode = "HTML")
					SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
	
				if somedict[EventID]["ReminderFormat"] == "OnceDay":

					Reminder = EventsData(User).property_event("Reminder", EventID)
					Time = EventsData(User).property_event("Time", EventID)
					days = Additional.FormatDays(int(Reminder), Settings["language"])
					if Reminder == "0": text = f"{number_event}) " + _("<b>$Name</b>\nНапоминание установлено на $Time день в день!").replace("$Name", Name).replace("$Time", Time)
					else: text = f"{number_event}) " +  _("<b>$Name</b>\nНапоминание установлено на $Time за $Reminder $days!").replace("$Name", Name).replace("$Time", Time).replace("$Reminder", Reminder).replace("$days", days)
					DeleteMessageNotification = Bot.send_message(
						Call.message.chat.id,
						text = text,
						reply_markup = InlineKeyboard.ChoiceEventToChangeReminder(EventID),
						parse_mode = "HTML")
					SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
	
				if somedict[EventID]["ReminderFormat"] == "WithoutReminders" and somedict[EventID]["Format"] == "Remained":
					DeleteMessageNotification = Bot.send_message(
						Call.message.chat.id,
						f"{number_event}) " + _("<b>%s</b>\nНапоминание отключено!") % (Name),
						reply_markup = InlineKeyboard.ChoiceEventToChangeReminder(EventID),
						parse_mode = "HTML")
					SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
				number_event += 1 		
				sleep(0.1)
		else:
			DeleteMessageNotification = Bot.send_message(
					Call.message.chat.id, 
					text = _("Чтобы изменить напоминание, сначала создайте событие!"),
					reply_markup = InlineKeyboard.AddNewEvent()
					)
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
		
	else:
		DeleteMessageNotification = Bot.send_message(
					Call.message.chat.id, 
					text = _("Чтобы изменить напоминание, сначала создайте событие!"),
					reply_markup = InlineKeyboard.AddNewEvent()
					)
		SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
		

	DeleteMessageNotification = Bot.send_message(
		Call.message.chat.id,
		_("<b>Для выхода</b> в предыдущее меню нажмите \"Назад\":"),
		reply_markup = InlineKeyboard.SteakActions(name_button = _("🔙 Назад"), delete = "MessageNotificationsChange"),
		parse_mode = "HTML"
		)
	SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
		
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("choice_event"))
def InlineButtonChoiceEventToAddReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)

	EventID = Call.data.split("_")[-1]
	User.set_property("EventID", EventID)
	Name = EventsData(User).property_event("Name", EventID)
	DeleteMessageNotification = Bot.send_message(
		Call.message.chat.id,
		_("Выберите тип напоминания для события <b>%s</b>:") % Name,
		reply_markup = InlineKeyboard.ChoiceFormatReminderChange(),
		parse_mode = "HTML"
	)
	SaveMessageID(User, DeleteMessageNotification.id, ["Leavechangenotifications", "MessageNotificationsChange"])
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("settings_for"))
def InlineButtonSettingsforReminder(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	DeleteMessageNotification = Bot.send_message(
		Call.message.chat.id,
		_("Выберите тип напоминания:"),
		reply_markup = InlineKeyboard.ChoiceFormatReminderNew()
		)
	SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
	Bot.answer_callback_query(Call.id)
	
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("every_day_reminder"))
def ProcessEveryDayReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	subtype = Call.data.split("_")[-1]
	User.set_temp_property("ReminderFormat", "EveryDay")
	EventID = User.get_property("EventID")

	if isEventExist(User, EventID): Name = EventsData(User).property_event("Name", EventID)
	else: Name = User.get_property("Name")

	if subtype == "start": 
		User.set_property("Oncereminders_button", subtype)
		remains = Additional.Calculator(User.get_property("Date"))
		if remains < 0: 
			DeleteMessageNotification = Bot.send_message(
				Call.message.chat.id,
				text = _("Укажите, какой формат отсчёта вам показывать?"),
				reply_markup = InlineKeyboard.ChoiceFormat()
			)
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])

		elif remains == 0: 
			if DataModes(User).type == None: reply_markup = InlineKeyboard.SettingsNotifications(EventID, Send = "SendMessagewithEmoji", new_user = True)
			else: reply_markup = InlineKeyboard.SettingsNotifications(EventID, Send = "SendMessagewithEmoji")
			DeleteMessageNotification = Bot.send_message(
				chat_id = Call.message.chat.id,
				text = _("Данные сохранены!\n\nВаше событие $Name сегодня!!! 😊".replace("$Name", Name)),
				reply_markup = reply_markup,
				parse_mode = "HTML"
			)
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
			Data = GetDataEvent(User)
			SetDataEvent(User, Data, EventID)

		else:
			if DataModes(User).type == None: reply_markup = InlineKeyboard.SettingsNotifications(EventID, Send = "SendMessagewithEmoji", new_user = True)
			else: reply_markup = InlineKeyboard.SettingsNotifications(EventID, Send = "SendMessagewithEmoji")
			days = Additional.FormatDays(remains, Settings["language"])
			DeleteMessageNotification = Bot.send_message(
				chat_id = Call.message.chat.id,
				text = _("Данные сохранены!\n\nДо события <b>$Name</b> осталось $remains $days!\n\nБудем ждать его вместе с <u>ежедневными напоминаниями!</u> 🛎").replace("$Name", Name).replace("$remains", str(remains)).replace("$days", days),
				reply_markup = reply_markup,
				parse_mode = "HTML"
			)
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
			Data = GetDataEvent(User)
			SetDataEvent(User, Data, EventID)

	if subtype == "change":
		Name = EventsData(User).property_event("Name", EventID)
		DeleteMessageNotification = Bot.send_message(
			Call.message.chat.id,
			_("Вы хотите включить ежедневные напоминания для события <b>$Name</b>?").replace("$Name", Name),
			parse_mode = "HTML",
			reply_markup = InlineKeyboard.Confirmation("EveryNotifications", subtype)
			)
		SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("once_reminder"))
def ProcessOnceDayReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	subtype = Call.data.split("_")[-1]
	EventID = User.get_property("EventID")

	if isEventExist(User, EventID) and EventsData(User).property_event("Format", EventID) == "Passed":
		DeleteMessageNotification = SendChangeFormat(Bot, Call, InlineKeyboard)
		return

	DeleteMessageNotification = Bot.send_message(
			Call.message.chat.id,
			_("В день события мы вам пришлём напоминание! 🛎 \n\nВ какое время вы бы хотели получить его?\n\n<i>Пример: 18:30</i>"),
			reply_markup = InlineKeyboard.ChoiceAnotherDay(),
			parse_mode = "HTML"
			)
	User.set_expected_type("time")
	User.set_property("Oncereminders_button", subtype)
	SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("without_reminders"))
def ProcessWithoutReminders(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	subtype = Call.data.split("_")[-1]
	EventID = User.get_property("EventID")
	Name = EventsData(User).property_event("Name", EventID)
	if subtype == "change": text = _("Хотите отключить все напоминания для события <b>$Name</b>? ").replace("$Name", Name)
	else: text = _("Хотите отключить все напоминания для события <b>$Name</b>?").replace("$Name", Name)
	DeleteMessageNotification = Bot.send_message(
		Call.message.chat.id,
		text,
		reply_markup = InlineKeyboard.Confirmation("WithoutNotifications", subtype),
		parse_mode = "HTML"
		)
	SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])

	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Confirmation"))
def ProcessConfirmation(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	notification_type = Call.data.split("_")[1]
	subtype = Call.data.split("_")[2]
	EventID = User.get_property("EventID")
	Name = EventsData(User).property_event("Name", EventID)

	if notification_type == "WithoutNotifications":
		if subtype == "change": button = InlineKeyboard.SteakActions(name_button = _("Спасибо!"), delete = "MessageNotificationsChange", update = "AllReminders")
		else: button = InlineKeyboard.SteakActions(name_button = _("Спасибо!"), delete = "MessageNotificationsChange", update = "WithoutReminders")

		Data = {"ReminderFormat": "WithoutReminders", "Reminder": None, "Time": None}
		DeleteMessageNotification = Bot.send_message(
			Call.message.chat.id,
			_("Для события <b>%s</b> все напоминания отключены! 🔕\n\nНо не переживайте! День в день мы вас все равно о нём уведомим!") % Name,
			reply_markup = button,
			parse_mode = "HTML"
		)
		SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])

	if notification_type == "EveryNotifications":
		Data = {"ReminderFormat": "EveryDay", "Reminder": None, "Time": None}
		DeleteMessageNotification = Bot.send_message(
		Call.message.chat.id,
			_("Для события <b>%s</b> ежедневные напоминания включены!") % Name,
			reply_markup = InlineKeyboard.SteakActions(name_button = _("Спасибо!"), delete = "MessageNotificationsChange", update = "AllReminders"),
			parse_mode = "HTML"
		)
		SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])
		
	SetPropertyEvent(User, Data, EventID)
	
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Change_name"))
def ProcessChangeName(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	User.set_property("emoji", True)
	WaitingName = Bot.send_message(
		Call.message.chat.id,
		_("Напишите свое новое имя!"),
		reply_markup = InlineKeyboard.SteakActions(name_button =_("Спасибо, ещё не придумал)"), delete = "WaitingName")
		)
	User.set_expected_type("call")
	SaveMessageID(User, WaitingName.id, ["WaitingName", "Changename"])

	Bot.answer_callback_query(Call.id)
	
@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Steak"))
def ProcessSteakActions(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)
	User.set_expected_type(None)
	Delete = Call.data.split("_")[1]
	Update = Call.data.split("_")[2]
	Send = Call.data.split("_")[3]
	if not Send:
		Bot.delete_message(Call.message.chat.id, Call.message.id)
	if Delete: 
		DeleteMessageID(User, Call, telemaster, Delete)
	if Update:
		EventID = User.get_property("EventID")
		Name = EventsData(User).property_event("Name", EventID)
		if Update == "WithoutReminders": 
			remains = Additional.Calculator(EventsData(User).property_event("Date", EventID))
			if remains < 0: 
				skinwalker = str(Additional.Skinwalker(EventsData(User).property_event("Date", EventID)))
				remains = str(Additional.Calculator(skinwalker))
				
			days = Additional.FormatDays(remains, language = "ru")
			DeleteMessageNotification = Bot.send_message(
				chat_id = Call.message.chat.id,
				text = _("Данные сохранены!\n\nДо события <b>$Name</b> осталось $remains $days!\n\nНапоминание о нем придет только <u>день в день</u>! 🛎").replace("$Name", Name).replace("$remains", remains).replace("$days", days),
				reply_markup = InlineKeyboard.SettingsNotifications(EventID),
				parse_mode = "HTML"
			)
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])

		if Update == "OnceDay": 
			Reminder = EventsData(User).property_event("Reminder", EventID)
			Time = EventsData(User).property_event("Time", EventID)
			days = Additional.FormatDays(Time, language = "ru")

			if Reminder == "0": text = "Итак, подытожим!\n\nВаше событие: <b>$Name</b>\n\nНапоминание о нём придёт <b>в $Time день в день!</b> 🛎".replace("$Name", Name).replace("$Time", Time)
			else: text = "Итак, подытожим!\n\nВаше событие: <b>$Name</b>\n\nНапоминание о нём придёт <b>в 18:30 за $Reminder $days</b>! 🛎".replace("$Name", Name).replace("$Time", Time).replace("$Reminder", Reminder).replace("$days", days)
			DeleteMessageNotification = Bot.send_message(

				chat_id = Call.message.chat.id,
				text = text,
				reply_markup = InlineKeyboard.SettingsNotifications(EventID),
				parse_mode = "HTML"
			)
			SaveMessageID(User, DeleteMessageNotification.id, ["MessageNotificationsChange"])

		if Update == "AllReminders":
			ProcessChange_reminders(Call)
	if Send: SendMessagewithEmoji(Bot, Call, InlineKeyboard)
	Bot.answer_callback_query(Call.id)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("Emoji"))
def ProcessWithEmoji(Call: types.CallbackQuery):
	User = Manager.auth(Call.from_user)	
	Reaction = Call.data.split("_")[1]
	Type = Call.data.split("_")[2]
	if Reaction == "🤗":
		PutReaction(Bot, Call, Reaction)
		DeleteMessageID(User, Call, telemaster, "Changename")
	
	if Reaction == "❤️" and User.has_property("Oncereminders_button") and User.get_property("Oncereminders_button") != "change": PutReaction(Bot, Call, Reaction)
	if Type == "events": DeleteMessageID(User, Call, Bot, "MessagesMyEvents")

			
	Bot.answer_callback_query(Call.id)

@Bot.message_handler(content_types = ["audio", "document", "video"])
def File(Message: types.Message):
	User = Manager.auth(Message.from_user)
	AdminPanel.procedures.files(Bot, User, Message)

AdminPanel.decorators.photo(Bot, Manager)

Bot.infinity_polling()