"""1.Написать функцию host_ping(), в которой с помощью утилиты ping будет
проверяться доступность сетевых узлов. Аргументом функции является список,
в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом
соответствующего сообщения («Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""
from subprocess import Popen, PIPE
from ipaddress import ip_address
from socket import gethostbyname


def host_ping(network):
    result = {'available': [], 'not_available': []}
    for node in network:
        try:
            network_node_ip = ip_address(node)
        except ValueError:
            network_node_ip = gethostbyname(node)
            network_node_ip = ip_address(network_node_ip)
        process = Popen(f'ping {network_node_ip} -w 50 -n 1', stdout=PIPE)
        process.wait()
        if process.returncode == 0:
            result['available'].append(network_node_ip)
        else:
            result['not_available'].append(network_node_ip)
    return result


if __name__ == '__main__':
    print(host_ping(['mail.ru', 'yandex.ru', 'gb.ru']))