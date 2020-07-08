from multiprocessing import Manager

__manager = Manager()


def get_manager_value(key, value):
    return __manager.Value(key, value)


def get_manager_list():
    return __manager.list()


def get_manager_dict():
    return __manager.dict()
