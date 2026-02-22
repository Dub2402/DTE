from dublib.Engine.GetText import _

from typing import TYPE_CHECKING

from telebot import types

if TYPE_CHECKING:
	from Source.Core.Enums import TrashMessagesTypes

def settingsmenu() -> types.InlineKeyboardMarkup:
	"""Меню настройки уведомлений."""

	menu = types.InlineKeyboardMarkup()

	determinations = {
		_("🔕 Отключить напоминания"): "delete_reminder",
		_("🔔 Изменить напоминания"): "change_reminder",
		_("🕰 Время ежедн. напоминаний"): "time_every_reminders",
		_("🤭 Режим бота"): "bot_mode",
		_("🔁 Сменить имя и пол"): "change_name",
		_("🌐 Сменить часовой пояс"): "tz_change",
		_("🔙 Назад"): "steak_messageSettings__",
	}

	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)
	return menu

def delete(text: str) -> types.InlineKeyboardMarkup:
	"""
	Кнопка удаления сообщения.

	:param text: Подпись кнопки удаления.
	:type text: str
	"""

	menu = types.InlineKeyboardMarkup()
	menu.add(types.InlineKeyboardButton(text, callback_data = "delete")) 

	return menu

def choice_gender() -> types.InlineKeyboardMarkup:
	"""Кнопки выбора пола."""

	menu = types.InlineKeyboardMarkup()
	determinations = {
		_("Мужчина 👨"): "gender_1",
		_("Женщина 👩"): "gender_0"
	}
	for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)

	return menu
	
def emoji(emoji: str, type_trash: TrashMessagesTypes | None = None) -> types.InlineKeyboardMarkup:
	"""
	Кнопка-эмодзи.

	:param emoji: Эмодзи
	:type emoji: str
	:param type_trash: Тип сообщений, которые нужно удалить.
	:type type_trash: TrashMessagesTypes | None
	"""

	menu = types.InlineKeyboardMarkup()
	menu.add(types.InlineKeyboardButton(emoji, callback_data = f"emoji_{emoji}_{type_trash.value}"), row_width = 1)

	return menu