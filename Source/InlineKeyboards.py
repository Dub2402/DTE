from dublib.TelebotUtils import UserData
from telebot import types

class InlineKeyboards:
	"""Генератор кнопочного Inline-интерфейса."""

	def __init__(self):
		"""Генератор кнопочного Inline-интерфейса."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
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
	
	def СhoiceEvent(self, EventID: int) -> types.InlineKeyboardMarkup:

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