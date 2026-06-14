from .Enums import MediaPath, ExcelFilesPath
from setup_project import ExcelTemplater

from pathlib import Path
import logging
import pandas
import sys
import os

class LaunchGuard:
    """Проверяет наличие всех приватных данных, при отсутствии которых могут возникать критические ошибки или некорректная работа функций при работе бота."""

    __supported_languages = ("ru", "en")

    def __init__(self, language: str):
        self.__language = language

    def check_readiness(self):
        """Запускает глобальную проверку проекта. 
        При провале - происходит экстренное завершение процесса.

        :param language: Код языка.
        :type language: str
        """

        logging.info("🛡️  Проверка готовности бота к запуску.")

        check_functions = (
            self.__check_env_variable, 
            self.__check_media_files,
            self.__check_excel_files
        )
           
        if any([check_readiness() for check_readiness in check_functions]):
            logging.critical("☠️  Запуск бота невозможен. Исправьте ошибки выше.")
            sys.exit(1)

        logging.info("🚀 Проверка Guard пройдена успешно. Система стабильна!")
    
    def __check_env_variable(self) -> bool:
        """Проверяет присутствуют ли все необходимые переменные окружения.

        :return: Статус: необходимо ли экстренное завершение процесса.
        :rtype: bool
        """

        is_critical_failed = False

        functions = {
            "TOKEN": self.__valid_token,
            "PASSWORD": self.__valid_password,
            "CHAT_ID": self.__valid_chat_id,
        }

        for environment_variable, validation_function in functions.items():
            environment_value = os.getenv(environment_variable)

            if environment_value:
                is_critical_failed |= not validation_function(environment_value)

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
            logging.critical("Токен должен содержать две части, разделённые двоеточием.")
            return False
        
        return True
    
    def __valid_password(self, password: str) -> bool:
        """Проверяет валидность пароля.

        :param token: Пароль.
        :type token: str
        :return: Статус: валидность пароля.
        :rtype: bool
        """

        if len(password.strip()) < 1: 
            logging.critical("Пароль должен содержать как минимум один символ.")
            return False
        
        else: return True

    def __valid_chat_id(self, chat_id: str) -> bool:
        """Проверяет валидность id чата.

        :param chat_id: ID чата.
        :type chat_id: str
        :return: Статус: валидность id чата.
        :rtype: bool
        """

        if not chat_id.isdigit(): 
            logging.critical("ID чата должен состоять только из цифр.")
            return False
        
        else: return True
    
    def __check_media_files(self) -> bool:
        """Проверяет присутствуют ли все необходимые медиафайлы.

        :return: Статус: необходимо ли экстренное завершение процесса.
        :rtype: bool
        """

        is_critical_failed = False

        for element in MediaPath: 
            file_path = Path(element.value)

            if file_path.exists(): logging.debug(f"Файл \"{element.value}\" найден.")

            else:
                element_name = file_path.stem
                is_localized_file = any(element_name.endswith(f"_{lang}") for lang in self.__supported_languages)

                if not is_localized_file or element_name.endswith(f"_{self.__language}"):
                    logging.critical(f"Файл \"{element.value}\" не найден.")
                    is_critical_failed = True
                    
                else:
                    logging.warning(f"Файл \"{element.value}\" не найден [optional]. Некоторые функции бота могут работать некорректно.")

        return is_critical_failed
    
    def __check_excel_files(self) -> bool:
        """Проверяет присутствуют ли все необходимые excel файлы и имеются ли там все необходимые данные в колонках.

        :return: Статус: необходимо ли экстренное завершение процесса.
        :rtype: bool
        """

        is_critical_failed = False
        required_headers = ExcelTemplater.headers()

        for element in ExcelFilesPath:
            file_path = Path(element.value)

            if not file_path.exists(): 
                logging.critical(f"Файл \"{element.value}\" не найден.")
                is_critical_failed = True
                continue

            else:
                try: data_frame = pandas.read_excel(file_path)
                except Exception as E: logging.critical(f"Не удалось прочитать файл \"{file_path.name}\" - {E}.")

                actual_columns = set(data_frame.columns)
                missing_columns =  set(required_headers) - actual_columns

                if missing_columns:
                    missing_str = ", ".join(column for column in missing_columns)
                    logging.critical(f"В файле \"{file_path.name}\" отсутствуют обязательные колонки: \"{missing_str}\"")
                    is_critical_failed = True
                
                data_frame.dropna(how='all', inplace=True)

                if data_frame.empty:
                    logging.critical(f"Файл \"{file_path.name}\" пуст.")
                    is_critical_failed = True
                    continue
                
                has_empty_fields = False
                
                for column in required_headers:

                    if column not in actual_columns: continue

                    field_series_nan = data_frame[column].isna()
                    
                    if field_series_nan.any():
                        data_rows_indices_nan = data_frame.index[field_series_nan]
                        excel_row_numbers_nan = [data_rows_index + 2 for data_rows_index in data_rows_indices_nan]
                        excel_row_number_nan = ", ".join(str(number) for number in excel_row_numbers_nan)
                        if len(excel_row_number_nan) == 1:
                            logging.critical(f"Ошибка в файле \"{file_path.name}\": в колонке \"{column}\" есть незаполненные ячейки в строке {excel_row_number_nan}!")
                        else:
                            logging.critical(f"Ошибка в файле \"{file_path.name}\": в колонке \"{column}\" есть незаполненные ячейки в строках: {excel_row_number_nan}!")
                        has_empty_fields = True

                if has_empty_fields: is_critical_failed = True

        return is_critical_failed