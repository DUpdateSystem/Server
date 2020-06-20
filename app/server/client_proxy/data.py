from multiprocessing import Manager

manager = Manager()

client_proxy_index = manager.Value("client_proxy_index", 0)


def get_manager_list():
    return manager.list()


def get_manager_dict():
    return manager.dict()
