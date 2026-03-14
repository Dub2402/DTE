from Source.Modules.Eventer import Eventer
from Source.Core.Enums import BotModes, TrashMessagesTypes

from dublib.TelebotUtils import TeleMaster
from dublib.Methods.Data import ToIterable

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
	from dublib.TelebotUtils import UserData

	from telebot import TeleBot

class ExtendedUser:
	"""Расширенные данные пользователя."""

	@property
	def bot_mode(self) -> BotModes:
		"""Режим работы бота."""

		return BotModes(self.__user.get_property("mode"))

	@property
	def call(self) -> str | None:
		"""Обращение к пользователю."""

		return self.__user.get_property("call")
	
	@property
	def is_male(self) -> bool | None:
		"""Состояние: имеет ли пользователь мужской пол."""

		return self.__user.get_property("is_male")
	
	@property
	def new_user(self) -> bool: 
		"""Состояние новый ли пользователь."""

		return self.__user.get_property("new_user")

	@property
	def user(self) -> UserData:
		"""Данные пользователя."""

		return self.__user

	@property
	def eventer(self) -> Eventer:
		"""Обработчик событий."""

		return self.__eventer

	def __get_messages_id(self, types: Iterable[str] | None = None) -> tuple[int]:
		"""
		Возвращает последовательность ID сообщений по заданным типам.

		:param types: Типы для поиска.
		:type types: Iterable[str] | None
		:return: Последовательность ID сообщений.
		:rtype: tuple[int]
		"""

		MessagesID = list()

		if types is None:
			for MessageID in self.__user.get_property("trash_messages"):
				MessageID: str
				MessageID = int(MessageID.split(":")[0])
				MessagesID.append(MessageID)

		else:
			for MessageID in self.__user.get_property("trash_messages"):
				MessageID: str

				for CurrentType in types:
					if ":" in MessageID and MessageID.endswith(CurrentType):
						MessageID = int(MessageID.split(":")[0])
						MessagesID.append(MessageID)

		return tuple(MessagesID)

	def __init__(self, user: "UserData"):
		"""
		Расширенные данные пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""
		
		self.__user = user

		self.__user.set_property("trash_messages", list(), force = False)

		self.__eventer = Eventer(self.__user)

	def delete_trash_messages(self, bot: "TeleBot", types: str | Iterable[str] | None = None):
		"""
		Удаляет запомненные ранее сообщения.

		:param bot: Бот Telegram.
		:type bot: TeleBot
		:param types: Один или несколько типов сообщений. При отсутствии спецификации удаляет все запомненные.
		:type types: str | Iterable[str] | None
		"""

		masterbot = TeleMaster(bot)

		if not types:
			MessagesID = self.__get_messages_id()
			masterbot.safely_delete_messages(self.__user.id, MessagesID, complex = True)
			
		else:
			types = ToIterable(types)
			MessagesID = self.__get_messages_id(types)
			masterbot.safely_delete_messages(self.__user.id, MessagesID, complex = True)

	def remember_trash_message(self, message_id: int, type: TrashMessagesTypes | None = None):
		"""
		Запоминает сообщение для удаления в будущем.

		:param message_id: ID сообщения.
		:type message_id: int
		:param type: Тип сообщения. Может содержать только латиницу, цифры и нижние подчёркивания.
		:type type: str | None
		:raise ValueError: Выбрасывается при невалидном типе.
		"""

		Messages: list[str] = self.__user.get_property("trash_messages")
		NewMessage = str(message_id)

		if type: NewMessage += f":{type.value}"

		Messages.append(NewMessage)
		self.__user.set_property("trash_messages", Messages)
