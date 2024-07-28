from dublib.TelebotUtils import UserData
from telebot import types

class InlineKeyboards:

	def __init__(self):
		pass

	def RemoveEvent(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		RemoveEvent = types.InlineKeyboardButton(
			"🗑️ Удалить", 
			callback_data = f"remove_event_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(RemoveEvent)

		return Menu
	
	def ChoiceEventToAddReminder(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Choice = types.InlineKeyboardButton(
			"🎯 Создать напоминание", 
			callback_data = f"choice_event_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(Choice)

		return Menu
	
	def AddShare(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Share = types.InlineKeyboardButton(
			"Поделиться", 
			switch_inline_query='\n\nЛучший бот для отсчитывания дней до праздника 🥳\nПользуйся на здоровье!)'
			)
		
		Menu.add(Share)

		return Menu

	def AddNewEvent(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Create = types.InlineKeyboardButton(
			"Создать событие", 
			callback_data = "create_event"
			)
		
		Menu.add(Create)

		return Menu

	def RemoveReminder(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		RemoveReminder = types.InlineKeyboardButton(
			"🗑️ Удалить", 
			callback_data = f"remove_reminder_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(RemoveReminder)

		return Menu
	
	def ChoiceFormat(self, user: UserData, FreeID: str) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()
		
		# Генерация кнопок.
		Remained = types.InlineKeyboardButton(
			"Сколько дней осталось", 
			callback_data = f"remained_days_{FreeID}"
			)
		Passed = types.InlineKeyboardButton(
			"Сколько дней прошло", 
			callback_data = f"passed_days_{FreeID}"
			)

		# Добавление кнопок в меню.
		Menu.add(Remained, Passed)
		
		return Menu