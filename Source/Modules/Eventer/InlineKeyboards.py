from Source.Core.ExtendedUser import ExtendedUser
from Source.Core.Enums import StatusWorking
from Source.Modules.Eventer import EventTypes

from dublib.Engine.GetText import _

from telebot import types

def add_new_event() -> types.InlineKeyboardMarkup:
	"""Кнопка создать событие."""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Создать событие"), callback_data = "create_event")]])

def format_reminder(type_reminders: StatusWorking) -> types.InlineKeyboardMarkup:
	"""
	Выбор типа напоминаний.

	:param type_reminders: Тип наборов кнопок.
	:type type_reminders: StatusWorking
	"""

	menu = types.InlineKeyboardMarkup()

	sets_reminders = {
		StatusWorking.new: {
			_("Разовое напоминание"): "one_time_reminder",
			_("Отсчитывать дни"): "count_down_event"
		},
		StatusWorking.hot_fix: {
			_("Без напоминаний"): "without_reminders",
			_("Создать разовое напоминание"): "one_time_reminder",
			_("🔙 Назад"): "delete"
		},
		StatusWorking.change: {
			_("Включить ежедневные напоминания"): "every_day_reminder",
			_("Включить разовое напоминание"): "one_time_reminder",
			_("Без напоминаний"): "without_reminders",
			_("Оставить всё как есть"): "delete"
		}
	}
	
	for text in sets_reminders[type_reminders].keys(): menu.add(types.InlineKeyboardButton(text, callback_data = sets_reminders[type_reminders][text]), row_width = 1)

	return menu

def confirm_reminder(type_reminders: EventTypes.counting | EventTypes.no_nofifications) -> types.InlineKeyboardMarkup:
	"""
	Уточнение правильности выбора типа уведомлений.

	:param type_reminders: Тип уведомлений, который должен быть включён.
	:type type_reminders: EventTypes.counting | EventTypes.no_nofifications
	"""

	type_reminders = type_reminders.value

	menu = types.InlineKeyboardMarkup()

	determinations = {
		_("Да"): f"confirm_{type_reminders}",
		_("Нет"): "delete"
	}

	buttons = [types.InlineKeyboardButton(string, callback_data = determinations[string]) for string in determinations.keys() ]
	menu.add(*buttons, row_width = 2)
	
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
		menu.add(types.InlineKeyboardButton(_("Исправить"), callback_data = "fix_reminder_date"), row_width = 1)
		button_text = "Спасибо!"
		
	menu.add(types.InlineKeyboardButton(button_text, callback_data = "thanks"), row_width = 1)
	
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
		_("Изменить 🔔"): "fix_reminder",
		_("Режим бота 🤭"): "bot_mode",
		_("Спасибо, все супер!"): "thanks"
	}

	if extended_user.user.has_property("change_reminder_after_saving_mode_bot"): 
		buttons = [types.InlineKeyboardButton(string, callback_data = determinations[string]) for string in determinations.keys() ]
		menu.add(*buttons, row_width = 2)

	else: 
		determinations.pop(_("Режим бота 🤭"))
		determinations = {k.replace(_("Изменить 🔔"), _("Изменить напоминания")): v for k, v in determinations.items()}
		for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)
		
	return menu

def choice_another_day() -> types.InlineKeyboardMarkup:
	"""Выбор другого дня для разового уведомления."""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Хочу в другой день!"), callback_data = "another_day")]])

def remove_event(event_id: int) -> types.InlineKeyboardMarkup:
	"""
	Кнопка удаления события.

	:param event_id: id удаляемого события.
	:type event_id: int
	"""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("Удалить"), callback_data = f"remove_event_{event_id}")]])

def disable_reminder(event_id: int) -> types.InlineKeyboardMarkup:
	"""
	Кнопка отключения напоминания.

	:param event_id: id отключаемого напоминания.
	:type event_id: int
	"""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("🔕 Отключить"), callback_data = f"disable_reminder_{event_id}")]])

def change_reminder(event_id: int) -> types.InlineKeyboardMarkup:
	"""
	Кнопка изменения напоминания.

	:param event_id: id изменяемого напоминания.
	:type event_id: int
	"""

	return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = _("🔔 Изменить напоминание"), callback_data = f"change_reminder_{event_id}")]])