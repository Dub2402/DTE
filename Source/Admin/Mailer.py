from .ReplyKeyboards import ReplyKeyboards

from dublib.TelebotUtils import UserData, UsersManager
from dublib.Polyglot import Markdown
from telebot import TeleBot, types
from threading import Thread
from time import sleep

import random

class Mailer:
	"""Рассыльщик."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __BuildButton(self, text: str, link: str) -> types.InlineKeyboardButton:
		"""
		Создаёт кнопку-ссылку.
			text – подпись кнопки;
			link – ссылка.
		"""

		# Разметка кнопки.
		Markup = types.InlineKeyboardMarkup()
		# Если данные доступны, создать кнопку.
		if text and link: Markup.add(types.InlineKeyboardButton(text, link))

		return Markup

	def __BuildMediaGroup(self, caption: str, files: dict) -> list[types.InputMedia]:
		"""
		Строит медиа группу из описания.
			caption – подпись для первого файла;
			types – словарь данных файлов.
		"""

		# Медиа группа.
		MediaGroup = list()

		# Для каждого файла.
		for File in files:
			# Определение наличия подписи.
			Caption = None if MediaGroup else caption
			# Проверка типов
			if File["type"] == "photo": MediaGroup.append(types.InputMediaPhoto(media = File["file_id"], caption = Caption))
			if File["type"] == "video": MediaGroup.append(types.InputMediaVideo(media = File["file_id"], caption = Caption))
			if File["type"] == "audio": MediaGroup.append(types.InputMediaAudio(media = File["file_id"], caption = Caption))
			if File["type"] == "document": MediaGroup.append(types.InputMediaDocument(media = File["file_id"], caption = Caption))

		return MediaGroup

	def __Mailing(self, admin: UserData, targets: list[UserData]):
		"""
		Метод ведения рассылки.
			admin – администратор;\n
			targets – список целей.
		"""

		# Статистика рассылки.
		Progress = 0.0
		Sended = 0
		Errors = 0
		# Отправка сообщения: рассылка начата.
		self.__Bot.send_message(
			chat_id = admin.id,
			text = "Рассылка начата.",
			reply_markup = ReplyKeyboards().mailing(admin)
		)
		# Отправка сообщения: идникация прогресса.
		MessageID = self.__Bot.send_message(
			chat_id = admin.id,
			text = f"*📨 Рассылка*\n\n⏳ Прогресс: {Markdown(Progress).escaped_text}%\n✉️ Отправлено: {Sended}\n❌ Ошибок: {Errors}",
			parse_mode = "MarkdownV2"
		).id

		# Для каждого пользователя.
		for Index in range(len(targets)):
			
			# Если подан сигнал остановки.
			if admin.get_property("mailing") == None:
				# Сброс свойства.
				admin.set_property("mailing", False)
				# Остановка цикла.
				break

			try:
				# Отправка сообщения.
				self.send_message(admin, targets[Index].id)

			except: Errors += 1

			else: Sended += 1

			# Расчёт прогресса.
			Progress = (Sended + Errors) / len(targets) * 100
			# Редактирование сообщения: индикация прогресса.
			self.__Bot.edit_message_text(
				chat_id = admin.id,
				message_id = MessageID,
				text = f"*📨 Рассылка*\n\n⏳ Прогресс: {Markdown(Progress).escaped_text}% \\({Index + 1} из {len(targets)}\\)\n✉️ Отправлено: {Sended}\n❌ Ошибок: {Errors}",
				parse_mode = "MarkdownV2"
			)
			# Выжидание интервала.
			sleep(0.1)

		# Установка свойства: рассылка не ведётся.
		admin.set_property("mailing", False)
		# Отправка сообщения: рассылка завершена.
		self.__Bot.send_message(
			chat_id = admin.id,
			text = "Рассылка завершена.",
			reply_markup = ReplyKeyboards().mailing(admin)
		)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, bot: TeleBot):
		"""
		Хранилище данных медиа-файлов.
			bot – бот Telegram.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Бот.
		self.__Bot = bot
		# Поток рассылки.
		self.__MailingThread = None

	def send_message(self, admin: UserData, user_id: int):
		"""
		Отправляет сообщение пользователю.
			admin – администратор;\n
			user_id – идентификатор пользователя.
		"""

		# Получение данных для отправки.
		Text = admin.get_property("mailing_caption")
		Files = admin.get_property("mailing_content")
		ButtonLabel = admin.get_property("button_label")
		ButtonLink = admin.get_property("button_link")
		# Определения методов отправки вложения.
		SendMethods = {
			"photo": self.__Bot.send_photo,
			"video": self.__Bot.send_video,
			"audio": self.__Bot.send_audio,
			"document": self.__Bot.send_document
		}

		# Если имеется несколько вложений.
		if len(Files) > 1:
			# Отправка медиа группы.
			self.__Bot.send_media_group(
				chat_id = user_id,
				media = self.__BuildMediaGroup(Text, Files)
			)

		# Если имеется только одно вложение.
		elif len(Files) == 1:
			# Получение данных о файле.
			FileType = Files[0]["type"]
			FileID = Files[0]["file_id"]
			# Отправка сообщения.
			SendMethods[FileType](
				user_id,
				FileID,
				caption = Text,
				parse_mode = "HTML",
				reply_markup = self.__BuildButton(ButtonLabel, ButtonLink)
			)
			
		else:
			# Отправка сообщения.
			self.__Bot.send_message(
				chat_id = user_id,
				text = Text,
				parse_mode = "HTML",
				disable_web_page_preview = True,
				reply_markup = self.__BuildButton(ButtonLabel, ButtonLink)
			)

	def start_mailing(self, admin: UserData, users_manager: UsersManager):
		"""
		Отправляет сообщение пользователю.
			admin – администратор;\n
			users_manager – объект управления пользователями.
		"""

		# Выборка.
		Sampling = admin.get_property("sampling")
		# Цели.
		Targets = None

		# Если в выборке указано число пользователей.
		if type(Sampling) == int:

			try:
				# Выбор случайного числа целей.
				Targets = random.sample(users_manager.users, Sampling)
			
			except ValueError:
				# Выбрать всех пользователей.
				Targets = users_manager.users

		# Если выборка не задана.
		elif Sampling == None:
			# Выбрать всех пользователей.
			Targets = users_manager.users

		# Установка свойства: рассылка ведётся.
		admin.set_property("mailing", True)
		# Создание и запуск потоки
		self.__MailingThread = Thread(target = self.__Mailing, args = [admin, Targets])
		self.__MailingThread.start()