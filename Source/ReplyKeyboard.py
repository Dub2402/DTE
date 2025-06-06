from dublib.TelebotUtils import UserData
from telebot import types
from Source.Functions import _

class ReplyKeyboard:

	def __init__(self):
		pass

	def AddMenu(self) -> types.ReplyKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)

		# Генерация кнопок.
		CreateEvent = types.KeyboardButton(_("➕ Новое событие"))
		ListEvents = types.KeyboardButton(_("🗓 Мои события"))
		List = types.KeyboardButton(_("🛎 Настройка напоминаний"))
		Share = types.KeyboardButton(_("📢 Поделиться с друзьями"))

		# Добавление кнопок в меню.
		Menu.add(CreateEvent, ListEvents, List, Share, row_width = 2)
		
		return Menu
