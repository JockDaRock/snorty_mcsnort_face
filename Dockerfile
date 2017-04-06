FROM python:alpine

#Change these values dependant on your environment
ENV MQTT="test.mosquitto.org" MQTTPORT=1883 NETINT="enp0s3"


RUN pip install --upgrade pip setuptools wheel
COPY requirements.txt .
RUN pip install -r requirements.txt

#Copy applications
COPY snort_socket.py .
COPY snort_parser.py .
COPY snort_api.py .
COPY super_snort.conf .
COPY simple_snort.conf /etc/snort/simple_snort.conf
COPY rules /etc/snort/rules

#Replace apk directories with the latest directories
RUN echo "http://dl-3.alpinelinux.org/alpine/edge/main" > /etc/apk/repositories

RUN apk upgrade --update-cache --available
RUN apk add --no-cache snort daq supervisor git

RUN sed -i '/import alert/c\import snortunsock.alert as alert' /usr/local/lib/python3.6/site-packages/snortunsock/snort_listener.py

EXPOSE 5000

#run processes from Supervisor
ENTRYPOINT ["/usr/bin/supervisord","-c","/super_snort.conf"]
