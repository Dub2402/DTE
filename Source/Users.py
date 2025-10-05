from dublib.TelebotUtils import UserData

class User:
	"""Осуществляет быстрый доступ к основным данным пользователя."""

	@property
	def call(self):
		"""Обращение к пользователю."""

		return self.__user.get_property("call")

	def __init__(self, user: UserData):
		"""Инициализация основных данных пользователя."""

		self.__user = user
