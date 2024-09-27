import psutil
import yaml
from prometheus_client import start_http_server, Gauge, Info
import time
from concurrent.futures import ThreadPoolExecutor


# 读取YAML文件
def read_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(e)


# 获取进程数据
def print_process(pid):
    # 使用进程ID获取进程对象
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"进程ID {pid} 不存在")
        time.sleep(1)
        return [-1, '进程不存在', 0, 0, 0]

    # 打印结果: 进程ID, 进程名称, CPU利用率, 内存, 内存占用率
    return [pid, process.name(), process.cpu_percent(interval=1), process.memory_info().rss, process.memory_percent()]


# 使用函数
yaml_file_path = 'config.yml'  # 替换为你的YAML文件路径
data = read_yaml(yaml_file_path)
pid_list = data['pid_list']

# exporter信息
subprocess_exporter_info = Info('subprocess_exporter_info', '子进程监控基础信息')
subprocess_info = Gauge('subprocess_info', '子进程信息', ['pid', 'name'])
cpu_utilization = Gauge('cpu_utilization', 'CPU利用率', ['pid', 'name'])
memory = Gauge('memory', '内存(MB)', ['pid', 'name'])
memory_usage_rate = Gauge('memory_usage_rate', '内存占用率', ['pid', 'name'])

# 赋值
subprocess_exporter_info.info({'version': '1.1.1', 'author': '岳罡', 'blog': 'https://www.cnblogs.com/test-gang'})
def process_request(pid_lists):
    for i in pid_lists:
        a = print_process(i)
        subprocess_info.labels(pid=f'{i}', name=f'{a[1]}')
        cpu_utilization.labels(pid=f'{i}', name=f'{a[1]}').set(a[2])
        memory.labels(pid=f'{i}', name=f'{a[1]}').set(a[3]/1048576)
        memory_usage_rate.labels(pid=f'{i}', name=f'{a[1]}').set(a[4])


if __name__ == '__main__':
    # 启动 HTTP 服务器，默认监听在 8000 端口
    start_http_server(data['config']['start_http_server'])


    # 创建 ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as executor:  # 控制线程池大小为4
        # 循环处理请求
        while True:
            # 提交任务给线程池
            future = executor.submit(process_request, pid_list)
            time.sleep(4)

