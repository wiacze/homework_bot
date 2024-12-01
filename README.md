## homework_bot

Телеграм-бот для отслеживания статуса проверки домашнего задания. Периодически отсылает запрос к API Я.Практикума, в случае изменения статуса проверки присылает одно из следующих сообщений:
- Работа взята на проверку ревьюером;
- Работа проверена: у ревьюера есть замечания;
- Работа проверена: ревьюеру всё понравилось. Ура!

Бот делает запросы к эндпоинту `https://practicum.yandex.ru/api/user_api/homework_statuses/`, доступ к которому возможен по токену. Получить токен можно по [адресу](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a).

## Как запустить проект:
<details>
  <summary>Инструкция по развертыванию для Windows</summary>

> [!NOTE]
> Перед запуском проекта убедитесь, что у вас зарегистрирован бот, к которому вы планируете подключаться. Сделать это можно, как не странно, через телеграм-бота @BotFather

#### Клонировать/скачать и перейти в репозиторий:
```bash
git clone git@github.com:wiacze/homework_bot.git
cd homework_bot
```

#### Создать и активировать виртуальное окружение:
```bash
python -m venv venv
source venv/script/activate
```

#### Установить зависимости и обновить pip:
```bash
pip install -r requirements.txt
python -m pip install --upgrade pip
```

#### Создать и заполнить .env файл согласно образцу:
```env
PRACTICUM_TOKEN=<Токен, необходимый для доступа к API>
TELEGRAM_TOKEN=<Токен, необходимый для работы телеграм-бота>
TELEGRAM_CHAT_ID=<ID пользователя ботом>
```

#### Запустить проект:
```bash
python homework.py
```

</details>

## Стек
`Python 3.9`
