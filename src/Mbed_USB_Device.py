from PySide6.QtCore import QObject, Signal, Slot
import logging
import ruamel.yaml
from labjack import ljm
import numpy as np
import time
import sys
import src.K64F_Functions as K64F_Functions
import serial
from serial.serialutil import SerialException

log = logging.getLogger(__name__)

class Mbed_USB_Device(QObject):
    emitData = Signal(str, np.ndarray)
    updateOffsets = Signal(str, list, list)

    def __init__(self, name, id, connection, channels, Com_Port, dataTypes, slopes, offsets, autozero, controlRate, baudrate=115200):
        super().__init__()
        self.name = name
        self.id = id 
        self.connection = connection
        self.channels = channels
        # self.addresses = addresses
        self.baudrate = baudrate
        self.Com_Port = Com_Port
        self.dataTypes = dataTypes
        self.slopes = np.asarray(slopes)
        self.offsets = np.asarray(offsets)
        self.autozero = np.asarray(autozero)
        self.numFrames = len(self.addresses)
        self.controlRate = controlRate
        self.handle = None
        self.openConnection()
        self.initialiseSettings()
        # self.script = "src/acquire.lua"
        # self.loadLua()
        # self.executeLua()

    def openConnection(self):
        # Method to open a device connectio
        if self.connection == 11: # Mbed USB Device defined as 11 
            try:
                self.handle = serial.Serial(port=self.Com_Port, baudrate=self.baudrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
                self.name = "Mbed_TBA"   # Need to implement properly 
                log.info("Connected to " + self.name + ".")
            except SerialException:
                ljme = sys.exc_info()[1]
                log.warning(ljme) 
            except Exception:
                e = sys.exc_info()[1]
                log.warning(e)

    def initialiseSettings(self):
        # Method to initialise the device.
        if self.handle != None:
            self.ADCmaxVoltage = 5
            self.ADCminVoltage = -1 * self.ADCmaxVoltage
            self.ADCResolution = 16

            self.ADC_Data_Offset = 4
            self.ADC_Data_Bytes = 16

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

            # Set the control loop interval at address 46180 in microseconds.
            ljm.eWriteAddress(self.handle, 46180, 0, int((1/self.controlRate)*1000000))
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
            # Read from the device and apply slope and offsets.
            self.handle = ljm.open(7, self.connection, self.id)
            self.raw = np.asarray(ljm.eReadAddresses(self.handle, self.numFrames, self.addresses, self.dataTypes))
            self.data = self.slopes*(self.raw - self.offsets)
            self.emitData.emit(self.name, self.data)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot()
    def recalculateOffsets(self):
        # Method to autozero channels as required by the configuration.
        adjustOffsets = (self.raw-self.offsets)*self.autozero
        self.offsets = self.offsets + adjustOffsets

        # Update the device configuration.
        self.updateOffsets.emit(self.name, self.channels, self.offsets.tolist())
        log.info("Autozero applied to device.")

        
