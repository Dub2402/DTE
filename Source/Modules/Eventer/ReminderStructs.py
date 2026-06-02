from dataclasses import dataclass
from datetime import time

@dataclass(frozen = True)
class ReminderTime:
	hour: int
	minute: int

	def to_string(self) -> str:
		"""
		Строковое отображение времени напоминания пользователя.

		:return: Строка времени напоминания.
		:rtype: str
		"""

		return f"{self.hour:02d}:{self.minute:02d}"
	
	def to_time(self) -> time:
		"""
		Отображение времени напоминания пользователя в формате time.

		:return: Время напоминания в time.
		:rtype: time
		"""
		return time(hour=self.hour, minute=self.minute)

@dataclass(frozen = True)
class ReminderData:
	days_before_event: int
	time: ReminderTime | None

	def to_dict(self) -> dict[str, int | str | None]:
		"""
		Словарное отображение напоминания пользователя.

		:return: Словарь напоминания.
		:rtype: dict[str, int | str | None]
		"""

		return {
			"days": self.days_before_event,
			"time": self.time.to_string() if self.time else None
		}
