from dublib.Engine.GetText import _

from telebot import types

def menu() -> types.ReplyKeyboardMarkup:
	"""Главное меню."""

	menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
	buttons = [
		types.KeyboardButton("✏️ " + _("Новое событие")), 
		types.KeyboardButton("📜 " + _("Мои события")), 
		types.KeyboardButton("🛎 " + _("Настройка напоминаний")), 
		types.KeyboardButton("👄 " + _("Поделиться с друзьями"))
	] 
	menu.add(*buttons, row_width = 2)

	return menu