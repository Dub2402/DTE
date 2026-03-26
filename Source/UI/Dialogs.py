from Source.Modules.Eventer import InlineKeyboards as EventsInlineKeyboards, EventTypes, Event
from Source.Core.Enums import TrashMessagesTypes, MediaPath, BotModes
from Source.Modules.Timezoner import TimezonerInlineKeyboards
from Source.Core.ExtendedUser import ExtendedUser
from Source.UI import InlineKeyboards
from Source.UI import ReplyKeyboard

from dublib.TelebotUtils import TeleCache, UserData
from dublib.Engine.GetText import _

from time import sleep
import random
import os

import telebot

class UserDialogs:

	def __init__(self, bot: telebot.TeleBot, cacher: TeleCache):
		self.__bot = bot
		self.__cacher = cacher

	def info(self, user: UserData):
		"""
		Отправляет текст информации о боте.
		
		:param user: Пользователь и его данные.
		:type user: UserData
		"""

		Text = (_("@Dnido_bot предназначен для запоминания событий, отслеживания дней, а также установки различных напоминаний!\n"),
			_("<b>Здесь вы можете:</b>\n- Отсчитывать дни ДО события"),
			_("- Отсчитывать дни ПОСЛЕ события"),
			_("- Ставить напоминания о событии день в день в определенное время"),
			_("- Ставить напоминание о событии день в день без определенного времени (по умолчанию в 7 утра)"),
			_("- Ставить напоминание о событии за несколько дней до события в определенное время\n"),
			_("На каждое событие вы можете изменить тип напоминания в любой момент)\n"),
			_("<b><i>Пользуйтесь, и не забывайте делиться с друзьями!</i></b>")
		)

		self.__bot.send_message(
			chat_id = user.id,
			text = "\n".join(Text),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.delete(text = _("Ясненько"))
		)

	def start(self, user: UserData):
		"""
		Отправка текстового сообщения с изображением, или без него.
		
		:param user: Пользователь и его данные.
		:type user: UserData
		"""

		text = _("<b>ДОБРО ПОЖАЛОВАТЬ!</b>\n\nЯ бот, помогающий запоминать события и узнавать, сколько дней до них осталось.")
		
		self.__bot.send_photo(
			chat_id = user.id, 
			photo = self.__cacher.get_real_cached_file(MediaPath.start.value, autoupload_type = telebot.types.InputMediaPhoto).file_id,
			caption = text,
			parse_mode = "HTML"
		)

	def greeting(self, user: UserData) -> str:
		"""
		Возвращает приветственное сообщение в зависимости от режима бота.

		:param user: Данные пользователя.
		:type user: UserData
		:return: Текст сообщения.
		:rtype: str
		"""

		extended_user = ExtendedUser(user)

		messages = {
			BotModes.classic: (None, ", мы рады тебя видеть снова! 🤗"),
			BotModes.sweetie: (None, ", солнышко моё! Рад, что ты тут! Я скучал 💕"),
			BotModes.buddy: {
				True: (None, ", братишка! Красссавчик, что вернулся! Рад тебя видеть! 🔥"),
				False: ("Оуу,", ", девочка моя!) Ты опять тут!? Как я рад тебя видеть! 🔥")
			},
			BotModes.motivator: ("Какие люди!", ", ты ли?) Ну наконец-то, наш лидер вернулся! 🏆"),
			BotModes.gaslighter: (None, " г#вно еб#ное! Ты че тут опять трешься?) А ну сваливай нах#й!"),
		}

		bot_mode = extended_user.bot_mode
		if bot_mode == BotModes.random: bot_mode = random.choice(tuple(Value for Value in BotModes))

		used_strings = messages[bot_mode]
		if type(used_strings) == dict: used_strings = used_strings[extended_user.is_male]

		message = ""
		if used_strings[0]: message += used_strings[0] + " "
		message += extended_user.call
		message += used_strings[1]

		self.__bot.send_message(user.id, message, reply_markup = ReplyKeyboard.menu())

	def ask_name(self, user: UserData):
		"""
		Отправка текстового сообщения c просьбой написать имя пользователя.

		:param user: Пользователь и его данные.
		:type user: UserData
		"""

		self.__bot.send_message(user.id, _("Давайте познакомимся!\nНапишите свое имя! 🤗"))

	def greet_by_name(self, extended_user: ExtendedUser):
		"""
		Приветственное сообщение, после того, как узнали как обращаться к пользователю и сохраняем его.

		:param user: Расширенные данные пользователя.
		:type user: ExtendedUser
		"""

		text: str  = _("Приятно познакомиться, $call!")

		name_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = text.replace("$call", extended_user.call),
			reply_markup = ReplyKeyboard.menu()
		)
		
		extended_user.remember_trash_message(name_message.id, TrashMessagesTypes.acquaintance)
		
		return
	
	def ask_gender(self, user: UserData):
		"""
		Cообщение, после того, как узнали как обращаться к пользователю и сохраняем его. 

		:param user: Пользователь и его данные.
		:type user: UserData
		"""

		gender_message = self.__bot.send_message(
			chat_id = user.id,
			text = _("Укажите, пожалуйста, ваш пол. Это для лучшей адаптации бота под вас:"),
			reply_markup = InlineKeyboards.choice_gender()
		)
		
		ExtendedUser(user).remember_trash_message(gender_message.id, TrashMessagesTypes.acquaintance)

	def gendered_thanks(self, user: UserData):
		"""
		Отправляет сообщение после того как пользователь выбрал пол и сохраняем его.
		
		:param user: Пользователь и его данные.
		:type user: UserData
		"""

		extended_user = ExtendedUser(user)

		gender_text = _("Наш мужчина") if user.get_property("is_male") else _("Наша женщина")
		text: str = _("Спасибо большое! $gender_text, $name!)")
	
		gender_message = self.__bot.send_message(
			chat_id = user.id,
			text = text.replace("$gender_text", gender_text).replace("$name", extended_user.call),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.emoji("🤗")
		)

		extended_user.remember_trash_message(gender_message.id, TrashMessagesTypes.acquaintance)

	def ask_timezone(self, user: UserData):
		"""
		Отправляет сообщение для того, чтобы выбрать часовой пояс.

		:param user: Пользователь и его данные.
		:type user: UserData
		"""

		self.__bot.send_message(
			chat_id = user.id,
			text = _("Спасибо большое!\n\nА теперь нам нужен ваш часовой пояс. Сколько сейчас времени у вас на телефоне? 🕐"),
			parse_mode = "HTML",
			reply_markup = TimezonerInlineKeyboards().timezone_first_page()
		)

	def ask_name_event(self, extended_user: ExtendedUser, additional_text: str = "", button: InlineKeyboards = InlineKeyboards.delete(_("Cпасибо, чуть позже!"))):
		"""
		Запускает процедуру создания события.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		extended_user.user.set_expected_type("name")

		text = _("Введите, пожалуйста, название события, которое вы так ждёте!")

		new_event = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = text + additional_text,
			parse_mode = "HTML",
			reply_markup = button
		)

		extended_user.remember_trash_message(new_event.id, TrashMessagesTypes.events)

	def ask_date_event(self, user: UserData):
		"""
		Отправляет сообщение о том, что необходимо написать имя события.

		:param user: Пользователь и его данные.
		:type user: UserData
		"""

		self.__bot.send_message(
			chat_id = user.id,
			text = _("А теперь мне нужна дата вашего события 🤔 \n\n<i>Пример: 01.01.2000</i>"), 
			parse_mode = "HTML"
		)

	def incorrect_date(self, user: UserData):
		"""
		Отправляет сообщение о том, что дата введена неверно.

		:param user: Пользователь и его данные.
		:type user: UserData
		"""

		self.__bot.send_message(user.id, _("Вы ввели не соответствующую формату дату. Повторите попытку."))

	def ask_reminder_format(self, extended_user: ExtendedUser):
		"""
		Отправляет сообщение о том, что необходимо выбрать режим напоминаний.

		:param user: Расширенные данные пользователя.
		:type user: ExtendedUser
		"""

		text = _("Супер! Хотите получить разовое напоминание или отсчитывать дни?)") 

		if extended_user.user.has_property("create_reminder"): text = text + "\n\n<b>Совет:</b> <i>Для своего ДР часто выбирают отсчитывать дни, а вот для ДР других - разовые напоминания 🤭</i>"

		reminder_format_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = text,
			reply_markup = EventsInlineKeyboards.format_reminder("without_reminders"),
			parse_mode = "HTML"
		)

		extended_user.user.remove_property("create_reminder")

		extended_user.remember_trash_message(reminder_format_message.id, TrashMessagesTypes.events)

	def ask_reminder_format_again(self, extended_user: ExtendedUser):
		"""
		Отправляет сообщение о том, что необходимо выбрать режим напоминаний.

		:param user: Расширенные данные пользователя.
		:type user: ExtendedUser
		"""

		reminder_format_again_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = _("Выберите тип напоминания:") ,
			reply_markup = EventsInlineKeyboards.format_reminder("without_counting"),
			parse_mode = "HTML"
		)

		extended_user.remember_trash_message(reminder_format_again_message.id, TrashMessagesTypes.events)	

	def ask_time_reminder(self, extended_user: ExtendedUser):
		"""
		Отправляет сообщение о необходимости выбрать время для напоминаний.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		time_reminder_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = _("В день события мы вам пришлём напоминание! 🛎 \n\nВ какое время вы бы хотели получить его?\n\n<i>Пример: 18:30</i>"),
			reply_markup = EventsInlineKeyboards.choice_another_day(),
			parse_mode = "HTML"
			)
		
		extended_user.remember_trash_message(time_reminder_message.id, TrashMessagesTypes.events)

	def ask_day_and_time_reminder(self, extended_user: ExtendedUser):
		"""
		Отправляет сообщение о необходимости выбрать время и дату для напоминаний.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		working_event = extended_user.eventer.working_event
	
		day_and_time_reminder_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = _("Укажите, за сколько дней и в какое время вам напомнить о событии <b>$name</b>? 🔊\n\n<i>Пример: 10 18:30 (означает за 10 дней и в 18:30)</i>").replace("$name", working_event.name),
			parse_mode = "HTML"
			)

		extended_user.remember_trash_message(day_and_time_reminder_message.id, TrashMessagesTypes.events)

	def error_input(self, extended_user: ExtendedUser):
		"""
		Отправляет сообщение о неверном вводе.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		input_error_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = _("Я не совсем понял, что вы от меня хотите. Повторите попытку.")
		)
		
		extended_user.remember_trash_message(input_error_message.id, TrashMessagesTypes.events)

	def ask_format_counting(self, extended_user: ExtendedUser):
		"""
		Отправляет сообщение о том, что необходимо выбрать формат отслеживания события.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		format_counting_message = self.__bot.send_message(
			extended_user.user.id,
			text = _("Укажите, какой формат отсчёта вам показывать?"),
			reply_markup = EventsInlineKeyboards.counter_type()
		)
		
		extended_user.remember_trash_message(format_counting_message.id, TrashMessagesTypes.events)

	def my_events(self, extended_user: ExtendedUser, remove_events: bool = False):
		"""
		Отправляет приветственное сообщение и сообщения со всеми событиями.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		if remove_events: extended_user.delete_trash_messages(self.__bot, TrashMessagesTypes.events.value)

		eventer = extended_user.eventer

		if not eventer.events:
			self.__bot.send_message(
				chat_id = extended_user.user.id, 
				text = _("Вы не создали ни одного события 🙄\nНужно это дело исправить!)"),
				parse_mode = "HTML", 
				reply_markup = EventsInlineKeyboards.add_new_event()
			)
			return

		number_event = 1
		text: str = _("Приветствую, $call!")
		name_message = self.__bot.send_message(
			chat_id = extended_user.user.id, 
			text = text.replace("$call", extended_user.call), 
			parse_mode = "HTML"
		)

		extended_user.remember_trash_message(name_message.id, TrashMessagesTypes.events)

		for event in eventer.events:

			difference = event.calculate_date_difference()
			
			if difference == 0: self.my_event(extended_user, EventTypes.today, number_event, event.id, difference)

			else: self.my_event(extended_user, event.counter_type, number_event, event.id, difference)
				
			number_event += 1 		
			sleep(0.1)

		end_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = _("Хорошего вам дня!)"),
			reply_markup = InlineKeyboards.emoji("❤️")
		)
		extended_user.remember_trash_message(end_message.id, TrashMessagesTypes.events)

	def my_event(self, extended_user: ExtendedUser, event_type: EventTypes, number_event: int, event_id: int, difference: int):
		"""
		Отправка сообщений события.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		:param event_type: Тип события.
		:type event_type: EventTypes
		:param number_event: Порядковый номер события.
		:type number_event: int
		:param event_id: ID события.
		:type event_id: int
		:param difference: Количество дней между событиями.
		:type difference: int
		"""

		event = extended_user.eventer[event_id]
		
		texts = {
			EventTypes.today: "$number_event) " + _("Ваше событие <b>$name</b> сегодня."),
			EventTypes.remained: "$number_event) " + _("<b>$name</b> наступит через $remains $days!"),
			EventTypes.passed: "$number_event) " + _("Событие <b>$name</b> было $remains $days назад!")
		}

		replaces = {
			"$name": event.name,
			"$remains": str(difference),
			"$days": event.formating_word_day(difference),
			"$number_event": str(number_event)
		}

		final_text: str = texts[event_type]

		for start_replace in replaces.keys(): final_text = final_text.replace(start_replace, replaces[start_replace])
		
		event_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = final_text,
			parse_mode = "HTML",
			reply_markup = EventsInlineKeyboards.remove_event(event_id)
		)
			
		extended_user.remember_trash_message(event_message.id, TrashMessagesTypes.events)

	def save_counting_event(self, extended_user: ExtendedUser, event: Event):
		"""
		Отправка сообщения о том, что сообщение сохранено.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		:param event: Событие.
		:type event: Event
		"""	

		texts = {
			EventTypes.today: _("Ваше событие $name сегодня!!! 😊"),
			EventTypes.remained: _("До события <b>$name</b> осталось $remains $days!\n\nБудем ждать его вместе с <u>ежедневными напоминаниями!</u> 🛎"),
			EventTypes.passed: _("Ваше событие <b>$name</b> произошло $remains $days назад!")
		}

		difference = event.calculate_date_difference()

		event_type = EventTypes.today if difference == 0 else event.counter_type
		final_text: str = _("Данные сохранены!\n\n") + texts[event_type]

		replaces = {
			"$name": event.name,
			"$remains": str(abs(difference)),
			"$days": event.formating_word_day(difference)
		}
		for start_replace in replaces.keys(): final_text = final_text.replace(start_replace, replaces[start_replace])

		event_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = final_text,
			parse_mode = "HTML",
			reply_markup = EventsInlineKeyboards.change_reminder_after_saving_event(extended_user, event.id)
		)

		extended_user.remember_trash_message(event_message.id, TrashMessagesTypes.events)
	
	def save_reminder(self, extended_user: ExtendedUser, event: Event, count_elements: int):
		"""
		Сохраняет событие с одноразовым напоминанием.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		:param event: Событие.
		:type event: Event
		:param count_elements: Количество элементов, описывающих напоминание.
		:type count_elements: int
		"""

		days_before_event = event.reminder.days_before_event

		reminder_data = _("в <b>$time день в день!</b>") if event.reminder.days_before_event == 0 else _("в <b>$time</b> за <b>$days_before_event $days</b>!")
		final_text: str = _("✅ Данные сохранены!\n\nМы вам напомним о событии <b>$name</b> ") + reminder_data

		replaces = {
			"$name": event.name,
			"$time": event.reminder.time.to_string(),
			"$days_before_event": str(days_before_event), 
			"$days": event.formating_word_day(days_before_event)
		}
		for start_replace in replaces.keys(): final_text = final_text.replace(start_replace, replaces[start_replace])

		event_message = self.__bot.send_message(
			chat_id = extended_user.user.id,
			text = final_text,
			parse_mode = "HTML",
			reply_markup = EventsInlineKeyboards.saving_reminder(count_elements)
		)

		extended_user.remember_trash_message(event_message.id, TrashMessagesTypes.events)

	def message_with_button_emoji(self, extended_user: ExtendedUser):
		"""
		Отправка сообщения с кнопкой эмодзи.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		self.__bot.send_message(
			extended_user.user.id,
			_("И вам спасибо!\nХорошего дня! ))"),
			reply_markup = InlineKeyboards.emoji("❤️")
		)

	def ask_turn_off_reminders(self, extended_user: ExtendedUser):
		"""
		Отправляет сообщение с уточнением, нужно ли отключать все уведомления.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		name = extended_user.eventer.working_event.name
		text: str = _("Хотите отключить все напоминания для события <b>$name</b>?")
		
		ask_turn_off_reminders_message = self.__bot.send_message(
			extended_user.user.id,
			text.replace("$name", name),
			reply_markup = EventsInlineKeyboards.confirm_reminder("without_reminders"),
			parse_mode = "HTML"
		)

		extended_user.remember_trash_message(ask_turn_off_reminders_message.id, TrashMessagesTypes.events)

	def turn_off_reminders(self, extended_user: ExtendedUser):
		"""
		Отправляет сообщение о том, что выключены все уведомления.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		name = extended_user.eventer.working_event.name
		text: str = _("Для события <b>$name</b> все напоминания отключены! 🔕\n\nНо не переживайте! День в день мы вас все равно о нём уведомим!")
		
		turn_off_reminders_message = self.__bot.send_message(
			extended_user.user.id,
			text.replace("$name", name),
			reply_markup = InlineKeyboards.delete(_("Спасибо!")),
			parse_mode = "HTML"
		)

		extended_user.remember_trash_message(turn_off_reminders_message.id, TrashMessagesTypes.events)

	def notifications_options(self, extended_user: ExtendedUser):
		"""
		Отправляет настройки напоминаний.

		:param extended_user: Расширенные данные пользователя.
		:type extended_user: ExtendedUser
		"""

		settings_notifications = self.__bot.send_message(extended_user.user.id, _("Выберите пункт, который вы хотите настроить:"), reply_markup = InlineKeyboards.settingsmenu())
		extended_user.remember_trash_message(settings_notifications.id, TrashMessagesTypes.events)

	def share_with_friends(self, extended_user: ExtendedUser):
		"""
		Отправляет сообщение поделиться с друззьями.

		:param user: Расширенные данные пользователя.
		:type user: ExtendedUser
		"""

		path = MediaPath.qr_code_ru if os.environ["DTE_LANG"]  == "ru" else MediaPath.qr_code_en

		self.__bot.send_photo(
			chat_id = extended_user.user.id,  
			photo = self.__cacher.get_real_cached_file(path.value, autoupload_type = telebot.types.InputMediaPhoto).file_id,
			caption = _("@Dnido_bot\n@Dnido_bot\n@Dnido_bot\n\nПросто <b>Т-т-топовый</b> бот для отсчёта дней до событий 🥳\n\n<b><i>Пользуйся и делись с друзьями!</i></b>"), 
			reply_markup = InlineKeyboards.add_share(),
			parse_mode = "HTML" 
			)