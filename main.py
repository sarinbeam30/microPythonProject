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

HIGH_DATA_LIST = LOW_DATA_LIST = []
THRESHOLD = 100

i2c_sensor = I2C(0)
i2c_sensor.init(mode=I2C.MASTER, baudrate=115200, pins=('P9','P10'))

#SCAN DEVICE
devices = i2c_sensor.scan()
print('i2c devices found:',len(devices))
for device in devices:
    print("Decimal address: ",device," | Hexa address: ",hex(device))

########### -------------- WIFI SECTION ------------------ ****************

wlan = WLAN(mode=WLAN.STA)
# wlan.connect("True_wifi_2.4G", auth=(WLAN.WPA2, "024688154"), timeout=5000)
# wlan.connect("Android_Note5_AP", auth=(WLAN.WPA2, "kznm7052"), timeout=5000)
wlan.connect("TP-Link_357E", auth=(WLAN.WPA2, "35983255"), timeout=5000)

while not wlan.isconnected():
    time.sleep_ms(50)
print("WIFI is connected")


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

client = MQTTClient(client_id=MQTT_LORAGATEWAY_ID, server=MQTT_BROKER_URL, port=MQTT_BROKER_PORT, ssl=False, user=MQTT_BROKER_USER, password=MQTT_BROKER_PWD, keepalive=120)
client.set_callback(sub_cb)
client.connect()
print('MQTT is connected')

def mqtt_publish_encoding(topic_name, value):
    mqtt_topic = "{}".format(topic_name)
    mqtt_msg = ujson.dumps(value)

    print(str(mqtt_topic) + " : " + str(mqtt_msg))
    time.sleep(2)
    client.publish(topic=topic_name, msg=value, qos=1, retain=False)
    client.check_msg()

def setRTCLocalTime():
    rtc = machine.RTC()
    rtc.ntp_sync("pool.ntp.org")
    utime.sleep_ms(750)
    # utime.timezone(+18000)
    utime.timezone(25200)
    time = utime.localtime()
    # print("SET MANUAL TIME : " + str(time[2]) + "-" + str(time[1]) + "-" + str(time[0]) + " " + str(time[3]+12)+":"+str(time[4])+":"+str(time[5]))
    if(time[4] < 10):
        set_time =  str(time[2]) + "/" + str(time[1]) + "/" + str(time[0]) + " " + str(time[3])+":0"+str(time[4])+":"+str(time[5])

    elif(time[5] < 10):
        set_time =  str(time[2]) + "/" + str(time[1]) + "/" + str(time[0]) + " " + str(time[3])+":"+str(time[4])+":0"+str(time[5])
    
    elif(time[4] < 10 and time[5] < 10):
        set_time =  str(time[2]) + "/" + str(time[1]) + "/" + str(time[0]) + " " + str(time[3])+":0"+str(time[4])+":0"+str(time[5])

    else:
        set_time =  str(time[2]) + "/" + str(time[1]) + "/" + str(time[0]) + " " + str(time[3])+":"+str(time[4])+":"+str(time[5])

    set_time = str(set_time)
    return set_time

def create_Json_file():
    information_dict = {}
    information_dict[MQTT_TOPIC_ID_OF_SENSOR] = MQTT_MSG_ID_OF_SENSOR
    information_dict[MQTT_TOPIC_VALUE] = get_water_level()
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

def getHigh12_and_Low8_SectionValue():
    try:
        #RESET_LIST
        LOW_DATA_LIST = []
        HIGH_DATA_LIST = []

        low_data = i2c_sensor.readfrom(LOW_ADDRESS, 8)
        high_data = i2c_sensor.readfrom(HIGH_ADDRESS,12) 
        print("\n-- READ LEAW [LOW] && [HIGH] --")
    
    except OSError:
        print("-- ERROR AGAIN ---")
        time.sleep(5)
    
    else:
        print("LOW_DATA_FROM_FUNCTION : " ,end=" ")
        for i in range(0,8):
            LOW_DATA_LIST.append(low_data[i])
            print(str(LOW_DATA_LIST[i]), end=" ")
        print('\n')

        print("HIGH_DATA_FROM_FUNCTION : " ,end=" ")
        for i in range(0,12):
            HIGH_DATA_LIST.append(high_data[i])
            print(str(HIGH_DATA_LIST[i]), end=" ")
        print('\n')
        time.sleep(0.75)

    time.sleep(3)
    return LOW_DATA_LIST, HIGH_DATA_LIST

def get_water_level():
    sensorvalue_min = 250
    sensorvalue_max = 255
    low_count = 0
    high_count = 0

    while True:
        # SET_UP
        touch_val = trig_section = 0
        LOW_DATA_LIST = HIGH_DATA_LIST = []

        getHigh12_and_Low8_SectionValue()
        LOW_DATA_LIST = getHigh12_and_Low8_SectionValue()[0]
        HIGH_DATA_LIST = getHigh12_and_Low8_SectionValue()[1]

        # CHECK_LOW_VALUE
        try:
            print("LOW_DATA : " ,end=" ")
            for i in range(0, len(LOW_DATA_LIST)):
                print(str(LOW_DATA_LIST[i]), end=" ")
                if(LOW_DATA_LIST[i] >= sensorvalue_min and LOW_DATA_LIST[i] <= sensorvalue_max):
                    low_count += 1
                if(low_count == 8):
                    print('\n LOW_PASS')
        except IndexError:
            print("\n--  LOW-INDEX-ERROR AGAIN  ---")
            time.sleep(2)
        

        # CHECK_HIGH_VALUE
        try:
            print("\nHIGH_DATA : " ,end=" ")
            for i in range(0,len(HIGH_DATA_LIST)):
                print(str(HIGH_DATA_LIST[i]), end=" ")
                if(HIGH_DATA_LIST[i] >= sensorvalue_min and HIGH_DATA_LIST[i] <= sensorvalue_max):
                    high_count += 1
                if(high_count == 12):
                    print('\n HIGH_PASS')
            print('\n')
        except IndexError:
            print("\n-- HIGH-INDEX-ERROR AGAIN ---")
            time.sleep(2)
            
        # CALCULATE_WATER_LEVEL
        try:
            for i in range(0,8):
                if(LOW_DATA_LIST[i] > THRESHOLD):
                    touch_val |= 1 << i
            
            for i in range(0,12):
                if(HIGH_DATA_LIST[i] > THRESHOLD):
                    touch_val |= 1 << (8+i)

            time.sleep(3)

            while(touch_val and 0x01):
                trig_section += 1
                touch_val >>= 1
            
            value = trig_section * 5
            print('water_level : ' + str(value) + " %\n")
            return value
            time.sleep(3)

        except IndexError:
            print("-- CALCULATE-INDEX-ERROR AGAIN ---\n")
            time.sleep(3)  

########### -------------- MAIN ------------------ ****************
mqtt_publish()
    

    
    





