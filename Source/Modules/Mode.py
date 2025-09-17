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
			_("🦖 Газлайтер (18+)"): "gaslighter",
			_("🚦 Рандом"): "random",
			_("🔙 Back"): "delete_mode",
		}

		for string in modes.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = modes[string]), row_width = 1)

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

		@self.__modes.bot.callback_query_handler(func = lambda Callback: Callback.data in ("classic", "sweetie", "buddy", "motivator", "gaslighter", "random"))
		def choice_bot_mode(Call: types.CallbackQuery):
			user = self.__modes.users.auth(Call.from_user)

			texts = {
			"classic": _("Классик - это режим бота, который общается с вами в формально-официальном тоне. Все чётко, без лишних слов и по существу. Пример: День рождения наступит через 41 день!"),
			"sweetie": _("👼 Няшка"),
			"buddy": _("🍺 Кореш"),
			"motivator": _("💪 Мотиватор"),
			"gaslighter": _("🦖 Газлайтер (18+)"),
			"random": _("🚦 Рандом")
		}


			self.__modes.bot.send_message(
				chat_id = Call.message.chat.id,
				text = "1",
				parse_mode = "HTML",
				reply_markup = InlineTemplates.modes_bot()
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