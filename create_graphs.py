import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from request_generator import getPodName
from io import StringIO
from csv import writer

sns.set_theme()


class LogGraphs:
    def __init__(self, name):
        self.name = name
        self.log_location = 'logs/{name}_logs.txt'.format(name=self.name.replace(' ', '_'))

    def get_log_file(self):
        name = getPodName(pod_namespace='default', label='app=locust-master')

        os.system(
            'kubectl cp -n default -c locust-master {pod_name}:/home/locust/logs.txt "{loc}"'.format(pod_name=name,
                                                                                                     loc=self.log_location)
        )

    def log_to_frame(self):
        with open(self.log_location, mode='r', encoding='UTF-8') as f:
            output = StringIO()
            csv_writer = writer(output)

            for line in f:
                if "perf_log" in line:
                    split = line.split(";")
                    csv_writer.writerow([split[1], split[3], split[4], split[5]])
                else:
                    pass

        output.seek(0)  # we need to get back to the start of the BytesIO
        df = pd.read_csv(output, names=['success', 'response_time', 'response_length', 'time'], header=None)

        df['time'] = pd.to_numeric(df['time'])
        df['response_time'] = pd.to_numeric(df['response_time'])
        df['response_length'] = pd.to_numeric(df['response_length'])
        df['time'] = pd.to_numeric(df['time'])

        return df

    def getDataframe(self, get_logs_from_pod=True):
        if get_logs_from_pod:
            self.get_log_file()
        return self.log_to_frame()

    def generateGraph(self, get_logs_from_pod=True):
        log_df = self.getDataframe(get_logs_from_pod)
        log_df['response_time'] = pd.to_numeric(log_df['response_time'])

        with open('stats/{name}_stats.txt'.format(name=self.name.replace(' ', '_')), 'w') as f:
            f.write("There is {len} requests.\n".format(len=len(log_df)))
            print("There is {len} requests.".format(len=len(log_df)))

            f.write("Average response time: {mean}\n".format(mean=log_df['response_time'].mean(axis=0)))
            print("Average response time: {mean}".format(mean=log_df['response_time'].mean(axis=0)))

            f.write("Response time median: {mean}\n".format(mean=log_df['response_time'].median(axis=0)))
            print("Response time median: {mean}".format(mean=log_df['response_time'].median(axis=0)))

            f.write("Response time std: {mean}\n".format(mean=log_df['response_time'].std(axis=0)))
            print("Response time std: {mean}".format(mean=log_df['response_time'].std(axis=0)))

            f.write("Response time 1th percentile: {mean} [ms]\n".format(mean=log_df['response_time'].quantile(0.01)))
            print("Response time 1th percentile: {mean} [ms]".format(mean=log_df['response_time'].quantile(0.01)))

            f.write("Response time 5th percentile: {mean} [ms]\n".format(mean=log_df['response_time'].quantile(0.05)))
            print("Response time 5th percentile: {mean} [ms]".format(mean=log_df['response_time'].quantile(0.05)))

            f.write("Response time 90th percentile: {mean} [ms]\n".format(mean=log_df['response_time'].quantile(0.9)))
            print("Response time 90th percentile: {mean} [ms]".format(mean=log_df['response_time'].quantile(0.9)))

            f.write("Response time 95th percentile: {mean} [ms]\n".format(mean=log_df['response_time'].quantile(0.95)))
            print("Response time 95th percentile: {mean} [ms]".format(mean=log_df['response_time'].quantile(0.95)))

            f.write("Response time 99th percentile: {mean} [ms]\n".format(mean=log_df['response_time'].quantile(0.99)))
            print("Response time 99th percentile: {mean} [ms]".format(mean=log_df['response_time'].quantile(0.99)))

            f.write(
                "Response time 99.9th percentile: {mean} [ms]\n".format(mean=log_df['response_time'].quantile(0.999)))
            print("Response time 99.9th percentile: {mean} [ms]".format(mean=log_df['response_time'].quantile(0.999)))

            f.write("max Response time {mean} [ms]\n".format(mean=log_df['response_time'].max()))
            print("max Response time {mean} [ms]".format(mean=log_df['response_time'].max()))

            f.write("min Response time {mean} [ms]\n".format(mean=log_df['response_time'].min()))
            print("min Response time {mean} [ms]".format(mean=log_df['response_time'].min()))

            f.write("success/failure: {res}\n".format(res=log_df['success'].value_counts(dropna=False)))
            print("success/failure: {res}\n".format(res=log_df['success'].value_counts(dropna=False)))

        #[..] generate graphs
