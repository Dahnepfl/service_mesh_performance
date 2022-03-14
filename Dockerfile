FROM locustio/locust:2.7.3

COPY locustfile.py locustfile.py
#RUN locust -f locustfile.py --master -H http://locust-master:8089

EXPOSE 8020
