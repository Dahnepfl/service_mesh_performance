import os
from request_generator import getPodName
import time


def setup_helm():
    os.system('helm repo add hashicorp https://helm.releases.hashicorp.com')
    os.system('helm repo add grafana https://grafana.github.io/helm-charts')
    os.system('helm repo add prometheus-community https://prometheus-community.github.io/helm-charts')


def install_consul():
    os.system(
        'helm install -f ./consul/config.yaml consul hashicorp/consul --create-namespace -n consul --version "0.39.0"')
    while getPodName(label='app=consul', pod_namespace='consul', exit_on_error=False) == '':
        print("waiting consul installation")
        time.sleep(0.2)

    time.sleep(15)
    os.system('kubectl apply -f consul/disable_timeout.yaml')


def install_consul_with_mtls():
    os.system(
        'helm install -f ./consul/secure-dc1.yaml consul hashicorp/consul --create-namespace -n consul --version "0.39.0"')
    while getPodName(label='app=consul', pod_namespace='consul', exit_on_error=False) == '':
        print("waiting consul installation")
        time.sleep(0.2)

    time.sleep(15)
    os.system('kubectl apply -f consul/intentions.yaml')
    os.system('kubectl apply -f consul/disable_timeout.yaml')


def install_consul_with_mtls_observability():
    os.system(
        'helm install -f ./consul/config_metrics.yaml consul hashicorp/consul --create-namespace -n consul --version "0.39.0"')
    while getPodName(label='app=consul', pod_namespace='consul', exit_on_error=False) == '':
        print("waiting consul installation")
        time.sleep(0.2)

    os.system(
        'helm install -f ./consul/prometheus-values.yaml prometheus prometheus-community/prometheus --version "14.9.2" --wait')

    while getPodName(label='app=prometheus', pod_namespace='default', exit_on_error=False) == '':
        print("waiting app=prometheus installation")
        time.sleep(0.2)

    time.sleep(15)
    os.system('kubectl apply -f consul/disable_timeout.yaml')


def uninstall_consul():
    os.system('kubectl delete -f consul/disable_timeout.yaml')

    os.system(
        'helm delete prometheus')
    os.system('helm delete consul -n consul')
    while getPodName(label='app=consul', pod_namespace='consul', exit_on_error=False) != '':
        print("waiting consul uninstall")
        time.sleep(0.2)
