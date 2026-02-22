from Source.UI import InlineKeyboards as MainInlineKeyboards
from Source.Core.Enums import BotModes
from . import InlineKeyboards
from .Titler import get_bot_mode_title

from dublib.TelebotUtils import TeleMaster
from dublib.Engine.GetText import _

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from dublib.TelebotUtils import UsersManager

	from telebot import types, TeleBot

class Decorators:
	"""Набор декораторов."""

	def __init__(self, bot: "TeleBot", users: "UsersManager"):
		
		self.__bot = bot
		self.__users = users

		self.__masterbot = TeleMaster(self.__bot)
		
	def inline_keyboards(self):
		"""Обработка Inline-кнопок."""

		@self.__bot.callback_query_handler(func = lambda Callback: Callback.data == "bot_mode")
		def choice_bot_mode(Call: types.CallbackQuery):
			self.__users.auth(Call.from_user)
			
			self.__bot.send_message(
				chat_id = Call.message.chat.id,
				text = "Здесь вы можете выбрать режим бота, а именно то, как он будет с вами общаться:",
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.modes_bot()
			)
			
			self.__bot.answer_callback_query(Call.id)

		@self.__bot.callback_query_handler(func = lambda Callback: Callback.data == "approve_18")
		def approve_18(Call: types.CallbackQuery):
			self.__users.auth(Call.from_user)

			warning_text = (
				"<b>" + _("Осторожно! ") + "</b>" + _("Следующий материал несёт в себе нецензурные и оскорбительные высказывания. Он предназначен строго для лиц от 18 лет!" + "\n"),
				"<b>" + _("Уверены в том, что хотите просмотреть содержимое? Вам есть 18?") + "</b>"
			)
			
			self.__bot.send_message(
				chat_id = Call.message.chat.id,
				text = "\n".join(warning_text),
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.answer()
			)
			
			self.__masterbot.safely_delete_messages(Call.message.chat.id, Call.message.id)

		@self.__bot.callback_query_handler(func = lambda Callback: Callback.data in ("classic", "sweetie", "buddy", "motivator", "gaslighter", "random"))
		def bot_mode(Call: types.CallbackQuery):
			self.__users.auth(Call.from_user)

			basic_text = "<b>" + get_bot_mode_title(BotModes(Call.data).value) + " </b>" + _("- это режим бота, который" + " ")
			end_text = "<i>" +  _("Пример:") + "</i>\n"
			event_text = "<b>" + _("День рождения ") + "</b>" + _("наступит через") + " <b>41</b> " + _("день!")

			texts = {
				BotModes.classic:(
					basic_text + _("общается с вами в формально-официальном тоне. Все чётко, без лишних слов и по существу. ") + end_text,
					event_text
				),
				BotModes.sweetie: (
					basic_text + _("общается с вами ласково и нежно. Его задача вызвать у вас теплые эмоции и расположить. ") + end_text,
					_("Солнышко моё! ") + event_text + _("Главное не забывай улыбаться! ☺️")
				),
				BotModes.buddy: (
					basic_text + _("имитирует вашего давнего приятеля, с которым вы хорошо знакомы. Он общается довольно фамильярно. ") + end_text,
					_("Братуухаа! ") + event_text + _("Давай там, хвост пистолетом, обнял!")
				),
				BotModes.motivator: (
					basic_text + _("старается зарядить вас позитивной энергией, взбодрить и вызвать прилив сил. ") + end_text,
					_("Эй, кто тут самый крутой?) ") + event_text + _("А пока, хватай удачу за хвост!")
				),
				BotModes.gaslighter: (
					basic_text + _("будет оскорблять вас, всячески унижать, в общем относится, как к полному ничтожеству. ") + end_text,
					_("Слышишь, у#бище! ") + event_text + _(" Живи, пока я тебе п#зды не дал!")
				),
				BotModes.random: (
					basic_text + _("совмещает в себе все образы, представленные выше, и чередует их на свое усмотрение. ") + "\n",
					_("Сегодня вам может написать Няшка, завтра - Мотиватор, а послезавтра пожалует и сам Газлайтер.")
				)
			}

			self.__bot.send_message(
				chat_id = Call.message.chat.id,
				text = "\n".join(texts[Call.data]),
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.use_mode(type_mode = Call.data)
			)
			
			self.__masterbot.safely_delete_messages(Call.message.chat.id, Call.message.id)

		@self.__bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("apply"))
		def apply_bot_mode(Call: types.CallbackQuery):
			self.__users.auth(Call.from_user)
			self.__masterbot.safely_delete_messages(Call.message.chat.id, Call.message.id)

			type_mode = BotModes(Call.data.split("_")[-1])
			warning_text = "\n\n<b><i>" + _("Тем самым вы подтверждаете, что вам есть 18 лет!") + "</i></b>" if type_mode in (BotModes.gaslighter, BotModes.random) else None

			self.__bot.send_message(
				chat_id = Call.message.chat.id,
				text = _("Хотите применить режим бота") + "<b> " + get_bot_mode_title(type_mode) + "</b>" + "?" + warning_text,
				parse_mode = "HTML",
				reply_markup = InlineKeyboards.answer(type_mode)
			)
			
			self.__bot.answer_callback_query(Call.id)

		@self.__bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("yes"))
		def save_bot_mode(Call: types.CallbackQuery):
			user = self.__users.auth(Call.from_user)

			type_mode = BotModes(Call.data.split("_")[-1])
			suffix = "(18+)" if type_mode == BotModes.gaslighter else None

			self.__bot.send_message(
				chat_id = Call.message.chat.id,
				text = _("Режим") + "<b> " + get_bot_mode_title(type_mode, True, suffix) + "</b> " + _("активирован") + "!",
				parse_mode = "HTML",
				reply_markup = MainInlineKeyboards.delete("Окей")
			)
			
			self.__masterbot.safely_delete_messages(Call.message.chat.id, Call.message.id)

			user.set_property("mode", type_mode)
