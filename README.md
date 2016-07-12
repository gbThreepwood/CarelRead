# CarelRead
Tool to communicate with the RS485 bus of the Carel IR32 series refrigeration controllers.


I have not been able to obtain any documentation for the proprietary communication protocol.

# Reverse engineering

Here are some inital thoughts while attemting to reverse engineer the protocol. The data is captured while the proprietary Carel PlantVisor monitoring software is running in normal operation.


## Command
After some initalization it seems the monitoring software is continously sending the commands:
- 0x05 0xF8
- 0x05 0x31
- 0x05 0x32
- 0x05 0x33
- 0x05 0x34
- 0x05 0x35
- 0x05 0x36

The first byte is the enquire character in ASCII.
From Wikipedia: The enquire character (ENQ) is generally used by a master station to ask a
slave station to send its next message.

The second byte is likely the address of the controller

## Response

The response is 23 bytes long when these commands are issued.

###Example responses

02 31 52 45 30 30 39 45 46 44 39 35 39 39 39 35 30 32 30 30 03 34 35  

02 35 52 45 30 30 38 43 46 44 38 45 39 39 39 35 30 32 30 30 03 35 35

###Interpretation
The response always starts with 0x02 followed by the assumed adress of the
controller, e.g.:
0x02 0x31 ...

0x02 corresponds to ASCII `Start of text`

The next two bytes are always 0x52 and 0x45, corresponding to ASCII R and E.

The following two bytes are always 0x30, corresponding to ASCII 0(zero).

The following two bytes contain the reading of the primary temperature sensor.

E.g: 0x38 0x43, which decodes to ASCII 8C. If these two ASCII characters are interpreted as a hexadecimal value, the result is 140, i.e. the temperature is 14.0 degrees celsius.

The next two bytes are 0x38 0x43, ASCII: F and D.

The next two bytes have some small variations between the different controllers. This may be the reading from the secondary sensor.


The following eight bytes are always:
0x039 0x39 0x39 0x35 0x30 0x32 0x30 0x30 Corresponding to ASCII: 99950200 

These are followed by 0x03, ASCII: `End of text` 

The last two bytes are varying. Is this some kind of checksum?
From Wikipedia: A widely used convention is to make the two characters preceding ETX a checksum
or CRC for error-detection purposes


TODO:
- Tamper with the temperature, and see how the controller behaves
- Connect secondary sensor and see if it is possible to obtain a reading

====================================================
Command

Start byte
0x02 - ASCII `Start of text`
0x06 - ASCII: `Acknowledge`
0x05 - Used in normal operation. ASCII: `Enquiry`
