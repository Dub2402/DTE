from dublib.Engine.GetText import _

from telebot import types

def add_new_event() -> types.InlineKeyboardMarkup:
	"""Кнопка создать событие."""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Создать событие"), callback_data = "create_event")]])

def remove_event(event_id: int) -> types.InlineKeyboardMarkup:
	"""
	Кнопка удаление события.

	:param event_id: id удаляемого события.
	:type event_id: int
	"""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Удалить"), callback_data = f"remove_event_{event_id}")]])

def format_reminder() -> types.InlineKeyboardMarkup:
	"""Выбор типа напоминаний для только что созданного события."""

	Menu = types.InlineKeyboardMarkup()
	
	OnceReminder = types.InlineKeyboardButton(
		_("Разовое напоминание"), 
		callback_data = "one_time"
		)
	EveryReminders = types.InlineKeyboardButton(
		_("Отсчитывать дни"), 
		callback_data = "counting"
		)

	Menu.add(OnceReminder, EveryReminders, row_width = 1)
	
	return Menu