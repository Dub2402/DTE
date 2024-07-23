from dublib.TelebotUtils import UserData
from telebot import types

class InlineKeyboard:
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
		Remove = types.InlineKeyboardButton("🗑️ Удалить", callback_data = f"remove_event_{EventID}")
		# Добавление кнопок в меню.
		Menu.add(Remove)

		return Menu