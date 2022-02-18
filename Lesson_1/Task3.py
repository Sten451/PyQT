"""3.Написать функцию host_range_ping_tab(), возможности которой основаны на функции
из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам,
представленным в табличном формате (использовать модуль tabulate).
Таблица должна состоять из двух колонок и выглядеть примерно так:
"""
from tabulate import tabulate
from Task1 import host_ping
from Task2 import host_range_ping


def host_range_ping_tab(result):
    print(tabulate(result, headers='keys', tablefmt="grid"))

ip_array = host_ping(['mail.ru', 'yandex.ru', 'gb.ru'])
result = host_range_ping(ip_array)
host_range_ping_tab(result)