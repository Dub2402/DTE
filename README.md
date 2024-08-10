# CalculatorDateBot 
**CalculatorDateBot** – [telegram](https://telegram.org)-бот, помогающий запоминать события и узнавать сколько дней до них осталось.

# Порядок установки и использования
1. Загрузить репозиторий. Распаковать.
2. Установить [Python](https://www.python.org/downloads/) версии 3.10 и выше. Рекомендуется добавить в PATH.
3. Установить пакеты при помощи следующей команды, выполненной из директории скрипта.

```
pip install -r requirements.txt
```
4. Настроить бота путём редактирования [_Settings.json_](#Settings).
5. Запустить файл _main.py_.
```
python main.py
``` 
6. Перейти в чат с ботом, токен которого указан в настройках, и следовать его инструкциям.

# Settings.json

<a name="Settings"></a> 

```JSON
"token": "",
"password": "",
"default_reminders": {"hour": null, "minute": ""},
"every_reminders": {"hour": null, "minute": ""},
"once_reminders": {"hour": null, "minute": ""}
```

Сюда необходимо занести токен бота Telegram (можно получить у [BotFather](https://t.me/BotFather)).

---

_Copyright © Dub Irina. 2024._
