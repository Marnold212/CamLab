<<<<<<< HEAD
import numpy as np 
import serial.tools.list_ports as port_list
import serial

def List_All_Mbed_USB_Devices(Buadrate = 115200):
=======
from ctypes.wintypes import HANDLE
from serial.serialutil import SerialException
import serial.tools.list_ports as port_list
import serial
import numpy as np 

# Scans connected USB Devices and attempts to connect to any with name beginning "mbed Serial Port" - may not be best method
# Returns an array with [0]: No. mbed devices connected over USB, [1]: Array corresponding to COM_PORT for each device 
# [2]: 

#### How will we convey COM_PORT - very important for this serial connection
#### Don't forget to check if 115200 has any effect on performance or if overhead dominates for such short transfers  

# def List_All_Mbed_USB_Devices(self):
def List_All_Mbed_USB_Devices():
>>>>>>> ef201362b9151a380c985dd5acef6b7b21de82f9
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
<<<<<<< HEAD
            if(ports[i][1].startswith("mbed Serial Port") or ports[i][1].startswith("USB Serial Device")):     # port[i] is a particular device - port[i][1] is the description of the device - port[i][1][0:16] are the characters containing the mbed Serial Port description
                try:
                    Serial_device = serial.Serial(port=COM_Port, baudrate=Buadrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
=======
            if(ports[i][1].startswith("mbed Serial Port")):     # port[i] is a particular device - port[i][1] is the description of the device - port[i][1][0:16] are the characters containing the mbed Serial Port description
                default_baudrate = 115200 # Assume all boards use default baudrate of 9600 
                try:
                    Serial_device = serial.Serial(port=COM_Port, baudrate=default_baudrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
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
            
            if(ports[i][1].startswith("USB Serial Device")):     
                default_baudrate = 115200 # Assume all boards use default baudrate of 9600 
                try:
                    Serial_device = serial.Serial(port=COM_Port, baudrate=default_baudrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
>>>>>>> ef201362b9151a380c985dd5acef6b7b21de82f9
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
<<<<<<< HEAD
    return(Num_Mbed_Devices, COM_PORTS, connectionType, ID_USB, VID_PID)
=======

    return(Num_Mbed_Devices, COM_PORTS, connectionType, ID_USB, VID_PID)

# Instructions + Expected Number of Bytes Returned 
_Read_32_Reg_Instruction = "30" # 0x30
_Expected_Bytes_Read_32_Reg = 5 # 4 bytes + '/n'
_Read_16_Reg_Instruction = "31"  # 0x31
_Expected_Bytes_Read_16_Reg = 3 # 2 bytes + '/n'
_Read_8_Reg_Instruction = "32" # 0x32
_Expected_Bytes_Read_8_Reg = 2 # 1 byte + '/n'

# Intended for reading 8 channel 16 bit ADC readings (4 x 32 bits)
_Read_128_Reg_Instruction = "36" # 036
_Expected_Bytes_Read_128_Reg = 17 # 16 bit (2 bytes) x 8channels + '\n'

# Instructions + Expected Number of Bytes Returned 
_Write_32_Reg_Instruction = "33" # 0x33
_Expected_Bytes_Write_32_Reg = 5 # 4 bytes + '/n'
_Write_16_Reg_Instruction = "34" # 0x34
_Expected_Bytes_Write_16_Reg = 3 # 2 bytes + '/n'
_Write_8_Reg_Instruction = "35" # 0x35
_Expected_Bytes_Write_8_Reg = 2 # 1 byte + '/n'

_SPI_Write_Instruction = "40" # 0x40

def Hex_To_Dec(input):  # input of form "40048024"
    return int(input, 16)

def Hex_To_Bin(input): # input of form "40048024"
    return bin(int(input, 16))

def Hex_To_Bytes(input): # input of form "40048024"
    return bytes.fromhex(input)


# Uses private function - returns data written to Register in hex form 
def Write_32_Reg(Serial_Device, Target_Address, Hex_Value):
    # if not self.IsConnected:
    #     raise Exception ("No connected mbed Device")
    if(len(Target_Address) != 10 or not Target_Address.startswith("0x")):
        raise Exception ("Register Address should be 4 bytes/8 hex digits long and be in format 0x00000000")
    if(len(Hex_Value) > (4*2 + 2) or not Hex_Value.startswith("0x")):
        raise Exception ("Trying to Write an Invalid value to mbed Register")
    Target_Address = Target_Address[2:] # Remove "0x"
    Hex_Value = Hex_Value[2:] # Remove "0x"
    Reg_Contents = _Serial_Write(Serial_Device, _Write_32_Reg_Instruction, Target_Address, Hex_Value, _Expected_Bytes_Write_32_Reg)
    # if(len(Reg_Contents) != 2*(self._Expected_Bytes_Write_32_Reg - 1)): # Expect 32 bits returned 
    #     raise Exception ("0x33 Issue with Returned Data")
    if(Reg_Contents != Hex_Value): # We expect to recieve the same value we wrote to an address on the mbed
        # raise Exception ("0x33 Issue with Returned Data")
        print("0x33 Non-Matching Response (Could be a Set Register)")
    return Reg_Contents  # Hex Form 

def Write_16_Reg(Serial_Device, Target_Address, Hex_Value):
    # if not self.IsConnected:
    #     raise Exception ("No connected mbed Device")
    if(len(Target_Address) != 10 or not Target_Address.startswith("0x")):
        raise Exception ("Register Address should be 4 bytes/8 hex digits long and be in format 0x00000000")
    if(len(Hex_Value) > (2*2 + 2) or not Hex_Value.startswith("0x")):
        raise Exception ("Trying to Write an Invalid value to mbed Register")
    Target_Address = Target_Address[2:] # Remove "0x"
    Hex_Value = Hex_Value[2:] # Remove "0x"
    Reg_Contents = _Serial_Write(Serial_Device, _Write_16_Reg_Instruction, Target_Address, Hex_Value, _Expected_Bytes_Write_16_Reg)
    # if(len(Reg_Contents) != 2*(self._Expected_Bytes_Write_16_Reg - 1)): # Expect 32 bits returned (subtract the EOL byte)
    #     raise Exception ("0x34 Issue with Returned Data")
    if(Reg_Contents != Hex_Value):
        # raise Exception ("0x34 Issue with Returned Data")
        print("0x34 Non-Matching Response (Could be a Set Register)")
    return Reg_Contents  # Hex Form 

def Write_8_Reg(Serial_Device, Target_Address, Hex_Value):
    # if not self.IsConnected:
    #     raise Exception ("No connected mbed Device")
    if(len(Target_Address) != 10 or not Target_Address.startswith("0x")):
        raise Exception ("Register Address should be 4 bytes/8 hex digits long and be in format 0x00000000")
    if(len(Hex_Value) > (1*2 + 2) or not Hex_Value.startswith("0x")):
        raise Exception ("Trying to Write an Invalid value to mbed Register")
    Target_Address = Target_Address[2:] # Remove "0x"
    Hex_Value = Hex_Value[2:] # Remove "0x"
    Reg_Contents = _Serial_Write(Serial_Device, _Write_8_Reg_Instruction, Target_Address, Hex_Value, _Expected_Bytes_Write_8_Reg)
    # if(len(Reg_Contents) != 2*(self._Expected_Bytes_Write_8_Reg - 1)): # Expect 32 bits returned (subtract the EOL byte)
    #     raise Exception ("0x35 Issue with Returned Data")
    if(Reg_Contents != Hex_Value):
        # raise Exception ("0x35 Issue with Returned Data")
        print("0x35 Non-Matching Response (Could be a Set Register)")
    return Reg_Contents  # Hex Form 

# Uses private function - returns data contained in Register in hex form 
def Read_128_Reg(Serial_Device, Target_Address): # Target_Address in form of "0x40048024"
    # if not self.IsConnected:
    #     raise Exception ("No connected mbed Device")
    if(len(Target_Address) != 10 or not Target_Address.startswith("0x")):
        raise Exception ("Register Address should be 4 bytes/8 hex digits long and be in format 0x00000000")
    Target_Address = Target_Address[2:]
    Reg_Contents = _Serial_Read(Serial_Device, _Read_128_Reg_Instruction, Target_Address, _Expected_Bytes_Read_128_Reg)
    if(len(Reg_Contents) != 2*(_Expected_Bytes_Read_128_Reg - 1)): # Expect 32 bits returned 
        raise Exception ("0x36 Issue with Returned Data")
    return Reg_Contents  # Hex Form 

# Uses private function - returns data contained in Register in hex form 
def Read_32_Reg(Serial_Device, Target_Address): # Target_Address in form of "0x40048024"
    # if not self.IsConnected:
    #     raise Exception ("No connected mbed Device")
    if(len(Target_Address) != 10 or not Target_Address.startswith("0x")):
        raise Exception ("Register Address should be 4 bytes/8 hex digits long and be in format 0x00000000")
    Target_Address = Target_Address[2:]
    Reg_Contents = _Serial_Read(Serial_Device, _Read_32_Reg_Instruction, Target_Address, _Expected_Bytes_Read_32_Reg)
    if(len(Reg_Contents) != 2*(_Expected_Bytes_Read_32_Reg - 1)): # Expect 32 bits returned 
        raise Exception ("0x30 Issue with Returned Data")
    return Reg_Contents  # Hex Form 

def Read_16_Reg(Serial_Device, Target_Address): # Target_Address in form of "0x40048024"
    # if not self.IsConnected:
    #     raise Exception ("No connected mbed Device")
    if(len(Target_Address) != 10 or not Target_Address.startswith("0x")):
        raise Exception ("Register Address should be 4 bytes/8 hex digits long and be in format 0x00000000")
    Target_Address = Target_Address[2:]
    Reg_Contents = _Serial_Read(Serial_Device, _Read_16_Reg_Instruction, Target_Address, _Expected_Bytes_Read_16_Reg)
    if(len(Reg_Contents) != 2*(_Expected_Bytes_Read_16_Reg - 1)): # Expect 16 bits returned 
        raise Exception ("0x31 Issue with Returned Data")
    return Reg_Contents  # Hex Form

def Read_8_Reg(Serial_Device, Target_Address): # Target_Address in form of "0x40048024"
    # if not self.IsConnected:
    #     raise Exception ("No connected mbed Device")
    if(len(Target_Address) != 10 or not Target_Address.startswith("0x")):
        raise Exception ("Register Address should be 4 bytes/8 hex digits long and be in format 0x00000000")
    Target_Address = Target_Address[2:]
    Reg_Contents = _Serial_Read(Serial_Device, _Read_8_Reg_Instruction, Target_Address, _Expected_Bytes_Read_8_Reg)
    if(len(Reg_Contents) != 2*(_Expected_Bytes_Read_8_Reg - 1)): # Expect 8 bits returned 
        raise Exception ("0x32 Issue with Returned Data")
    return Reg_Contents  # Hex Form

def _Serial_Read(Serial_Device, Instruction, Target_Address, Expected_Bytes):
    # Assume arguments are valid for given instruction - check in public method
    # Assume Target Address & Instructions are in form "40048024", "30" - no "0x" prefix
    # Expected_Bytes inludes the '\n' we expect at end of communication
    
    byte_Command = (b'%b%b\n' % (bytes.fromhex(Instruction), bytes.fromhex(Target_Address)))   
    return _Serial_Command_Response(Serial_Device, byte_Command, Expected_Bytes)

def _Serial_Write(Serial_Device, Instruction, Target_Address, Hex_Value, Expected_Bytes):
    # Assume arguments are valid for given instruction - check in public method
    # Assume Target Address, Hex_value & Instructions are in form "40048024", "30" - no "0x" prefix
    # Expected_Bytes inludes the '\n' we expect at end of communication
    # Writes the Hex_Value to the Targeted_Address 

    byte_Command = (b'%b%b%b\n' % (bytes.fromhex(Instruction), bytes.fromhex(Target_Address), bytes.fromhex(Hex_Value)))
    return _Serial_Command_Response(Serial_Device, byte_Command, Expected_Bytes)
    
# Returns a list of the raw 16 bit unsigned values from ADC channels 0-7
# Returns 4 x uint32_t : Note the effect that this has on the received byte order: V2, V1, V4, V3, etc. 
def Read_8_ADC_U16_Values(Serial_Device, Target_Address):
    if(len(Target_Address) != 10 or not Target_Address.startswith("0x")):
        raise Exception ("Register Address should be 4 bytes/8 hex digits long and be in format 0x00000000")
    raw_data = Read_128_Reg(Serial_Device, Target_Address)
    data = []
    for x in range(0, 8, 2):
        y = x+1   # Due to byte order of device - 
        data.append(Hex_To_Dec(raw_data[(4*y) + 0 : (4*y) + 4]))
        data.append(Hex_To_Dec(raw_data[(4*x) + 0 : (4*x) + 4]))
    return data

# Assumes Data recieved is from an AD7606
def Convert_ADC_Raw(Raw_Reading, ADC_Resolution, Max_Min_Voltage): 
    Signed_Value = np.int16(Raw_Reading)  
    quant_step = (2 * Max_Min_Voltage) / (2**ADC_Resolution)
    return Signed_Value * quant_step

# SPI Message must be given in hex form e.g. (24, A7, 08, 00, FF) -> 24A70800FF etc. 
def SPI_Write(Serial_Device, SPI_Device, Message):
    # if not self.IsConnected:
    #     raise Exception ("No connected mbed Device")
    if(len(Message) % 2 != 0):
        raise Exception ("Invalid SPI Message")
    Bytes_Message = len(Message) / 2 # Length of SPI Message, which is also returned as an error checking step 
    Expected_Bytes_Returned = (int)(Bytes_Message) + 1  # EOL, Message
    SPI_Message = _Serial_SPI_Write(Serial_Device, _SPI_Write_Instruction, SPI_Device, Bytes_Message, Message, Expected_Bytes_Returned)
    # Reg_Contents = self._Serial_Read(self._Read_8_Reg_Instruction, Target_Address, self._Expected_Bytes_Read_8_Reg)
    # if(len(Reg_Contents) != 2*(self._Expected_Bytes_Read_8_Reg - 1)): # Expect 8 bits returned 
    #     raise Exception ("0x32 Issue with Returned Data")
    if(SPI_Message.upper() != Message.upper()):
        print(SPI_Message.upper(), Message.upper())
        raise Exception ("0x40 Issue with Returned Data")
    return SPI_Message.upper() # Hex Form Still 

def _Serial_SPI_Write(Serial_Device, Instruction, SPI_Device, Len_Message, Message, Expected_Bytes):

    byte_Command = b'%b%b%b%b\n' % (bytes.fromhex(Instruction), (int)(SPI_Device).to_bytes(1, byteorder='big'), (int)(Len_Message).to_bytes(1, byteorder='big'), bytes.fromhex(Message))
    return _Serial_Command_Response(Serial_Device, byte_Command, Expected_Bytes)

def _Serial_Command_Response(Serial_Device, byte_Command, Expected_Bytes):
    try:
        num1 = Serial_Device.write(byte_Command)   # num1 is number of bytes sent 
    except:
        raise Exception ("Error writing to mbed Serial Device")
    serialString = "" # Used to hold data coming over UART
    # NEED TO ADD A TIMEOUT TO FOLLOWING LINE

    # Removing while(1) should allow the read(size=Expected_Bytes) to naturally timeout after configured time 

    ''' Don't need this chucnk since we know how many bytes we expect to get back 
        Therefore we can use the builtin timeout from the pyserial library  
    while(1):
        print(self.Serial_Device.in_waiting)
        if self.Serial_Device.in_waiting > 0:
            # Read data out of the buffer until a carriage return / new line is found
            # Note there is an inherant issue with this where, if a transmitted value has the equivalent hex value of 0a, it triggers the end of line
            # If we are sending unsigned bytes across channel, inevitably some will have the value of '\n' character 
            # serialString = serialPort.readline()
    '''

    serialString = Serial_Device.read(size=Expected_Bytes)
    serialString = serialString.hex()  # Decode bytes into raw hex values
    # if(serialString[Expected_Bytes-1] != 10):    # 10 = 0x0a = '\n' LF character in Ascii 
    if(serialString[-2: ] != '0a'):    # 10 = 0x0a = '\n' LF character in Ascii 
        print(serialString)
        raise Exception ("Issue with Received Data") # Need to implement proper error handling
    else:
        return serialString[:-2]





# Testing 
if __name__ == "__main__":
    mbed_USB_info = List_All_Mbed_USB_Devices()

    for i in range(5):
        print(mbed_USB_info[i])

    serial_port = serial.Serial(port="COM4", baudrate=115200, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)

    # print(Read_32_Reg(serial_port, "0x40048054"))
    # print(Read_32_Reg(serial_port, "0x40048058"))
    # print(Read_32_Reg(serial_port, "0x4004805C"))
    # print(Read_32_Reg(serial_port, "0x40048060"))
    print(Read_32_Reg(serial_port, "0x1FFF0000"))
    print(Read_32_Reg(serial_port, "0x1FFF0004"))
    print(Read_32_Reg(serial_port, "0x1FFF0008"))
    print(Read_32_Reg(serial_port, "0x1FFF000C"))

# Serial_device = serial.Serial(port="COM4", baudrate=9600, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
# Target_Register = "0x40048024"
# Received_String = Read_K64F_Hex_Register(Serial_device, Target_Register, 4)
# print("READ COMMAND (0x30): Requested Register = %s; Contents of Register(Hex) = %s" % (Target_Register , Received_String[:-2]))

>>>>>>> ef201362b9151a380c985dd5acef6b7b21de82f9
