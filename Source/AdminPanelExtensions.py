from Source.TeleBotAdminPanel import InlineKeyboards
from Source import TeleBotAdminPanel

from dublib.TelebotUtils import UsersManager

import telebot

def NewStatistics(bot: telebot.TeleBot, users: UsersManager, message: telebot.types.Message):
		"""
		Обрабатывает Reply-кнопку: 📊 Статистика
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			message – сообщение от пользователя.
		"""
		User = users.auth(message.from_user)

		UsersCount = len(users.users)
		BlockedUsersCount = 0
		Mans, Womans, Undefined = 0, 0, 0

		for user in users.users:
			if user.is_chat_forbidden: BlockedUsersCount += 1

			if user.has_property("Gender"):
				if user.get_property("Gender") == "man": Mans += 1
				elif user.get_property("Gender") == "woman": Womans += 1
				else: Undefined += 1

			else: Undefined += 1

		MansPercents = Mans / UsersCount * 100
		WomansPercents = Womans / UsersCount * 100
		UndefinedPercents =  Undefined / UsersCount * 100

		if str(MansPercents).endswith(".0"): MansPercents = int(MansPercents)
		if str(WomansPercents).endswith(".0"): WomansPercents = int(WomansPercents)
		if str(UndefinedPercents).endswith(".0"): UndefinedPercents = int(UndefinedPercents)

		Counts = [len(users.premium_users), len(users.get_active_users()), BlockedUsersCount]
		Percentages = [None, None, None]

		for Index in range(len(Counts)):
			Percentages[Index] = round(Counts[Index] / UsersCount * 100, 1)
			if str(Percentages[Index]).endswith(".0"): Percentages[Index] = int(Percentages[Index])

		Text = (
			"<b>📊 Статистика</b>\n",
			f"👤 Всего пользователей: <b>{UsersCount}</b>",
			f"⭐ Из них Premium: <b>{Counts[0]}</b> (<i>{Percentages[0]}%</i>)",
			f"🧩 Активных за сутки: <b>{Counts[1]}</b> (<i>{Percentages[1]}%</i>)",
			f"⛔ Заблокировали: <b>{Counts[2]}</b> (<i>{Percentages[2]}%</i>)",
			"",
			f"🧔🏻 Мужчин: <b>{Mans}</b> (<i>{MansPercents}%</i>)",
			f"👩🏼 Женщин <b>{Womans}</b> (<i>{WomansPercents}%</i>)",
			f"🌈 Не определились: <b>{Undefined}</b> (<i>{UndefinedPercents}%</i>)"
		)

		bot.send_message(
			chat_id = message.chat.id,
			text = "\n".join(Text),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.extract() 
		)


TeleBotAdminPanel.ReplyFunctions.Statistics = NewStatistics