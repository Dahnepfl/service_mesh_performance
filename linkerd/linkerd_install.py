
import os
from request_generator import getPodName
import time


def install_linkerd():
    os.system('linkerd install | kubectl apply -f -')
    os.system('linkerd check')
    os.system('kubectl get -n default deploy -o yaml | linkerd inject - | kubectl apply -f -')
    os.system('kubectl annotate namespace default config.linkerd.io/disable-identity=true')

    while getPodName(label='linkerd.io/control-plane-component=proxy-injector', pod_namespace='linkerd', exit_on_error=False) == '':
        print("waiting linkerd.io/control-plane-component=proxy-injector installation")
        time.sleep(0.2)

    os.system('kubectl apply -f linkerd/backend_retry.yaml')
    os.system('kubectl apply -f linkerd/counter_retry.yaml')



def install_linkerd_mtls():
    os.system('linkerd install | kubectl apply -f -')
    os.system('linkerd check')
    os.system('kubectl get -n default deploy -o yaml | linkerd inject - | kubectl apply -f -')

    while getPodName(label='linkerd.io/control-plane-component=proxy-injector', pod_namespace='linkerd', exit_on_error=False) == '':
        print("waiting linkerd.io/control-plane-component=proxy-injector installation")
        time.sleep(0.2)

    os.system('kubectl apply -f linkerd/backend_retry.yaml')
    os.system('kubectl apply -f linkerd/counter_retry.yaml')

def install_linkerd_mtls_observability():
    os.system('linkerd install | kubectl apply -f -')
    os.system('linkerd check')
    os.system('kubectl get -n default deploy -o yaml | linkerd inject - | kubectl apply -f -')

    while getPodName(label='linkerd.io/control-plane-component=proxy-injector', pod_namespace='linkerd', exit_on_error=False) == '':
        print("waiting linkerd.io/control-plane-component=proxy-injector installation")
        time.sleep(0.2)

    # Observability
    os.system('linkerd viz install | kubectl apply -f -')
    os.system('linkerd check')

    os.system('kubectl apply -f linkerd/backend_retry.yaml')
    os.system('kubectl apply -f linkerd/counter_retry.yaml')


def uninstall_linkerd():
    os.system('linkerd viz uninstall | kubectl delete -f -')
    os.system('linkerd uninstall | kubectl delete -f -')

