import multiprocessing

# worker num
async_worker_num = 16  # 并行协程数
thread_worker_num = multiprocessing.cpu_count() * 2  # 并行线程数

# net
#worker_url = f'tcp://0.0.0.0:/worker%d_%d.ipc'
#worker_url = f'ipc:///{ipc_dir}/worker%d_%d.ipc'

# process time limit
timeout_getter = 45

# data config
cloud_rule_hub_url = "https://raw.githubusercontent.com/DUpdateSystem/UpgradeAll-rules/master/rules/rules.json"
db_url = "upa@upa-db:3306"
db_password = "upa-password"

# data renew
auto_refresh_hour = 6
