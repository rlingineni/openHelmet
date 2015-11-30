import smbus
import time
import os
import math

#======================================================================#
#	Addresses
#----------------------------------------------------------------------#
addr_temperature = 0x48
addr_accelerometer = 0x4C
addr_light = 0x29
addr_pressure = 0x60
addr_expander = 0x20
#======================================================================#

#======================================================================#
#	REGISTERS
#----------------------------------------------------------------------#
accel_register_tilt = 0x03
accel_register_intsu = 0x06
accel_register_mode = 0x07
accel_register_sr = 0x08
accel_register_pdet = 0x09
accel_register_pd = 0x0A
#----------------------------------------------------------------------#

# Define a class for the accelerometer readings
class MMA7660():
    bus = smbus.SMBus(1)
    
    def getValues(self):
        results = self.bus.read_i2c_block_data(addr_accelerometer, 0x00)
        return results
    def init(self):
        self.bus.write_byte_data(addr_accelerometer,accel_register_mode,0x00)
        self.bus.write_byte_data(addr_accelerometer,accel_register_intsu,0x04)
        self.bus.write_byte_data(addr_accelerometer,accel_register_sr,0x01)
        self.bus.write_byte_data(addr_accelerometer,accel_register_pdet,0x0F)
        self.bus.write_byte_data(addr_accelerometer,accel_register_pd,0x0F)
        self.bus.write_byte_data(addr_accelerometer,accel_register_mode,0x41)
    def getY(self):
                results = self.getValues()
                x = results[0]
                y = results[1]
                z = results[2]
                tilt = results[3]
                time.sleep(0.01)
                return y
    

''' mma = MMA7455()

mma.init()
tilt=0
for a in range(1000):
    while tilt&0x20==0:
        results = mma.getValues()
        x = results[0]
        y = results[1]
        z = results[2]
        tilt = results[3]
        time.sleep(0.01)
        print("X=", x, "Y=", y,"Z=",z)

os.system("clear") '''
