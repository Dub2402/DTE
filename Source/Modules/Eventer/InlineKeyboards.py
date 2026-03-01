from Source.Core.ExtendedUser import ExtendedUser

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
		callback_data = "one_time_reminder"
	)
	
	EveryReminders = types.InlineKeyboardButton(
		_("Отсчитывать дни"), 
		callback_data = "count_down_event"
	)

	Menu.add(OnceReminder, EveryReminders, row_width = 1)
	
	return Menu

def counter_type() -> types.InlineKeyboardMarkup:
	"""Меню выбора формата отслеживания."""

	Menu = types.InlineKeyboardMarkup()
	
	Remained = types.InlineKeyboardButton(
		_("Сколько дней осталось"), 
		callback_data = "counter_remained"
	)
	
	Passed = types.InlineKeyboardButton(
		_("Сколько дней прошло"), 
		callback_data = "counter_passed"
	)

	Menu.add(Remained, Passed, row_width = 1)
	
	return Menu

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def	change_reminder_after_saving_event(extended_user: ExtendedUser, event_id: int) -> types.InlineKeyboardMarkup:
	"""Уточняющее меню выбора напоминаний для только что созданного события."""

	Menu = types.InlineKeyboardMarkup()

	Change = types.InlineKeyboardButton(
		_("Изменить 🔔"), 
		callback_data = f"settings_for_{event_id}"
		)
	
	Bote_Mode = types.InlineKeyboardButton(
		_("Режим бота 🤭"), 
		callback_data = f"bot_mode"
		)

	Choice = types.InlineKeyboardButton(
		_("Настроить напоминания"), 
		callback_data = f"settings_for_{event_id}"
		)
	
	Steak = types.InlineKeyboardButton(
		_("Спасибо, все супер!"), 
		callback_data = f"for_delete"
		)
	
	if extended_user.user.has_property("change_reminder_after_saving_mode_bot"):
		Menu.add(Change, Bote_Mode, row_width = 2)
		Menu.add(Steak, row_width = 2)
	
	else: Menu.add(Choice, Steak, row_width = 1)

	return Menu