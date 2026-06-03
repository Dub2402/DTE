from Source.Modules.Eventer import Eventer
from Source.Core.Enums import BotModes, TrashMessagesTypes, StatusWorking

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
	def working_event_id(self) -> int | None:
		"""Cтатус работы с ботом."""

		return self.__user.get_property("working_event_id")
	
	@property
	def status_working(self) -> str:
		"""Cтатус работы с ботом."""

		return self.__user.get_property("status_working")

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
	
	def __delete(self, MessagesID: tuple[int]):
		"""
		Удаление данных об удалённых сообщениях в данных пользователя.

		:param MessagesID: Список id сообщений, которые были удалены.
		:type MessagesID: tuple[int]
		"""

		Messages_with_types: list[str] = self.__user.get_property("trash_messages")
	
		for MessageID in MessagesID:
			prefix = f"{MessageID}:"
			for item in Messages_with_types:
				if item.startswith(prefix):
					Messages_with_types.remove(item)

		self.__user.set_property("trash_messages", Messages_with_types)
		
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

		if not types: MessagesID = self.__get_messages_id()
			
		else:
			types = ToIterable(types)
			MessagesID = self.__get_messages_id(types)

		masterbot.safely_delete_messages(self.__user.id, MessagesID, complex = True)
		self.__delete(MessagesID)
		
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

	def switching_working_event_id(self, event_id: int | None = None):
		"""
		Переключает на id события с которым мы в данный момент работаем.

		:param event_id: Id cобытия, с которым мы в данный момент работаем, defaults to None
		:type event_id: int | None, optional
		"""

		return self.__user.set_property("working_event_id", event_id)

	def switching_status_working(self, status: StatusWorking):
		"""
		Меняет статус работы с ботом.

		:param status: Статус работы с ботом.
		:type status: StatusWorking
		"""

		return self.__user.set_property("status_working", status.value)