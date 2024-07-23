from datetime import datetime, date

def CheckValidDate(Date: str)-> bool:
	try:
		datetime.fromisoformat(Date)
		return True
	except ValueError:
		return False

def Calculator(event) -> int:
	today = date.today()
	remains = (date.fromisoformat(event) - today).days
	
	return remains

def GetFreeID(Events) -> int:
	Increment = list()
	for key in Events.keys():
		Increment.append(key)
	Increment.sort()
	if not Increment:
		FreeID = 1
	else: 
		FreeID = Increment[-1]
		FreeID = int(FreeID) + 1

	return FreeID
		
