from dublib.TelebotUtils import UserData
from telebot import types

class InlineKeyboards:
	"""Генератор Inline-интерфейса."""

	def __init__(self):
		"""Генератор Inline-интерфейса."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		pass

	def sampling(self, admin: UserData):
		"""
		Строит Inline-интерфейс: выборка.
			admin – администратор.
		"""

		#---> Генерация кнопочного интерфейса.
		#==========================================================================================#
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()
		# Генерация кнопки.
		LastSampling = types.InlineKeyboardButton("1K", callback_data = "sampling_last")
		AllSampling = types.InlineKeyboardButton("Все", callback_data = "sampling_all")
		Cancel = types.InlineKeyboardButton("Отмена", callback_data = "sampling_cancel")
		# Добавление кнопки в меню.
		Menu.add(LastSampling, AllSampling, row_width = 2)
		Menu.add(Cancel, row_width = 1)

		return Menu
		