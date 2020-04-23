from machine import I2C
from lib.umqtt.simple import MQTTClient
from network import WLAN
import machine
import time
import ujson
import utime
import pycom
import ubinascii
import struct
import _thread

#BUFFER -- bytearray([12])

# Node use Yellow LED
pycom.heartbeat(False)

# I2C init 
#ADDRESS
HIGH_ADDRESS = 0x78
LOW_ADDRESS = 0x77

HIGHT_DATA_LIST = LOW_DATA_LIST = []

i2c_sensor = I2C(0)
i2c_sensor.init(mode=I2C.MASTER, baudrate=115200, pins=('P9','P10'))

#SCAN DEVICE
devices = i2c_sensor.scan()
print('i2c devices found:',len(devices))
for device in devices:
    print("Decimal address: ",device," | Hexa address: ",hex(device))

def getHigh12SectionValue():
    # high_data = ubinascii.b2a_base64(i2c_sensor.readfrom(HIGH_ADDRESS,12))
    high_data = i2c_sensor.readfrom(HIGH_ADDRESS,12)
    print("HIGH DATA : " + str(high_data))
    HIGHT_DATA_LIST.append(high_data)
    time.sleep(2)

def getLow8SectionValue():
    low_data = i2c_sensor.readfrom(LOW_ADDRESS, 8)
    print("LOW_DATA : " + str(low_data))
    LOW_DATA_LIST.append(low_data)
    time.sleep(2)

# count = 0
# while count < 10:
#     print("TEST")
#     getHigh12SectionValue()
#     getLow8SectionValue()
#     count += 1
#     time.sleep(0.5)

while True:
    # high_data = i2c_sensor.readfrom(HIGH_ADDRESS,12)
    try:
        high_data = i2c_sensor.readfrom(HIGH_ADDRESS,12)
        low_data = i2c_sensor.readfrom(LOW_ADDRESS,8)
        high_write_to_mem = i2c_sensor.writeto_mem(addr=HIGH_ADDRESS, memaddr=HIGH_ADDRESS, buf=high_data)
        low_write_to_mem = i2c_sensor.writeto_mem(addr=LOW_ADDRESS, memaddr=LOW_ADDRESS, buf=low_data)

        # i2c_sensor.deinit()
        print("\n-- READ LEAW --")
        
    except OSError:
        print("-- ERROR AGAIN ---")
        time.sleep(5)
    else:
        print("HIGH_DATA : {0:d}".format(high_data[0]))
        print("LOW_DATA : {0:d}".format(low_data[0]))

        # high_value = struct.unpack("B",high_data[0])
        # high_value = ubinascii.b2a_base64(high_data)
        # print("HIGH DATA : " + str(high_value))
        print("high_write -- " + str(high_write_to_mem))
        print("low_write -- " + str(low_write_to_mem))
        time.sleep(0.75)


# for i in range(8):
#     high_data.append(high_value)

# print('High data : ', end='\n\n')
# for i in range(len(high_data)):
#     print(str(high_data[i]), end='\n')



########### -------------- WIFI SECTION ------------------ ****************

wlan = WLAN(mode=WLAN.STA)
# wlan.connect("True_wifi_2.4G", auth=(WLAN.WPA2, "024688154"), timeout=5000)
wlan.connect("Android_Note5_AP", auth=(WLAN.WPA2, "kznm7052"), timeout=5000)


while not wlan.isconnected():  
    machine.idle()
print("Connected to WiFi\n")


########### -------------- MQTT SECTION ------------------ ****************
# MQTT Initialize
MQTT_BROKER_URL = "hairdresser.cloudmqtt.com"
MQTT_BROKER_PORT = 17758
MQTT_BROKER_SSL = 27758
MQTT_BROKER_USER = "odbyktmn"
MQTT_BROKER_PWD = "9esnfcLYs5wF"
MQTT_LORAGATEWAY_ID = str(machine.rng())

########### -------------- DATA SECTION ------------------ ****************
# MQTT DATA Initialize
MQTT_TOPIC_ID_OF_SENSOR = "#SENSOR"
MQTT_MSG_ID_OF_SENSOR = "1"
MQTT_TOPIC_VALUE = "VALUE"
MQTT_MSG_VALUE = "100"
MQTT_TOPIC_DATE_AND_TIME = "DATE_AND_TIME"
# MQTT_MSG_DATE_AND_TIME = "01/04/2020 15:00"
MQTT_TOPIC_LATITUDE = "LATITUDE"
MQTT_MSG_LATITUDE = "1.23456"
MQTT_TOPIC_LONGTITUDE = "LONGITUDE"
MQTT_MSG_LONGTITUDE = "2.34567"
information_dict = {}
encoded_dict = {}


subscribe_complete = 0           # flag for subcribe callback complete
def sub_cb(topic, msg):
   print((topic,msg))

# client = MQTTClient("TEST_1","io.adafruit.com",user="sarin_beam30", password="aio_KfjF62zN6EnyAXjMiZhXJyBtz8E0", port=1883)
client = MQTTClient(client_id=MQTT_LORAGATEWAY_ID, server=MQTT_BROKER_URL, port=MQTT_BROKER_PORT, ssl=False, user=MQTT_BROKER_USER, password=MQTT_BROKER_PWD, keepalive=120)
client.set_callback(sub_cb)
client.connect()
print('MQTT is connected')

def mqtt_publish_encoding(topic_name, value):
    mqtt_topic = "{}".format(topic_name)
    mqtt_msg = ujson.dumps(value)

    print(str(mqtt_topic) + ":" + str(mqtt_msg))
    time.sleep(2)
    client.publish(topic=topic_name, msg=value, qos=1, retain=False)
    client.check_msg()

def setRTCLocalTime():
    rtc = machine.RTC()
    rtc.ntp_sync("pool.ntp.org")
    utime.sleep_ms(750)
    # utime.timezone(+18000)
    utime.timezone(25200)
    # print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')
    time = utime.localtime()
    # print("SET MANUAL TIME : " + str(time[2]) + "-" + str(time[1]) + "-" + str(time[0]) + " " + str(time[3]+12)+":"+str(time[4])+":"+str(time[5]))
    if(time[4] < 10):
        set_time =  str(time[2]) + "-" + str(time[1]) + "-" + str(time[0]) + " " + str(time[3])+":0"+str(time[4])+":"+str(time[5])

    elif(time[5] < 10):
        set_time =  str(time[2]) + "-" + str(time[1]) + "-" + str(time[0]) + " " + str(time[3])+":"+str(time[4])+":0"+str(time[5])
    
    elif(time[4] < 10 and time[5] < 10):
        set_time =  str(time[2]) + "-" + str(time[1]) + "-" + str(time[0]) + " " + str(time[3])+":0"+str(time[4])+":0"+str(time[5])

    else:
        set_time =  str(time[2]) + "-" + str(time[1]) + "-" + str(time[0]) + " " + str(time[3])+":"+str(time[4])+":"+str(time[5])

    set_time = str(set_time)
    return set_time

def create_Json_file():
    information_dict = {}
    information_dict[MQTT_TOPIC_ID_OF_SENSOR] = MQTT_MSG_ID_OF_SENSOR
    information_dict[MQTT_TOPIC_VALUE] = MQTT_MSG_VALUE
    information_dict[MQTT_TOPIC_DATE_AND_TIME] = setRTCLocalTime()
    information_dict[MQTT_TOPIC_LATITUDE] = MQTT_MSG_LATITUDE
    information_dict[MQTT_TOPIC_LONGTITUDE] = MQTT_MSG_LONGTITUDE
    
    encoded_dict = ujson.dumps(information_dict)
    return encoded_dict
    
def mqtt_publish():
    try:
        while True:
            print("Publishing...")
            time.sleep(3)
            mqtt_publish_encoding("/BOARD_1", create_Json_file())
            time.sleep(3)
            print("Publish : DONE")
            time.sleep(10)
    finally:
        client.disconnect()
        print("Disconnected from MQTT server.")

########### -------------- MAIN ------------------ ****************
mqtt_publish()
    

    
    





