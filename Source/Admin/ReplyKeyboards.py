from dublib.TelebotUtils import UserData
from telebot import types

class ReplyKeyboards:
	"""Генератор кнопочного интерфейса."""

	def __init__(self):
		"""Генератор кнопочного интерфейса."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		pass

	def admin(self) -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: панель управления."""

		# Кнопочное меню.
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		# Генерация кнопок.
		Mailing = types.KeyboardButton("👤 Рассылка")
		Statistics = types.KeyboardButton("📊 Статистика")
		Close = types.KeyboardButton("❌ Закрыть")
		# Добавление кнопок в меню.
		Menu.add(Mailing, Statistics, Close, row_width = 2)

		return Menu

	def cancel(self) -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: отмена."""

		# Кнопочное меню.
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		# Генерация кнопок.
		Cancel = types.KeyboardButton("❌ Отмена")
		# Добавление кнопок в меню.
		Menu.add(Cancel)

		return Menu
	
	def editing(self) -> types.ReplyKeyboardMarkup:
		"""Строит кнопочный интерфейс: редактирование сообщения."""

		# Кнопочное меню.
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		# Генерация кнопок.
		Ok = types.KeyboardButton("✅ Завершить")
		Cancel = types.KeyboardButton("❌ Отмена")
		# Добавление кнопок в меню.
		Menu.add(Ok, Cancel, row_width = 1)

		return Menu
	
	def mailing(self, user: UserData) -> types.ReplyKeyboardMarkup:
		"""
		Строит кнопочный интерфейс: рассылка.
			user – администратор.
		"""

		# Подпись кнопки.
		ButtonText = "Удалить" if user.get_property("button_link") else "Добавить"
		Status = "🔴 Остановить" if user.get_property("mailing") else "🟢 Запустить"
		# Кнопочное меню.
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		# Генерация кнопок.
		Start = types.KeyboardButton(Status)
		Sampling = types.KeyboardButton("🎯 Выборка")
		View = types.KeyboardButton("🔎 Просмотр")
		Edit = types.KeyboardButton("✏️ Редактировать")
		Button = types.KeyboardButton(f"🕹️ {ButtonText} кнопку")
		Back = types.KeyboardButton("↩️ Назад")
		# Добавление кнопок в меню.
		Menu.add(Start, Sampling, View, Edit, Button, Back, row_width = 1)

		return Menu