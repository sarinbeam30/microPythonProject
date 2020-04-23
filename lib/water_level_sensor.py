import pycom
import utime
from machine import I2C

class WATER_LEVEL_SENSOR:
    def __init__(self, i2c, high_addr=0x78, low_addr=0x77, period=150):
        self.i2c = I2C(scl=Pin(10), sda=Pin(9))
        self.high_addr = high_addr
        self.low_addr = low_addr
        self.period = period

        # self.i2c.writeto(high_addr, bytes([0x10]))
        # self.i2c.writeto(low_addr, bytes([0x10]))

        self.high_value = []
        self.low_value = []

    
    def getHigh12SectionValue(self):
        self.i2c.writeto(self.high_addr, bytes([0x12]))
        utime.sleep(0.01)
        read_data = self.i2c.readfrom(self.high_addr,12)
        self.high_value.append(read_data)
    
    def getLow8SectionValue(self):
        self.i2c.writeto(self.low_addr, bytes([0x8]))
        utime.sleep(0.01)
        read_data = self.i2c.readfrom(self.low_addr,8)
        self.low_value.append(read_data)
    
    def check(self):
        sensorvalue_min = 250
        sensorvalue_max = 255
        low_count = 0
        high_count = 0

        while(True):
            low_count = high_count = 0
            self.getLow8SectionValue()
            self.getHigh12SectionValue()
            

            print("low 8 sections value = ", end='')
            for i in range(len(self.low_value)):
                print(self.low_value[i], end='')
                print(',', end='')

                if(self.low_value[i] >= sensorvalue_min and self.low_value[i] <= sensorvalue_max):
                    low_count += 1
                if(low_count == 8):
                    print("PASS")
            print('\n')


        
    
    

    
        


