
import os
from request_generator import getPodName
import time


def helm_prepare():
    os.system('helm repo add kuma https://kumahq.github.io/charts')

def helm_install():
    os.system('helm install --version 0.8.1 --create-namespace --namespace kuma-system kuma kuma/kuma')
    os.system('kubectl annotate namespace default kuma.io/mesh=default')
    os.system('kubectl annotate namespace default kuma.io/sidecar-injection=enabled')
    while getPodName(label='app=kuma-control-plane', pod_namespace='kuma-system', exit_on_error=False) == '':
        print("waiting app=kuma-control-plane installation")
        time.sleep(0.2)

    time.sleep(5)
    os.system('kubectl delete -f kuma/disable_retries.yaml')
    os.system('kubectl delete -f kuma/disable_timeout.yaml')


def helm_install_mtls():
    helm_install()
    os.system('kubectl apply -f kuma/mtls.yaml')

def helm_install_observability():
    helm_install()
    os.system('kumactl install metrics | kubectl apply -f -')
    os.system('kubectl apply -f kuma/metrics.yaml')
    while getPodName(label='app=grafana', pod_namespace='kuma-metrics', exit_on_error=False) == '':
        print("waiting app=grafana installation")
        time.sleep(0.2)

def helm_install_mtls_jwt():
    helm_install()
    os.system('kubectl apply -f kuma/mtls.yaml')
    os.system('kubectl apply -f kuma/jwt_envoy.yaml')

def helm_uninstall():
    os.system('kubectl delete -f kuma/metrics.yaml')
    os.system('kumactl install metrics | kubectl delete -f -')

    os.system('helm delete kuma -n kuma-system')
    os.system('kubectl delete namespace kuma-system')
    while getPodName(label='app=kuma-control-plane', pod_namespace='kuma-system', exit_on_error=False) != '':
        print("waiting kuma-control-plane uninstall")
        time.sleep(0.2)

def install_kuma():
    os.system('kumactl install control-plane | kubectl apply -f -')
    os.system('kubectl annotate namespace default kuma.io/mesh=default')
    os.system('kubectl annotate namespace default kuma.io/sidecar-injection=enabled')
    while getPodName(label='app=kuma-control-plane', pod_namespace='kuma-system', exit_on_error=False) == '':
        print("waiting app=kuma-control-plane installation")
        time.sleep(0.2)


def uninstall_kuma():
    os.system('kumactl install control-plane | kubectl delete -f -')
    while getPodName(label='app=kuma-control-plane', pod_namespace='kuma-system', exit_on_error=False) != '':
        print("waiting kuma-control-plane uninstall")
        time.sleep(0.2)
