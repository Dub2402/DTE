from Source.TeleBotAdminPanel.Extractor import Extractor, CellData

from dublib.TelebotUtils import UserData

def GetBankingData(User: UserData) -> str | None:

	if User.has_property("Gender"):
		Gender = User.get_property("Gender")
		return Gender

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ В ВЫПИСКУ ДОПОЛНИТЕЛЬНЫХ КОЛОНОК <<<<< #
#==========================================================================================#

def get_gender(User: UserData) -> CellData:
	return CellData(GetBankingData(User))

Extractor.Columns["Пол"] = get_gender
