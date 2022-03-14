from __future__ import print_function

import time

import os
from kubernetes import client, config
from kubernetes.stream import stream
from kubernetes.client import configuration
import sys

# create an instance of the API class

config.load_kube_config()

configuration.assert_hostname = False
api_instance = client.CoreV1Api()


def run_command_locust_master(command):
    exec_command = [
        '/bin/sh',
        '-c',
        command]
    resp = stream(api_instance.connect_get_namespaced_pod_exec, getPodName(pod_namespace='default'), 'default',
                  container='locust-master',
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)
    print("Response: " + resp)


def start(users):
    run_command_locust_master(
        "curl -X POST -F 'user_count={users}' -F 'spawn_rate=20' -F 'host=http://counter-api.default.svc.cluster.local:8081'  http://localhost:8089/swarm".format(
            users=str(users)))


def stop():
    run_command_locust_master("curl -X GET http://localhost:8089/stop")


def delete_all():
    os.system('kubectl delete all --all -n default')
    os.system('kubectl delete all --all -n istio-system')
    os.system('kubectl delete all --all -n linkerd')
    os.system('kubectl delete all --all -n kuma-system')
    os.system('kubectl delete all --all -n kuma-metrics')
    os.system('kubectl delete all --all -n consul')
    os.system('kubectl delete namespace linkerd')
    os.system('kubectl delete namespace kuma-system')
    os.system('kubectl delete namespace istio-system')
    os.system('kubectl delete namespace consul')


def install_locust():
    os.system('kubectl apply -f locust-deployment/deployment.yaml -n default')
    os.system('kubectl apply -f locust-deployment/deployment-worker.yaml -n default')
    #os.system('kubectl apply -f locust-deployment/hpa.yaml -n default')

    while getPodName(label='app=locust-master', pod_namespace='default', exit_on_error=False) == '':
        print("waiting locust-master to be available...")
        time.sleep(0.2)

    while getPodName(label='app=locust-worker', pod_namespace='default', exit_on_error=False) == '':
        print("waiting locust-worker to be available...")
        time.sleep(0.2)


def delete_locust():
    os.system('kubectl delete -f locust-deployment/hpa.yaml -n default')
    os.system('kubectl delete -f locust-deployment/deployment.yaml -n default')

    while getPodName(label='app=locust-master', pod_namespace='default', exit_on_error=False) != '':
        print("waiting locust-master to be deleted...")
        time.sleep(0.2)

    os.system('kubectl delete -f locust-deployment/deployment-worker.yaml -n default')

    while getPodName(label='app=locust-worker', pod_namespace='default', exit_on_error=False) != '':
        print("waiting locust-worker to be deleted...")
        time.sleep(0.2)


def deploy_app():
   # os.system('kubectl apply -f backend-api/deployment.yaml')
    os.system('kubectl apply -f counter-api/deployment.yaml')

   # while getPodName(label='app=backend-api', exit_on_error=False) == '':
   #     print("waiting backend-api to be available...")
   #     time.sleep(0.2)

    while getPodName(label='app=counter-api', exit_on_error=False) == '':
        print("waiting counter-api to be available...")
        time.sleep(0.2)


def delete_app():
    os.system('kubectl delete -f counter-api/deployment.yaml')
   # os.system('kubectl delete -f backend-api/deployment.yaml')
   # while getPodName(label='app=backend-api', exit_on_error=False) != '':
   #     print("waiting backend-api to be deleted...")
   #     time.sleep(1)

    while getPodName(label='app=counter-api', exit_on_error=False) != '':
        print("waiting counter-api to be deleted...")
        time.sleep(1)


def getPodName(label='app=locust-master', pod_namespace='default', exit_on_error=True):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace=pod_namespace, label_selector=label)
    name = ''
    for pod in pod_list.items:
        if pod.status.phase == 'Running' and len(pod.status.container_statuses) > 0 and \
                pod.status.container_statuses[0].ready:
            name = pod.metadata.name
        else:
            print("Pod status: {stat}".format(stat=pod.status.phase))

    if name == '' and exit_on_error:
        print("Master pod not found")
        quit()

    return name


if sys.argv[0] == 'request_generator.py':
    if len(sys.argv) != 2:
        print('args: \'start\' or \'stop\'');
    elif sys.argv[1] == 'start':
        start(10)
    elif sys.argv[1] == 'stop':
        stop();
    else:
        print('args: \'start\' or \'stop\'');


def re_deploy_app():
    os.system('kubectl delete pods --all -n default')

    # while getPodName(label='app=backend-api', exit_on_error=False) == '':
    #     print("waiting backend-api to be available...")
    #     time.sleep(0.2)

    while getPodName(label='app=counter-api', exit_on_error=False) == '':
        print("waiting counter-api to be available...")
        time.sleep(0.2)