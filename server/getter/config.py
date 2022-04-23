import multiprocessing

# worker num
async_worker_num = 16  # 并行协程数
thread_worker_num = multiprocessing.cpu_count() * 2  # 并行线程数

# process time limit
timeout_getter = 45

# data config
cloud_rule_hub_url = "https://raw.githubusercontent.com/DUpdateSystem/UpgradeAll-rules/master/rules/rules.json"

# data renew
auto_refresh_hour = 6
