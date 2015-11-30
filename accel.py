#!/usr/bin/env python

debug = True

#======================================================================#
#
#========== Accelerometer Demonstration Script 05/04/2014 =============#
#
#  Accelerometer Demo script for Sensors board
#
# www.circuitsurgery.co.uk
#
#======================================================================#

print ""
print "====================== Accelerometer Demonstration ============================="
print "                      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print ""
print "www.circuitsurgery.co.uk"
print ""

import sys
import smbus
import time
import RPi.GPIO as gpio
import spidev
import random

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

bus = smbus.SMBus(1)
spi = spidev.SpiDev()

#======================================================================#
#	Variables
#----------------------------------------------------------------------#

accel_interrupt = 4
halln = 15
halls = 14
barrier_send = 23
barrier_receive = 24
ip = [halls,halln,barrier_receive,accel_interrupt]		# Input ports
op = [barrier_send]			# Output ports
ball = 0b00011000	# Initial position of "ball" for accelerometer demo
slp = 1.1	# Create floating point variable

results = bytearray()

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

#======================================================================#
#	BITS in REGISTERS
#----------------------------------------------------------------------#
accel_intsu_bits = ['fbint','plint','pdint','asint','gint','shintz','shinty','shintz']
accel_tilt_bits = ['BaFro[0]','BaFro[1]','PoLa[0]','PoLa[1]','PoLa[2]','Tap','Alert','Shake']

#======================================================================#
# set GPIO ports
#----------------------------------------------------------------------#
for n in range(4):
	gpio.setup(ip[n],gpio.IN)

gpio.setup(op[0],gpio.OUT)

#======================================================================#
#	Functions
#----------------------------------------------------------------------#
def shake():
	spi.open(0,0)
	for n in range(10):
		spi.xfer2([0x40,0x09,random.randrange(0,255,3)])
		time.sleep(0.05)
		spi.xfer2([0x40,0x09,0x00])
		time.sleep(0.01)
	bus.write_quick(addr_accelerometer)	# quick write to reset the chip
	spi.close()

def tap(b):
	spi.open(0,0)
	for n in range(10):
		spi.xfer2([0x40,0x09,b<<1])
		time.sleep(0.1)
		spi.xfer2([0x40,0x09,b>>1])
		time.sleep(0.1)
	spi.xfer2([0x40,0x09,b])
	bus.write_quick(addr_accelerometer)	# quick write to reset the chip
	spi.close()


#======================================================================#
#======================================================================#
# ---------- SET EXPANSION PORTS FOR OUTPUT ----------
#----------------------------------------------------------------------#

spi.open(0,0)

# Set port expander ports to o/p
resp = spi.xfer2([0x40,0x00,0x00])	# device addr, reg 00, set to 00
# Set all bits to "0" (turn LEDs off)
resp = spi.xfer2([0x40,0x09,0x00])	# device addr, reg 09, set to 00

#======================================================================#

# ** Set up Accelerometer **
# ******* MMA7660 *******

# REGISTERS
# ~~~~~~~~~
# Bit ---> |    7   |    6   |    5   |   4  |    3  |   2   |   1   |   0   |
# intsu 06 | SHINTX | SHINTY | SHINTZ | GINT | ASINT | PDINT | PLINT | FBINT |
# Mode  07 |  IAH   |  IPP   |  SCPS  | ASE  |  AWE  |  TON  |   -   | MODE  |

# Set interrupt behaviour via the INTSU register (0x06)

# To write to the registers the MODE bit in the MODE (0x07) register
#	must be set to 0, placing the device in Standby Mode
bus.write_byte_data(addr_accelerometer,accel_register_mode,0x00)

# Allow Tap/Pulse detection
# Enable Tap/Pulse interrupt in the INTSU register
# PDINT bit set, so successful tap detection causes interrupt
bus.write_byte_data(addr_accelerometer,accel_register_intsu,0x04)
bus.write_byte_data(addr_accelerometer,accel_register_sr,0x00)

# Set tap/pulse detection threshold (0x0F = +/- 16 counts)
bus.write_byte_data(addr_accelerometer,accel_register_pdet,0x0F)

# Set tap/pulse debounce (0x00 =  requires 2 adjacent tap detection
# tests to be the same to trigger a tap event and set the Tap bit in
# the TILT (0x03) register, and optionally set an interrupt if PDINT is
# set in the INTSU (0x06) register. Tap detection response time is
# nominally 0.52 ms.)
# ** This equates to the "Sensitivity" parameter              **
# ** The higher the value, the lower the sensitivity          **
# ** Setting of 0x0F (16 tests) seems to be about right       **
bus.write_byte_data(addr_accelerometer,accel_register_pd,0x0F)

# Mode register (0x07) bit 0 must be "1" for chip to be active
# Set MODE to 1, IPP to 1 (interrupt o/p = push/pull)
#     IAH to 0 (interrupt = active low)
bus.write_byte_data(addr_accelerometer,accel_register_mode,0x41)

#Get the user to position the Pi
print "Place the Raspberry Pi on a flat, level surface"
print "and tap the board when done."
bus.write_quick(addr_accelerometer)	# write required to reset interrupt
tilt=0
while tilt&0x20==0:
	results = bus.read_i2c_block_data(addr_accelerometer, 0x00)
	x = results[0]
	y = results[1]
	z = results[2]
	tilt = results[3]
	time.sleep(0.01)	# Wait for next sample to be acquired

print "Tap detected, so assuming Pi is level"

while True:
	if debug:
		print ""
		if gpio.input(accel_interrupt) == 0:
			print "Interrupt detected"
			bus.write_quick(addr_accelerometer)	# write required to reset interrupt

	time.sleep(0.01)	# Ensure enough time for next sample to be acquired
	results = bus.read_i2c_block_data(addr_accelerometer, 0x00)
	x = results[0]
	y = results[1]
	z = results[2]
	tilt = results[3]
	
	if tilt & 0x20 > 0:
		tap(ball)
	
	if tilt & 0x80 > 0:
		shake()
	
	if debug:
		print "x ", hex(x), "   y ", hex(y), "   z ", hex(z)
		for n in range(8):
			bit = tilt & (1 << n)
			if bit <> 0:
				print accel_tilt_bits[n],"  "


	spi.open(0,0)
	if y&0x1F < 0x04:
		spi.xfer2([0x40,0x09,ball])	# Level!
	else:
		if y&0x20 == 0:
			slp=(32.0-(y&0x1F))/20.0	# calculate waiting time
			ball = ball>>1
			if ball < 0x03:
				ball = 0x03	# endstop
			spi.xfer2([0x40,0x09,ball])	# Anti-Clockwise
		else:
			slp=(32.0-(y^0x3F))/20.0	# calculate waiting time (2's comp)
			ball = ball<<1
			if ball > 0xC0:
				ball = 0xC0	# endstop
			spi.xfer2([0x40,0x09,ball])	# Clockwise!
	print bin(ball)
	spi.close()

	time.sleep(slp)


