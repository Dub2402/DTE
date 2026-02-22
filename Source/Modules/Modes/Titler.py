from Source.Core.Enums import BotModes

from types import MappingProxyType

bot_modes_data = MappingProxyType({
	BotModes.classic: ("✅", "Классик"),
	BotModes.sweetie:("👼", "Няшка"),
	BotModes.buddy: ("🍺", "Кореш"),
	BotModes.motivator: ("💪", "Мотиватор"),
	BotModes.gaslighter: ("🦖", "Газлайтер"),
	BotModes.random: ("🚦", "Рандом")
})

def get_bot_mode_title(mode: BotModes, emoji: bool = False, suffix: str | None = None) -> str:
	"""
	Возвращает заголовок режима бота.

	:param mode: Режим бота.
	:type mode: BotModes
	:param emoji: Нужно ли добавить эмодзи к заголовку.
	:type emoji: bool
	:param suffix: Добавляемое значение.
	:type suffix: str
	:return: Заголовок режима бота.
	:rtype: str
	"""

	Title = bot_modes_data[mode][1]
	if emoji: Title = bot_modes_data[mode][0] + f" {Title}"
	if suffix: Title = f"{Title} {suffix}"

	return Title