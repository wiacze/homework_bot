import os
import sys
import time
import requests
import logging

from http import HTTPStatus
from telebot import TeleBot
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler


load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'homework_logger.log', maxBytes=50000000, backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logger.debug('Сообщение отправлено.')
    except Exception:
        text = 'Сообщение не отправлено.'
        logger.error(text)
        raise Exception(text)


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError('Эндпоинт недоступен.')
        return response.json()
    except requests.RequestException as error:
        logger.error('Не удалось получить ответ от API.')
        return error


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ответ не является словарем.')
    current_date = response.get('current_date')
    homeworks = response.get('homeworks')
    if (homeworks is None or current_date is None):
        raise KeyError('Ошибка значений словаря.')
    if not isinstance(homeworks, list):
        raise TypeError('Содержимое словаря не является списком.')
    return homeworks


def parse_status(homework):
    """Извлекает статус из информации о конкретной домашней работе."""
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise KeyError('Не удалось извлечь название д/з.')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise KeyError('Не удалось извлечь статус и/или недопустимый статус.')
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Недоступность переменной окружения.')
        sys.exit()

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    logger.info('Бот начал работу.')

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
