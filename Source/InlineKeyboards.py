from dublib.TelebotUtils import UserData
from telebot import types
from Source.Instruments import _

class InlineKeyboards:

	def __init__(self):
		pass

	def SettingsMenu(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		DeleteReminder = types.InlineKeyboardButton(_("🔕 Отключить напоминания"), callback_data = f"Delete_reminder")
		ChangeReminder = types.InlineKeyboardButton(_("🔔 Изменить напоминание"), callback_data = f"Change_reminder")
		Сhange = types.InlineKeyboardButton(_("🔁 Изменить имя"), callback_data = f"Change")
		Info = types.InlineKeyboardButton(_("ℹ️ Инфа"), callback_data = f"Info")
		Return = types.InlineKeyboardButton(_("🔙 Назад"), callback_data = f"Return")
		# Добавление кнопок в меню.
		Menu.add(DeleteReminder, ChangeReminder, Сhange, Info, Return, row_width= 1) 

		return Menu

	def OK(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		OK = types.InlineKeyboardButton(_("Ясненько"), callback_data = f"OK")
		
		# Добавление кнопок в меню.
		Menu.add(OK, row_width= 1) 

		return Menu

	def RemoveEvent(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		RemoveEvent = types.InlineKeyboardButton(
			_("Удалить"), 
			callback_data = f"remove_event_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(RemoveEvent)

		return Menu

	def ChoiceEventToChangeReminder(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Choice = types.InlineKeyboardButton(
			_("🔔 Изменить напоминание"), 
			callback_data = f"choice_event_{EventID}"
			)
		
		# Добавление кнопок в меню.
		Menu.add(Choice)

		return Menu
	
	def ChoiceReminderForNewEvent(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Choice = types.InlineKeyboardButton(
			_("Настроить напоминания"), 
			callback_data = f"choice_event_{EventID}_"
			)
		
		# Добавление кнопок в меню.
		Menu.add(Choice)

		return Menu
	
	def AddShare(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Share = types.InlineKeyboardButton(
			_("Поделиться"), 
			switch_inline_query = "\n\n" +  _("Просто топовый бот для отсчёта дней до события 🥳")
			)
		
		Menu.add(Share)

		return Menu

	def AddNewEvent(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Create = types.InlineKeyboardButton(
			_("Создать событие"), 
			callback_data = "create_event"
			)
		
		Menu.add(Create)

		return Menu

	def RemoveReminder(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		RemoveReminder = types.InlineKeyboardButton(
			_("🔕 Отключить"), 
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
			_("Сколько дней осталось"), 
			callback_data = f"remained_days_{FreeID}"
			)
		Passed = types.InlineKeyboardButton(
			_("Сколько дней прошло"), 
			callback_data = f"passed_days_{FreeID}"
			)

		# Добавление кнопок в меню.
		Menu.add(Remained, Passed, row_width = 1)
		
		return Menu
	
	def ChoiceFormatReminderNew(self, user: UserData) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()
		
		# Генерация кнопок.
		EveryDayReminders = types.InlineKeyboardButton(
			_("Оставить ежедневные напоминания"), 
			callback_data = "every_day_reminder"
			)
		OnceReminder = types.InlineKeyboardButton(
			_("Создать разовое напоминание"), 
			callback_data = "once_reminder"
			)
		WithOutReminders = types.InlineKeyboardButton(
			_("Без напоминаний"), 
			callback_data = "without_reminders"
			)

		# Добавление кнопок в меню.
		Menu.add(EveryDayReminders, OnceReminder, WithOutReminders, row_width = 1)
		
		return Menu
	

	def ChoiceFormatReminderChange(self, user: UserData) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()
		
		# Генерация кнопок.
		EveryDayReminders = types.InlineKeyboardButton(
			_("Включить ежедневные напоминания"), 
			callback_data = "every_day_reminder"
			)
		OnceReminder = types.InlineKeyboardButton(
			_("Включить разовое напоминание"), 
			callback_data = "once_reminder"
			)
		WithOutReminders = types.InlineKeyboardButton(
			_("Без напоминаний"), 
			callback_data = "without_reminders"
			)

		# Добавление кнопок в меню.
		Menu.add(EveryDayReminders, OnceReminder, WithOutReminders, row_width = 1)
		
		return Menu