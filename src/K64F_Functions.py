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



def _Serial_Read_Raw_Bytes(Serial_Device, Expected_Bytes):
    serialBytes = "" # Used to hold data coming over UART

    serialBytes = Serial_Device.read(size=Expected_Bytes)
    if(len(serialBytes) != Expected_Bytes):
        print("Error", serialBytes)
    else:
        return serialBytes


def _Decode_Raw_ADC(input, Num_Channels = 8):
    data = []
    if(len(input) != Num_Channels * 2):
        print("Erorr with provided Raw ADC Data", len(input), (Num_Channels * 2))
    else:
        for x in range(Num_Channels):
            data.append(np.int16(int.from_bytes(input[2*x : 2*x + 2], 'little')))
    return data

def _Convert_ADC_Raw(Raw_Reading, ADC_Resolution, Max_Min_Voltage): 
    quant_step = (2 * Max_Min_Voltage) / (2**ADC_Resolution)
    return Raw_Reading * quant_step

def Read_ADC_Voltage(input, Num_Channels = 8, ADC_Resolution = 16, Max_Min_Voltage = 5):
    Voltages = []
    Raw_2s_comp_values = _Decode_Raw_ADC(input, Num_Channels)
    # If invalid input: Raw_2s_comp_values will be an empty list, so return value will also be empty
    for x in Raw_2s_comp_values:
        Voltages.append(_Convert_ADC_Raw(x, ADC_Resolution, Max_Min_Voltage))
    return Voltages


def Read_Time_In_Secs(input, Num_Bytes = 2):
    if(len(input) != Num_Bytes):
        print("Erorr with provided RTC Data")
    else:
        return np.uint32(int.from_bytes(input, 'little'))

def Read_Compressed_PWM_Duty(input, Num_Channels = 6):
    Duty_Cycles = []
    if(len(input) != Num_Channels):
        print("Error with PWM data")
    else:
        for x in input:   # Auto conversion from bytes to int?? Seems to work anyways 
            Duty_Cycles.append(x) 
    return Duty_Cycles

def Read_Sample(Serial_Device, Expected_Bytes):
    Raw_Data = _Serial_Read_Raw_Bytes(Serial_Device, Expected_Bytes)
    
    Time = Read_Time_In_Secs(Raw_Data[0:4], 4)
    Voltages = Read_ADC_Voltage(Raw_Data[4:20], 8)
    PWM_Duties = Read_Compressed_PWM_Duty(Raw_Data[20:26], 6)

    return Time, Voltages, PWM_Duties