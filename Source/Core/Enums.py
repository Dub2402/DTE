import enum

class TrashMessagesTypes(enum.Enum):
	greeting = "greeting"
	gender = "gender"
	new_event = "new_event"
	my_events = "my_events"
	settings_notifications = "settings_notifications"

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

class PropertiesUser(enum.Enum):
	working_event_id = "working_event_id"