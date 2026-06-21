from .Enums import MediaPath, ExcelFilesPath
from setup_project import ExcelTemplater, BuildStatusInformer

from pathlib import Path
import logging
import pandas
import sys
import os

SUPPORTED_LANGUAGES = ("ru", "en")

class LaunchGuard:
    """Проверяет наличие всех приватных данных, при отсутствии которых могут возникать критические ошибки или некорректная работа функций при работе бота."""

    def __init__(self, language: str):
        """
        Инициализация проверки.

        :param language: Код текущего языка бота.
        :type language: str
        """

        self.__language = language

    def check_readiness(self):
        """Запускает глобальную проверку проекта. 
        При провале - происходит экстренное завершение процесса.

        :param language: Код языка.
        :type language: str
        """

        logging.info("Проверка готовности бота к запуску.\n")

        is_failed = False

        check_map = {
            Path(".env"): (
                "Файл конфигурации «.env»", 
                self.__check_env_variable
            ),
            Path(MediaPath.start.folder): (
                f"Директория медиафайлов «{MediaPath.start.folder}»", 
                self.__check_media_files
            ),
            Path(ExcelFilesPath.buddy.folder): (
                f"Директория таблиц «{ExcelFilesPath.buddy.folder}»", 
                self.__check_excel_files
            )
        }

        for target_path, (element_name, deep_check_function) in check_map.items():

            if not target_path.exists():
                logging.critical(f"📦 [СТРУКТУРА]: {element_name} отсутствует.")
                is_failed = True
            
            else:
                if deep_check_function():
                    is_failed = True

        if is_failed:
            BuildStatusInformer.status_with_border("", 2)
            logging.info("☠️  Запуск бота невозможен. \n💡 ПОДСКАЗКА: ОШИБКИ КАТЕГОРИИ [СТРУКТУРА] МОЖНО ИСПРАВИТЬ, ЗАПУСТИВ: python setup_project.py")  
            BuildStatusInformer.status_with_border("", 1)              
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
                logging.critical(f"[ДАННЫЕ] В .env отсутствует переменная '{environment_variable}'")
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
            logging.critical("✍️  [ДАННЫЕ]: Токен не должен содержать пробелов.")
            return False
    
        if ":" not in token: 
            logging.critical("✍️  [ДАННЫЕ]: Токен должен содержать двоеточие.")
            return False
        
        if len(token.split(':')) != 2: 
            logging.critical("✍️  [ДАННЫЕ]: Токен должен содержать две части, разделённые двоеточием.")
            return False
        
        return True
    
    def __valid_password(self, password: str) -> bool:
        """Проверяет валидность пароля.

        :param token: Пароль.
        :type token: str
        :return: Статус: валидность пароля.
        :rtype: bool
        """

        if len(password.strip()) > 1: 
            logging.critical("✍️  [ДАННЫЕ]: Пароль должен содержать как минимум один символ.")
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
            logging.critical("✍️  [ДАННЫЕ]: ID чата должен состоять только из цифр.")
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

            if file_path.exists(): logging.debug(f"📦 [СТРУКТУРА]: Файл \"{element.value}\" найден.")

            else:
                element_name = file_path.stem
                is_localized_file = any(element_name.endswith(f"_{lang}") for lang in SUPPORTED_LANGUAGES)

                if not is_localized_file or element_name.endswith(f"_{self.__language}"):
                    logging.critical(f"✍️  [ДАННЫЕ]: Файл \"{element.value}\" не найден.")
                    is_critical_failed = True
                    
                else:
                    logging.warning(f"✍️  [ДАННЫЕ]: Файл \"{element.value}\" не найден [optional]. Некоторые функции бота могут работать некорректно.")

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
                logging.critical(f"📦 [СТРУКТУРА]: Файл \"{element.value}\" не найден.")
                is_critical_failed = True
                continue

            else:
                try: data_frame = pandas.read_excel(file_path)
                except Exception as E: logging.critical(f"Не удалось прочитать файл \"{file_path.name}\" - {E}.")

                actual_columns = set(data_frame.columns)
                missing_columns =  set(required_headers) - actual_columns

                if missing_columns:
                    missing_str = ", ".join(column for column in missing_columns)
                    logging.critical(f"✍️  [ДАННЫЕ]: В файле \"{file_path.as_posix()}\" отсутствуют обязательные колонки: \"{missing_str}\"")
                    is_critical_failed = True
                
                data_frame.dropna(how='all', inplace=True)

                if data_frame.empty:
                    logging.critical(f"✍️  [ДАННЫЕ]: Файл \"{file_path.as_posix()}\" пуст.")
                    is_critical_failed = True
                    continue
                
             
                has_empty_fields = False
                row_errors = {}  
                
                for column in required_headers:
                    if column not in actual_columns: 
                        continue

                    field_series_nan = data_frame[column].isna()
                    
                    if field_series_nan.any():
                        data_rows_indices_nan = data_frame.index[field_series_nan]
                        
                        for data_index in data_rows_indices_nan:
                            excel_row = data_index + 2
                            if excel_row not in row_errors:
                                row_errors[excel_row] = []
                            row_errors[excel_row].append(f"«{column}»")

                if row_errors:
                    has_empty_fields = True
                    error_rows = sorted(row_errors.keys())
                    rows_str = ", ".join(str(excel_row) for excel_row in sorted(row_errors.keys()))

                    word_ending = "строке" if len(error_rows) == 1 else "строках"
                    
                    logging.critical(
                        f"✍️  [ДАННЫЕ]: Файл \"{file_path.as_posix()}\": обнаружены незаполненные поля в {word_ending}: {rows_str}."
                    )

                if has_empty_fields: 
                    is_critical_failed = True

        return is_critical_failed