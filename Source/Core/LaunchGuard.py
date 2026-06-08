from .Enums import MediaPath, ExcelFilesPath

from pathlib import Path
import itertools
import openpyxl
import logging
import os

class LaunchGuard:
	"""Проверяет наличие всех приватных данных, при отсутствии которых могут возникать критические ошибки или некорректная работа функций при работе бота."""

	def __init__(self):
		"""
		Инициализирует словарь приватных переменных окружения среды в зависимости от . 
		Генерирует кортеж названий столбцов таблиц c помощью  модуля ``itertools``.
		"""

		self.__config_manifest = {
			"required": ("TOKEN", ), 
			"optional": ("PASSWORD", "CHAT_ID")
		}

		genders = ("МУЖ", "ЖЕН")
		types = ("Ежедневные", "Разовые и день в день")
		numbers = ("1", "2")
		self.__required_headers = tuple(
			f"{gender} {types} {numbers}" 
			for gender, types, numbers in itertools.product(genders, types, numbers)
		)

	def check_all(self, language: str):
		"""Запускает глобальную проверку проекта. 
		При провале - происходит экстренное завершение процесса.

		:param language: Код языка.
		:type language: str
		"""
	
		logging.debug("🛡️ Проверка готовности бота к запуску.")
		critical_failed = False

		for environment_variable in self.__config_manifest["required"]:

			if not os.getenv(environment_variable):
				logging.critical(f"В .env отсутствует переменная '{environment_variable}'")
				critical_failed = True

		for environment_variable in self.__config_manifest["optional"]:

			if not os.getenv(environment_variable):
				logging.error(f"В .env отсутствует переменная '{environment_variable}'. Некоторые функции бота могут работать некорректно.")	

		for element in MediaPath:

			if os.path.exists(element.value):
				logging.debug(f"Файл \"{element.value}\" найден.")

			else:
				element_name = Path(element.value).stem

				if element_name.endswith(f"_{language}"):
					logging.error(f"Файл не найден \"{element.value}\". Некоторые функции бота могут работать некорректно.")
					critical_failed = True

				else:
					logging.warning(f"Файл \"{element.value}\" не найден [optional]. Некоторые функции бота могут работать некорректно.")

		for element in ExcelFilesPath:

			if not os.path.exists(element.value):
				logging.critical(f"Отсутствует файл таблицы '{element.value}'")
				critical_failed = True
					
		if critical_failed: 
			logging.critical("🛑 Запуск бота невозможен. Исправьте ошибки выше.")
			exit(-1)

		logging.info("🚀 Проверка Guard пройдена успешно. Система стабильна!")
