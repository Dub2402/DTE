from Source.Core.Enums import BotModes, ConfirmTypes

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
		_("🔙 Назад"): "delete",
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

	return menu

def apply(type_mode: BotModes) -> types.InlineKeyboardMarkup:
	"""
	Возвращает клавиатуру с кнопкой применить режим бота.

	:param type_mode: Режим работы бота.
	:type type_mode: BotModes
	"""

	menu = types.InlineKeyboardMarkup()

	determinations = {
		_("Применить"): "apply_" + type_mode.value,
		_("🔙 Назад"): "delete"
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

	return menu

def confirm(type_mode: BotModes, type_confirm: ConfirmTypes) -> types.InlineKeyboardMarkup:
	"""
	Кнопки согласия/отказа.

	:param type_mode: Режим работы бота.
	:type type_mode: BotModes
	:param type_confirm: Тип согласия/отказа.
	:type type_confirm: ConfirmTypes
	"""

	menu = types.InlineKeyboardMarkup()
	
	yes_callback_data = type_mode.value if type_confirm == ConfirmTypes.approve_18 else "yes_" + type_mode.value + "_" + type_confirm.value

	determinations = {
		_("Да"): yes_callback_data,
		_("Нет"): "delete"
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 2)

	return menu