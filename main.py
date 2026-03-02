from Source.Modules.Timezoner import TimezonerInlineKeyboards, TimezonerDecorators
from Source.Core.ExtendedUser import ExtendedUser
from Source.Core.Enums import TrashMessagesTypes
from Source.Modules.Eventer import EventTypes
from Source.TeleBotAdminPanel import Panel
from Source.UI.Dialogs import UserDialogs
from Source.UI import InlineKeyboards
from Source.Core import MediaChecker

from dublib.TelebotUtils import TeleCache, TeleMaster, UsersManager
from dublib.Engine.Configurator import Config
from dublib.Engine.GetText import GetText
from dublib.Methods.Data import Zerotify

import logging
import os

from telebot import TeleBot, types
from dotenv import load_dotenv

#---> Инициализация объектов.
#==========================================================================================#

settings = Config("Settings.json")
settings.load()
load_dotenv()
if not os.environ.get("DTE_LANG"): os.environ["DTE_LANG"] = "ru"

MediaChecker.check_media()

bot = TeleBot(settings["token"])
masterbot = TeleMaster(bot)
manager = UsersManager("Data/Users")
dialogs = UserDialogs(bot)
adminpanel = Panel(bot, manager, settings["password"])

cacher = TeleCache()
cacher.set_bot(bot)
cacher.set_chat_id(settings["chat_id"])

GetText.initialize("DTE", settings["language"], "locales")
_ = GetText.gettext

#---> Настройка логгирования.
#==========================================================================================#

logging.basicConfig(
	level = logging.INFO,
	encoding = "utf-8",
	filename = "LOGING.log",
	filemode = "w",
	format = '%(asctime)s - %(levelname)s - %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S'
)
logging.getLogger("pyTelegramBotAPI").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

#---> Взаимодействие с ботом.
#==========================================================================================#

@bot.message_handler(commands = ["start"])
def start(message: types.Message):

	is_new_user = not manager.is_user_exists(message.from_user.id)
	user = manager.auth(user = message.from_user) 

	user.suppress_saving(True)

	if is_new_user:
		user.set_property("mode", "classic")
		user.set_property("is_mode_choice", False)
		user.set_property("create_reminder", True)
		user.set_property("change_reminder_after_saving_mode_bot", True)

	user.set_property("events", {}, force = False)
	user.set_property("is_male", True)
	user.set_property("emoji", False)
	user.reset_expected_type()
	user.suppress_saving(False)
	
	dialogs.start(user, cacher)  
	
	if user.has_property("call"): dialogs.greeting(user)
		
	else:
		dialogs.ask_name(user)
		user.set_expected_type("call")

@bot.message_handler(commands = ["admin"])
def admin(message: types.Message):

	user = manager.auth(message.from_user)
	
	password = message.text.split(" ")[1:]
	password = " ".join(password).strip()

	if not adminpanel.login(user, Zerotify(password)):
		bot.send_message(user.id, "Доступ запрещён.")

	else:
		keyboard = adminpanel.open(user)
		bot.send_message(user.id, "Панель управления открыта.", reply_markup = keyboard)

@bot.message_handler(commands = ["infa"])
def infa(message: types.Message):

	user = manager.auth(message.from_user)

	Text = (
		"@Dnido_bot " + _("предназначен для запоминания событий, отслеживания дней, а также установки различных напоминаний!\n"),
		_("<b>Здесь вы можете:</b>\n- Отсчитывать дни ДО события"),
		_("- Отсчитывать дни ПОСЛЕ события"),
		_("- Ставить напоминания о событии день в день в определенное время"),
		_("- Ставить напоминание о событии день в день без определенного времени (по умолчанию в 7 утра)"),
		_("- Ставить напоминание о событии за несколько дней до события в определенное время\n"),
		_("На каждое событие вы можете изменить тип напоминания в любой момент)\n"),
		"<b><i>" + _("Пользуйтесь, и не забывайте делиться с друзьями!") + "</i></b>"
	)

	bot.send_message(user.id, "\n".join(Text), "HTML", reply_markup = InlineKeyboards.delete(_("Ясненько")))

@bot.message_handler(content_types = ["text"])
def text(message: types.Message):

	user = manager.auth(message.from_user)
	extended_user = ExtendedUser(user)

	if adminpanel.procedures.text(message): return

	match user.expected_type:

		case "call":
			extended_user.remember_trash_message(message.id, TrashMessagesTypes.greeting)
			user.set_property("call", message.text)
			user.reset_expected_type()
			dialogs.greet_by_name(extended_user)
			dialogs.ask_gender(user)

		case "name":
			temporary_event = extended_user.eventer.temp_event
			if temporary_event:  extended_user.eventer.remove_event(temporary_event.id)
			new_event = extended_user.eventer.create_event()
			new_event.set_name(message.text)
			dialogs.ask_date_event(user)
			user.set_expected_type("date")
		
		case "date":
			new_event = extended_user.eventer.temp_event

			try: new_event.set_date(message.text)
			except ValueError: 
				dialogs.incorrect_date(user)
				return
			
			user.reset_expected_type()
			dialogs.ask_reminder_format(extended_user)
		
		case "reminder":
			pass
	
		case _:
			if len(message.text) > 2:
				{
					"✏️ " + _("Новое событие"): dialogs.ask_name_event, 
					"🛎 " + _("Настройка напоминаний"): dialogs.notifications_options, 
					"📜 " + _("Мои события"): dialogs.my_events
				}[message.text](extended_user)
	
TimezonerDecorators(bot, manager, InlineKeyboards)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("gender"))
def gender(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	user.set_property("is_male", bool(int(call.data.split("_")[-1])))

	if user.get_property("emoji"): dialogs.gendered_thanks(user)

	else:
		bot.delete_message(call.message.chat.id, call.message.id)
		user.set_expected_type("timezone")		
		bot.send_message(
			chat_id = call.message.chat.id,
			text = _("Спасибо большое!\n\nА теперь нам нужен ваш часовой пояс. Сколько сейчас времени у вас на телефоне? 🕐"),
			parse_mode = "HTML",
			reply_markup = TimezonerInlineKeyboards().timezone_first_page()
		)
	
	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("create_event"))
def create_event(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	extendeed_user = ExtendedUser(user) 
	dialogs.ask_name_event(extendeed_user, " 😉 \n\n<i>Например: День рождения</i>", button = None)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("count_down_event"))
def counting(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	new_event = extended_user.eventer.temp_event

	new_event.switching_notifications(True)
	if new_event.is_date_passed: dialogs.ask_format_counting(extended_user)
	else: 
		new_event.set_counter_type(EventTypes.remained)
		dialogs.save_counting_event(extended_user, new_event)
		new_event.untemp()

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("counter_"))
def save_counter_type(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	new_event = extended_user.eventer.temp_event

	counter_type = call.data.split("_")[-1]
	new_event.set_counter_type(EventTypes(counter_type))
	dialogs.save_counting_event(extended_user, new_event)
	new_event.untemp()

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("one_time_reminder"))
def one_time(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	dialogs.ask_time_reminder(extended_user)
	user.set_expected_type("reminder_data")

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("another_day"))
def InlineButtonAnotherDay(Call: types.CallbackQuery):
	"""Отправка сообщения для выбора дня и времени разовых напоминаний."""
	
	user = manager.auth(Call.from_user)
	extended_user = ExtendedUser(user)

	dialogs.ask_day_and_time_reminder(extended_user)
	user.set_expected_type("reminder_data")
	
	bot.answer_callback_query(Call.id)

bot.infinity_polling()