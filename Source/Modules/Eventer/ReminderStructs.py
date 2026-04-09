from dataclasses import dataclass

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
