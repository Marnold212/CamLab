import numpy as np 
import serial.tools.list_ports as port_list
import serial

def List_All_Mbed_USB_Devices(Buadrate = 115200):
    ports = list(port_list.comports())
    Num_Serial_Devices = len(ports)
    Num_Mbed_Devices = 0
    COM_PORTS = []
    connectionType = []  # Create a unique value for USB K64F devices which trigger new functions  
    # Say 11 = mbed USB, 10 = mbed ANY, 12 = mbed TCP, 14 = mbed WIFI 
    VID_PID = []   # USB VID:PID are the Vendor/Product ID respectively - smae for each K64F Board? - You can determine HIC ID from last 8 digits of Serial Number? 
    # Note that the 0240 at the start of Serial Number refers to the K64F Family 
    ID_USB = []   # ID_USB will be the USB serial number - should be unique
    Baud_Rate = []  # For now assume all operating at 9600 - may change later so might need to add later on 
    # IP = []  # Don't think we need this for USB Serial(Mbed) devices 
    if Num_Serial_Devices > 0:
        for i in range(Num_Serial_Devices):
            COM_Port = ports[i].usb_description()   # ports[i].device outputs COM_PORT    (Note port[i][0][0:16]  is a particular device - port[i][0] is the COM Port of the device)
            if(ports[i][1].startswith("mbed Serial Port") or ports[i][1].startswith("USB Serial Device")):     # port[i] is a particular device - port[i][1] is the description of the device - port[i][1][0:16] are the characters containing the mbed Serial Port description
                try:
                    Serial_device = serial.Serial(port=COM_Port, baudrate=Buadrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
                except:
                    raise Exception ("Issues connecting with mbed Device on %s", COM_Port) # Need to implement proper error handling 
                # How can we/Do we need to check we have actually connected to device - and that it is meant to be used for what we are using it for 
                if(not Serial_device.readable()):
                    raise Exception ("Issues connecting with mbed Device on %s", COM_Port) # Need to implement proper error handling 
                Num_Mbed_Devices += 1
                COM_PORTS.append(COM_Port)
                USB_INFO = ports[i].usb_info().split('=') # USB-PID should be Unique 
                USB_VIDPID = USB_INFO[1].split(' ')[0]
                VID_PID.append(USB_VIDPID)
                USB_Serial_Number = USB_INFO[2].split(' ')[0]
                ID_USB.append(USB_Serial_Number)
                connectionType.append(11)     # Added 10 onto definitions used by LJM library to avoid mixing up - however can change if confusing 
                Serial_device.close()    # Close COM Port communication once info obtained 
    return(Num_Mbed_Devices, COM_PORTS, connectionType, ID_USB, VID_PID)