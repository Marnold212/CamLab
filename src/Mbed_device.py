from PySide6.QtCore import QObject, Signal, Slot
import logging
import serial
from serial.serialutil import SerialException
from serial.serialwin32 import Serial
import ruamel.yaml
from labjack import ljm
import numpy as np
from time import sleep
import sys
from src.K64F_Functions import *

log = logging.getLogger(__name__)

class Mbed_Device(QObject):
    emitData = Signal(np.ndarray)

    def __init__(self, id, connection, ADC_Address, dataTypes, Com_Port, baudrate=115200):
        super().__init__()
        self.handle = None  # Stores Pyserial object for communication 
        self.Com_Port = Com_Port
        self.baudrate = baudrate
        self.ADC_Address = ADC_Address
        self.aDataTypes = dataTypes
        self.id = id 
        self.connection = connection
        self.script = "src/acquire.lua"
        self.openConnection()
        self.initialiseSettings()
        # self.loadLua()
        # self.executeLua()

    def openConnection(self):
        # Method to open a device connection
        if self.connection == 11: # Mbed USB Device defined as 11 
            try:
                self.handle = serial.Serial(port=self.Com_Port, baudrate=self.baudrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
                self.name = "Mbed_TBA"
                log.info("Connected to " + self.name + ".")
            except SerialException:
                ljme = sys.exc_info()[1]
                log.warning(ljme) 
            except Exception:
                e = sys.exc_info()[1]
                log.warning(e)
        
        else: 
            log.info("Invalid Connection Type")

    def initialiseSettings(self):
        # Method to initialise Mbed Device
        # Currently Only reading Raw ADC values from device 
        # In future, may need to convert Raw ADC values to correct voltages in order to perform onboard control calculations

        self.ADCmaxVoltage = 5
        self.ADCminVoltage = -1 * self.ADCmaxVoltage
        self.ADCResolution = 16


    def loadLua(self):
        try:
            # Read the Lua script.
            with open(self.script, "r") as f:
                lua = f.read()
            lua_length = len(lua)

            # Disable a running script by writing 0 to LUA_RUN twice. Wait for the Lua VM to shut down (and some T7 firmware versions need
            # a longer time to shut down than others) in between the repeated commands.
            ljm.eWriteName(self.handle, "LUA_RUN", 0)
            sleep(2)
            ljm.eWriteName(self.handle, "LUA_RUN", 0)

            # Write the size and the Lua Script to the device.
            ljm.eWriteName(self.handle, "LUA_SOURCE_SIZE", lua_length)
            ljm.eWriteNameByteArray(
                self.handle, "LUA_SOURCE_WRITE", lua_length, bytearray(lua, encoding="utf8")
            )

            # Start the script with debug output disabled.
            ljm.eWriteName(self.handle, "LUA_DEBUG_ENABLE", 1)
            ljm.eWriteName(self.handle, "LUA_DEBUG_ENABLE_DEFAULT", 1)
            log.info("Lua script loaded.")
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def executeLua(self):
        # Method to execute a Lua script.
        try:
            ljm.eWriteName(self.handle, "LUA_RUN", 1)
            log.info("Lua script executed.")
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def readValues(self):
        # Method to read registers on device.
        try:
            # Read from the device.
            # self.handle = ljm.open(7, self.connection, self.id)
            # data = np.asarray(ljm.eReadAddresses(self.handle, self.numFrames, self.aAddresses, self.aDataTypes))
            data = Read_8_ADC_U16_Values(self.handle, self.ADC_Address)

            for x in range(8):
                # data[x] = data[x] / (2.**16.) * 5
                data[x] = self.Convert_ADC_Raw(data[x], self.ADCResolution, self.ADCmaxVoltage)
            
            data = np.asarray(data)
            # log.info(data)
            self.emitData.emit(data)
        except SerialException:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
        
        # Assumes Data recieved is from an AD7606
    def Convert_ADC_Raw(self, Raw_Reading, ADC_Resolution, Max_Min_Voltage): 
        Signed_Value = np.int16(Raw_Reading)  
        quant_step = (2 * Max_Min_Voltage) / (2**ADC_Resolution)
        return Signed_Value * quant_step
