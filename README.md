# Sport Career Tracker

Интерактивный трекер футбольной карьеры в стиле FIFA 23. Проект принимает результаты реальных матчей, развивает карточку игрока, рассчитывает стоимость и зарплату, ведёт чемпионат и Кубок, выдаёт награды и показывает карьерные новости.

## Возможности

- Добавление матчей чемпионата и Кубка с датой, голами, передачами, пробегом и командным счётом.
- Автоматический расчёт рейтинга матча, характеристик `OVR`, `PAC`, `SHO`, `PAS`, `DRI`, `DEF`, `PHY` и трансферной стоимости.
- Базовые карточки игрока: бронзовая, серебряная и золотая.
- Специальные карточки по приоритету: `TOTY > POTM > TOTW > MOTM`.
- Локальные FIFA-style шаблоны карточек, фотография игрока и логотип «Твенте».
- Турнирная таблица чемпионата из 20 команд со взвешенной симуляцией соперников.
- Рейтинг бомбардиров чемпионата по голам и голевым передачам.
- Кубковая сетка на выбывание и отдельный рейтинг бомбардиров Кубка.
- Витрина клубных трофеев и личных наград.
- Career Summary на русском языке: матчи, победы, ничьи, поражения, голы, передачи, стоимость и зарплата.
- Зарплатные бонусы за рыночный рост, командные титулы и личные награды.
- Динамические новости о победах, хет-триках, наградах и выигранном Кубке.
- История последних матчей и сохранение прогресса в SQLite.

## Стек

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic Settings
- HTML, Tailwind CSS CDN, FontAwesome и чистый JavaScript

## Архитектура

Проект разделён по MVC и сервисным слоям:

```text
backend/app/
├── controllers/   # FastAPI-роуты
├── models/        # SQLAlchemy-модели
├── views/         # Pydantic-схемы
├── services/      # Бизнес-логика и симуляции
├── core/          # Настройки из переменных окружения
├── db/            # Подключение и инициализация SQLite
└── main.py        # Точка входа FastAPI

assets/images/     # Локальные изображения, не публикуются в Git
index.html         # Однофайловый адаптивный фронтенд
```

Все коэффициенты формул, бонусы, штрафы и лимиты находятся в `.env`. Файлы проекта ограничены 400 строками.

## Локальный запуск

1. Создайте виртуальное окружение:

```powershell
python -m venv .venv
```

2. Установите зависимости:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Создайте локальный файл настроек:

```powershell
Copy-Item .env.example .env
```

4. Запустите сервер:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Если виртуальное окружение расположено на уровень выше проекта:

```powershell
..\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

5. Откройте:

- приложение: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

## Локальные изображения

Изображения намеренно не публикуются в GitHub. После клонирования положите личные файлы в `assets/images/`:

```text
player_face.png
twente_logo.png
card_bronze.png
card_silver.png
card_gold.png
card_motm.png
card_totw.png
card_potm.png
card_toty.png
award_motm_gray.png
award_motm_color.png
award_totw_gray.png
award_totw_color.png
award_potm_gray.png
award_potm_color.png
award_toty_gray.png
award_toty_color.png
trophy_champ_gray.png
trophy_champ_color.png
trophy_fa_gray.png
trophy_fa_color.png
motm_news.png
totw_news.png
potm_news.png
toty_news.png
cup_news.png
match_win_news.png
hattrick_news.png
```

Папка сохраняется в репозитории благодаря `.gitkeep`. `.gitignore` исключает изображения, `.env` и локальную SQLite-базу.

## Основные API-маршруты

- `POST /api/v1/match/add`
- `GET /api/v1/player`
- `GET /api/v1/history`
- `GET /api/v1/career-summary`
- `GET /api/v1/league/table`
- `GET /api/v1/league/scorers`
- `GET /api/v1/cup`
- `GET /api/v1/cup/scorers`

## Состояние перед стартом

Тестовые данные очищены. Новая карьера начинается с `OVR 60`, стоимости `$100,000`, зарплаты `$500`, пустой таблицы чемпионата и первого раунда Кубка.
