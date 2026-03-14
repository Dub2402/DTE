from Source.Core.ExtendedUser import ExtendedUser

from dublib.Engine.GetText import _

from telebot import types

def add_new_event() -> types.InlineKeyboardMarkup:
	"""Кнопка создать событие."""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Создать событие"), callback_data = "create_event")]])

def format_reminder() -> types.InlineKeyboardMarkup:
	"""Выбор типа напоминаний для только что созданного события."""

	menu = types.InlineKeyboardMarkup()

	determinations = {
		_("Разовое напоминание"): "one_time_reminder",
		_("Отсчитывать дни"): "count_down_event"
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

	return menu

def counter_type() -> types.InlineKeyboardMarkup:
	"""Меню выбора формата отслеживания."""

	menu = types.InlineKeyboardMarkup()

	determinations = {
		_("Сколько дней осталось"): "counter_remained",
		_("Сколько дней прошло"): "counter_passed"
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

	return menu

def saving_reminder(count_elements: int) -> types.InlineKeyboardMarkup:
	"""
	Выбор правильно ли сохранены одноразовые напоминания для события.

	:param count_elements: Количество элементов в напоминании.
	:type count_elements: int
	"""

	button_text = "Спасибо"
	
	menu = types.InlineKeyboardMarkup(row_width = 1)

	if count_elements == 2: 
		menu.add(types.InlineKeyboardButton(_("Исправить"), callback_data = "change_reminder"), row_width = 1)
		button_text = "Спасибо!"
		
	menu.add(types.InlineKeyboardButton(button_text, callback_data = "save_no"), row_width = 1)
	
	return menu

def	change_reminder_after_saving_event(extended_user: ExtendedUser, event_id: int) -> types.InlineKeyboardMarkup:
	"""
	Уточняющее меню выбора напоминаний для только что созданного события.

	:param extended_user: Расширенные данные пользователя.
	:type extended_user: ExtendedUser
	:param event_id: ID события
	:type event_id: int
	"""

	menu = types.InlineKeyboardMarkup()

	determinations = {
		_("Изменить 🔔"): f"settings_for_{event_id}",
		_("Режим бота 🤭"): "bot_mode",
		_("Спасибо, все супер!"): "for_delete"
	}

	if extended_user.user.has_property("change_reminder_after_saving_mode_bot"): 
		buttons = [ types.InlineKeyboardButton(string, callback_data = determinations[string]) for string in determinations.keys() ]
		menu.add(*buttons, row_width = 2)

	else: 
		determinations.pop(_("Режим бота 🤭"))
		determinations = {k.replace(_("Изменить 🔔"), _("Настроить напоминания")): v for k, v in determinations.items()}
		for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)
		
	return menu

def choice_another_day() -> types.InlineKeyboardMarkup:
	"""Выбор другого дня для разового уведомления."""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Хочу в другой день!"), callback_data = "another_day")]])

def remove_event(event_id: int) -> types.InlineKeyboardMarkup:
	"""
	Кнопка удаление события.

	:param event_id: id удаляемого события.
	:type event_id: int
	"""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Удалить"), callback_data = f"remove_event_{event_id}")]])
