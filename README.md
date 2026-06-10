# Web Reverse Lab

Web Reverse Lab — это REST API сервис для первичного анализа бинарных файлов.

Проект позволяет загружать исполняемые файлы, выполнять их автоматический анализ с использованием стандартных Linux-утилит и Ghidra Headless, сохранять результаты в базе данных и получать их через REST API.

---

## Возможности

### Управление файлами

* Загрузка файлов
* Получение списка файлов
* Получение информации о файле по ID
* Удаление файлов
* Автоматическое сохранение файлов на диске

### Анализ файлов

* Определение типа файла через `file`
* Извлечение строк через `strings`
* Вычисление SHA256-хеша
* Кэширование результатов анализа
* Поиск по строкам анализа

### Ghidra Headless

* Автоматический запуск Ghidra Headless
* Извлечение пользовательских функций
* Получение ассемблерного листинга функций
* Кэширование результатов Ghidra-анализа

### База данных

* SQLite
* Связи через Foreign Keys
* Каскадное удаление связанных данных
* Хранение истории анализа

---

## Используемые технологии

* Python 3
* FastAPI
* SQLite
* Ghidra Headless
* Uvicorn
* Git
* subprocess
* pathlib

---

## Архитектура проекта

```text
Web_reverse_lab/
│
├── app/
│   ├── main.py
│   │
│   ├── analysis/
│   │   ├── analyzer.py
│   │   ├── ghidra.py
│   │   ├── ghidra_script.py
│   │   └── ghidra_result/
│   │
│   └── databases/
│       └── database.py
│
├── uploads/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Установка

Клонировать репозиторий:

```bash
git clone https://github.com/Marsik112/Web_reverse_lab.git
cd Web_reverse_lab
```

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Активировать окружение:

Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

---

## Запуск

Запустить сервер:

```bash
uvicorn app.main:app --reload
```

После запуска:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## Ghidra

Для работы Ghidra Headless необходимо установить Ghidra.

По умолчанию используется путь:

```text
/opt/ghidra/support/analyzeHeadless
```

При необходимости путь можно изменить в модуле Ghidra.

---

## API

### Проверка работоспособности

```http
GET /
```

---

### Загрузка файла

```http
POST /files
```

Поддерживаемые расширения:

```text
.exe
.elf
.bin
.so
.dll
```

Максимальный размер:

```text
50 MB
```

---

### Получение списка файлов

```http
GET /files
```

---

### Получение информации о файле

```http
GET /files/{file_id}
```

---

### Удаление файла

```http
DELETE /files/{file_id}
```

---

### Анализ файла

```http
GET /files/{file_id}/analysis
```

Возвращает:

* тип файла
* SHA256
* строки файла
* время анализа

---

### Поиск по строкам

```http
GET /files/{file_id}/analysis/search?filter=password
```

Пример:

```http
GET /files/1/analysis/search?filter=http
```

---

### Ghidra-анализ

```http
GET /files/{file_id}/ghidra
```

Возвращает:

* пользовательские функции
* адреса функций
* ассемблерный листинг

---

## База данных

### Таблица files

```text
id
filename
size
upload_time
status
```

### Таблица analysis

```text
id
file_id
file_result
strings_output
sha256
analysis_time
```

### Таблица ghidra

```text
id
file_id
func_json
analysis_time
```

---

## Пример сценария использования

1. Загрузить бинарный файл.
2. Получить его ID.
3. Выполнить первичный анализ.
4. Выполнить поиск по строкам.
5. Запустить анализ через Ghidra.
6. Изучить найденные функции и ассемблерный код.

---

## Roadmap

Планируемые улучшения:

* PostgreSQL
* SQLAlchemy
* Pydantic Models
* Docker
* JWT Authentication
* Logging
* Unit Tests
* Фоновое выполнение анализа
* Дополнительные анализаторы ELF и PE файлов

---

## Автор

Marsik112

Учебный проект для изучения Python Backend Development, Reverse Engineering и анализа бинарных файлов.
