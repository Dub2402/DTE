from dublib.Engine.GetText import _

from telebot import types

def settingsmenu() -> types.InlineKeyboardMarkup:
	"""Меню настройки уведомлений."""

	menu = types.InlineKeyboardMarkup()

	determinations = {
		_("🔕 Отключить напоминания"): "disable_reminders",
		_("🔔 Изменить напоминания"): "change_reminders",
		_("🕰 Время ежедн. напоминаний"): "time_every_reminders",
		_("🤭 Режим бота"): "bot_mode",
		_("🔁 Сменить имя и пол"): "change_name",
		_("🌐 Сменить часовой пояс"): "tz_change",
		_("🔙 Назад"): "steak_messageSettings__",
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]))
	return menu

def delete(text: str, callback_data: str = "delete") -> types.InlineKeyboardMarkup:
	"""
	Кнопка удаления сообщения.

	:param text: Подпись кнопки удаления.
	:type text: str
	"""

	menu = types.InlineKeyboardMarkup()
	menu.add(types.InlineKeyboardButton(text, callback_data = callback_data))

	return menu

def clearning(text: str) -> types.InlineKeyboardMarkup:
	"""
	Кнопка удаления нескольких сообщений.

	:param text: Подпись кнопки удаления.
	:type text: str
	"""

	menu = types.InlineKeyboardMarkup()
	menu.add(types.InlineKeyboardButton(text, callback_data = "clearning")) 

	return menu

def choice_gender() -> types.InlineKeyboardMarkup:
	"""Кнопки выбора пола."""

	menu = types.InlineKeyboardMarkup()
	determinations = {
		_("Мужчина 👨"): "gender_1",
		_("Женщина 👩"): "gender_0"
	}
	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]))

	return menu
	
def emoji(emoji: str) -> types.InlineKeyboardMarkup:
	"""
	Кнопка-эмодзи.

	:param emoji: Эмодзи.
	:type emoji: str
	"""

	menu = types.InlineKeyboardMarkup()
	menu.add(types.InlineKeyboardButton(emoji, callback_data = f"emoji_{emoji}"))

	return menu

def add_share() -> types.InlineKeyboardMarkup:
	"""Меню поделиться или выйти назад."""

	menu = types.InlineKeyboardMarkup()

	menu.add(types.InlineKeyboardButton(_("Поделиться"), switch_inline_query = "\n\n" +  _("Просто **Т-т-топовый** бот для отсчёта дней до событий 🥳")))

	menu.add(types.InlineKeyboardButton(_("🔙 Назад"), callback_data = "delete"))

	return menu