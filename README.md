# ADS Server

Run in Python3.8

### Install dependencies

We recommend you to use pip package manager.

```
pip install Flask
pip install pandas
pip install numpy
pip install twilio
```

### How to use it 

#### Run api in local environment

* At the root folder of the project

Windows 10
```
py -m Serveur.api
```

Linux system
```
python3.8 -m Serveur.api
```

#### Run sensor manager in local environment
* At the root folder of the project

Windows 10
```
py -m Serveur.sensor_manager
```

Linux system
```
python3.8 -m Serveur.sensor_manager
```

#### Using twilio api 

The best way is to follow the tutorial : https://www.twilio.com/docs/sms/quickstart/python 

#### For testing or running any oth module
* At the root folder of the project

Windows 10
```
py -m Serveur.<module_name>
```

Linux system
```
python3.8 -m Serveur.<module_name>
```

### Make a test

Run 

```
py -m Serveur.api
```

And add a log file in reception_log