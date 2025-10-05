from dublib.TelebotUtils.Users import UserData, UsersManager
from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _

from telebot import TeleBot, types
from types import MappingProxyType
from typing import Any, Literal

import logging

ModesParameters = MappingProxyType(
	{
	"type": "classic"
	}
)

class Data:
	"""Класс данных, связаных с режимом бота."""

	@property
	def type(self):
		"""Режим бота."""

		return self.__Data["type"]

	def __init__(self, user: UserData):
		"""
		Контейнер бонусных данных пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__User = user
	
		self.__Data = self.__ValidateDate()

	def __ValidateDate(self) -> dict[str, Any]:
		"""
		Проверяет валидность бонусных данных пользователя.

		:return: Данные пользователя.
		:rtype: dict[str, Any]
		"""
		
		if not self.__User.has_property("mode"):
			self.__User.set_property("mode", ModesParameters.copy())
			
		else:
			Data: dict = self.__User.get_property("mode")

			for Key in ModesParameters.keys():

				if Key not in Data.keys():
					Data[Key] = ModesParameters[Key]
					logging.debug(f"For user #{self.__User.id} key \"{Key}\" set to default.")

			self.__User.set_property("mode", Data)

		return self.__User.get_property("mode")
	
	def __SetParameter(self, key: Literal["type"], value: Any):
		"""
		Сохраняет параметры бонусных данных пользователя.

		:param key: Ключ параметра.
		:type key: Literal["type"]
		:param value: Значение параметра.
		:type value: Any
		"""
		
		self.__Data[key] = value
		
		self.save()

	def save(self):
		"""Сохраняет бонусные данные пользователя."""

		self.__User.set_property("mode", self.__Data)

	def set_type_mode(self, type_mode: str):
		"""
		Передаёт параметры для сохранения типа режим бота для пользователя.

		:param count: Режим бота.
		:type count: str
		"""

		self.__SetParameter("type", type_mode)

class InlineTemplates:
	"""Набор inline keyboards."""

	def modes_bot() -> types.InlineKeyboardMarkup:
		"""Выбор режимов бота.

		:return: inline keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		modes = {
			_("✅ Классик (по умолчанию)"): "classic",
			_("👼 Няшка"): "sweetie",
			_("🍺 Кореш"): "buddy",
			_("💪 Мотиватор"): "motivator",
			_("🦖 Газлайтер (18+)"): "approve_18",
			_("🚦 Рандом"): "random",
			_("🔙 Назад"): "delete_mode",
		}

		for string in modes.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = modes[string]), row_width = 1)

		return menu
	
	def use_mode(type_mode: str) -> types.InlineKeyboardMarkup:
		"""Возвращает клавиатуру с кнопкой применить режима бота.

		:param type_mode: название режима бота на английском языке.
		:type type_mode: str
		:return: inline keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()

		modes = {
			_("Применить"): f"apply_{type_mode}",
			_("🔙 Назад"): "bot_mode"
		}

		for string in modes.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = modes[string]), row_width = 1)

		return menu
	
	def answer(type_answer: str = "") -> types.InlineKeyboardMarkup:
		"""Возвращает клавиатуру ответа пользователя на вопрос.

		:param type_answer: тип ответа, defaults to ""
		:type type_answer: str, optional
		:return: inline keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		menu = types.InlineKeyboardMarkup()
		
		modes = {
				_("Да"): f"yes_{type_answer}",
				_("Нет"): "no"
			}

		if type_answer == "is_18+":
			modes = {
				_("Да"): "gaslighter",
				_("Нет"): "bot_mode"
			}

		for string in modes.keys(): menu.add(types.InlineKeyboardButton(string, callback_data = modes[string]), row_width = 2)

		return menu
	
	def delete_all() -> types.InlineKeyboardMarkup:
		"""Возвращает клавиатуру с итогом режима бота.

		:return: inline keyboard.
		:rtype: types.InlineKeyboardMarkup
		"""

		return types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text = "Окей", callback_data = "delete_all")]])

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
			
			self.__modes.master_bot.safely_delete_messages(
				Call.message.chat.id,
				Call.message.id
				)
			
			self.__modes.bot.answer_callback_query(Call.id)

		@self.__modes.bot.callback_query_handler(func = lambda Callback: Callback.data == "approve_18")
		def approve_18(Call: types.CallbackQuery):
			user = self.__modes.users.auth(Call.from_user)

			text_approval = (
				"<b>" + _("Осторожно! ") + "</b>" + _("Следующий материал несёт в себе нецензурные и оскорбительные высказывания. Он предназначен строго для лиц от 18 лет!" + "\n"),
				"<b>" + _("Уверены в том, что хотите просмотреть содержимое? Вам есть 18?") + "</b>"
				)
			self.__modes.bot.send_message(
				chat_id = Call.message.chat.id,
				text = "\n".join(text_approval),
				parse_mode = "HTML",
				reply_markup = InlineTemplates.answer(type_answer = "is_18+")
				)
			
			self.__modes.master_bot.safely_delete_messages(
				Call.message.chat.id,
				Call.message.id
				)
			
			self.__modes.bot.answer_callback_query(Call.id)

		@self.__modes.bot.callback_query_handler(func = lambda Callback: Callback.data in ("classic", "sweetie", "buddy", "motivator", "gaslighter", "random"))
		def bot_mode(Call: types.CallbackQuery):
			user = self.__modes.users.auth(Call.from_user)		

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
				text = "\n".join(texts[Call.data]),
				parse_mode = "HTML",
				reply_markup = InlineTemplates.use_mode(type_mode = Call.data)
				)
			
			self.__modes.master_bot.safely_delete_messages(
				Call.message.chat.id,
				Call.message.id
				)
			
			self.__modes.bot.answer_callback_query(Call.id)

		@self.__modes.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("apply"))
		def apply_bot_mode(Call: types.CallbackQuery):
			user = self.__modes.users.auth(Call.from_user)
			self.__modes.master_bot.safely_delete_messages(
				Call.message.chat.id,
				Call.message.id
				)
			type_mode = Call.data.split("_")[-1]

			if type_mode == "gaslighter" or type_mode == "random":
				self.__modes.bot.send_message(
				chat_id = Call.message.chat.id,
				text = _("Хотите применить режим бота") + "<b> " + self.__modes.type_modes[type_mode][-1] + "</b>" + "?\n\n<b>" + _("Тем самым вы подтверждаете, что вам есть 18 лет!") + "</b>",
				parse_mode = "HTML",
				reply_markup = InlineTemplates.answer(type_answer = type_mode)
				)

			else:
				self.__modes.bot.send_message(

					chat_id = Call.message.chat.id,
					text = _("Хотите применить режим бота") + "<b> " + self.__modes.type_modes[type_mode][-1] + "</b>" + "?",
					parse_mode = "HTML",
					reply_markup = InlineTemplates.answer(type_answer = type_mode)
					)
			
			self.__modes.bot.answer_callback_query(Call.id)

		@self.__modes.bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("yes"))
		def save_bot_mode(Call: types.CallbackQuery):
			user = self.__modes.users.auth(Call.from_user)

			self.__modes.bot.send_message(
				chat_id = Call.message.chat.id,
				text = _("Режим") + "<b> " + self.__modes.type_modes[Call.data.split("_")[-1]][0] + self.__modes.type_modes[Call.data.split("_")[-1]][-1] + "</b> " + _("активирован") + "!",
				parse_mode = "HTML",
				reply_markup = InlineTemplates.delete_all()
				)
			
			self.__modes.master_bot.safely_delete_messages(
				Call.message.chat.id,
				Call.message.id
				)
			
			self.__modes.bot.answer_callback_query(Call.id)

		@self.__modes.bot.callback_query_handler(func = lambda Callback: Callback.data == "delete_all")
		def save_bot_mode(Call: types.CallbackQuery):
			user = self.__modes.users.auth(Call.from_user)
			self.__modes.master_bot.safely_delete_messages(
				Call.message.chat.id,
				Call.message.id
				)
			
			self.__modes.bot.answer_callback_query(Call.id)

class Modes:
	"""Основной класс, отвечающий за режимы бота."""

	@property
	def users(self):
		"""Данные пользователей."""
		return self.__users
	
	@property
	def bot(self):
		"""Telegram bot."""

		return self.__bot
	
	@property
	def master_bot(self):
		"""TeleMaster bot."""

		return self.__master_bot
	
	@property
	def type_modes(self):
		"""Название режимов бота."""

		return self.__modes
	
	@property
	def decorators(self):
		"""Набор декораторов."""

		return self.__Decorators

	def __init__(self, usersmanager: UsersManager, bot: TeleBot):

		self.__users = usersmanager
		self.__bot = bot
		self.__master_bot = TeleMaster(self.__bot)

		self.__modes = {
			"classic": ["✅ ", "Классик"],
			"sweetie": ["👼 ", "Няшка"],
			"buddy": ["🍺 ", "Кореш"],
			"motivator": ["💪 ", "Мотиватор"],
			"gaslighter": ["🦖 ", "Газлайтер"],
			"random": ["🚦 ", "Рандом"]
			}

		self.__Decorators = Decorators(self)