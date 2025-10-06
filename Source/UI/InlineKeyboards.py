from dublib.TelebotUtils import UserData
from dublib.Engine.GetText import _

from telebot import types

class InlineKeyboard:

	def SettingsMenu() -> types.InlineKeyboardMarkup:
		"""Меню настройки уведомлений."""

		menu = types.InlineKeyboardMarkup()

		determinations = {
			_("🔕 Отключить напоминания"): "Delete_reminder",
			_("🔔 Изменить напоминания"): "Change_reminder",
			_("🕰 Время ежедн. напоминаний"): "time_every_reminders",
			_("🤭 Режим бота"): "bot_mode",
			_("🔁 Сменить имя и пол"): "Change_name",
			_("🌐 Сменить часовой пояс"): "tz_change",
			_("🔙 Назад"): "Steak_MessageSettings__",
		}

		for string in determinations.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = determinations[string]), row_width = 1)
		return menu

	def AddShare() -> types.InlineKeyboardMarkup:
		"""Меню поделиться или выйти назад."""
		Menu = types.InlineKeyboardMarkup()

		Share = types.InlineKeyboardButton(
			_("Поделиться"), 
			switch_inline_query = "\n\n" +  _("Просто **Т-т-топовый** бот для отсчёта дней до событий 🥳")
			)
		Steak = types.InlineKeyboardButton(_("🔙 Назад"), callback_data = f"Steak___")
		
		Menu.add(Share, Steak, row_width = 1)

		return Menu

	def ChoiceGender():
		"""Выбор пола."""

		Menu = types.InlineKeyboardMarkup()
		
		Men = types.InlineKeyboardButton(
			_("Мужчина 👨"), 
			callback_data = "Gender_man"
			)
		Women = types.InlineKeyboardButton(
			_("Женщина 👩"), 
			callback_data = "Gender_woman"
			)
		
		Menu.add(Men, Women, row_width = 1)
		
		return Menu
	
	def ChoiceAnotherDay() -> types.InlineKeyboardMarkup:
		"""Выбор другого дня для разового уведомления."""

		Menu = types.InlineKeyboardMarkup()
		
		AnotherDay = types.InlineKeyboardButton(
			_("Хочу в другой день!"), 
			callback_data = "AnotherDay"
			)

		Menu.add(AnotherDay, row_width = 1)
		
		return Menu

	def ChoiceFormat() -> types.InlineKeyboardMarkup:
		"""Меню выбора формата события."""

		Menu = types.InlineKeyboardMarkup()
		
		Remained = types.InlineKeyboardButton(
			_("Сколько дней осталось"), 
			callback_data = f"Format_Remained"
			)
		Passed = types.InlineKeyboardButton(
			_("Сколько дней прошло"), 
			callback_data = f"Format_Passed"
			)

		Menu.add(Remained, Passed, row_width = 1)
		
		return Menu

	def Saving(buttons: list, text_save: str, delete: str = "", reaction: str = "") -> types.InlineKeyboardMarkup:
		"""Сохранить ли данные события:
			buttons: кнопки которые, необходимо добавить в клавиатуру;
			text_save: текст для кнопки сохранить, если он нужен;
			delete: что необходимо удалить;
			reaction: вид реакции на сообщение.
		"""
		
		Menu = types.InlineKeyboardMarkup(row_width = 1)

		for button in buttons:
			if button == "notSave":
				Menu.add(
					types.InlineKeyboardButton(
					_("Исправить"), 
					callback_data = f"Save_no_{delete}"
					))
			if button == "Save":
				Menu.add(
					types.InlineKeyboardButton(
					text_save, 
					callback_data = f"Save_yes{reaction}"
					))
		
		return Menu

	def ChoiceFormatReminderStart() -> types.InlineKeyboardMarkup:
		"""Выбор типа напоминаний для только что созданного события."""

		Menu = types.InlineKeyboardMarkup()
		
		OnceReminder = types.InlineKeyboardButton(
			_("Разовое напоминание"), 
			callback_data = "once_reminder_start"
			)
		EveryReminders = types.InlineKeyboardButton(
			_("Отсчитывать дни"), 
			callback_data = "every_day_reminder_start"
			)

		Menu.add(OnceReminder, EveryReminders, row_width = 1)
		
		return Menu

	def SettingsNotifications(EventID: int, Send: str = "", new_user: bool = False) -> types.InlineKeyboardMarkup:
		"""Уточняющее меню выбора напоминаний для только что созданного события."""

		Menu = types.InlineKeyboardMarkup()

		Change = types.InlineKeyboardButton(
			_("Изменить 🔔"), 
			callback_data = f"settings_for_{EventID}"
			)
		
		Bote_Mode = types.InlineKeyboardButton(
			_("Режим бота 🤭"), 
			callback_data = f"bot_mode"
			)

		Choice = types.InlineKeyboardButton(
			_("Настроить напоминания"), 
			callback_data = f"settings_for_{EventID}"
			)
		
		Steak = types.InlineKeyboardButton(
			_("Спасибо, все супер!"), 
			callback_data = f"Steak___{Send}"
			)
		
		if new_user: 
			Menu.add(Change, Bote_Mode, row_width = 2)
			Menu.add(Steak, row_width = 2)
		
		else: Menu.add(Choice, Steak, row_width = 1)

		return Menu

	def ChoiceFormatReminderNew() -> types.InlineKeyboardMarkup:
		"""Дополнительное меню выбора напоминаний для только что созданного события."""

		Menu = types.InlineKeyboardMarkup()
		
		OnceReminder = types.InlineKeyboardButton(
			_("Создать разовое напоминание"), 
			callback_data = "once_reminder_new"
			)
		WithOutReminders = types.InlineKeyboardButton(
			_("Без напоминаний"), 
			callback_data = "without_reminders_new"
			)
		Steak = types.InlineKeyboardButton(_("🔙 Назад"), callback_data = f"Steak___")

		Menu.add(WithOutReminders, OnceReminder, Steak, row_width = 1)
		
		return Menu
	
	def ChoiceFormatReminderChange() -> types.InlineKeyboardMarkup:
		"""Выбор типа напоминаний при изменении напоминаний."""
		Menu = types.InlineKeyboardMarkup()
		
		EveryDayReminders = types.InlineKeyboardButton(
			_("Включить ежедневные напоминания"), 
			callback_data = "every_day_reminder_change"
			)
		OnceReminder = types.InlineKeyboardButton(
			_("Включить разовое напоминание"), 
			callback_data = "once_reminder_change"
			)
		WithOutReminders = types.InlineKeyboardButton(
			_("Без напоминаний"), 
			callback_data = "without_reminders_change"
			)
		Steak = types.InlineKeyboardButton(
			_("Оставить как есть!"), 
			callback_data = "Steak_Leavechangenotifications__"
			)

		Menu.add(EveryDayReminders, OnceReminder, WithOutReminders, Steak, row_width = 1)
		
		return Menu
	
	def ChoiceEventToChangeReminder(EventID: int) -> types.InlineKeyboardMarkup:
		"""Изменить напоминание при выборе соответствующего напоминания."""
		Menu = types.InlineKeyboardMarkup()

		Choice = types.InlineKeyboardButton(
			_("🔔 Изменить напоминание"), 
			callback_data = f"choice_event_{EventID}"
			)
		
		Menu.add(Choice)

		return Menu
	
	def ChoiceEventToRemoveReminder(EventID: int) -> types.InlineKeyboardMarkup:
		"""Удаление напоминаний."""

		Menu = types.InlineKeyboardMarkup()

		RemoveReminder = types.InlineKeyboardButton(
			_("🔕 Отключить"), 
			callback_data = f"remove_reminder_{EventID}"
			)
		
		Menu.add(RemoveReminder)

		return Menu

	def Confirmation(notification_type, subtype: str) -> types.InlineKeyboardMarkup:

		"""
		Подтверждение выбора типа уведомлений:
			notification_type: WithoutNotifications/EveryNotifications;
			subtype: change.
		"""

		Menu = types.InlineKeyboardMarkup()
		
		Yes = types.InlineKeyboardButton(
			_("Да"), 
			callback_data = f"Confirmation_{notification_type}_{subtype}"
			)
		No = types.InlineKeyboardButton(
			_("Нет"), 
			callback_data = "Steak___"
			)

		Menu.add(Yes, No, row_width = 2)
		
		return Menu

	def SendEmoji(emoji: str, delete_type: str = "") -> types.InlineKeyboardMarkup:

		"""
		Отправляет эмодзи в виде кнопки под сообщением:
			emoji: вид эмодзи;
			delete_type: указывает на тип, удаляемых сообщений (к примеру, events).
		"""

		Menu = types.InlineKeyboardMarkup()

		Emoji = types.InlineKeyboardButton(
			(emoji), 
			callback_data = f"Emoji_{emoji}_{delete_type}"
			)
		
		Menu.add(Emoji, row_width =1)

		return Menu

	def SteakActions(name_button: str, emoji: str = "", delete: str = "", update: str = ""):
		"""
		Меню-конструктор, выполняющий различные действия пользователя.
			name_button: название кнопки, видимое для пользователя;
			delete: что требуется удалить;
			update: что требуется обновить.
		"""

		Menu = types.InlineKeyboardMarkup()

		Steak = types.InlineKeyboardButton(name_button, callback_data = f"Steak_{delete}_{update}_")
		
		Menu.add(Steak, row_width= 1) 

		return Menu
