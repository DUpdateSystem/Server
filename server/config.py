import multiprocessing

debug_mode = False
auto_refresh_hour = 6
cloud_rule_hub_url = "https://raw.githubusercontent.com/DUpdateSystem/UpgradeAll-rules/master/rules/rules.json"
db_url = "upa@upa-db:3306"
db_password = "upa-password"

timeout_api = 15
timeout_getter = 45

# service discovery
node_activity_time = 60

# getter
async_worker_num = 16  # 并行协程数
thread_worker_num = multiprocessing.cpu_count() * 2  # 并行线程数

# service url
worker_url = 'ipc:///tmp/worker{i}_{i}.ipc'
discovery_url = 'ipc:///tmp/worker{i}.ipc'
