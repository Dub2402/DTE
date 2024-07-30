from dublib.TelebotUtils import UserData
from telebot import types

class ReplyKeyboard:

	def __init__(self):
		pass

	def AddMenu(self, user: UserData) -> types.ReplyKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)

		# Генерация кнопок.
		CreateEvent = types.KeyboardButton("➕ Новое событие")
		ListEvents = types.KeyboardButton("🗓 Мои события")
		List = types.KeyboardButton("⚙️ Настройки")
		Share = types.KeyboardButton("📢 Поделиться с друзьями")

		# Добавление кнопок в меню.
		Menu.add(CreateEvent, ListEvents, List, Share, row_width = 2)
		
		return Menu

	# def AddMenuEvents(self, user: UserData) -> types.ReplyKeyboardMarkup:
	# 	# Кнопочное меню.
	# 	Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)

	# 	# Генерация кнопок.
	# 	CreateEvent = types.KeyboardButton("➕ Новое событие")
	# 	ListEvents = types.KeyboardButton("🗓 Мои события")
	# 	DeleteEvent = types.KeyboardButton("🗑 Удалить событие")
	# 	Return = types.KeyboardButton("⬅ Назад")

	# 	# Добавление кнопок в меню.
	# 	Menu.add(CreateEvent, ListEvents, DeleteEvent, Return, row_width = 2)
		
	# 	return Menu
	
	# def AddMenuReminders(self, user: UserData) -> types.ReplyKeyboardMarkup:
	# 	# Кнопочное меню.
	# 	Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)

	# 	# Генерация кнопок.
	# 	CreateReminder = types.KeyboardButton("➕ Создать напоминание")
	# 	# ListReminders = types.KeyboardButton("🗓 Мои события")
	# 	DeleteReminder = types.KeyboardButton("🗑 Удалить напоминание")
	# 	Return = types.KeyboardButton("⬅ Назад")

	# 	# Добавление кнопок в меню.
	# 	Menu.add(CreateReminder, DeleteReminder, Return, row_width = 2)
		
	# 	return Menu
	
