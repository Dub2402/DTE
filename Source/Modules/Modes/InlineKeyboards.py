from Source.Core.Enums import BotModes

from dublib.Engine.GetText import _

from telebot import types

def modes_bot() -> types.InlineKeyboardMarkup:
	"""Выбор режимов бота."""

	menu = types.InlineKeyboardMarkup()

	determinations = {
		_("✅ Классик (по умолчанию)"): "classic",
		_("👼 Няшка"): "sweetie",
		_("🍺 Кореш"): "buddy",
		_("💪 Мотиватор"): "motivator",
		_("🦖 Газлайтер (18+)"): "approve_18",
		_("🚦 Рандом"): "random",
		_("🔙 Назад"): "delete_mode",
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

	return menu

def answer(type_mode: BotModes) -> types.InlineKeyboardMarkup:

	"""
	Кнопки согласия/отказа выбранного режима бота.

	:param type_mode: Режим работы бота.
	:type type_mode: BotModes
	"""

	menu = types.InlineKeyboardMarkup()
	
	determinations = {
		_("Да"): f"yes_" + type_mode.value,
		_("Нет"): "no"
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 2)

	return menu

def use_mode(type_mode: str) -> types.InlineKeyboardMarkup:
	"""
	Возвращает клавиатуру с кнопкой применить режим бота.

	:param type_mode: Название режима бота на английском языке.
	:type type_mode: str
	"""

	menu = types.InlineKeyboardMarkup()

	determinations = {
		_("Применить"): f"apply_{type_mode}",
		_("🔙 Назад"): "bot_mode"
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

	return menu