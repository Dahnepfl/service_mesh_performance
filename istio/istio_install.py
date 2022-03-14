
import os
from request_generator import getPodName
import time


def helm_prepare():
    os.system('helm repo add istio https://istio-release.storage.googleapis.com/charts')

def helm_install_mtls_jwt():
    helm_install_mtls()
    os.system('kubectl apply -f istio/jwt_base.yaml')

def helm_install_mtls_observability():
    helm_install_with_telemetry()
    os.system('kubectl apply -f istio/mtls.yaml')
    os.system('kubectl apply -f istio/addons/')

def helm_install_mtls_opa():
    helm_install_without_telemetry()

    time.sleep(10)
    os.system('kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/opa-envoy-plugin/main/examples/istio/quick_start.yaml')
    while getPodName(label='app=admission-controller', pod_namespace='opa-istio', exit_on_error=False) == '':
        print("waiting app=admission-controller opa installation")
        time.sleep(0.2)

    time.sleep(1)
    os.system('kubectl label namespace default opa-istio-injection="enabled"')
    time.sleep(1)
    os.system('kubectl apply -f istio/opa/service_entry.yaml')
    time.sleep(1)
    os.system('kubectl apply -f istio/opa/config_map.yaml')




def helm_uninstall_mtls_opa():
    os.system('kubectl delete -f istio/mtls.yaml')
    os.system('kubectl delete -f istio/opa/service_entry.yaml')
    os.system('kubectl delete -f istio/opa/config_map.yaml')
    os.system('kubectl delete -f https://raw.githubusercontent.com/open-policy-agent/opa-envoy-plugin/main/examples/istio/quick_start.yaml')
    helm_uninstall()

def helm_install_mtls_jwt_envoy():
    helm_install_mtls()
    os.system('kubectl apply -f istio/jwt_envoy.yaml')

def helm_install_without_telemetry():
    helm_uninstall()
    os.system('kubectl create namespace istio-system')
    os.system('helm install istio-base istio/base -n istio-system --version "1.12.2"')
    time.sleep(1)
    os.system('helm install istiod istio/istiod -n istio-system --wait  --set telemetry.enabled=false --set telemetry.v2.enabled=false --version "1.12.2"')
    time.sleep(1)
    while getPodName(label='app=istiod', pod_namespace='istio-system', exit_on_error=False) == '':
        print("waiting istiod installation")
        time.sleep(0.2)
    time.sleep(5)
    os.system('kubectl label namespace default istio-injection=enabled')
    os.system('kubectl apply -f istio/disable_retries.yaml')

def helm_install_mtls():
    helm_install_without_telemetry()
    os.system('kubectl apply -f istio/mtls.yaml')

def helm_install_with_telemetry():
    helm_uninstall()
    os.system('kubectl create namespace istio-system')
    os.system('helm install istio-base istio/base -n istio-system')
    time.sleep(1)
    os.system('helm install istiod istio/istiod -n istio-system --wait')
    time.sleep(1)
    while getPodName(label='app=istiod', pod_namespace='istio-system', exit_on_error=False) == '':
        print("waiting istiod installation")
        time.sleep(0.2)

    time.sleep(5)
    os.system('kubectl label namespace default istio-injection=enabled')
    os.system('kubectl apply -f istio/disable_retries.yaml')


def helm_uninstall():
    os.system('kubectl delete -f istio/disable_retries.yaml')
    os.system('kubectl delete -f istio/mtls.yaml')
    os.system('kubectl delete -f istio/jwt_envoy.yaml')
    os.system('kubectl delete -f istio/jwt_base.yaml')
    os.system('kubectl delete -f istio/addons/')
    os.system('helm delete istiod -n istio-system')
    time.sleep(1)
    os.system('helm delete istio-base -n istio-system')
    time.sleep(1)
    while getPodName(label='app=istiod', pod_namespace='istio-system', exit_on_error=False) != '':
        print("waiting istiod uninstall")
        time.sleep(0.2)

    os.system('kubectl delete all --all -n istio-system')
    os.system('kubectl delete namespace istio-system')

# not used, helm prefered
def install_istio():
    os.system('istioctl install --set profile=demo -y')
    os.system('kubectl label namespace default istio-injection=enabled')
    while getPodName(label='app=istiod', pod_namespace='istio-system', exit_on_error=False) == '':
        print("waiting istiod installation")
        time.sleep(0.2)


def uninstall_istio():
    os.system('istioctl manifest generate --set profile=demo | kubectl delete --ignore-not-found=true -f -')
    os.system('istioctl tag remove default')
    os.system('kubectl delete namespace istio-system')
    while getPodName(label='app=istiod', pod_namespace='istio-system', exit_on_error=False) != '':
        print("waiting istiod uninstall")
        time.sleep(0.2)
