from Source.Core.Enums import MediaPath, ExcelFilesPath
from Source.Core.Utils.ExcelTemplater import ExcelTemplater
from Source.Core.Utils import BuildStatusInformer

from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.CLI.TextStyler.FastStyler import FastStyler
from dublib.Methods.System import Clear

from pathlib import Path
from enum import Enum 
import requests
import shutil

Clear()

BUILD_ERRORS = []

class BuildStatus(str, Enum):
	CREATED = "CREATED"
	SKIPPED = "SKIPPED"
	FAILED = "FAILED"

def setup_directories():
	"""Инициализирует создание необходимых директорий и выводит в консоль результат процесса."""

	BuildStatusInformer.continue_building_status("📁 1. Cоздание необходимых директорий")
	indent = True

	for folder in (MediaPath.start.folder, ExcelFilesPath.buddy.folder):
		text = f"Директория \"{folder}\""

		if Path(folder).exists(): status = BuildStatus.SKIPPED

		else:
			try: 
				MakeRootDirectories(folder)
				status = BuildStatus.CREATED

			except Exception as text_error:
				status = BuildStatus.FAILED
				BUILD_ERRORS.append(f"[ДИРЕКТОРИИ]: Не удалось создать папки. Ошибка: {text_error}")

		BuildStatusInformer.continue_building_status(text, status, indent)
	
def setup_excel_templates():
	"""Проверяет и создает Excel-шаблоны."""

	BuildStatusInformer.continue_building_status("📊 2. Создание Excel-шаблонов.")
	
	indent = True
	status = None

	for table_path in ExcelFilesPath:
		file_path = Path(table_path.value)
		text = f"Шаблон таблицы Excel {file_path.name}"

		if file_path.exists(): status = BuildStatus.SKIPPED

		else: 

			try:
				ExcelTemplater.create_excel_files(file_path)
				status = BuildStatus.CREATED
				
			except Exception as text_error:
				status = BuildStatus.FAILED 
				BUILD_ERRORS.append(f"[EXCEL ТАБЛИЦЫ]: Не удалось создать папки. Ошибка: {text_error}")
		
		BuildStatusInformer.continue_building_status(text, status, indent)

def download_example_env():
	"""Скачивает .env.example."""

	url = "https://raw.githubusercontent.com/Dub2402/DTE/main/.env.example"
	response = requests.get(url)

	if response.status_code == 200:
		with open(".env.example", "wb") as file: file.write(response.content)

def setup_env_file():
	"""Настраивает конфигурационный файл .env на основе шаблона .env.example."""
	
	env_path = Path(".env")
	example_path = Path(".env.example")

	if env_path.exists(): status = BuildStatus.SKIPPED

	else:

		if not example_path.exists():

			try: download_example_env()

			except Exception as text_error: 
				BUILD_ERRORS.append(f"[ПЕРЕМЕННЫЕ СРЕДЫ]: Не удалось создать .env так как .env.example не существует, а скачать из репозитория не удалось. Ошибка: {text_error}")
				status = BuildStatus.FAILED

		else:
			
			try:
				shutil.copy(example_path, env_path)
				example_path.unlink(missing_ok=True)
				status = BuildStatus.CREATED

			except Exception as text_error: 
				BUILD_ERRORS.append(f"[ПЕРЕМЕННЫЕ СРЕДЫ]: Не удалось создать .env так как .env.example не существует. Ошибка: {text_error}")
				status = BuildStatus.FAILED
	
	BuildStatusInformer.continue_building_status("📝 3. Добавление конфигурации .env", status)

if __name__ == "__main__":

	BuildStatusInformer.status_with_border("👨‍💻 Начало автосборки проекта.", BuildStatusInformer.BorderPlace.BOTTOM)

	setup_directories()
	setup_excel_templates()
	setup_env_file()

	if not BUILD_ERRORS: BuildStatusInformer.status_with_border("🚀 Сборка успешно завершена!", BuildStatusInformer.BorderPlace.TOP)
	else: 
		BuildStatusInformer.status_with_border(FastStyler("❌ Проблемы при сборке:\n").decorate.bold, BuildStatusInformer.BorderPlace.TOP)
		for error in BUILD_ERRORS:
			print(error)

	BuildStatusInformer.status_with_border(BuildStatusInformer.generate_instruction_for_user(), BuildStatusInformer.BorderPlace.TOP)