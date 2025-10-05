from Source.UI.InlineKeyboards import InlineKeyboard

from dublib.TelebotUtils.Users import UsersManager, UserData
from dublib.Engine.GetText import _

from datetime import datetime, timedelta, timezone

from telebot import TeleBot, types

#==========================================================================================#
# >>>>> ФУНКЦИИ <<<<< #
#==========================================================================================#

def CorrectUserTime(user_time: str, delta: int) -> datetime:
	"""
	Корректирует время пользователя в UTC0.

	:param user_time: Заданное пользователем время в формате **%H:%M**.
	:type user_time: str
	:param delta: Целочисленная разница в часах между часовыми поясами.
	:type delta: int
	:return: Скорректированное время в формате **%H:%M**.
	:rtype: datetime
	"""
	UserHour, UserMinute = user_time.split(":")
	UserHour = int(UserHour)
	Today = datetime.now(timezone.utc) + timedelta(hours = delta)
	Today = Today.date()

	UserTime = datetime.combine(Today, datetime.strptime(f"{UserHour}:{UserMinute}:00", "%H:%M:%S").time())
	Delta = timedelta(hours = delta)
	CorrectedTime = UserTime - Delta

	return CorrectedTime.replace(tzinfo=timezone.utc)

def Replacing_timezone(User: UserData) -> int:
	if User.has_property("timezone"): Delta = User.get_property("timezone")
	else: Delta = 3

	return Delta

#==========================================================================================#
# >>>>> НАБОРЫ ДЕКОРАТОРОВ <<<<< #
#==========================================================================================#

def TimezonerDecorators(bot: TeleBot, users: UsersManager, inline_keyboard: InlineKeyboard):
	"""
	Набор декораторов для обработки выбора часового пояса.

	:param bot: Бот Telegram.
	:type bot: TeleBot
	:param users: Менеджер пользователей.
	:type users: UsersManager
	"""

	@bot.callback_query_handler(func = lambda Callback: Callback.data == "tz_more")
	def TimezonesMore(Call: types.CallbackQuery):
		users.auth(Call.from_user)
		bot.edit_message_reply_markup(
			chat_id = Call.message.chat.id,
			message_id = Call.message.id,
			reply_markup = TimezonerInlineKeyboards().timezone_second_page()
		)

		bot.answer_callback_query(Call.id)

	@bot.callback_query_handler(func = lambda Callback: Callback.data == "tz_back")
	def TimezonesBack(Call: types.CallbackQuery):
		users.auth(Call.from_user)
		bot.edit_message_reply_markup(
			chat_id = Call.message.chat.id,
			message_id = Call.message.id,
			reply_markup = TimezonerInlineKeyboards().timezone_first_page()
		)

		bot.answer_callback_query(Call.id)

	@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("tz_select"))
	def TimezoneSelect(Call: types.CallbackQuery):
		User = users.auth(Call.from_user)
		bot.delete_message(Call.message.chat.id, Call.message.id)
		TimezoneCode = int(Call.data[len("tz_select_"):].replace("m", "-"))
		User.set_property("timezone", TimezoneCode)

		bot.send_message(
			chat_id = Call.message.chat.id,
			text = _("Отлично! Вот и настроили!\n\nПришла пора создать ваше первое событие! 🙌"), 
			reply_markup = inline_keyboard.AddNewEvent(),
			parse_mode = "HTML"
			)
		
		bot.answer_callback_query(Call.id)
	
	@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("tz_change"))
	def TimezoneChange(Call: types.CallbackQuery):
		User = users.auth(Call.from_user)

		bot.send_message(
			chat_id = Call.message.chat.id,
			text = _("Выберите, пожалуйста, ваш новый часовой пояс:"), 
			reply_markup = TimezonerInlineKeyboards().timezone_first_page(),
			parse_mode = "HTML"
			)
		
		bot.send_message(
			chat_id = Call.message.chat.id,
			text = _("<b>" + _("Для выхода") + "</b>" + _("в предыдущее меню нажмите \"Назад\":")), 
			reply_markup = inline_keyboard.SteakActions(name_button = _("🔙 Назад"), delete = "MessageNotificationsDeactivate"),
			parse_mode = "HTML"
			)
		
		bot.answer_callback_query(Call.id)

#==========================================================================================#
# >>>>> ШАБЛОНЫ <<<<< #
#==========================================================================================#

class TimezonerInlineKeyboards:
	"""Коллекция генераторов Inline-интерфейса."""

	def __init__(self):
		"""Коллекция генераторов Inline-интерфейса."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__MainTimezones = {
			1: _("Берлин"),
			7: _("Бангкок"),
			2: _("Киев"),
			8: _("Пекин"),
			3: _("Москва"),
			9: _("Токио"),
			4: _("Дубай"),
			10: _("Сидней"),
			5: _("Ташкент"),
			11: _("Солом. о-ва"),
			6: _("Дакка"),
			12: _("Окленд")
		}
		self.__SecondaryTimezones = {
			-12: _("Бейкер"),
			-6: _("Мехико"),
			-11: _("Паго-Паго"),
			-5: _("Нью-Йорк"),
			-10: _("Гонолулу"),
			-4: _("Каракас"),
			-9: _("Анкоридж"),
			-3: _("Буэнос-Айрес"),
			-8: _("Лос-Анджелес"),
			-2: _("Южная Георгия"),
			-7: _("Денвер"),
			-1: _("Азорские о-ва"),
		}

	def timezone_first_page(self) -> types.InlineKeyboardMarkup:
		"""Строит Reply-интерфейс: выбор часового пояса (страница 1)."""

		Menu = types.InlineKeyboardMarkup(row_width = 3)
		TimezoneButtons = list()
		UTC_Now = datetime.now(timezone.utc)
		
		for Timezone, City in self.__MainTimezones.items():
			TimezoneCode = str(Timezone)
			RegionalTime = UTC_Now + timedelta(hours = Timezone)
			RegionalTime = RegionalTime.strftime("%H:%M")
			if TimezoneCode.startswith("-"): TimezoneCode = "m" + TimezoneCode.lstrip("-")
			TimezoneButtons.append(types.InlineKeyboardButton(f"{City} [{RegionalTime}]", callback_data = f"tz_select_{TimezoneCode}"))

		Menu.add(*TimezoneButtons, row_width = 2)
		Menu.add(types.InlineKeyboardButton(_("Ещё ▶️"), callback_data = "tz_more"))

		return Menu
	
	def timezone_second_page(self) -> types.InlineKeyboardMarkup:
		"""Строит Reply-интерфейс: выбор часового пояса (страница 2)."""

		Menu = types.InlineKeyboardMarkup(row_width = 3)
		TimezoneButtons = list()
		UTC_Now = datetime.now(timezone.utc)
		
		for Timezone, City in self.__SecondaryTimezones.items():
			TimezoneCode = str(Timezone)
			RegionalTime = UTC_Now + timedelta(hours = Timezone)
			RegionalTime = RegionalTime.strftime("%H:%M")
			if TimezoneCode.startswith("-"): TimezoneCode = "m" + TimezoneCode.lstrip("-")
			TimezoneButtons.append(types.InlineKeyboardButton(f"{City} [{RegionalTime}]", callback_data = f"tz_select_{TimezoneCode}"))

		Menu.add(*TimezoneButtons, row_width = 2)
		UTC_Now = UTC_Now.strftime("%H:%M")
		Menu.add(types.InlineKeyboardButton(_("Гринвич") + f" [{UTC_Now}]", callback_data = "tz_select_0"))
		Menu.add(types.InlineKeyboardButton(_("◀️ Назад"), callback_data = "tz_back"))

		return Menu