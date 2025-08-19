from dublib.Engine.GetText import _

from telebot import types

class ReplyKeyboard:

	def __init__(self):
		pass

	def AddMenu(self) -> types.ReplyKeyboardMarkup:
		""" Осовное меню."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)

		CreateEvent = types.KeyboardButton("✏️ " + _("Новое событие"))
		ListEvents = types.KeyboardButton("📜 " + _(" Мои события"))
		List = types.KeyboardButton(_("🛎 Настройка напоминаний"))
		Share = types.KeyboardButton(_("👄 Поделиться с друзьями"))

		Menu.add(CreateEvent, ListEvents, List, Share, row_width = 2)
		
		return Menu
