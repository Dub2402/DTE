from datetime import date
import dateparser

def CheckValidDate(Date: str)-> bool:
	try:
		dateparser.parse(Date, settings={'DATE_ORDER': 'DMY'}).date()
		return True
	except:
		return False

def Calculator(event: str) -> int:
	today = date.today()
	remains = (dateparser.parse(event, settings={'DATE_ORDER': 'DMY'}).date() - today).days
	
	return remains

def GetFreeID(Events: dict) -> int:
	Increment = list()
	for key in Events.keys(): Increment.append(int(key))
	Increment.sort()
	FreeID = 1
	if Increment: FreeID = max(Increment) + 1

	return FreeID
		
