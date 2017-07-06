import ibmiotf.device
from Sensortag_classes import *


class PiSensor:

    def __int__(self):
        print 'initial sensor'

    def sendMQTT(self, jsonData):
        try:
            options = {
                "org": "034pt5",
                "type": "MQTTDevice",
                "id": "donniemqttdevice1",
                "auth-method": "token",
                "auth-token": "zaq12wsx",
                "clean-session": "true"
            }
            client = ibmiotf.device.Client(options)
            client.connect()
            client.publishEvent("status", "json", jsonData)
        except ibmiotf.ConnectionException as e:
            print e

    def sendMQTTStart(self, jsonData):
        try:
            options = {
                "org": "034pt5",
                "type": "MQTT",
                "id": "chumqttdevice",
                "auth-method": "token",
                "auth-token": "1qazxsw2",
                "clean-session": "true"
            }
            client = ibmiotf.device.Client(options)
            client.connect()
            client.publishEvent("status", "json", jsonData)
        except ibmiotf.ConnectionException as e:
            print e

    def getEnv(self):
        tag = SensorTag(bluetooth_adr='24:71:89:06:93:84')  # pass the Bluetooth Address
        tag.char_write_cmd(0x24, 01)  # Enable temperature sensor
        ir_temp_celsius, ambient_temp_celsius = self.hexTemp2C(tag.char_read_hnd(0x21, "temperature"))
        tag.char_write_cmd(0x44, 01)
        lux_luminance = self.hexLum2Lux(tag.char_read_hnd(0x41, "luminance"))
        tag.char_write_cmd(0x2C, 01)
        rel_humidity = self.hexHum2RelHum(tag.char_read_hnd(0x29, "humidity"))
        tag.char_write_cmd(0x34, 01)
        bar_pressure = self.hexPress2Press(tag.char_read_hnd(0x31, "barPressure"))
        return {"temperature": ambient_temp_celsius, "humidity": rel_humidity, "pressure": bar_pressure, "brightness": lux_luminance}

    def hexTemp2C(self, raw_temperature):
        string_temp = raw_temperature[0:2] + ' ' + raw_temperature[2:4] + ' ' + raw_temperature[4:6] + ' ' + raw_temperature[6:8]  # add spaces to string
        # TODO:Fix the following line so that I don't have to add and to remove spaces
        raw_temp_bytes = string_temp.split()  # Split into individual bytes
        raw_ambient_temp = int('0x' + raw_temp_bytes[3] + raw_temp_bytes[2],
                               16)  # Choose ambient temperature (reverse bytes for little endian)
        raw_IR_temp = int('0x' + raw_temp_bytes[1] + raw_temp_bytes[0], 16)
        IR_temp_int = raw_IR_temp >> 2 & 0x3FFF
        ambient_temp_int = raw_ambient_temp >> 2 & 0x3FFF  # Shift right, based on from TI
        ambient_temp_celsius = float(ambient_temp_int) * 0.03125  # Convert to Celsius based on info from TI
        IR_temp_celsius = float(IR_temp_int) * 0.03125
        ambient_temp_fahrenheit = (ambient_temp_celsius * 1.8) + 32  # Convert to Fahrenheit

        print "INFO: IR Celsius:    %f" % IR_temp_celsius
        print "INFO: Ambient Celsius:    %f" % ambient_temp_celsius
        # print "Fahrenheit: %f" % ambient_temp_fahrenheit
        return (IR_temp_celsius, ambient_temp_celsius)

    def hexLum2Lux(self, raw_luminance):
        m = "0FFF"
        e = "F000"
        raw_luminance = int(raw_luminance, 16)
        m = int(m, 16)  # Assign initial values as per the CC2650 Optical Sensor Dataset
        exp = int(e, 16)  # Assign initial values as per the CC2650 Optical Sensor Dataset
        m = (raw_luminance & m)  # as per the CC2650 Optical Sensor Dataset
        exp = (raw_luminance & exp) >> 12  # as per the CC2650 Optical Sensor Dataset
        luminance = (m * 0.01 * pow(2.0, exp))  # as per the CC2650 Optical Sensor Dataset
        return luminance  # returning luminance in lux

    def hexHum2RelHum(self, raw_humidity):
        humidity = float(
            (int(raw_humidity, 16))) / 65536 * 100  # get the int value from hex and divide as per Dataset.
        return humidity

    def hexPress2Press(self, raw_pressure):
        pressure = int(raw_pressure, 16)
        pressure = float(pressure) / 100.0
        return pressure

if __name__ == "__main__":
    sensor = PiSensor()
    jsonData = sensor.getEnv()
    sensor.sendMQTT(jsonData)
