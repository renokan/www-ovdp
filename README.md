# OVDPs website (Flask framework)

**Что анализируем**: Результаты размещения облигаций внутренних государственных займов.
**Источник данных**: API (в формате json) Национального банка Украины (НБУ).

Проект состоит из двух частей - загрузки (конвертации) данных и отображения.
За загрузку отвечает `run_loader.py` - исполняемый файл, запускаемый по крону.
За запуск приложения (Flask framework) отвечает `run_server.py`.

```
www-ovdp/
 ├── venv/
 ├── instance/
 │    ├── logs/
 │    └── local_settings.py
 ├── run_server.py
 ├── run_loader.py
 ├── loader.py
 ├── utils_load.py
 └── ovdp/
      ├── static/
      │    └── reports/
      ├── templates/
      ├── __init__.py
      ├── default_settings.py
      ├── views.py
      ├── utils_app.py
      ├── queries.py
      └── auctions.db
```

## Внешний вид (Centos 7 + nginx + uwsgi)

![Screenshot](screenshot-flask_ovdp__index.png)
![Screenshot](screenshot-flask_ovdp__stats.png)
![Screenshot](screenshot-flask_ovdp__year.png)
![Screenshot](screenshot-flask_ovdp__auctions.png)
