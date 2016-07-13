# CarelRead
Tool to communicate with the RS485 bus of the Carel IR32 series refrigeration controllers.

The manual states that the controller network address is a number between 0 and 15, i.e. a maximum of 16 unitis may be connected.

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

The next two bytes are always 0x52 and 0x45, corresponding to ASCII R and E. (READ?)

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


## Additional data

If the temperature sensor is disconnected, the controller displays a error message. The following is the response to a read request while the sensor is disconnected:

02:31:52:45:46:44:39:45:46:44:39:43:30:30:32:35:30:41:31:30:03:37:34

Byte number 5 and 6 has changed from 0x00 to 0x46 and 0x44, corresponding to ASCII: FD. (Failed device?)

Byte 7 and 8 decodes to a temperature of 15.8 degrees celcius.

Byte 9 and 10 decodes to FD (Failed device for secondary sensor?)


### Initialization
The following commands are executed during the initialization of the control software.

#### Enquire
Command
02 31 3f 03 37 35
.1?.75          

Response
02 31 56 35 03 3c 31
.1V5.<1         

The byte 0x3f corresponds to ASCII: ?(question mark). This command is likely used to enquire all the controlers. The command is repeated several times when the controller is missing.

The response may be the version of the installed firmware. Version 5 in this case?

#### Unknown
Command
02 31 54 44 45 03 31 33
.1TDE.13 

Response
02 31 52 44 31 41 41 39 31 35 30 32 30 34 30 30 33 31 46 32 03 32 30
.1RD1AA91502040031F2.20

	
Second example
02 33 54 44 45 03 31 35
.3TDE.15

02 33 52 44 31 43 36 36 31 36 34 41 30 34 30 30 33 31 43 32 03 32 37
.3RD1C66164A040031C2.27         


This command is only executed if the previous command has retured some valid data.

The response has a length of 23 bytes.

#### Unknown 2

First example:
02 31 52 45 49 03 31 36                           
.1REI.16

Response:
02 31 52 45 30 30 39 45 46 44 39 34 39 39 39 35 30 32 30 30 03 34 34
.1RE009EFD9499950200.44

Second example:

02 33 52 45 49 03 31 38
.3REI.18        

Response:
02 33 52 45 30 30 41 30 46 44 38 39 39 39 39 35 30 32 30 30 03 33 3d
.3RE00A0FD8999950200.3=

I suppose the command is "REI", but the meaning is still obscure to me.

The response has a length of 23 bytes.


#### Unknown 3

02 31 52 49 4a 03 31 3b
.1RIJ.1;

02 31 52 49 30 30 31 45 30 30 31 45 30 30 30 35 30 30 31 34 03 30 37
.1RI001E001E00050014.07         


02 33 52 49 4a 03 31 3d
.3RIJ.1=

02 33 52 49 30 30 31 45 30 30 31 45 30 30 30 35 30 30 31 34 03 30 39
.3RI001E001E00050014.09




TODO:
- Tamper with the temperature, and see how the controller behaves
- Connect secondary sensor and see if it is possible to obtain a reading

====================================================
Command

Start byte
- 0x02 - ASCII `Start of text`
- 0x06 - ASCII: `Acknowledge`
- 0x05 - Used in normal operation. ASCII: `Enquiry`
