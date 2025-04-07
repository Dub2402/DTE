from dublib.TelebotUtils import UserData
from telebot import types
from Source.Functions import _

class InlineKeyboard:

	def __init__(self):
		pass

	def SettingsMenu(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		DeleteReminder = types.InlineKeyboardButton(_("🔕 Отключить напоминания"), callback_data = f"Delete_reminder")
		ChangeReminder = types.InlineKeyboardButton(_("🔔 Изменить напоминание"), callback_data = f"Change_reminder")
		Сhange = types.InlineKeyboardButton(_("🔁 Изменить имя"), callback_data = f"Change_name")
		Info = types.InlineKeyboardButton(_("ℹ️ Инфа"), callback_data = f"Info")
		Return = types.InlineKeyboardButton(_("🔙 Назад"), callback_data = f"Return")
		# Добавление кнопок в меню.
		Menu.add(DeleteReminder, ChangeReminder, Сhange, Info, Return, row_width= 1) 

		return Menu
	
	def ChoiceEventToRemoveReminder(self, EventID: int) -> types.InlineKeyboardMarkup:
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

	def OK(self) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		OK = types.InlineKeyboardButton(_("Ясненько"), callback_data = f"OK")
		
		# Добавление кнопок в меню.
		Menu.add(OK, row_width= 1) 

		return Menu
	
	def AddNewEvent(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Create = types.InlineKeyboardButton(
			_("Создать событие"), 
			callback_data = "create_event"
			)
		
		Menu.add(Create)

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
	
	def DeleteMessage(self, Text: str, object: str = "") -> types.InlineKeyboardMarkup:

		Menu = types.InlineKeyboardMarkup()

		Button = types.InlineKeyboardButton(
			Text, 
			callback_data = "Back_{}".format(object)
			)
		
		# Добавление кнопок в меню.
		Menu.add(Button, row_width =1)

		return Menu


	def ChoiceReminderForNewEvent(self, EventID: int) -> types.InlineKeyboardMarkup:
		# Кнопочное меню.
		Menu = types.InlineKeyboardMarkup()

		# Генерация кнопок.
		Choice = types.InlineKeyboardButton(
			_("Настроить напоминания"), 
			callback_data = f"choice_event_{EventID}_"
			)
		Thanks = types.InlineKeyboardButton(
			_("Спасибо, все супер!"), 
			callback_data = f"Thanks"
			)
		
		# Добавление кнопок в меню.
		Menu.add(Choice, Thanks, row_width =1)

		return Menu
	
	def AddShare(self) -> types.InlineKeyboardMarkup:
		Menu = types.InlineKeyboardMarkup()

		Share = types.InlineKeyboardButton(
			_("Поделиться"), 
			switch_inline_query = "\n\n" +  _("Просто Т-т-топовый бот для отсчёта дней до событий 🥳")
			)
		Back = types.InlineKeyboardButton(_("🔙 Назад"), callback_data = f"Back")
		
		Menu.add(Share, Back, row_width = 1)

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
		
		# # Генерация кнопок.
		# EveryDayReminders = types.InlineKeyboardButton(
		# 	_("Оставить ежедневные напоминания"), 
		# 	callback_data = "every_day_reminder"
		# 	)
		OnceReminder = types.InlineKeyboardButton(
			_("Создать разовое напоминание"), 
			callback_data = "once_reminder"
			)
		WithOutReminders = types.InlineKeyboardButton(
			_("Без напоминаний"), 
			callback_data = "without_reminders"
			)
		Back = types.InlineKeyboardButton(_("🔙 Назад"), callback_data = f"Back")

		# Добавление кнопок в меню.
		Menu.add(WithOutReminders, OnceReminder, Back, row_width = 1)
		
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