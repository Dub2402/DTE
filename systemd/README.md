# systemd
**systemd** – это подсистема инициализации и управления службами в Linux. С её помощью возможна настройка автоматического запуска сервисов и мониторинга ресурсов.

## Порядок инициализации
1. Открыть файл _DTE.service_ и подставить в него данные о расположении скрипта.
2. Поместить _DTE.service_ в директорию `/etc/systemd/system`.
3. Запустить терминал и последовательно выполнить следующие команды:
```
systemctl daemon-reload
systemctl start DTE
systemctl enable DTE
systemctl status DTE
```
**Примечание:** Если доступ к серверу осуществляется не от **root**, то для исполнения потребуется получить права суперпользователя. Для этого добавьте `sudo` в начале каждой строки.

4. Проверить появившийся в терминале статус сервиса. Он должен выглядеть так: `Active: active (running)`.
