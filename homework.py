import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_API = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
STATUSES = {
    'rejected': 'К сожалению в работе нашлись ошибки.',
    'approved':
    'Ревьюеру всё понравилось, можно приступать к следующему уроку.',
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log', filemode='w')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    hw_status = homework.get('status')
    if hw_status not in STATUSES:
        logging.info(hw_status, exc_info=True)
        return f'Неизвестный статус работы "{homework_name}".'
    verdict = STATUSES[hw_status]
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_API,
            params={'from_date': current_timestamp},
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
        )
        return homework_statuses.json()

    except requests.exceptions.RequestException as e:
        logging.error(e, exc_info=True)
        return {}


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, text=message)


def catch_index_error(hw_dict, index):
    try:
        return hw_dict.get('homeworks')[index]
    except IndexError:
        logging.info(IndexError, exc_info=True)
        return {}


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    logging.debug('Бот запущен.')
    current_timestamp = int(time.time())
    new_homework = {}

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        catch_index_error(new_homework, 0)),
                    bot_client
                )
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            logging.exception()
            send_message(f'Бот столкнулся с ошибкой: {e}', bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
