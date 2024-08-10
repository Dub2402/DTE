from .InlineKeyboards import InlineKeyboards
from .ReplyKeyboards import ReplyKeyboards
from .Input import UserInput
from .Mailer import Mailer
from ..ReplyKeyboard import ReplyKeyboard

from dublib.TelebotUtils import UserData, UsersManager
from telebot import TeleBot, types

def InitializeCommands(bot: TeleBot, password: str, users: UsersManager):
	"""
	Набор декораторов: команды.
		bot – экземпляр бота;\n
		password – пароль администратора;\n
		users – менеджер пользователей.
	"""

	# Обработка команды: admin.
	@bot.message_handler(commands = ["admin"])
	def CommandAdmin(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Создание дополнительных свойств.
		User.set_property("mailing_caption", None, force = False)
		User.set_property("mailing_content", [], force = False)
		User.set_property("button_label", None, force = False)
		User.set_property("button_link", None, force = False)
		User.set_property("sampling", None, force = False)
		User.set_property("mailing", False, force = False)
		# Получение слов в сообщении.
		MessageWords = Message.text.split(" ")

		# Если указывался пароль.
		if not User.has_permissions("admin") and len(MessageWords) == 2:
			# Выдача прав администратора.
			User.add_permissions("admin")

			# Если пароль верный.
			if MessageWords[1] == password:
				bot.send_message(
					chat_id = Message.chat.id,
					text = "Пароль принят. Доступ разрешён.",
					reply_markup = ReplyKeyboards().admin()
				)

			else:
				# Отправка сообщения: доступ запрещён.
				bot.send_message(
					chat_id = Message.chat.id,
					text = "Неверный пароль."
				)

		else:

			# Если пользователь имеет права администратора.
			if User.has_permissions("admin"):
				# Отправка сообщения: доступ разрешён.
				bot.send_message(
					chat_id = Message.chat.id,
					text = "Доступ разрешён.",
					reply_markup = ReplyKeyboards().admin()
				)

			else:
				# Отправка сообщения: доступ запрещён.
				bot.send_message(
					chat_id = Message.chat.id,
					text = "Доступ запрещён."
				)

def InitializeReplyKeyboard(bot: TeleBot, users: UsersManager):
	"""
	Набор декораторов: Reply-кнопки.
		bot – экземпляр бота;\n
		users – менеджер пользователей.
	"""

	# Обработка кнопки: 🎯 Выборка.
	@bot.message_handler(content_types = ["text"], regexp = "🎯 Выборка")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Установка ожидаемого типа.
		User.set_expected_type(UserInput.Sampling.value)
		# Отправка сообщения: введите выборку.
		bot.send_message(
			chat_id = Message.chat.id,
			text = f"*Укажите выборку*\n\nТекущее количество пользователей: {len(users.users)}",
			parse_mode = "MarkdownV2",
			reply_markup = InlineKeyboards().sampling(User)
		)

	# Обработка кнопки: 🕹️ Добавить кнопку.
	@bot.message_handler(content_types = ["text"], regexp = "🕹️ Добавить кнопку")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Установка ожидаемого типа.
		User.set_expected_type(UserInput.ButtonLabel.value)
		# Отправка сообщения: введите подпись.
		bot.send_message(
			chat_id = Message.chat.id,
			text = "Введите подпись для кнопки.",
			reply_markup = ReplyKeyboards().cancel()
		)

	# Обработка кнопки: ✅ Завершить.
	@bot.message_handler(content_types = ["text"], regexp = "✅ Завершить")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Установка ожидаемого типа.
		User.set_expected_type(None)
		# Чистка временных свойств.
		User.clear_temp_properties()
		# Отправка сообщения: отправьте сообщение.
		bot.send_message(
			chat_id = Message.chat.id,
			text = "Сообщение сохранено.",
			reply_markup = ReplyKeyboards().mailing(User)
		)

	# Обработка кнопки: ❌ Закрыть.
	@bot.message_handler(content_types = ["text"], regexp = "❌ Закрыть")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Отправка сообщения: панель управления закрыта.
		bot.send_message(
			chat_id = Message.chat.id,
			text = "Панель управления закрыта.",
			reply_markup = ReplyKeyboard().AddMenu(User)
		)

	# Обработка кнопки: 🟢 Запустить.
	@bot.message_handler(content_types = ["text"], regexp = "🟢 Запустить")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Привязка рассыльщика к пользователю.
		User.set_object("mailer", Mailer(bot))
		
		# Если сообщение не задано.
		if not User.get_property("mailing_caption") and not User.get_property("mailing_content"):
			# Отправка сообщения: сообщение не задано.
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы не задали сообщение для рассылки."
			)

		else:
			# Просмотр сообщения.
			User.get_object("mailer").start_mailing(User, users)

	# Обработка кнопки: ↩️ Назад.
	@bot.message_handler(content_types = ["text"], regexp = "↩️ Назад")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Отправка сообщения: статистика недоступна.
		bot.send_message(
			chat_id = Message.chat.id,
			text = "Панель управления.",
			reply_markup = ReplyKeyboards().admin()
		)

	# Обработка кнопки: ❌ Отмена.
	@bot.message_handler(content_types = ["text"], regexp = "❌ Отмена")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Установка ожидаемого типа.
		User.set_expected_type(None)

		try:
			# Возвращение временных свойств.
			Caption = User.get_property("temp_mailing_caption")
			Content = User.get_property("temp_mailing_content")
			User.clear_temp_properties()
			User.set_property("mailing_caption", Caption)
			User.set_property("mailing_content", Content)
			
		except: pass

		# Отправка сообщения: действие отменено.
		bot.send_message(
			chat_id = Message.chat.id,
			text = "Действие отменено.",
			reply_markup = ReplyKeyboards().mailing(User)
		)

	# Обработка кнопки: 🔴 Остановить.
	@bot.message_handler(content_types = ["text"], regexp = "🔴 Остановить")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Отправка сигнала для остановки рассылки.
		User.set_property("mailing", None)

	# Обработка кнопки: 🔎 Просмотр.
	@bot.message_handler(content_types = ["text"], regexp = "🔎 Просмотр")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		
		# Если сообщение не задано.
		if not User.get_property("mailing_caption") and not User.get_property("mailing_content"):
			# Отправка сообщения: сообщение не задано.
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Вы не задали сообщение для рассылки."
			)

		else:
			# Просмотр сообщения.
			Mailer(bot).send_message(User, User.id)

	# Обработка кнопки: 👤 Рассылка.
	@bot.message_handler(content_types = ["text"], regexp = "👤 Рассылка")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Отправка сообщения: статистика недоступна.
		bot.send_message(
			chat_id = Message.chat.id,
			text = "Управление рассылкой.",
			reply_markup = ReplyKeyboards().mailing(User)
		)

	# Обработка кнопки: ✏️ Редактировать.
	@bot.message_handler(content_types = ["text"], regexp = "✏️ Редактировать")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Установка ожидаемого типа.
		User.set_expected_type(UserInput.Message.value)
		# Установка временных свойств.
		Caption = User.get_property("mailing_caption")
		Content = User.get_property("mailing_content")
		User.set_temp_property("temp_mailing_caption", Caption)
		User.set_temp_property("temp_mailing_content", Content)
		# Чистка текущих свойств.
		User.set_property("mailing_caption", None)
		User.set_property("mailing_content", [])
		# Отправка сообщения: отправьте сообщение.
		bot.send_message(
			chat_id = Message.chat.id,
			text = "Отправьте сообщение, которое будет использоваться в рассылке.\n\nЕсли вы прикрепляете несколько вложений, для их упорядочивания рекомендуется выполнять загрузку файлов последовательно.",
			reply_markup = ReplyKeyboards().editing()
		)

	# Обработка кнопки: 📊 Статистика.
	@bot.message_handler(content_types = ["text"], regexp = "📊 Статистика")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Сбор статистики.
		PremiumUsersCount = len(users.premium_users)
		UsersCount = len(users.users)
		# Отправка сообщения: статистика.
		bot.send_message(
			chat_id = Message.chat.id,
			text = f"*📊 Статистика*\n\n👤 Всего пользователей: {UsersCount}\n⭐ С Premium\\-подпиской: {PremiumUsersCount}",
			parse_mode = "MarkdownV2"
		)

	# Обработка кнопки: 🕹️ Удалить кнопку.
	@bot.message_handler(content_types = ["text"], regexp = "🕹️ Удалить кнопку")
	def Button(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)
		# Удаление данных кнопки.
		User.set_property("button_label", None)
		User.set_property("button_link", None)
		# Отправка сообщения: кнопка удалена.
		bot.send_message(
			chat_id = Message.chat.id,
			text = "Кнопка удалена.",
			reply_markup = ReplyKeyboards().mailing(User)
		)

def InitializeText(bot: TeleBot, message: types.Message, user: UserData) -> bool:
	"""
	Дополнительная обработка: текст.
		bot – экземпляр бота;\n
		message – сообщение;\n
		user – пользователь.
	"""

	# Если пользователь имеет права администратора и задано ожидаемое значение.
	if user.has_permissions("admin") and user.expected_type:

		# Если ожидается сообщение для рассылки.
		if user.expected_type == UserInput.Message.value:
			# Запоминание подписи кнопки.
			user.set_property("mailing_caption", message.html_text)

			return True

		# Если ожидается подпись кнопки.
		if user.expected_type == UserInput.ButtonLabel.value:
			# Запоминание подписи кнопки.
			user.set_property("button_label", message.text)
			# Установка ожидаемого типа.
			user.set_expected_type(UserInput.ButtonLink.value)
			# Отправка сообщения: отправьте ссылку.
			bot.send_message(
				chat_id = message.chat.id,
				text = "Отправьте ссылку, которая будет помещена в кнопку.",
				reply_markup = ReplyKeyboards().cancel()
			)

			return True
		
		# Если ожидается сообщение для рассылки.
		if user.expected_type == UserInput.ButtonLink.value:
			# Запоминание подписи кнопки.
			user.set_property("button_link", message.text)
			# Установка ожидаемого типа.
			user.set_expected_type(None)
			# Отправка сообщения: кнопка прикреплена.
			bot.send_message(
				chat_id = message.chat.id,
				text = "Кнопка прикреплена к сообщению.",
				reply_markup = ReplyKeyboards().mailing(user)
			)

			return True

def InitializeInlineKeyboard(bot: TeleBot = None, users: UsersManager = None):
	"""
	Набор декораторов: Inline-кнопки.
		bot – экземпляр бота;\n
		users – менеджер пользователей.
	"""

	# Обработка Inline-кнопки: выборка.
	@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("sampling"))
	def InlineButton(Call: types.CallbackQuery):
		# Авторизация пользователя.
		User = users.auth(Call.from_user)
		# Изменение свойств пользователя.
		if Call.data.endswith("all"): User.set_property("sampling", None)
		if Call.data.endswith("last"): User.set_property("sampling", 1000)
		# Ответ на запрос.
		bot.answer_callback_query(Call.id)
		# Удаление сообщения.
		bot.delete_message(
			chat_id = User.id,
			message_id = Call.message.id
		)

		# Отправка сообщения: выборка установлена.
		if not Call.data.endswith("cancel"): bot.send_message(
			chat_id = User.id,
			text = "Выборка установлена.",
			reply_markup = ReplyKeyboards().mailing(User)
		)
			
		else:
			# Сброс ожидаемого типы.
			User.set_expected_type(None)

def InitializeFiles(bot: TeleBot, message: types.Message = None, user: UserData = None) -> bool:
	"""
	Дополнительная обработка: файлы.
		bot – экземпляр бота;\n
		message – сообщение;\n
		user – пользователь.
	"""

	# Если от администратора ожидается сообщение для рассылки.
	if user.has_permissions("admin") and user.expected_type == UserInput.Message.value:
		# Если есть подпись, записать её.
		if message.caption: user.set_property("mailing_caption", message.html_caption)
		# Сохранение данных о вложении.
		if message.content_type == "audio": user.get_property("mailing_content").append({"type": "audio", "file_id": message.audio.file_id})
		elif message.content_type == "document": user.get_property("mailing_content").append({"type": "document", "file_id": message.document.file_id})
		elif message.content_type == "video": user.get_property("mailing_content").append({"type": "video", "file_id": message.video.file_id})
	
def InitializePhoto(bot: TeleBot, users: UsersManager):
	"""
	Набор декораторов: фото.
		bot – экземпляр бота;\n
		users – менеджер пользователей.
	"""

	# Обработка файла.				
	@bot.message_handler(content_types = ["photo"])
	def File(Message: types.Message):
		# Авторизация пользователя.
		User = users.auth(Message.from_user)

		# Если от администратора ожидается сообщение для рассылки.
		if User.has_permissions("admin") and User.expected_type == "message":
			# Если есть подпись, записать её.
			if Message.caption: User.set_property("mailing_caption", Message.html_caption)
			# Сохранение данных о вложении.
			User.get_property("mailing_content").append({"type": "photo", "file_id": Message.photo[-1].file_id})