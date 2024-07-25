import os
import sys
import time
import logging
from http import HTTPStatus

import requests
from telebot import TeleBot
from telebot import apihelper
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filemode='a',
    filename='homework.log',
    format=('%(asctime)s - %(name)s - %(levelname)s'
            ' - %(funcName)s - %(message)s')
)


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
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    result = True
    for key, value in tokens.items():
        if not value:
            logging.error(f'{key} недоступен и/или отсутствует.')
            result = False
    return result


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logging.debug('Сообщение отправлено.')
    except apihelper.ApiException:
        logging.error('Сообщение не отправлено')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException:
        raise ConnectionError(
            'Ошибка при запросе к API, не удалось получить ответ.'
        )
    if response.status_code != HTTPStatus.OK:
        raise ConnectionError(
            'Код ответа не соответствует ожиданиям. '
            f'Код: {response.status_code}'
        )
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError(
            'Ответ API не является словарем. '
            f'Полученный тип данных: {type(response)}'
        )
    if 'current_date' not in response:
        raise KeyError('"current_date" отсутствует в ответе API.')
    current_date = response['current_date']
    if 'homeworks' not in response:
        raise KeyError('"homeworks" отсутствует в ответе API.')
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError(
            'Содержимое словаря "homeworks" не является списком. '
            f'Полученный тип данных: {type(homeworks)}'
        )
    return current_date, homeworks


def parse_status(homework):
    """Извлекает статус из информации о конкретной домашней работе."""
    if 'homework_name' not in homework:
        raise KeyError('Не удалось извлечь название домашки.')
    homework_name = homework['homework_name']
    if 'status' not in homework:
        raise KeyError('Не удалось извлечь статус домашки')
    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        raise KeyError(f'Некорректный статус домашки: {status}')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Недоступность переменной окружения.')
        sys.exit()

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = 0
    last_message = None
    logging.debug('Бот начал работу.')

    while True:
        try:
            response = get_api_answer(timestamp)
            if response:
                current_date, homeworks = check_response(response)
            else:
                logging.error('API не отвечает')
            if len(homeworks) > 0:
                message = parse_status(homeworks[0])
            else:
                logging.debug('Список пуст')
            if message and message != last_message:
                send_message(bot, message)
                last_message = message
            timestamp = current_date
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(error)
            if message != last_message:
                send_message(bot, message)
                last_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
