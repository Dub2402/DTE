import enum
import os

# =====================================================================
# 1. СИСТЕМНЫЕ ПУТИ 
# =====================================================================

class MediaPath(enum.Enum):
	start = "Resources/Media/start.jpg"
	qr_code_en = "Resources/Media/qr-code_en.jpg"
	qr_code_ru = "Resources/Media/qr-code_ru.jpg"

	@property
	def folder(self) -> str:
		"""Автоматически возвращает путь к папке, в которой лежит файл."""
		
		return os.path.dirname(self.value)

class ExcelFilesPath(enum.Enum):
	gaslighter = "Resources/Modes/Газлайтер.xlsx"
	buddy = "Resources/Modes/Кореш.xlsx"
	motivator = "Resources/Modes/Мотиватор.xlsx"
	sweetie = "Resources/Modes/Няшка.xlsx"

	@property
	def folder(self) -> str:
		"""Автоматически возвращает путь к папке, в которой лежит файл."""
		return os.path.dirname(self.value)

# =====================================================================
# 2. РЕЖИМЫ БОТА
# =====================================================================

class BotModes(enum.Enum):
	classic = "classic"
	sweetie = "sweetie"
	buddy = "buddy"
	motivator = "motivator"
	gaslighter = "gaslighter"
	random = "random"

class ConfirmTypes(enum.Enum):
	approve_18 = "approve"
	apply = "apply"

# =====================================================================
# 3. ЛОГИКА БОТА
# =====================================================================

class StatusWorking(enum.Enum):
	new = "new"
	hot_fix = "hot_fix"
	change = "change"

class TrashMessagesTypes(enum.Enum):
	acquaintance = "acquaintance"
	events = "events"
	disable_reminders = "disable_reminders"
	change_reminders = "change_reminders"
	mode_bot = "mode_bot"

class RemindersTypes(enum.Enum):
	today = "today"
	everyday = "everyday"
	once = "once"