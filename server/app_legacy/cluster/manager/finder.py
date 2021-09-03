# 客户端方式连接反查表
node_sid_map = {}
# 节点连接方式存储
node_map = {}

# node 软件源可用性统计
node_reliability_dict = {}


def add_client_node(ip: str, port: int, sid: str):
    host = f'{ip}:{port}'
    node_sid_map[sid] = host
    node_map[host] = sid
    if host not in node_reliability_dict:
        node_reliability_dict[host] = None


def get_host(sid: str) -> tuple[str, int]:
    host = node_sid_map[sid]
    ip, port = host.split(':')
    return ip, port


def del_node_sid(sid: str):
    host = node_sid_map.pop(sid)
    del node_map[host]


def del_node_host(ip: str, port: int):
    host = f'{ip}:{port}'
    del node_map[host]
    for sid, _host in node_sid_map:
        if _host == host:
            del node_sid_map[sid]
            break


def add_server_node(ip: str, port: int, client):
    host = f'{ip}:{port}'
    node_map[host] = client


def get_server_node(ip: str, port: int):
    host = f'{ip}:{port}'
    return node_map[host]


def del_server_node(ip: str, port: int):
    host = f'{ip}:{port}'
    del node_map[host]


def set_node_hub_reliability_sid(sid: str, hub_reliability_dict: dict):
    ip, port = get_host(sid)
    set_node_hub_reliability(ip, port, hub_reliability_dict)


def set_node_hub_reliability(ip: str, port: int, hub_reliability_dict: dict):
    host = f'{ip}:{port}'
    node_reliability_dict[host] = hub_reliability_dict


def get_node_reliability_dict() -> list:
    return node_reliability_dict
