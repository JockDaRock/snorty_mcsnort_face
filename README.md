# Snorty-McSnort-Face (Alpha)

This is my attempt (Proof of Concept) to run a small foot print version of a Snort Container Based off of a Python:Alpine container image.

>Disclaimer: This is still early stages.  So if you have any suggestions, problems, or requests you would like to see.  Please let me know!

There is a little bit of configuration required, but is fairly minimal and should get you going pretty quick.

## Requirements

1. Have Docker and Python (Python version 2 or 3 is fine) installed on the computer you are working from.
2. At Least basic knowledge of Python.
3. Knowledge of building and deploying Docker containers from commandline. 
4. Have a MQTT Broker to send alert messages to and receive alerts from.  Alternatively you can use the [Public Mosquitto MQTT Broker](https://test.mosquitto.org/) on port 1883 as your MQTT broker.
5. Familiarity with [Snort](https://www.snort.org/).
5. Snort rules you want to test.  Simple set of rules to get you going is already provided.

## Let's get started!!!

Git clone this repo to your computer in a terminal window.
```shell
$ git clone https://github.com/JockDaRock/snorty_mcsnort_face.git
```

Change you current working directory to snorty_mcsnort_face.

```shell
$ cd snorty_mcsnort_face
```

Modify the Dockerfile in this directory to account for your personal settings.

On line 4 of the Dockerfile change the values of MQTT and NETINT to reflect you environment and save the file.  It might look similar to the following:

```Dockerfile
ENV MQTT="test.mosquitto.org" MQTTPORT=1883 NETINT="eth0"
```

If you are feeling frisky and would like to modify the Python code in the snort_socket.py file, feel free to do so now.

Now let's build your container in your working directory.

```shell
$ docker build -t snort_face:latest .
```

Before we deploy the container, we will go ahead and run the Python program for the MQTT subcscriber.

In a different terminal window, navigate to the same working directory we are already in and modify line 3 the python file to connect to the MQTT Broker you are using.

```python
MQTT = "test.mosquitto.org"
```

Now that you have modified the file run the following command:

```shell
$ python mqtt_subscriber.py
```

When you are connected you should see a message in the terminal that looks like this:

```shell
$ Connected with result 0
```

For right now, move back to the first terminal window we started with.

Now let's deploy the container using the following command.

>Note: In the deployment of the Docker container we will be using --net=home flag.  This flag will give the Docker container the same network interfaces as the host.  This will give Snort the potential to monitor all traffic to and from the host.  If your host is set in promiscuous mode on your network, it will also give snort the potential to see everything on your network.

```shell
$ docker run -d --net=host --name snort_face0 snort_face
```

Now we will see if snort is working correctly.

From the same terminal window we deployed the Docker container, ping some other network device on your network.

```shell
$ ping 10.0.0.1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=1.81 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=1.90 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=1.53 ms
64 bytes from 10.0.0.1: icmp_seq=4 ttl=64 time=1.57 ms
64 bytes from 10.0.0.1: icmp_seq=5 ttl=64 time=2.16 ms
```

If you go back to terminal window where we have the python service, mqtt_subscriber.py running, you should see something like this being printed to the terminal over and over:

```shell
b'Pinging detected
```

That's it you are up and running.  Please feel free to put any more Snort rules in place that make sense for your network.  And please let me know what you think about this so far.

### Future

I will be adding better messaging and data parsing of alert packets through python to the message broker.

Adding ability to get alerts real-time or through intervals.

Thinking about adding logging support through [Elastic Stack](https://www.elastic.co/products).

Possibly adding fun services to show what is possible... like [SMS Through Tropo](https://www.tropo.com/) or chat messaging / collaboration through [Cisco Spark](https://developer.ciscospark.com/).
