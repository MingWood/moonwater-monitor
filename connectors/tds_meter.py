import sys
sys.path.append('../')
import time
from collections import deque
import smbus

# Get I2C bus
bus = smbus.SMBus(1)

# I2C address of the device
ADS1115_IIC_ADDRESS0				= 0x48
ADS1115_IIC_ADDRESS1				= 0x49

# ADS1115 Register Map
ADS1115_REG_POINTER_CONVERT			= 0x00 # Conversion register
ADS1115_REG_POINTER_CONFIG			= 0x01 # Configuration register
ADS1115_REG_POINTER_LOWTHRESH		= 0x02 # Lo_thresh register
ADS1115_REG_POINTER_HITHRESH		= 0x03 # Hi_thresh register

# ADS1115 Configuration Register
ADS1115_REG_CONFIG_OS_NOEFFECT		= 0x00 # No effect
ADS1115_REG_CONFIG_OS_SINGLE		= 0x80 # Begin a single conversion
ADS1115_REG_CONFIG_MUX_DIFF_0_1		= 0x00 # Differential P = AIN0, N = AIN1 (default)
ADS1115_REG_CONFIG_MUX_DIFF_0_3		= 0x10 # Differential P = AIN0, N = AIN3
ADS1115_REG_CONFIG_MUX_DIFF_1_3		= 0x20 # Differential P = AIN1, N = AIN3
ADS1115_REG_CONFIG_MUX_DIFF_2_3		= 0x30 # Differential P = AIN2, N = AIN3
ADS1115_REG_CONFIG_MUX_SINGLE_0		= 0x40 # Single-ended P = AIN0, N = GND
ADS1115_REG_CONFIG_MUX_SINGLE_1		= 0x50 # Single-ended P = AIN1, N = GND
ADS1115_REG_CONFIG_MUX_SINGLE_2		= 0x60 # Single-ended P = AIN2, N = GND
ADS1115_REG_CONFIG_MUX_SINGLE_3		= 0x70 # Single-ended P = AIN3, N = GND
ADS1115_REG_CONFIG_PGA_6_144V		= 0x00 # +/-6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V		= 0x02 # +/-4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V		= 0x04 # +/-2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V		= 0x06 # +/-1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V		= 0x08 # +/-0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V		= 0x0A # +/-0.256V range = Gain 16
ADS1115_REG_CONFIG_MODE_CONTIN		= 0x00 # Continuous conversion mode
ADS1115_REG_CONFIG_MODE_SINGLE		= 0x01 # Power-down single-shot mode (default)
ADS1115_REG_CONFIG_DR_8SPS			= 0x00 # 8 samples per second
ADS1115_REG_CONFIG_DR_16SPS			= 0x20 # 16 samples per second
ADS1115_REG_CONFIG_DR_32SPS			= 0x40 # 32 samples per second
ADS1115_REG_CONFIG_DR_64SPS			= 0x60 # 64 samples per second
ADS1115_REG_CONFIG_DR_128SPS		= 0x80 # 128 samples per second (default)
ADS1115_REG_CONFIG_DR_250SPS		= 0xA0 # 250 samples per second
ADS1115_REG_CONFIG_DR_475SPS		= 0xC0 # 475 samples per second
ADS1115_REG_CONFIG_DR_860SPS		= 0xE0 # 860 samples per second
ADS1115_REG_CONFIG_CMODE_TRAD		= 0x00 # Traditional comparator with hysteresis (default)
ADS1115_REG_CONFIG_CMODE_WINDOW		= 0x10 # Window comparator
ADS1115_REG_CONFIG_CPOL_ACTVLOW		= 0x00 # ALERT/RDY pin is low when active (default)
ADS1115_REG_CONFIG_CPOL_ACTVHI		= 0x08 # ALERT/RDY pin is high when active
ADS1115_REG_CONFIG_CLAT_NONLAT		= 0x00 # Non-latching comparator (default)
ADS1115_REG_CONFIG_CLAT_LATCH		= 0x04 # Latching comparator
ADS1115_REG_CONFIG_CQUE_1CONV		= 0x00 # Assert ALERT/RDY after one conversions
ADS1115_REG_CONFIG_CQUE_2CONV		= 0x01 # Assert ALERT/RDY after two conversions
ADS1115_REG_CONFIG_CQUE_4CONV		= 0x02 # Assert ALERT/RDY after four conversions
ADS1115_REG_CONFIG_CQUE_NONE		= 0x03 # Disable the comparator and put ALERT/RDY in high state (default)

mygain=0x02
coefficient=0.125
addr_G=ADS1115_IIC_ADDRESS0
class ADS1115():
	def setGain(self,gain):
		global mygain
		global coefficient
		mygain=gain
		if mygain == ADS1115_REG_CONFIG_PGA_6_144V:
			coefficient = 0.1875
		elif mygain == ADS1115_REG_CONFIG_PGA_4_096V:
			coefficient = 0.125
		elif mygain == ADS1115_REG_CONFIG_PGA_2_048V:
			coefficient = 0.0625
		elif mygain == ADS1115_REG_CONFIG_PGA_1_024V:
			coefficient = 0.03125
		elif mygain == ADS1115_REG_CONFIG_PGA_0_512V:
			coefficient = 0.015625
		elif  mygain == ADS1115_REG_CONFIG_PGA_0_256V:
			coefficient = 0.0078125
		else:
			coefficient = 0.125
	def setAddr_ADS1115(self,addr):
		global addr_G
		addr_G=addr
	def setChannel(self,channel):
		global mygain
		"""Select the Channel user want to use from 0-3
		For Single-ended Output
		0 : AINP = AIN0 and AINN = GND
		1 : AINP = AIN1 and AINN = GND
		2 : AINP = AIN2 and AINN = GND
		3 : AINP = AIN3 and AINN = GND
		For Differential Output
		0 : AINP = AIN0 and AINN = AIN1
		1 : AINP = AIN0 and AINN = AIN3
		2 : AINP = AIN1 and AINN = AIN3
		3 : AINP = AIN2 and AINN = AIN3"""
		self.channel = channel
		while self.channel > 3 :
			self.channel = 0
		
		return self.channel
	
	def setSingle(self):
		global addr_G
		if self.channel == 0:
			CONFIG_REG = [ADS1115_REG_CONFIG_OS_SINGLE | ADS1115_REG_CONFIG_MUX_SINGLE_0 | mygain | ADS1115_REG_CONFIG_MODE_CONTIN, ADS1115_REG_CONFIG_DR_128SPS | ADS1115_REG_CONFIG_CQUE_NONE]
		elif self.channel == 1:
			CONFIG_REG = [ADS1115_REG_CONFIG_OS_SINGLE | ADS1115_REG_CONFIG_MUX_SINGLE_1 | mygain | ADS1115_REG_CONFIG_MODE_CONTIN, ADS1115_REG_CONFIG_DR_128SPS | ADS1115_REG_CONFIG_CQUE_NONE]
		elif self.channel == 2:
			CONFIG_REG = [ADS1115_REG_CONFIG_OS_SINGLE | ADS1115_REG_CONFIG_MUX_SINGLE_2 | mygain | ADS1115_REG_CONFIG_MODE_CONTIN, ADS1115_REG_CONFIG_DR_128SPS | ADS1115_REG_CONFIG_CQUE_NONE]
		elif self.channel == 3:
			CONFIG_REG = [ADS1115_REG_CONFIG_OS_SINGLE | ADS1115_REG_CONFIG_MUX_SINGLE_3 | mygain | ADS1115_REG_CONFIG_MODE_CONTIN, ADS1115_REG_CONFIG_DR_128SPS | ADS1115_REG_CONFIG_CQUE_NONE]
		
		bus.write_i2c_block_data(addr_G, ADS1115_REG_POINTER_CONFIG, CONFIG_REG)
	
	def setDifferential(self):
		global addr_G
		if self.channel == 0:
			CONFIG_REG = [ADS1115_REG_CONFIG_OS_SINGLE | ADS1115_REG_CONFIG_MUX_DIFF_0_1 | mygain | ADS1115_REG_CONFIG_MODE_CONTIN, ADS1115_REG_CONFIG_DR_128SPS | ADS1115_REG_CONFIG_CQUE_NONE]
		elif self.channel == 1:
			CONFIG_REG = [ADS1115_REG_CONFIG_OS_SINGLE | ADS1115_REG_CONFIG_MUX_DIFF_0_3 | mygain | ADS1115_REG_CONFIG_MODE_CONTIN, ADS1115_REG_CONFIG_DR_128SPS | ADS1115_REG_CONFIG_CQUE_NONE]
		elif self.channel == 2:
			CONFIG_REG = [ADS1115_REG_CONFIG_OS_SINGLE | ADS1115_REG_CONFIG_MUX_DIFF_1_3 | mygain | ADS1115_REG_CONFIG_MODE_CONTIN, ADS1115_REG_CONFIG_DR_128SPS | ADS1115_REG_CONFIG_CQUE_NONE]
		elif self.channel == 3:
			CONFIG_REG = [ADS1115_REG_CONFIG_OS_SINGLE | ADS1115_REG_CONFIG_MUX_DIFF_2_3 | mygain | ADS1115_REG_CONFIG_MODE_CONTIN, ADS1115_REG_CONFIG_DR_128SPS | ADS1115_REG_CONFIG_CQUE_NONE]
		
		bus.write_i2c_block_data(addr_G, ADS1115_REG_POINTER_CONFIG, CONFIG_REG)
	
	def readValue(self):
		"""Read data back from ADS1115_REG_POINTER_CONVERT(0x00), 2 bytes
		raw_adc MSB, raw_adc LSB"""
		global coefficient
		global addr_G
		data = bus.read_i2c_block_data(addr_G, ADS1115_REG_POINTER_CONVERT, 2)
		
		raw_adc = data[0] * 256 + data[1]
		
		if raw_adc > 32767:
			raw_adc -= 65535
		raw_adc = int(float(raw_adc)*coefficient)
		return {'r' : raw_adc}

	def readVoltage(self,channel):
		self.setChannel(channel)
		self.setSingle()
		time.sleep(0.1)
		return self.readValue()

	def ComparatorVoltage(self,channel):
		self.setChannel(channel)
		self.setDifferential()
		time.sleep(0.1)
		return self.readValue()

class TDSMeter(object):
	MAX_BUFFER_LENGTH = 2

	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self, sensors_attached, sensor_id_to_index, sensor_compensations):
		if not hasattr(self, 'initialized'):
			self.initialized = True
			ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
			ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
			ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
			ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
			ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
			ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16
			self.ads1115 = ADS1115()
			#Set the IIC address
			self.ads1115.setAddr_ADS1115(0x48)
			#Sets the gain and input voltage range.
			self.ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
			self.sensors_attached = sensors_attached
			self.sensor_id_to_index = sensor_id_to_index
			self.sensor_compensations = sensor_compensations
			self.buffered_tds_values = deque()
	
	def read_voltage(self, index):
		return self.ads1115.readVoltage(index)['r']

	def translate_voltage_to_tds(self, voltage, sensor_id):
		### based on manual linear regression calibration ###
		calibration_terms = self.sensor_compensations[sensor_id]
		calculated_tds = calibration_terms['slope'] * voltage + calibration_terms['offset']
		if calculated_tds < 0:
			return 0
		return calculated_tds

	def read_tds(self, sensor_id):
		voltage = self.read_voltage(self.sensor_id_to_index[sensor_id])
		return self.translate_voltage_to_tds(voltage, sensor_id)

	def read_voltages_sequential(self):
		readings = []
		for i, name in enumerate(self.sensors_attached):
			readings.append(self.ads1115.readVoltage(self.sensor_id_to_index[name])['r'])
		return readings
	
	def read_tds_values(self):
		voltages = self.read_voltages_sequential()
		tds_values = {}
		for i, name in enumerate(self.sensors_attached):
			tds_values[name] = self.translate_voltage_to_tds(voltages[i], name)
		self.buffered_tds_values.append(tds_values)
		if len(self.buffered_tds_values) > TDSMeter.MAX_BUFFER_LENGTH:
			self.buffered_tds_values.popleft()
		return tds_values
	
	def get_buffered_tds_values(self):
		return self.buffered_tds_values

		

### default conversion code from CQRobot example which was off by almost a factor of 10 ###
# VREF = 5.0
# analogBuffer = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# analogBufferTemp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# analogBufferIndex = 0
# copyIndex = 0
# averageVoltage = 0
# tdsValue = 0
# temperature = 25

# def getMedianNum(iFilterLen):
# 	global analogBufferTemp
# 	bTemp = 0.0
# 	for j in range(iFilterLen-1):
# 		for i in range(iFilterLen-j-1):
# 			if analogBufferTemp[i] > analogBufferTemp[i+1]:
# 				bTemp = analogBufferTemp[i]
# 				analogBufferTemp[i] = analogBufferTemp[i+1]
# 				analogBufferTemp[i+1] = bTemp
# 	if iFilterLen & 1 > 0:
# 		bTemp = analogBufferTemp[(iFilterLen - 1)/2]
# 	else:
# 		bTemp = (analogBufferTemp[iFilterLen // 2] + analogBufferTemp[iFilterLen // 2 - 1]) / 2
# 	return float(bTemp)

# analogSampleTimepoint = time.time()
# printTimepoint = time.time()
# while True :
# 	if time.time() - analogSampleTimepoint > 0.04:
# 		#print(" test.......... ")
# 		analogSampleTimepoint = time.time()
# 		analogBuffer[analogBufferIndex] = ads1115.readVoltage(1)['r']
# 		analogBufferIndex = analogBufferIndex + 1
# 		if analogBufferIndex == 30:
# 			analogBufferIndex = 0

# 	if time.time()-printTimepoint > 0.8:
# 		#print(" test ")
# 		printTimepoint = time.time()
# 		for copyIndex in range(30):
# 			analogBufferTemp[copyIndex] = ads1115.readVoltage(1)['r']
# 		print(" A1:%dmV "%getMedianNum(30))
# 		averageVoltage = getMedianNum(30) * (VREF / 1024.0)
# 		compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)
# 		compensationVolatge = averageVoltage / compensationCoefficient
# 		tdsValue = (133.42 * compensationVolatge * compensationVolatge * compensationVolatge - 255.86 * compensationVolatge * compensationVolatge + 857.39 * compensationVolatge) * 0.5
# 		print(" A1:%dppm "%tdsValue)

#Get the Digital Value of Analog of selected channel
#adc1 = ads1115.readVoltage(1)
#time.sleep(0.2)
#print(" A1:%dmV "%(adc1['r']))

if __name__ == '__main__':
	meter = TDSMeter(
            ['RO_outlet_slowbar', 'mineral_boosted_slowbar', 'mineral_boosted_mainspro'],
            {'RO_outlet_slowbar': 1, 'mineral_boosted_slowbar': 2, 'mineral_boosted_mainspro':0},
            {'RO_outlet_slowbar': {'slope': 0.338, 'offset': -2.04},
			'mineral_boosted_slowbar': {'slope': 0.338, 'offset': -2.04},
			'mineral_boosted_mainspro': {'slope': 0.338, 'offset': -2.04}}
        )

	while True:
		time.sleep(.2)
		print(meter.read_tds_values())