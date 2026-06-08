from dublib.CLI.TextStyler import FastStyler

import logging
import os

class ColoredConsoleFormatter(logging.Formatter):
    """Кастомный форматтер для раскраски вывода системных логов в консоли.

    Преобразует итоговую строку лога, добавляя ANSI-последовательности окрашивания в зависимости 
    от уровня важности записи (Levelno).
    """

    def format(self, record: logging.LogRecord) -> str:
        """Форматирует и красит текстовую запись лога на основе ее уровня важности.

        :param record: Объект записи лога, содержащий метаданные события.
        :type record: logging.LogRecord
        :return: Отформатированная строка лога с ANSI-кодами для окрашивания текста.
        :rtype: str
        """
        
        log_string = super().format(record)

        color_map = {
            logging.CRITICAL: lambda s: FastStyler(s).colorize.red,
            logging.ERROR:    lambda s: FastStyler(s).colorize.bright_magenta,
            logging.WARNING:  lambda s: FastStyler(s).colorize.yellow,
            logging.INFO:     lambda s: FastStyler(s).colorize.white,
            logging.DEBUG:    lambda s: FastStyler(s).colorize.gray,
        }
        formatter_func = color_map.get(record.levelno)

        return formatter_func(log_string) if formatter_func else log_string

def ConfigurateLogger():
    """Глобальная конфигурация всей системы логирования проекта.

    Считывает переменные окружения ``LOG_LEVEL_FILE`` и ``LOG_LEVEL_CONSOLE``, 
    транслирует их в системные уровни библиотеки `logging` и инициализирует два 
    обработчика: :class:`logging.FileHandler` для записи в файл и 
    :class:`logging.StreamHandler` с применением кастомного форматтера 
    :class:`ColoredConsoleFormatter` для вывода в консоль.

    Уровень корневого логгера автоматически выставляется в минимальное значение 
    между двумя конфигурациями для предотвращения преждевременной фильтрации сообщений.
    """

    env_file = os.getenv("LOG_LEVEL_FILE", "DEBUG").upper()
    env_console = os.getenv("LOG_LEVEL_CONSOLE", "INFO").upper()

    level_file = getattr(logging, env_file, logging.INFO)
    level_console = getattr(logging, env_console, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.setLevel(min(level_file, level_console))

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%d.%m.%y %H:%M:%S'

    console_format = '[%(filename)s:%(lineno)d] — %(message)s'

    file_handler = logging.FileHandler(filename="logging.log", mode="w", encoding="utf-8")
    file_handler.setLevel(level_file)
    file_formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
   
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level_console)
    console_formatter = ColoredConsoleFormatter(fmt=console_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
