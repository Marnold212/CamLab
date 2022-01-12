from PySide6.QtCore import QObject, Signal, Slot, QSettings, QTimer, QThread
from src.models import DeviceTableModel, AcquisitionTableModel
from src.device import Device
import copy
import logging
import ruamel.yaml
import os
import sys
from labjack import ljm
import numpy as np
from src.K64F_Functions import *
from src.Mbed_device import Mbed_Device

from serial.serialutil import SerialException
import serial.tools.list_ports as port_list
import serial

log = logging.getLogger(__name__)

class Assembly(QObject):
    plotDataChanged = Signal(np.ndarray)
    samplesCount = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.plotData = []
        self.time = 0.00
        self.count = 0
        self.offsets = np.asarray((0, 0, 0, 0, 0, 0, 0, 0))
        self.newData = []

    @Slot(np.ndarray)
    def updateNewData(self, data):
        if np.shape(self.newData)[0] > 0:
            self.newData = np.vstack((self.newData, data))
        else:
            self.newData = data

    def updatePlotData(self):
        if np.shape(self.newData)[0] > 0: 
            dt = 0.001
            newData = self.newData
            self.newData = []
            numTimesteps = np.shape(newData)[0]
            timesteps = np.linspace(0, (numTimesteps-1)*dt, numTimesteps)
            timesteps += self.time
            self.count += numTimesteps
            self.samplesCount.emit(self.count)
            newLines = np.column_stack((timesteps, newData-self.offsets))
            if np.shape(self.plotData)[0] > 0:
                self.plotData = np.vstack((self.plotData, newLines)) 
            else: 
                self.plotData = newLines
            self.plotDataChanged.emit(self.plotData)
            self.time += numTimesteps*dt 

    def clearPlotData(self):
        self.plotData = self.plotData[-1,:]

    def autozero(self):
        self.offsets = np.average(self.plotData[-10:,1:], axis=0)

class Manager(QObject):
    updateUI = Signal(dict)
    configurationChanged = Signal(dict)
    addAcquisitionTable = Signal(str)
    updateAcquisitionTabs = Signal()
    clearAcquisitionTabs = Signal()
    startTimers = Signal()
    endTimers = Signal()
    connectSampleTimer = Signal(str)

    def __init__(self):
        super().__init__()
        self.configuration = {}
        self.acquisitionModels = {}
        self.acquisitionTables = {}
        self.devices = {}
        self.deviceThread = {}
        self.refreshing = False

        self.defaultAcquisitionTable = [
            {"channel": "AIN0", "name": "Ch_1", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN1", "name": "Ch_2", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN2", "name": "Ch_3", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN3", "name": "Ch_4", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN4", "name": "Ch_5", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN5", "name": "Ch_6", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN6", "name": "Ch_7", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN7", "name": "Ch_8", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
        ]

        # Instantiate the model for the device list.   
        self.deviceTableModel = DeviceTableModel()

        # Load last used configuration file.
        log.info("Finding previous YAML file location from QSettings.")
        self.settings = QSettings("CamLab", "Settings")
        self.settings.sync()
        self.findConfigurationPath()
        if self.configurationPath != None:
            self.loadConfiguration(self.configurationPath)
        else:
            self.initialiseDefaultConfiguration()

        # Create assembly thread.
        self.assembly = Assembly()
        log.info("Assembly thread instantiated.")
        self.assemblyThread = QThread(parent=self)
        log.info("Assembly thread created.")
        self.assembly.moveToThread(self.assemblyThread)
        self.assemblyThread.start()
        log.info("Assembly thread started.")

    def createDeviceThreads(self):
        self.devices = {}
        self.deviceThread = {}
        enabledDevices = self.deviceTableModel.enabledDevices()
        enabledDeviceList = []
        for device in enabledDevices:
            if(device["Device Type"] == "Labjack T7"):
                name = device["name"]
                id = device["id"]
                connection = device["connection"]

                # Function required HERE to generate addresses from acquisition table data.
                aAddresses = [46000, 46002, 46004, 46006, 46008, 46010, 46012, 46014]
                dt = ljm.constants.FLOAT32
                aDataTypes = [dt, dt, dt, dt, dt, dt, dt, dt]

                self.devices[name] = Device(id, connection, aAddresses, aDataTypes)
                log.info("Device instance instantiated for device named " + name + ".")
                self.deviceThread[name] = QThread(parent=self)
                log.info("Device thread created for device named " + name + ".")
                self.devices[name].moveToThread(self.deviceThread[name])
                self.deviceThread[name].start()
                log.info("Device thread started for device named " + name + ".")

                # Emit signal to connect sample timer to slot for the current device object.
                self.connectSampleTimer.emit(name)

                # Connections.
                self.devices[name].emitData.connect(self.assembly.updateNewData)
           
            elif(device["Device Type"] == "Mbed K64F"):
                name = device["name"]
                id = device["id"]
                connection = device["connection"]

                # Function required HERE to generate addresses from acquisition table data.
                K64F_ADC_Address = "0x1FFF0000"
                dt = ljm.constants.FLOAT32
                aDataTypes = [dt, dt, dt, dt, dt, dt, dt, dt]

                self.devices[name] = Mbed_Device(id, connection, K64F_ADC_Address, aDataTypes, device["address"])
                log.info("Device instance instantiated for device named " + name + ".")
                self.deviceThread[name] = QThread(parent=self)
                log.info("Device thread created for device named " + name + ".")
                self.devices[name].moveToThread(self.deviceThread[name])
                self.deviceThread[name].start()
                log.info("Device thread started for device named " + name + ".")

                # Emit signal to connect sample timer to slot for the current device object.
                self.connectSampleTimer.emit(name)

                # Connections.
                self.devices[name].emitData.connect(self.assembly.updateNewData)

    def loadDevicesFromConfiguration(self):
        # Find all devices listed in the configuration file.
        if "devices" in self.configuration:
            for device in self.configuration["devices"].keys():
                deviceInformation = {}
                deviceInformation["connect"] = True
                deviceInformation["name"] = device
                deviceInformation["id"] = self.configuration["devices"][device]["id"]
                deviceInformation["Device Type"] = self.configuration["devices"][device]["Device Type"]
                deviceInformation["connection"] = self.configuration["devices"][device]["connection"]
                deviceInformation["address"] = self.configuration["devices"][device]["address"]
                deviceInformation["status"] = False
                if(deviceInformation["Device Type"] == "Labjack T7"):
                    # Try to connect to each device using the ID.
                    try:
                        # If the connection is successful, set the device status to true.
                        handle = ljm.open(7, int(deviceInformation["connection"]), int(deviceInformation["id"]))
                        name = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
                        ljm.close(handle)
                        deviceInformation["status"] = True
                    except ljm.LJMError:
                        # Otherwise log the exception and set the device status to false.
                        ljme = sys.exc_info()[1]
                        log.warning(ljme) 
                    except Exception:
                        e = sys.exc_info()[1]
                        log.warning(e)
                    # Update acquisition table models and add TableView to TabWidget by emitting the appropriate Signal. Any changes in the table will be reflected immediately in the underlying configuration data.
                    self.deviceTableModel.appendRow(deviceInformation)
                    self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                    self.addAcquisitionTable.emit(name)

                elif(deviceInformation["Device Type"] == "Mbed K64F"):
                    default_baudrate = 115200 # Assume all boards use default baudrate of 9600 
                    try:
                        Serial_device = serial.Serial(port=deviceInformation["address"], baudrate=default_baudrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
                        name = "Mbed_TBA"
                        Serial_device.close()
                    except SerialException:
                        # Otherwise log the exception and set the device status to false.
                        ljme = sys.exc_info()[1]
                        log.warning(ljme) 
                    except Exception:
                        e = sys.exc_info()[1]
                        log.warning(e)
                    # Update acquisition table models and add TableView to TabWidget by emitting the appropriate Signal. Any changes in the table will be reflected immediately in the underlying configuration data.
                    self.deviceTableModel.appendRow(deviceInformation)
                    self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                    self.addAcquisitionTable.emit(name)

            log.info("Configuration loaded.")
        self.updateAcquisitionTabs.emit()
        self.updateUI.emit(self.configuration)

    
    def findDevices(self):
        """Method to find all available devices and return an array of connection properties.
        USB connections are prioritised over Ethernet and WiFi connections to minimise jitter."""

        # Boolean to indicate that the device list is refreshing.
        self.refreshing = True

        # Clear all tables and re-load the current configuration.
        self.deviceTableModel.clearData()
        self.acquisitionModels = {}
        self.acquisitionTables = {}
        self.clearAcquisitionTabs.emit()
        self.loadDevicesFromConfiguration()

        # Get a list of already existing devices.
        existingDevices = self.deviceTableModel._data
        ID_Existing = []
        for device in existingDevices:
            ID_Existing.append(device["id"])

        # Check for USB connectons first and add to available device list if not already enabled.
        log.info("Scanning for additional Labjack USB devices.")
        info = ljm.listAll(7, 1)
        devicesUSB = info[0]
        connectionType = info[2]
        ID_USB = info[3]
        IP = info[4]
        for i in range(devicesUSB):
            if ID_USB[i] not in ID_Existing:
                deviceInformation = {}
                deviceInformation["connect"] = False
                handle = ljm.open(7, 1, ID_USB[i])
                deviceInformation["name"] = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
                ljm.close(handle)
                deviceInformation["id"] = ID_USB[i]
                deviceInformation["Device Type"] = "Labjack T7"
                deviceInformation["connection"] = connectionType[i]
                deviceInformation["address"] = "N/A"
                deviceInformation["status"] = True
                self.deviceTableModel.appendRow(deviceInformation)
                self.updateUI.emit(self.configuration)
                
                # Make a deep copy to avoid pointers in the YAML output.
                acquisitionTable = copy.deepcopy(self.defaultAcquisitionTable)
                newDevice = {
                    "id": deviceInformation["id"],
                    "Device Type" : deviceInformation["Device Type"],
                    "connection": deviceInformation["connection"],
                    "address": deviceInformation["address"],
                    "acquisition": acquisitionTable
                }

                # If no previous devices are configured, add the "devices" key to the configuration.
                name = deviceInformation["name"]
                if "devices" not in self.configuration:
                    self.configuration["devices"] = {name: newDevice} 
                else:
                    self.configuration["devices"][name] = newDevice 

                # Update acquisition table models and add TableView to TabWidget by emitting the appropriate Signal. Any changes in the table will be reflected immediately in the underlying configuration data.
                self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                self.addAcquisitionTable.emit(name)
                self.updateAcquisitionTabs.emit()
                self.updateUI.emit(self.configuration)
        log.info("Found " + str(devicesUSB) + " Labjack USB device(s).")

        # Check TCP and add to list if not already in available device list.
        log.info("Scanning for Labjack TCP devices.")
        info = ljm.listAll(7, 2)
        numDevicesTCP = 0
        devicesTCP = info[0]
        connectionType = info[2]
        ID_TCP = info[3]
        IP = info[4]
        for i in range(devicesTCP):
            if ID_TCP[i] not in ID_USB and ID_TCP[i] not in ID_Existing:
                numDevicesTCP += 1
                deviceInformation = {}
                deviceInformation["connect"] = False
                # Name string requires a brief connection.
                handle = ljm.open(7, 2, ID_TCP[i])
                deviceInformation["name"] = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
                ljm.close(handle)
                deviceInformation["id"] = ID_TCP[i]
                deviceInformation["Device Type"] = "Labjack T7"
                deviceInformation["connection"] = connectionType[i]
                deviceInformation["address"] =  ljm.numberToIP(IP[i])
                deviceInformation["status"] = True
                self.deviceTableModel.appendRow(deviceInformation)
                self.updateUI.emit(self.configuration)

                # Make a deep copy to avoid pointers in the YAML output.
                acquisitionTable = copy.deepcopy(self.defaultAcquisitionTable)
                newDevice = {
                    "id": deviceInformation["id"],
                    "Device Type" : deviceInformation["Device Type"],
                    "connection": deviceInformation["connection"],
                    "address": deviceInformation["address"],
                    "acquisition": acquisitionTable
                }

                # If no previous devices are configured, add the "devices" key to the configuration.
                name = deviceInformation["name"]
                if "devices" not in self.configuration:
                    self.configuration["devices"] = {name: newDevice} 
                else:
                    self.configuration["devices"][name] = newDevice 

                # Update acquisition table models and add TableView to TabWidget by emitting the appropriate Signal. Any changes in the table will be reflected immediately in the underlying configuration data.
                self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                self.addAcquisitionTable.emit(name)
                self.updateAcquisitionTabs.emit()
                self.updateUI.emit(self.configuration)
        log.info("Found " + str(numDevicesTCP) + " Labjack TCP device(s).")

        # Wasn't working as part of a function, although other fixes have since been made 
        log.info("Scanning for additional Mbed USB devices.")
        
        Num_Mbed_Devices = 0
        COM_PORTS = []
        connectionType = []  # Create a unique value for USB K64F devices which trigger new functions  
        # Say 11 = mbed USB, 10 = mbed ANY, 12 = mbed TCP, 14 = mbed WIFI 
        VID_PID = []   # USB VID:PID are the Vendor/Product ID respectively - smae for each K64F Board? - You can determine HIC ID from last 8 digits of Serial Number? 
        # Note that the 0240 at the start of Serial Number refers to the K64F Family 
        ID_USB = []   # ID_USB will be the USB serial number - should be unique
        Baud_Rate = []  # For now assume all operating at 9600 - may change later so might need to add later on 
        # IP = []  # Don't think we need this for USB Serial(Mbed) devices 
        Num_Mbed_Devices, COM_PORTS, connectionType, ID_USB, VID_PID = List_All_Mbed_USB_Devices()

        for i in range(Num_Mbed_Devices):
            if ID_USB[i] not in ID_Existing:
                deviceInformation = {}
                deviceInformation["connect"] = False
                # handle = ljm.open(7, 1, ID_USB[i])
                # deviceInformation["name"] = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
                # ljm.close(handle)
                deviceInformation["name"] = "Mbed_TBA"
                deviceInformation["id"] = ID_USB[i]
                if(ID_USB[i][0:4] == "0240"):
                    deviceInformation["Device Type"] = "Mbed K64F"
                else:
                    deviceInformation["Device Type"] = ID_USB[i][0:4]
                deviceInformation["connection"] = connectionType[i]
                deviceInformation["address"] = COM_PORTS[i]
                deviceInformation["status"] = True
                self.deviceTableModel.appendRow(deviceInformation)
                self.updateUI.emit(self.configuration)
                
                # Make a deep copy to avoid pointers in the YAML output.
                acquisitionTable = copy.deepcopy(self.defaultAcquisitionTable)
                newDevice = {
                    "id": deviceInformation["id"],
                    "Device Type" : deviceInformation["Device Type"],
                    "connection": deviceInformation["connection"],
                    "address": deviceInformation["address"],
                    "acquisition": acquisitionTable
                }

                # If no previous devices are configured, add the "devices" key to the configuration.
                name = deviceInformation["name"]
                if "devices" not in self.configuration:
                    self.configuration["devices"] = {name: newDevice} 
                else:
                    self.configuration["devices"][name] = newDevice 
                # Update acquisition table models and add TableView to TabWidget by emitting the appropriate Signal. Any changes in the table will be reflected immediately in the underlying configuration data.
                self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                log.info(name)
                self.addAcquisitionTable.emit(name)
                self.updateAcquisitionTabs.emit()
                self.updateUI.emit(self.configuration)
        log.info("Found " + str(Num_Mbed_Devices) + " Mbed USB device(s).")

        # Boolean to indicate that the device list has finished refreshing.
        self.refreshing = False

    def configure(self):
        # Stop acquisition.
        self.endTimers.emit()

        # Close device threads.
        for name in self.deviceThread:
            self.deviceThread[name].quit()
            log.info("Thread for " + name + " stopped.")

        log.info("Configuring devices.")

    def run(self):
        # Create device threads.
        self.createDeviceThreads()

        # Start acquisition.
        self.startTimers.emit()
        log.info("Started acquisition and control.")

    def refreshDevices(self):
        log.info("Refreshing devices.")
        self.findDevices()

    def findConfigurationPath(self):
        if self.settings.value("configurationPath") == None:
            self.configurationPath = None
            log.info("No configuration file path found. Using defaults.")
        else:
            self.configurationPath = self.settings.value("configurationPath")
            log.info("Configuration file path found at " + str(self.configurationPath))
    
    def initialiseDefaultConfiguration(self):
        self.configuration = {}
        self.configuration["global"] = {
            "darkMode": True,
            "controlRate": 1000.00,
            "acquisitionRate": 100.00,
            "averageSamples": 10,
            "path": "/data",
            "filename": "junk"
            }
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def loadConfiguration(self, loadConfigurationPath):
        # Clear device table prior to loading devices from selected configuration.
        self.configuration = {}
        self.deviceTableModel.clearData()
        self.acquisitionModels = {}
        self.acquisitionTables = {}
        self.clearAcquisitionTabs.emit()
        try:    
            log.info("Loading configuration from " + loadConfigurationPath + " and saving location to QSettings.")
            with open(loadConfigurationPath, "r") as file:
                self.configuration = ruamel.yaml.load(file, Loader=ruamel.yaml.Loader) 
                log.info("Configuration file parsed.")
                self.configurationPath = loadConfigurationPath
                self.configurationChanged.emit(self.configuration)    
                self.settings.setValue("configurationPath", loadConfigurationPath)
                self.loadDevicesFromConfiguration()
        except (FileNotFoundError, TypeError):
            log.warning("Previous configuration file not found.")  
            self.initialiseDefaultConfiguration()

    @Slot(str)
    def saveConfiguration(self, saveConfigurationPath):
        # Make deep copies of the configuration and filter out devices that are not enabled in the device table.
        configuration = copy.deepcopy(self.configuration)
        devices = copy.deepcopy(self.configuration["devices"])
        enabledDevices = self.deviceTableModel.enabledDevices()
        enabledDeviceList = []
        for device in enabledDevices:
            enabledDeviceList.append(device["name"])
        for device in configuration["devices"]:
            if device not in enabledDeviceList:
                devices.pop(device)
        configuration["devices"] = devices

        # Save the yaml file and its path to QSettings.
        with open(saveConfigurationPath, "w") as file:
            yaml = ruamel.yaml.YAML()
            yaml.dump(configuration, file)
        self.settings.setValue("configurationPath", saveConfigurationPath)
        log.info("Saved configuration saved at " + saveConfigurationPath)

    @Slot()
    def clearConfiguration(self):
        self.configuration = {}
        self.loadConfiguration("/NoneExistentFile.yaml")
        self.updateUI.emit(self.configuration)
        log.info("Cleared configuration by loading defaults.") 

    @Slot(str)
    def updateAcquisitionRate(self, newAcquisitionRate):
        self.configuration["global"]["acquisitionRate"] = float(newAcquisitionRate)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New acquisition rate = " + newAcquisitionRate + " Hz")
        
    @Slot(str)
    def updateControlRate(self, newControlRate):
        self.configuration["global"]["controlRate"] = float(newControlRate)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New control rate = " + newControlRate + " Hz")

    @Slot(str)
    def updateAverageSamples(self, newAverageSamples):
        self.configuration["global"]["averageSamples"] = int(newAverageSamples)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New average samples = " + newAverageSamples)
        
    @Slot(str)
    def updatePath(self, newPath):
        self.configuration["global"]["path"] = str(newPath)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New path = " + newPath)

    @Slot(str)
    def updateFilename(self, newFilename):
        self.configuration["global"]["filename"] = str(newFilename)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New filename = " + newFilename)

    @Slot(bool)
    def updateDarkMode(self, newDarkMode):
        self.configuration["global"]["darkMode"] = newDarkMode
        self.configurationChanged.emit(self.configuration) 
        # log.info("New darkMode = " + str(newDarkMode))


    

    