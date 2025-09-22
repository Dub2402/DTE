from dublib.TelebotUtils.Users import UserData, UsersManager
from dublib.Engine.GetText import _

from telebot import TeleBot, types

class Data:

	@property
	def mode(self):
		"""Режим бота."""

		if not self.__User.has_property("mode"): self.__User.set_property("mode", "classic")
		return self.__User.get_property("mode")

	def __init__(self, user: UserData):
		"""
		Контейнер бонусных данных пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__User = user

class InlineTemplates:
	"""Режимы ботов."""

	def modes_bot():

		menu = types.InlineKeyboardMarkup()

		modes = {
			_("✅ Классик (по умолчанию)"): "classic",
			_("👼 Няшка"): "sweetie",
			_("🍺 Кореш"): "buddy",
			_("💪 Мотиватор"): "motivator",
			_("🦖 Газлайтер (18+)"): "approve_18",
			_("🚦 Рандом"): "random",
			_("🔙 Back"): "delete_mode",
		}

		for string in modes.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = modes[string]), row_width = 1)

		return menu
	
	def use_mode():

		menu = types.InlineKeyboardMarkup()

		modes = {
			_("Применить"): "2",
			_("🔙 Назад"): "3"
		}

		for string in modes.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = modes[string]), row_width = 1)

		return menu
	
	def is_18():

		menu = types.InlineKeyboardMarkup()

		modes = {
			_("Да"): "gaslighter",
			_("Нет"): "1"
		}

		for string in modes.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = modes[string]), row_width = 2)

		return menu

class Decorators:
	"""Набор декораторов."""

	def __init__(self, modes: "Modes"):
		self.__modes = modes
		
	def inline_keyboards(self):
		"""Обработка inline_keyboards."""

		@self.__modes.bot.callback_query_handler(func = lambda Callback: Callback.data == "bot_mode")
		def choice_bot_mode(Call: types.CallbackQuery):
			user = self.__modes.users.auth(Call.from_user)

			self.__modes.bot.send_message(
				chat_id = Call.message.chat.id,
				text = "Здесь вы можете выбрать режим бота, а именно то, как он будет с вами общаться:",
				parse_mode = "HTML",
				reply_markup = InlineTemplates.modes_bot()
				)
			
			self.__modes.bot.answer_callback_query(Call.id)

		@self.__modes.bot.callback_query_handler(func = lambda Callback: Callback.data == "approve_18")
		def choice_bot_mode(Call: types.CallbackQuery):
			user = self.__modes.users.auth(Call.from_user)

			text_approval = (
				"<b>" + _("Осторожно! ") + "</b>" + _("Следующий материал несёт в себе нецензурные и оскорбительные высказывания. Он предназначен строго для лиц от 18 лет!" + "\n"),
				"<b>" + _("Уверены в том, что хотите просмотреть содержимое? Вам есть 18?") + "</b>"
				)

			self.__modes.bot.send_message(
				chat_id = Call.message.chat.id,
				text = "\n".join(text_approval),
				parse_mode = "HTML",
				reply_markup = InlineTemplates.is_18()
				)
			
			self.__modes.bot.answer_callback_query(Call.id)

		@self.__modes.bot.callback_query_handler(func = lambda Callback: Callback.data in ("classic", "sweetie", "buddy", "motivator", "gaslighter", "random"))
		def choice_bot_mode(Call: types.CallbackQuery):
			user = self.__modes.users.auth(Call.from_user)

			mode = Call.data

			texts = {
			"classic": (
				"<b>" + _("Классик ") + "</b>" + _("- это режим бота, который общается с вами в формально-официальном тоне. Все чётко, без лишних слов и по существу. ") + "<i>" +  "Пример:" + "</i>\n",
				"<b>" + _("День рождения ") + "</b>" + _("наступит через") + "<b>" +  " 41 " + "</b>" + _("день!")
				),
			"sweetie": (
				"<b>" + _("Няшка ") + "</b>" + _("- это режим бота, который общается с вами ласково и нежно. Его задача вызвать у вас теплые эмоции и расположить. ") + "<i>" +  "Пример:" + "</i>\n",
				_("Солнышко моё! ") + "<b>" + _("День рождения ") + "</b>" + _("наступит через") + "<b>" +  " 41 " + "</b>" + _("день! Главное не забывай улыбаться! ☺️")
				),
			"buddy": (
				"<b>" + _("Кореш ") + "</b>" + _("- это режим бота, который имитирует вашего давнего приятеля, с которым вы хорошо знакомы. Он общается довольно фамильярно. ") + "<i>" +  "Пример:" + "</i>\n",
				_("Братуухаа! ") + "<b>" + _("День рождения ") + "</b>" + _("наступит через") + "<b>" +  " 41 " + "</b>" + _("день! Давай там, хвост пистолетом, обнял!")
				),
			"motivator": (
				"<b>" + _("Мотиватор ") + "</b>" + _("- это режим бота, который старается зарядить вас позитивной энергией, взбодрить и вызвать прилив сил. ") + "<i>" +  "Пример:" + "</i>\n",
				_("Эй, кто тут самый крутой?) ") + "<b>" + _("День рождения ") + "</b>" + _("наступит через") + "<b>" +  " 41 " + "</b>" + _("день! А пока, хватай удачу за хвост!")
				),
			"gaslighter": (
				"<b>" + _("Газлайтер ") + "</b>" + _("- это режим бота, который будет оскорблять вас, всячески унижать, в общем относится, как к полному ничтожеству. ") + "<i>" +  "Пример:" + "</i>\n",
				_("Слышишь, у#бище! ") + "<b>" + _("День рождения ") + "</b>" + _("наступит через") + "<b>" +  " 41 " + "</b>" + _("день! Живи, пока я тебе п#зды не дал!")
				),
			"random": (
				"<b>" + _("Рандом ") + "</b>" + _("- это режим бота, который совмещает в себе все образы, представленные выше, и чередует их на свое усмотрение. ") + "\n",
				_("Сегодня вам может написать Няшка, завтра - Мотиватор, а послезавтра пожалует и сам Газлайтер.")
				),
			}
			
			self.__modes.bot.send_message(
				chat_id = Call.message.chat.id,
				text = "\n".join(texts[mode]),
				parse_mode = "HTML",
				reply_markup = InlineTemplates.use_mode()
				)
			
			self.__modes.bot.answer_callback_query(Call.id)

class Modes:
	"""Главный класс, отвечающий за режимы бота."""

	@property
	def users(self):
		"""Данные пользователей."""
		return self.__users
	
	@property
	def bot(self):
		"""Telegram bot."""

		return self.__bot
	
	@property
	def decorators(self):
		"""Набор декораторов."""

		return self.__Decorators

	def __init__(self, usersmanager: UsersManager, bot: TeleBot):

		self.__users = usersmanager
		self.__bot = bot

		self.__Decorators = Decorators(self)