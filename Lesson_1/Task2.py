"""2.Написать функцию host_range_ping() для перебора ip-адресов из заданного
диапазона. Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""
from subprocess import Popen, PIPE
from Task1 import host_ping


def host_range_ping(array):
    result = {'available': [], 'not_available': []}

    not_available_lst = array['not_available']
    ip_array_lst = array['available']
    result['available'].extend(ip_array_lst)
    result['not_available'].extend(ip_array_lst)
    ip_array_lst.extend(not_available_lst)

    max = input("Введите макс дипазона: ")
    for ip_addr in ip_array_lst:
        last_oktet = int(str(ip_addr).split('.')[-1])

        for i in range(1, int(max)):
            new_ip = ip_addr + i if last_oktet < 245 else ip_addr - i
            process = Popen(f'ping {new_ip} -w 50 -n 1', stdout=PIPE)
            process.wait()
            if process.returncode == 0:
                result['available'].append(new_ip)
            else:
                result['not_available'].append(new_ip)
    return result


if __name__ == '__main__':
    network = ['mail.ru', 'yandex.ru', 'gb.ru']
    print(host_range_ping(host_ping(network)))