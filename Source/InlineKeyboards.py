from dublib.TelebotUtils import UserData
from telebot import types

class InlineKeyboards:

	def __init__(self):
		pass

	def SettingsMenu(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		DeleteEvent = types.InlineKeyboardButton("🗑 Удалить событие", callback_data = f"Remove_event")
		CreateReminder = types.InlineKeyboardButton("➕ Создать напоминание", callback_data = f"Create_reminder")
		DeleteReminder = types.InlineKeyboardButton("🗑 Удалить напоминание", callback_data = f"Delete_reminder")
		Сhange = types.InlineKeyboardButton("🔁 Изменить имя", callback_data = f"Change")
		Info = types.InlineKeyboardButton("ℹ️ Инфа", callback_data = f"Info")
		Return = types.InlineKeyboardButton("🔙 Назад", callback_data = f"Return")
		# Добавление кнопок в меню.
		Menu.add(DeleteEvent, DeleteReminder, CreateReminder, Сhange, Info, Return, row_width= 1) 

		return Menu

	def OK(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		OK = types.InlineKeyboardButton("Ясненько", callback_data = f"OK")
		
		# Добавление кнопок в меню.
		Menu.add(OK, row_width= 1) 

		return Menu

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
			"🔔 Создать напоминание", 
			callback_data = f"choice_event_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(Choice)

		return Menu

	def ChoiceEventToChangeReminder(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Choice = types.InlineKeyboardButton(
			"🔔 Изменить напоминание", 
			callback_data = f"choice_event_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(Choice)

		return Menu
	
	def AddShare(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Share = types.InlineKeyboardButton(
			"Поделиться", 
			switch_inline_query='\n\nПросто топовый бот для отсчёта дней до события 🥳'
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
			"🚫 Отключить", 
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
		Menu.add(Remained, Passed, row_width = 1)
		
		return Menu
	
	def ChoiceFormatReminder(self, user: UserData) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()
		
		# Генерация кнопок.
		EveryDayReminders = types.InlineKeyboardButton(
			"Включить ежедневные напоминания", 
			callback_data = "every_day_reminder"
			)
		OnceReminder = types.InlineKeyboardButton(
			"Включить разовое напоминание", 
			callback_data = "once_reminder"
			)
		WithOutReminders = types.InlineKeyboardButton(
			"Без напоминаний", 
			callback_data = "without_reminders"
			)

		# Добавление кнопок в меню.
		Menu.add(EveryDayReminders, OnceReminder, WithOutReminders, row_width = 1)
		
		return Menu