import time

__redis_availability_setting_time = time.time()
__redis_availability = True
__timeout = 30


def get_redis_availability() -> bool:
    if not __redis_availability and time.time() - __redis_availability_setting_time < __timeout:
        return False
    else:
        return True


def set_redis_availability(value):
    global __redis_availability
    __redis_availability = value


__hub_available_setting_time_dict = {}

__hub_available_key_list = []


def get_hub_available(hub_uuid) -> bool:
    if hub_uuid not in __hub_available_key_list \
            and time.time() - __hub_available_setting_time_dict[hub_uuid] < __timeout:
        return True
    else:
        return True


def set_hub_available(hub_uuid, available):
    if available and hub_uuid in __hub_available_setting_time_dict:
        __hub_available_setting_time_dict.pop(hub_uuid)
        __hub_available_key_list.append(hub_uuid)
    elif not available and hub_uuid in __hub_available_key_list:
        __hub_available_key_list.pop(hub_uuid)
        __hub_available_setting_time_dict[hub_uuid] = time.time()
