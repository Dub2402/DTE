from Source.Modules.Timezoner import TimezonerInlineKeyboards, TimezonerDecorators
from Source.Modules.Modes.Decorators import Decorators as ModesDecorators
from Source.Core.Enums import TrashMessagesTypes, StatusWorking
from Source.Core.LoggerConfig import ConfigurateLogger
from Source.Core.ExtendedUser import ExtendedUser
from Source.Core.LaunchGuard import LaunchGuard
from Source.Modules.Eventer import EventTypes
from Source.TeleBotAdminPanel import Panel
from Source.UI.Dialogs import UserDialogs
from Source.Core.Mailer import Mailer
from Source.UI import InlineKeyboards

from dublib.TelebotUtils import TeleCache, TeleMaster, UsersManager
from dublib.Engine.Configurator import Config
from dublib.Engine.GetText import GetText
from dublib.Methods.Data import Zerotify
from dublib.Methods.System import Clear

import os

from apscheduler.schedulers.background import BackgroundScheduler
from telebot.types import ReactionTypeEmoji
from telebot import TeleBot, types
from dotenv import load_dotenv

#---> Инициализация объектов.
#==========================================================================================#

Clear()

settings = Config("Settings.json")
settings.load()
load_dotenv()

ConfigurateLogger()
LaunchGuard(settings["language"]).check_readiness()

bot = TeleBot(os.environ.get("TOKEN"))
masterbot = TeleMaster(bot)
manager = UsersManager("Data/Users")
adminpanel = Panel(bot, manager, os.environ.get("PASSWORD"))

scheduler = BackgroundScheduler()
scheduler.remove_all_jobs()
mailer = Mailer(bot, manager, scheduler, settings)
scheduler.add_job(mailer.handler_notifications, 'interval', seconds=60)
scheduler.start()

cacher = TeleCache()
cacher.set_bot(bot)
cacher.set_chat_id(int(os.environ.get("CHAT_ID")))

dialogs = UserDialogs(bot, cacher, settings["language"])

GetText.initialize("DTE", settings["language"], settings["locale_dir"])
_ = GetText.gettext

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
	user.set_property("is_male", True, force = False)
	user.set_property("emoji", False)
	user.reset_expected_type()
	user.suppress_saving(False)
	
	dialogs.start(user)  
	
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

	buttons = {
    "✏️ " + _("Новое событие"): dialogs.ask_name_event,
    "🛎 " + _("Настройка напоминаний"): dialogs.notifications_options,
    "📜 " + _("Мои события"): dialogs.my_events,
    "👄 " + _("Поделиться с друзьями"): dialogs.share_with_friends
	}

	if message.text in buttons:
		buttons[message.text](extended_user)
		return

	match user.expected_type:

		case "call":
			extended_user.remember_trash_message(message.id, TrashMessagesTypes.acquaintance)
			user.set_property("call", message.text)
			user.reset_expected_type()
			dialogs.greet_by_name(extended_user)
			dialogs.ask_gender(user)

		case "name":
			new_event = extended_user.eventer.create_event()
			new_event.set_name(message.text)
			dialogs.ask_date_event(user)
			user.set_expected_type("date")
		
		case "date":
			new_event = extended_user.eventer.temp_event

			try: new_event.set_date(message.text)
			except AttributeError: 
				dialogs.incorrect_date(user)
				return
			
			user.reset_expected_type()
			dialogs.ask_reminder_format(extended_user)
		
		case "once_reminder":

			#TO-DO: НАПОМИНАНИЕ ЗА 10 ДНЕЙ, А ОСТАЛОСЬ 5.
			#TO-DO: НАПОМИНАНИЕ БОЛЬШЕ 365 ДНЕЙ.
			#TO-DO: НАПОМИНАНИЕ С МИНУСОМ ДНЕЙ.
			working_event = extended_user.eventer.working_event

			input_reminder_data = message.text.strip().split()
			count_elements = len(input_reminder_data)

			if count_elements not in (1, 2): 
				dialogs.error_input(extended_user)
				return
			
			else: 
				try: reminder_data = working_event.check_input_reminder(input_reminder_data, count_elements)
				except AttributeError:
					dialogs.error_input(extended_user)
					return
			
			working_event.set_reminder(reminder_data)
			if working_event.is_temp: working_event.untemp()
			user.reset_expected_type()

			dialogs.save_reminder(extended_user, working_event, count_elements)

		case "daily_reminder":

			new_event = extended_user.eventer.temp_event

			input_reminder_data = message.text.strip().split()
			count_elements = len(input_reminder_data)

			if count_elements != 1: 
				dialogs.error_input(extended_user)
				return
			
			else: 
				try: reminder_data = new_event.check_input_reminder(input_reminder_data, 1)
				except AttributeError:
					dialogs.error_input(extended_user)
					return
			
			new_event.set_reminder(reminder_data)
			dialogs.save_counting_event(extended_user, new_event)
			new_event.untemp()
	
TimezonerDecorators(bot, manager)
ModesDecorators(bot, manager).inline_keyboards()

@bot.callback_query_handler(func = lambda Callback: Callback.data == "clearning")
def clearning(call: types.CallbackQuery):
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	extended_user.delete_trash_messages(bot)

	if StatusWorking.change.value == extended_user.status_working: change_reminders(call)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data == "delete")
def delete(call: types.CallbackQuery):

	manager.auth(call.from_user)
	
	bot.delete_message(call.message.chat.id, call.message.id)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("delete_"))
def delete_trash_message(call: types.CallbackQuery):
	user = manager.auth(call.from_user)

	type_trash_message = call.data.removeprefix("delete_")

	ExtendedUser(user).delete_trash_messages(bot, type_trash_message)
	
	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("gender_"))
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

@bot.callback_query_handler(func = lambda Callback: Callback.data == "create_event")
def create_event(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user) 

	dialogs.ask_name_event(extended_user, " 😉 \n\n<i>Например: День рождения</i>", button = None)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data == "count_down_event")
def counting(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	new_event = extended_user.eventer.temp_event

	new_event.switching_notifications(True)
	if new_event.is_date_passed: dialogs.ask_format_counting(extended_user)
	else: 
		new_event.set_counter_type(EventTypes.remained)
		dialogs.ask_time_daily_reminder(extended_user)
		user.set_expected_type("daily_reminder")

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("counter_"))
def save_counter_type(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	new_event = extended_user.eventer.temp_event

	counter_type = call.data.split("_")[-1]
	new_event.set_counter_type(EventTypes(counter_type))

	dialogs.ask_time_daily_reminder(extended_user)
	user.set_expected_type("daily_reminder")

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data == "one_time_reminder")
def one_time(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	if extended_user.eventer.temp_event: extended_user.eventer.temp_event.set_counter_type(EventTypes.remained)
	else: extended_user.eventer.working_event.switching_notifications(False)

	dialogs.ask_time_reminder(extended_user)
	user.set_expected_type("once_reminder")

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data == "another_day")
def another_day(call: types.CallbackQuery):
	"""Отправка сообщения для выбора дня и времени разовых напоминаний."""
	
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	dialogs.ask_day_and_time_reminder(extended_user)
	user.set_expected_type("once_reminder")
	
	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data == "fix_reminder_date")
def fix_reminder_date(call: types.CallbackQuery):
	"""Отправка сообщения при нажатии на спасибо после сохранения напоминания для события."""

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	masterbot.safely_delete_messages(call.message.chat.id, call.message.id)
	dialogs.ask_day_and_time_reminder(extended_user)
	user.set_expected_type("once_reminder")

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data == "fix_reminder")
def fix_reminder(call: types.CallbackQuery):
	"""Отправка сообщения при нажатии на изменить при сохранении новоиспечённого события."""

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	extended_user.switching_status_working(StatusWorking.hot_fix)

	dialogs.ask_reminder_format_again(extended_user)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data == "thanks")
def thanks(call: types.CallbackQuery):
	"""Отправка сообщения при нажатии на спасибо после сохранения напоминания для события."""
	
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	if extended_user.status_working == StatusWorking.change.value: 
		extended_user.delete_trash_messages(bot, TrashMessagesTypes.change_reminders.value)
		change_reminders(call)
	else: dialogs.message_with_button_emoji(extended_user)
	
	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("emoji_"))
def put_emoji(call: types.CallbackQuery):
	"""Отправка реакции на сообщение."""
	
	manager.auth(call.from_user)
	emoji = call.data.split("_")[1]

	bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup = None)
	bot.set_message_reaction(call.message.chat.id, call.message.id, [ReactionTypeEmoji(emoji)])
	
	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("without_reminders"))
def without_reminders(call: types.CallbackQuery):
	"""Подтверждение отключения всех напоминаний для события."""
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	
	dialogs.ask_change_reminders(extended_user, EventTypes.no_nofifications)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("every_day_reminder"))
def every_day_reminder(call: types.CallbackQuery):
	"""Подтверждение включения ежедневных напоминаний."""

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	
	dialogs.ask_change_reminders(extended_user, EventTypes.counting)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("random_time_daily_reminder"))
def random_time_daily_reminder(call: types.CallbackQuery):
	"""Выбор стандартного времени для рассылки."""
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	new_event = extended_user.eventer.temp_event

	dialogs.save_counting_event(extended_user, new_event)
	new_event.untemp()

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("confirm_"))
def confirm(call: types.CallbackQuery):
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	type_reminders = call.data.split("_")[1] + "_" + call.data.split("_")[2]
	working_event = extended_user.eventer.working_event

	if type_reminders == EventTypes.no_nofifications.value: 
		dialogs.turn_off_reminders(extended_user)
		working_event.switching_notifications(False)
		working_event.set_reminder(None)

	if type_reminders == EventTypes.counting.value: 

		dialogs.turn_on_every_day_reminders(extended_user)
		working_event.switching_notifications(True)
		working_event.set_reminder(None)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("remove_event_"))
def remove_event(call: types.CallbackQuery):
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	extended_user.eventer.remove_event(int(call.data.split("_")[-1]))
	dialogs.my_events(extended_user, True)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data == "disable_reminders")
def disable_reminders(call: types.CallbackQuery):
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	if not extended_user.eventer.events: 
		dialogs.no_events(extended_user, TrashMessagesTypes.disable_reminders)
		return

	if extended_user.eventer.events_with_reminders: 
		dialogs.your_reminders(extended_user)

	else: dialogs.not_events_with_reminders(extended_user)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("disable_reminder_"))
def disable_reminder(call: types.CallbackQuery):
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	extended_user.switching_working_event_id(int(call.data.split("_")[-1]))

	working_event = extended_user.eventer.working_event
	working_event.switching_notifications(False)
	working_event.set_reminder(None)
	
	bot.delete_message(call.message.chat.id, call.message.id)

	extended_user.delete_trash_messages(bot, TrashMessagesTypes.disable_reminders.value)

	disable_reminders(call)

	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data == "change_reminders")
def change_reminders(call: types.CallbackQuery):

	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	eventer = extended_user.eventer

	if eventer.events: dialogs.your_events(extended_user)
	else: dialogs.no_events(extended_user, TrashMessagesTypes.change_reminders)

	dialogs.exit_with_delete(extended_user, TrashMessagesTypes.change_reminders)
		
	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("change_reminder_"))
def change_reminder(call: types.CallbackQuery):
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)
	extended_user.switching_working_event_id(int(call.data.split("_")[-1]))
	extended_user.switching_status_working(StatusWorking.change)

	dialogs.choice_reminder(extended_user)
	
	bot.answer_callback_query(call.id)

@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("standart_time_every_reminders"))
def standart_time_every_reminders(call: types.CallbackQuery):
	user = manager.auth(call.from_user)
	extended_user = ExtendedUser(user)

	# extended_user.switching_working_event_id(int(call.data.split("_")[-1]))
	# extended_user.switching_status_working(StatusWorking.change)

	# dialogs.choice_reminder(extended_user)
	
	bot.answer_callback_query(call.id)

bot.infinity_polling()				