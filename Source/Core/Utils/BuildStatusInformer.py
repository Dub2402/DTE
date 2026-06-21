from Source.Core.Enums import MediaPath, ExcelFilesPath

from dublib.CLI.TextStyler.FastStyler import FastStyler

from enum import Enum, auto
from pathlib import Path

WIDTH = 99     
INDENT = 5
STATUS_PAD = 11

class BorderPlace(Enum):
    TOP = auto()
    BOTTOM = auto()

def generate_instruction_for_user():
    """Генерирует текст в консоль об окончании сборки проекта."""

    excel_files = "\n► ".join([Path(file.value).name for file in ExcelFilesPath])
    media_files = "\n► ".join([Path(file.value).name for file in MediaPath])

    folder_excel = FastStyler("«" + ExcelFilesPath.buddy.folder + "»").decorate.bold
    folder_media = FastStyler("«" + MediaPath.start.folder + "»").decorate.bold
    env = FastStyler("«.env»").decorate.bold

    template_text = (
        "Для завершения настройки проекта необходимо:\n",
        f"1. Заполнить переменные в {env}\n",
        f"2. Заполнить данные в таблицах Excel, в папке {folder_media}:\n\n► {media_files}\n",
        f"3. Добавить изображения в папку {folder_excel}:\n\n► {excel_files}",
    )
    text = "\n".join(template_text)

    return text

def status_with_border(text: str, border_place: BorderPlace):
    """Выводит текст с границей в консоль.

    :param text: Текст.
    :type text: str
    :param border_place: Место отрисовки границы.
    :type border_place: BorderPlace
    """

    border = ("─" * (WIDTH + STATUS_PAD))

    match border_place:
        case BorderPlace.TOP: text = border + "\n" + text
        case BorderPlace.BOTTOM: text = text + "\n" + border

    print(text)

def continue_building_status(text: str, status: str | None = "", indent: bool = False):
    """Выводит статусы работы автосборщиком над запущенным процессом.

    :param text: Текст.
    :type text: str
    :param status: Статус.
    :type status: str | None
    :param indent: Статус необходимости отступа.
    :type indent: bool
    """

    if status: status = "[" + status + "]" 

    current_indent = INDENT if indent else 0
    current_width = WIDTH - current_indent

    print(" " * current_indent + text + "." * max(0, current_width - len(text)) + status)