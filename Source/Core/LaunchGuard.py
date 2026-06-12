from .Enums import MediaPath, ExcelFilesPath
from setup_project import ExcelTemplater

from pathlib import Path
import logging
import enum
import sys
import os

class EnvironmentVariables(enum.Enum):
    TOKEN = "TOKEN"
    PASSWORD = "PASSWORD"
    CHAT_ID = "CHAT_ID"

class LaunchGuard:
    """Проверяет наличие всех приватных данных, при отсутствии которых могут возникать критические ошибки или некорректная работа функций при работе бота."""

    __supported_languages = ("ru", "en")
    __required_headers = ExcelTemplater.headers

    def __init__(self, language: str):
        self.__language = language

    def check_readiness(self):
        """Запускает глобальную проверку проекта. 
        При провале - происходит экстренное завершение процесса.

        :param language: Код языка.
        :type language: str
        """
    
        logging.info("🛡️  Проверка готовности бота к запуску.")

        is_critical_failed_env = self.__check_env_variable()
        is_critical_failed_media = self.__check_media_files()
        is_critical_failed_excel = self.__check_excel_files()

        if is_critical_failed_env or is_critical_failed_media or is_critical_failed_excel: 
            logging.critical("☠️  Запуск бота невозможен. Исправьте ошибки выше.")
            sys.exit(1)

        logging.info("🚀 Проверка Guard пройдена успешно. Система стабильна!")
    
    def __check_env_variable(self) -> bool:
        """Проверяет присутствуют ли все необходимые переменные окружения.

        :return: Статус: необходимо ли экстренное завершение процесса.
        :rtype: bool
        """

        is_critical_failed = False

        for environment_variable in EnvironmentVariables:

            if os.getenv(environment_variable.value):
                if environment_variable == EnvironmentVariables.TOKEN:
                    is_critical_failed = not self.__valid_token(os.getenv(environment_variable.value))
                if environment_variable == EnvironmentVariables.PASSWORD:
                    is_critical_failed = not self.__valid_password(os.getenv(environment_variable.value))
                if environment_variable == EnvironmentVariables.CHAT_ID:
                    is_critical_failed = not self.__valid_password(os.getenv(environment_variable.value))
            else:
                logging.critical(f"В .env отсутствует переменная '{environment_variable}'")
                is_critical_failed = True
                
        return is_critical_failed
    
    def __valid_token(self, token: str) -> bool:
        """Проверяет валидность токена.

        :param token: Токен.
        :type token: str
        :return: Статус: валидность токена.
        :rtype: bool
        """

        if any(character.isspace() for character in token): 
            logging.critical("Токен не должен содержать пробелов.")
            return False
    
        if ":" not in token: 
            logging.critical("Токен должен содержать двоеточие.")
            return False
        
        if len(token.split(':')) != 2: 
            logging.critical("Токен должен содержать 2 части разделённые двоеточием.")
            return False
        
        return True
    
    def __valid_password(self, password: str) -> bool:
        """Проверяет валидность пароля.

        :param token: Пароль.
        :type token: str
        :return: Статус: валидность пароля.
        :rtype: bool
        """

        if len(password.strip()) >= 1: return True
        else: return False

    def __valid_chat_id(self, chat_id: str) -> bool:
        """Проверяет валидность id чата.

        :param chat_id: ID чата.
        :type chat_id: str
        :return: Статус: валидность id чата.
        :rtype: bool
        """

        if chat_id.isdigit(): return True
        else: return False
    
    def __check_media_files(self):

        is_critical_failed = False

        for element in MediaPath:
            file_path = Path(element.value)

            if file_path.exists():
                logging.debug(f"Файл \"{element.value}\" найден.")

            else:
                element_name = file_path.stem
                is_localized_file = any(element_name.endswith(f"_{lang}") for lang in self.__supported_languages)

                if not is_localized_file or element_name.endswith(f"_{self.__language}"):
                    logging.critical(f"Файл \"{element.value}\" не найден.")
                    is_critical_failed = True
                    
                else:
                    logging.warning(f"Файл \"{element.value}\" не найден [optional]. Некоторые функции бота могут работать некорректно.")

        return is_critical_failed
    
    def __check_excel_files(self):

        is_critical_failed = False

        missing_files = []

        for element in ExcelFilesPath:
            if not Path(element.value).exists():
                missing_files.append(element.value)
        if missing_files:
            is_critical_failed = True

        return is_critical_failed
    
    