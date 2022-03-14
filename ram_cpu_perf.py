from kubernetes import client, config
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import threading
import numpy as np


class RamCpuBenchmark:
    def __init__(self, name):
        self.thr = threading.Thread(target=self.collect_ram_cpu_perf, args=(), kwargs={})
        self.start_benchmark = False
        self.name = name

    def collect_ram_cpu_perf(self):

        print("*** Start RAM - CPU benchmark ***")
        config.load_kube_config()

        df = pd.DataFrame(columns=['container', 'cpu', 'ram', 'time'])
        df['cpu'] = pd.to_numeric(df['cpu'])
        df['ram'] = pd.to_numeric(df['ram'])
        df['time'] = pd.to_numeric(df['time'])
        api = client.CustomObjectsApi()
        i = 0
        initial_time = time.time()
        while self.start_benchmark:
            i = i + 1
            resource = api.list_namespaced_custom_object(group="metrics.k8s.io", version="v1beta1", namespace="default",
                                                         plural="pods", label_selector='app=counter-api')
            dictionary = {}
            for pod in resource["items"]:
                for container in pod['containers']:
                    memory = container['usage']['memory']
                    if len(container['usage']['cpu']) > 1 and len(container['usage']['memory']) > 2:
                        if 'Ki' in memory:
                            memory = int(memory[0:-2]) / 1000
                        else:
                            memory = int(memory[0:-2])

                        cpu = 0
                        if (container['usage']['cpu'])[-1] == 'n':
                            cpu = int(container['usage']['cpu'][0:-1]) / 1000000
                        elif (container['usage']['cpu'])[-1] == 'u':
                            cpu = int(container['usage']['cpu'][0:-1]) / 1000
                        else:
                            cpu = int(container['usage']['cpu'][0:-1])

                        if container['name'] not in dictionary:
                            dictionary[container['name']] = {"cpu": [], "ram": []}

                        dictionary[container['name']]["cpu"].append(cpu)
                        dictionary[container['name']]["ram"].append(memory)

            for key in dictionary:
                df.loc[len(df)] = \
                    {
                        'container': key,
                        'cpu': np.mean(dictionary[key]['cpu']),
                        'ram': np.mean(dictionary[key]['ram']),
                        'time': time.time() - initial_time
                    }
            if i % 15 == 0:
                self.create_graph_cpu_ram(df)

            time.sleep(0.75)
        print("*** END RAM - CPU benchmark ***")
        self.create_graph_cpu_ram(df, stats=True)

    def create_graph_cpu_ram(self, df, stats=False):
        if (len(df) == 0):
            return
        if stats:
            with open('stats/{name}_stats_usage.txt'.format(name=self.name.replace(' ', '_')), 'w') as f:
                f.write("There is {len} datas.\n".format(len=len(df)))
                print("There is {len} datas.".format(len=len(df)))
                f.write("service: ram: max {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].max()))
                f.write("service: ram: mean {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].mean()))
                f.write("service: ram: 80 {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].quantile(0.8)))
                f.write("service: ram: 90 {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].quantile(0.9)))
                f.write("service: ram: 99 {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].quantile(0.99)))
                print("service: ram: max {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].max()))
                print("service: ram: mean {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].mean()))
                print("service: ram: 80 {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].quantile(0.8)))
                print("service: ram: 90 {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].quantile(0.9)))
                print("service: ram: 99 {len}\n".format(len=df[df['container'] == 'counter-api']['ram'].quantile(0.99)))
                f.write("service: cpu: max {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].max()))
                f.write("service: cpu: mean {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].mean()))
                f.write("service: cpu: 80 {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].quantile(0.8)))
                f.write("service: cpu: 90 {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].quantile(0.9)))
                f.write("service: cpu: 99 {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].quantile(0.99)))
                print("service: cpu: max {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].max()))
                print("service: cpu: mean {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].mean()))
                print("service: cpu: 80 {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].quantile(0.8)))
                print("service: cpu: 90 {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].quantile(0.9)))
                print("service: cpu: 99 {len}\n".format(len=df[df['container'] == 'counter-api']['cpu'].quantile(0.99)))


                f.write("sidecar: ram: max {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].max()))
                f.write("sidecar: ram: mean {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].mean()))
                f.write("sidecar: ram: 80 {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].quantile(0.8)))
                f.write("sidecar: ram: 90 {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].quantile(0.9)))
                f.write("sidecar: ram: 99 {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].quantile(0.99)))
                print("sidecar: ram: max {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].max()))
                print("sidecar: ram: mean {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].mean()))
                print("sidecar: ram: 80 {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].quantile(0.8)))
                print("sidecar: ram: 90 {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].quantile(0.9)))
                print("sidecar: ram: 99 {len}\n".format(len=df[df['container'] != 'counter-api']['ram'].quantile(0.99)))
                f.write("sidecar: cpu: max {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].max()))
                f.write("sidecar: cpu: mean {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].mean()))
                f.write("sidecar: cpu: 80 {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].quantile(0.8)))
                f.write("sidecar: cpu: 90 {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].quantile(0.9)))
                f.write("sidecar: cpu: 99 {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].quantile(0.99)))
                print("sidecar: cpu: max {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].max()))
                print("sidecar: cpu: mean {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].mean()))
                print("sidecar: cpu: 80 {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].quantile(0.8)))
                print("sidecar: cpu: 90 {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].quantile(0.9)))
                print("sidecar: cpu: 99 {len}\n".format(len=df[df['container'] != 'counter-api']['cpu'].quantile(0.99)))

        sns.set_theme(style="darkgrid")
        sns.lineplot(x="time", y="ram",
                     hue="container",  # style="event",
                     data=df)
        plt.ylabel("Memory (Mi)")
        plt.xlabel("Time")
        plt.title("[{name}] RAM usage".format(name=self.name))
        plt.subplots_adjust(left=.17)
        plt.ylim(0, 512)
        plt.savefig("graphs/{name}-ram.png".format(name=self.name.replace(' ', '_')), bbox_inches='tight')
        print("graph saved to {name}-ram.png".format(name=self.name))
        plt.close()

        sns.lineplot(x="time", y="cpu",
                     hue="container",  # style="event",
                     data=df)
        plt.title("[{name}] CPU usage".format(name=self.name))
        plt.ylim(0, 325)
        plt.xlabel("Time")
        plt.ylabel("CPU (milli)")
        plt.savefig("graphs/{name}-cpu.png".format(name=self.name.replace(' ', '_')), bbox_inches='tight')
        print("graph saved to {name}-cpu.png".format(name=self.name))
        plt.close()

    def start(self):
        self.start_benchmark = True
        self.thr.start()
        if not self.thr.is_alive():
            print("Thread not working [ram_cpu_perf]")
            quit()

    def stop(self):
        self.start_benchmark = False
        self.thr.join()
