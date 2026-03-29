import enum

class TrashMessagesTypes(enum.Enum):
	acquaintance = "acquaintance"
	events = "events"
	reminders = "reminders"

class BotModes(enum.Enum):
	classic = "classic"
	sweetie = "sweetie"
	buddy = "buddy"
	motivator = "motivator"
	gaslighter = "gaslighter"
	random = None

class MediaPath(enum.Enum):
	start = "Media/start.jpg"
	qr_code_en = "Media/qr-code_en.jpg"
	qr_code_ru = "Media/qr-code_ru.jpg"
