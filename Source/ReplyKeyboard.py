from dublib.TelebotUtils import UserData
from telebot import types

class ReplyKeyboard:
	"""Генератор кнопочного интерфейса."""

	def __init__(self):
		"""Генератор кнопочного интерфейса."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		pass

	def AddMenu(self, user: UserData) -> types.ReplyKeyboardMarkup:
		"""
		Строит кнопочный интерфейс: создание.
			user – объектное представление пользователя.
		"""

		# Кнопочное меню.
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		# Генерация кнопок.
		Create = types.KeyboardButton("Новое событие")
		List = types.KeyboardButton("Мои события")
		Share = types.KeyboardButton("Поделиться с друзьями")
		# Добавление кнопок в меню.
		Menu.add(Create, List, Share, row_width = 1)
		
		return Menu
