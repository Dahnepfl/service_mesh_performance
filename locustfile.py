import math
import time
from locust import HttpUser, task, between, constant, constant_throughput, events
from locust.runners import MasterRunner, WorkerRunner
import logging
from urllib.request import urlopen

initial_time = [time.time()]

def get_token():
    with urlopen(
            "https://raw.githubusercontent.com/istio/istio/release-1.12/security/tools/jwt/samples/demo.jwt") as response:
        html_content = response.read()
        encoding = response.headers.get_content_charset('utf-8')
        html_text = html_content.decode(encoding)
        return str(html_text).replace('\n', '')

class QuickstartUser(HttpUser):
    host = "http://backend-api:8080"
    token_string = get_token()
    wait_time = constant_throughput(10)

    @task
    def hello_world(self):
        #        self.client.get(url="/backend/", headers={"authorization": "Bearer " + self.token_string})
        self.client.get(url="/", headers={"authorization": "Bearer " + self.token_string})
        #QuickstartUser.wait_time = constant_throughput(10 + math.floor((time.time() - initial_time[0]) / 2))
    #  super().wait_time = constant_throughput(1 + math.floor((time.time() - initial_time[0]) / 2))


# Let us Create an object
logger = logging.getLogger()


# Fired when the master receives a message of type 'acknowledge_users'
def on_acknowledge(msg, **kwargs):
    # print(msg.data)
    # logging.info(msg.data)
    logger.info("perf_log " + msg.data)


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if not isinstance(environment.runner, WorkerRunner):
        environment.runner.register_message('test_users', on_acknowledge)


env = []


@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    initial_time[0] = time.time()
    env.append(environment)


def success_request(request_type, name, response_time, response_length):
    msg = '; '.join(
        [str(request_type), 'success', name, str(response_time), str(response_length),
         str(time.time() - initial_time[0])])
    env[0].runner.send_message('test_users', msg)


def failure_request(exception, request_type, name, response_time, response_length):
    msg = '; '.join(
        [str(exception), 'failure', name, str(response_time), str(response_length), str(time.time() - initial_time[0])])
    env[0].runner.send_message('test_users', msg)


events.request_success.add_listener(success_request)
events.request_failure.add_listener(failure_request)

#   @task(3)
#   def view_items(self):
#       for item_id in range(10):
#           self.client.get(f"/item?id={item_id}", name="/item")
#           time.sleep(1)

#   def on_start(self):
#       self.client.post("/login", json={"username":"foo", "password":"bar"})
