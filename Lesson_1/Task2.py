"""2.Написать функцию host_range_ping() для перебора ip-адресов из заданного
диапазона. Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""
from Task1 import host_ping
from ipaddress import ip_address


def host_range_ping():
    while True:
        start_ip = input('Начальный IP ')
        try:
            last = int(start_ip.split('.')[3])
            break
        except Exception as e:
            print(e)
    while True:
        end = input('Количество адресов ')
        if not end.isnumeric():
            print('число')
        else:
            if (last + int(end)) > 254:
                print("Ошибка в адресе")
            else:
                break
    host_list = []
    [host_list.append(str(ip_address(start_ip)+x)) for x in range(int(end))]

    return host_ping(host_list)


if __name__ == '__main__':
    host_range_ping()

