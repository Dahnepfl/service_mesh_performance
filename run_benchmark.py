import consul.consul_install
import create_graphs
import kuma.kuma_install
import linkerd.linkerd_install
import request_generator
import time
import istio.istio_install
from ram_cpu_perf import RamCpuBenchmark
import os


def test_with_mesh(name, install_mesh_callback, uninstall_mesh_callback, users=4, j=1):
    name_with_rps = '[RPS = {rps}] {old}'.format(rps=(users * 10), old=name, j=j)
  #  name_with_rps = 'Run {j} - {old}'.format(old=name, j=j)

    install_mesh_callback()
    time.sleep(10)
    request_generator.deploy_app()
    time.sleep(20)
    request_generator.install_locust()
    time.sleep(20)

    print("*********")
    print("Start testing")
    bench = RamCpuBenchmark(name_with_rps)
    bench.start()

    request_generator.start(users)
    i = 70
    end = time.time() + 70
    while time.time() < end:
        print("[{n}]Remaining: {sec} seconds of testing...".format(sec=i, n=name_with_rps))
        i = i - 1
        time.sleep(1)

    request_generator.stop()
    bench.stop()
    request_generator.delete_app()
    time.sleep(10)
    create_graphs.LogGraphs(name_with_rps).generateGraph()
    request_generator.delete_locust()
    time.sleep(1)
    uninstall_mesh_callback()
    time.sleep(1)
    request_generator.delete_all()
    time.sleep(1)


def test_istio_with_telemetry(users=4, j=1):
    test_with_mesh('Istio with telemetry', istio.istio_install.helm_install_with_telemetry,
                   istio.istio_install.helm_uninstall, users=users, j=j)


def test_istio_without_telemetry(users=4, j=1):
    test_with_mesh('Istio basic', istio.istio_install.helm_install_without_telemetry,
                   istio.istio_install.helm_uninstall, users=users, j=j)


def test_istio_mtls(users=4, j=1):
    test_with_mesh('Istio mTLS', istio.istio_install.helm_install_mtls,
                   istio.istio_install.helm_uninstall, users=users, j=j)


def test_istio_mtls_jwt(users=4, j=1):
    test_with_mesh('Istio mTLS + mesh JWT', istio.istio_install.helm_install_mtls_jwt,
                   istio.istio_install.helm_uninstall, users=users, j=j)


def test_istio_mtls_observability(users=4, j=1):
    test_with_mesh('Istio mTLS + observability', istio.istio_install.helm_install_mtls_observability,
                   istio.istio_install.helm_uninstall, users=users, j=j)


def test_istio_mtls_jwt_envoy(users=4, j=1):
    test_with_mesh('Istio mTLS + Envoy JWT', istio.istio_install.helm_install_mtls_jwt_envoy,
                   istio.istio_install.helm_uninstall, users=users, j=j)


def test_istio_opa(users=4, j=1):
    test_with_mesh('Istio mTLS + OPA JWT', istio.istio_install.helm_install_mtls_opa,
                   istio.istio_install.helm_uninstall_mtls_opa, users=users, j=j)


def run_without_mesh(users=4, j=1):
    test_with_mesh('Without mesh', lambda: None, lambda: None, users=users, j=j)


def test_linkerd(users=4, j=1):
    test_with_mesh('Linkerd basic', linkerd.linkerd_install.install_linkerd, linkerd.linkerd_install.uninstall_linkerd,
                   users=users, j=j)


def test_linkerd_mtls(users=4, j=1):
    test_with_mesh('Linkerd mTLS', linkerd.linkerd_install.install_linkerd_mtls,
                   linkerd.linkerd_install.uninstall_linkerd, users=users, j=j)


def test_linkerd_mtls_observability(users=4, j=1):
    test_with_mesh('Linkerd mTLS + Observability', linkerd.linkerd_install.install_linkerd_mtls_observability,
                   linkerd.linkerd_install.uninstall_linkerd, users=users, j=j)


def test_kuma(users=4, j=1):
    test_with_mesh('Kuma basic', kuma.kuma_install.helm_install, kuma.kuma_install.helm_uninstall, users=users, j=j)


def test_kuma_mtls(users=4, j=1):
    test_with_mesh('Kuma mTLS', kuma.kuma_install.helm_install_mtls, kuma.kuma_install.helm_uninstall, users=users, j=j)


def test_kuma_mtls_obs(users=4, j=1):
    test_with_mesh('Kuma mTLS + Observability', kuma.kuma_install.helm_install_observability,
                   kuma.kuma_install.helm_uninstall, users=users, j=j)


def test_kuma_mtls_jwt(users=4, j=1):
    test_with_mesh('Kuma mTLS + envoy JWT', kuma.kuma_install.helm_install_mtls_jwt, kuma.kuma_install.helm_uninstall,
                   users=users, j=j)


def test_consul(users=4, j=1):
    test_with_mesh('Consul basic', consul.consul_install.install_consul, consul.consul_install.uninstall_consul,
                   users=users, j=j)


def test_consul_mtls(users=4, j=1):
    test_with_mesh('Consul mTLS', consul.consul_install.install_consul_with_mtls,
                   consul.consul_install.uninstall_consul, users=users, j=j)


def test_consul_mtls_observability(users=4, j=1):
    test_with_mesh('Consul Observability', consul.consul_install.install_consul_with_mtls_observability,
                   consul.consul_install.uninstall_consul, users=users, j=j)


# Prepare helm repo
consul.consul_install.setup_helm()
istio.istio_install.helm_prepare()
kuma.kuma_install.helm_prepare()
os.system('helm repo update')

# uninstall previous install
request_generator.delete_app()
consul.consul_install.uninstall_consul()
istio.istio_install.helm_uninstall_mtls_opa()
istio.istio_install.helm_uninstall()
linkerd.linkerd_install.uninstall_linkerd()
kuma.kuma_install.helm_uninstall()
request_generator.delete_all()

rps = [10, 20, 40, 60, 70, 100, 120, 150, 180]
for j in [557]:  # , 2, 3]:
    for i in rps:
        # Basic config
        run_without_mesh()
        test_istio_without_telemetry()
        test_consul()
        test_kuma()
        test_linkerd()

        # mTLS
        test_istio_mtls(users=i, j=j)
        test_kuma_mtls(users=i, j=j)
        test_linkerd_mtls(users=i, j=j)
        test_consul_mtls(users=i, j=j)

        # JWT
        test_istio_mtls_jwt(users=i, j=j)
        test_istio_mtls_jwt_envoy(users=i, j=j)
        test_kuma_mtls_jwt(users=i, j=j)
        test_istio_opa()
        # OBS
        test_kuma_mtls_obs(users=i, j=j)
        test_consul_mtls_observability(users=i, j=j)
        test_linkerd_mtls_observability(users=i, j=j)
        test_istio_mtls_observability(users=i, j=j)

