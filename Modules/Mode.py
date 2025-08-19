from dublib.TelebotUtils.Users import UserData
from dublib.Engine.GetText import _

class ModeBot:

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

	def modes_bot():

		modes = {
			_("✅ Классик (по умолчанию)"): "classic",
			_("👼 Няшка"): "sweetie",
			_("🍺 Кореш"): "buddy",
			_("💪 Мотиватор"): "motivator",
			_("🦖 Газлайтер (18+)"): "gaslighter",
			_("🚦 Рандом"): "random",
			_("🔙 Back"): "delete_mode",
		}
