"""Программа-клиент"""
import argparse
import logging
import threading
import sys, json, socket, time
from json import JSONDecodeError

from common.variables import ACCOUNT_LOGIN, USER, CURRENT_TIME, ACTION, DEF_PORT, DEF_IP_ADDRESS, \
    MAX_CONNECTIONS, CODE_RESPONSE, CODE_ERROR, CODE_PRESENCE, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, \
    RESPONSE_400, \
    EXIT, DESTINATION
from common.utils import get_message, send_message
import log.config_client_log
from decoration import log
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from metaclasses import ClientVerifier
from descriptors import Port, Host
from argparse import ArgumentParser
from time import time, sleep

logger = logging.getLogger('client')


@log
def argv_parser():
    # создаем парсер командной строки
    argv_pars = ArgumentParser()
    # создаем аргументы парсера - порт
    argv_pars.add_argument('port', default=DEF_PORT,
                           help='port on which to run', type=int, nargs='?')
    # создаем аргумент парсера ip адресс
    argv_pars.add_argument('addr', default=DEF_IP_ADDRESS, nargs='?')
    # создаем аргумент парсера mode (listen or send)
    argv_pars.add_argument('-n', '--name', nargs='?')
    # передаем парсеру параметры командной строки
    ip_and_port_and_mode = argv_pars.parse_args(sys.argv[1:])
    server_port = ip_and_port_and_mode.port
    server_ip_addr = ip_and_port_and_mode.addr
    client_name = ip_and_port_and_mode.name
    return server_ip_addr, server_port, client_name


class Client(metaclass=ClientVerifier):
    port = Port()
    ip = Host()

    def __init__(self, ip, port, clent_name):
        self.ip = ip
        self.port = port
        self.client_name = clent_name

    def print_info_help(self):
        print('''
    Привет!!! ты находишься в консольном мессенжере
    Команды:
    send - отправка сообщения
    help - вывести подсказки
    exit - выйти
        ''')

    def create_exit_message(self, account_name):
        '''
        Создает сообщение о выходе из мессенжера
        :param account_name:
        :return:
        '''
        return {ACTION: EXIT, CURRENT_TIME: time(), ACCOUNT_LOGIN: account_name}

    def create_message(self, sock, account_name='Guest'):
        to_user = input(
            'Введите имя пользователя, которому хотите отправить сообщение: ')
        message = input('Введите сообщение: ')

        message_create = {ACTION: MESSAGE, CURRENT_TIME: time(), SENDER: account_name,
                          DESTINATION: to_user, MESSAGE_TEXT: message}
        logger.debug(f'Создано сообщение {message_create}')
        try:
            send_message(sock, message_create)
            logger.info(f'Отправлено сообщение({message}) пользователю:{to_user}')
        except:
            logger.critical('Потеряно соединение с сервером')
            sys.exit(1)

    def user_interaction(self, sock):
        self.print_info_help()
        while True:
            command = input('Введите команду:  \n')
            if command == 'send':
                self.create_message(sock, self.client_name)
            elif command == 'help':
                self.print_info_help()
            elif command == 'exit':
                message_exit = self.create_exit_message(self.client_name)
                send_message(sock, message_exit)
                param = {'username': self.client_name}
                logger.info('Пользователь %(username)d вышел из мессенжера', param)
                sleep(0.5)
                break
            else:
                print('Введенная команда недоступна. '
                      'Введите help для просмотра доступных комманд')

    def handler_message_from_users(self, sock):
        while True:
            try:
                message = get_message(sock)
                if ACTION in message and message[
                    ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT \
                        in message and DESTINATION in message and \
                        message[DESTINATION] == self.client_name:
                    print(
                        f'Получено сообщение от пользователя {message[SENDER]}:'
                        f'\n{message[MESSAGE_TEXT]}')
                    logger.info(
                        f'Получено сообщение от пользователя {message[SENDER]}:'
                        f'\n{message[MESSAGE_TEXT]}')
                else:
                    logger.error(
                        f'От сервера получено некорректное сообщение:{message}')
            except IncorrectDataRecivedError:
                logger.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break

    def create_greetings(self, account_name='Guest'):
        # генерация запроса о присутствии клиента
        return {ACTION: CODE_PRESENCE, CURRENT_TIME: time(),
                USER: {ACCOUNT_LOGIN: self.client_name}}

    def handler_response_from_server(self, message):
        # print(message)
        logger.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if CODE_RESPONSE in message:
            if message[CODE_RESPONSE] == 200:
                return '200 : OK'
            elif message[CODE_RESPONSE] == 400:
                raise ServerError(f'400 : {message[CODE_ERROR]}')
        raise ReqFieldMissingError(CODE_RESPONSE)

    def base(self):
        try:
            # создаем сетевой потоковый сокет
            sock_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # устанавливаем соединение с сокетом
            # print(server_ip_addr, server_port)
            sock_1.connect((self.ip, self.port))
            # для теста метакласса
            # sock_1.listen()
            # создаем сообщение о присутствии клмента на сервере
            messages_to_server = self.create_greetings()
            # кодируем данные в байты и отправляем на сервер
            send_message(sock_1, messages_to_server)
            answer = self.handler_response_from_server(get_message(sock_1))
            logger.info(
                f'Установлено соединение с сервером. Ответ от сервера {answer}')
            print('Соединение с сервером установлено')

        except JSONDecodeError:
            logger.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as error:
            logger.error(
                f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            logger.error(f'В ответе сервера отсутствует необходимое поле '
                         f'{missing_error.missing_field}')
            sys.exit(1)
        except ConnectionRefusedError:
            logger.critical(
                f'Не удалось подключиться к серверу {self.ip}:{self.port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно,
            # создаем 2 потока- один принимает сообщение, другой - отправляет
            # поток принимающий сообщений
            receive_mess = threading.Thread(
                target=self.handler_message_from_users, args=(sock_1,))
            # receive_mess.daemon = True
            receive_mess.start()
            send_mess = threading.Thread(target=self.user_interaction,
                                         args=(sock_1,))
            # send_mess.daemon=True
            send_mess.start()
            logger.debug('Потоки запущены')


@log
def main():
    server_ip_addr, server_port, client_name = argv_parser()
    print(f'Клиент {client_name} подключён.')
    if not client_name:
        client_name = input('Введите имя поьзователя')
    logger.info(f'Запущен клиент с ip-адресом{server_ip_addr}, порт:{server_port},'
                f'с именем:{client_name}')
    client = Client(server_ip_addr, server_port, client_name)
    client.base()


if __name__ == '__main__':
    main()
