import enum

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

class MediaPath(enum.Enum):
	start = "Media/start.jpg"
	qr_code_en = "Media/qr-code_en.jpg"
	qr_code_ru = "Media/qr-code_ru.jpg"


	