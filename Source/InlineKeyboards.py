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
		Remove = types.InlineKeyboardButton(
			"🗑️ Удалить", 
			callback_data = f"remove_event_{EventID}"
			)
		# Добавление кнопок в меню.
		Menu.add(Remove)

		return Menu
	

	def AddShare(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()
		Share = types.InlineKeyboardButton(
			"Поделиться", 
			switch_inline_query='\n\nЛучший бот для отсчитывания дней до праздника 🥳\n\nПользуйся на здоровье!)'
			)
		Menu.add(Share)

		return Menu

	