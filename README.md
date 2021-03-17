# Serialization
This documentation will contain explanation for the serialization API built by **Team Gilroy** throughout the course of the Spring 2021 semester in CS 158B.

Group members:
- Alvin Jiang
- Le Duy Vu
- Muhammad Umer Sheikh
- Xochitl Medina Arreola

# Table of Contents
1. [What is serialization.py?](#what-is-serialization.py?)
2. [Why is serialization.py designed like this?](#why-is-serialization.py-designed-like-this?)
3. [How does serialization.py work?](#how-does-serialization.py-work?)

## What is serialization.py?

The file contains the class Serializer which makes networking programs more readable and shorter. 
This serialization API enables users to create and unpack network packets according to user input format (for example, RFCs).

## Why is serialization.py designed like this?

Since the design was not specified, we tried to be creative with our solution. 
Obviously, there may be multiple designs with different functionalities which meet this requirement; our design is one of them. 
After consideration, we decided to make the API essentially a class because all of our group members are familiar with the concept of OOP/OOD.

## How does serialization.py work?
This portion will help users to understand how functions operate based on their functionalities. 
We tried to make our API simply to understand, but still we **highly encourage** other users to read through the code and documentation, and ask questions if any portion is not clear. 
We tried our best to make the documentation concise, and easy to read.

To make it easier, we used one class called
```python
class Serializer:
```
and inside this class we have all our functions. 
The Serializer class helps users easily encode and decode binary packets when it is provided the format of a packet in a dictionary.

The class has 2 OrderedDict variables which remembers how the keys were interested. 
We used *OrderedDict()* instead of *dict()* since *dict()* does not keep track of insertion order, and gives the value in a random order.

The first dictionary **fieldLengths** is used to remember the name of the fields in the packet together with their lengths in bit. 
The second dictionary **fieldValues** stores the actual value of those fields in binary string.

#### Constructor: __init __(self, format_dict)

*__init __* is the only constructor of the class. 
It initializes **fieldLengths** with the users predefined dictionary for section or packet format.
*fieldValues* is also initialized based on the format dictionary and its values are filled with 0. 
The constructor complains if **format_dict** is not a dictionary. 

Note for the predefined format dictionary from users: 
- Field name must be str and field length must be int
- If field length is not fixed in the RFC but depends on the actual data of that field (for example, the QNAME field of DNS question section), put the length as 0.
```python
     def __init__(self, format_dict):
        if self.validate_format(format_dict):

            self.fieldLengths = OrderedDict()
            
            self.fieldValues = OrderedDict()

            for field in format_dict:
               
                self.fieldLengths[field] = format_dict[field]

                self.fieldValues[field] = self.fieldLengths[field] * '0'
        else:
            print('Invalid format: {}'.format(format_dict))
```
<br>

#### Function: update_format(self, format_dict)

Similar to *init* function it deals with the format. 
This function allows users to work with a new format without creating another Serializer object. 
Note that **fieldValues** keeps its content after this operation.
```python

    def update_format(self, format_dict):
 
        if self.validate_format(format_dict):
            self.fieldLengths = OrderedDict()
            for field in format_dict:
                self.fieldLengths[field] = format_dict[field]
        else:
            print('Invalid format: {}'.format(format_dict))
```
<br>

#### Function: get_format(self)

*get_format* retrieves the format of the section/packet, and return the format dictionary.
```python
    def get_format(self):
        
        return self.fieldLengths
```
<br>

#### Function: get_data(self)

*get_data* retrieves the **fieldvalues** dictionary of the section or packet, and return the data dictionary.
```python
    def get_data(self):
       
        return self.fieldValues
```
<br>

##### Function: refresh_field(self)

*refresh_field* removes the content in the value dictionary, and generate a new value dictionary based on the format dictionary. 
None is returned.
```python
    def refresh_fields(self):
        
        self.fieldValues.clear()
 
        for field in self.fieldLengths:
            self.fieldValues[field] = self.fieldLengths[field] * '0'
```
<br>

#### Function: set_field(self, field_name, value)

*set_field* sets the value of the specified **FIELD_NAME** if it exists. 
*field_name* is the name of the field being changed, must be a str, and it is also case sensitive.
*value* can only be type int, bitstring, or bytes.<br>
Note: If the field length is not pre-determined, only a bitstring or a bytes is accepted, int does not work for this field.

| Type                | Variable       |
| :-------------      | :------------- |
| String              | field_name     |
| Int/Bitstring/Bytes | value          |


```python
    def set_field(self, field_name, value):
        
        # argument validity check
        if type(field_name) == str and field_name in self.fieldLengths and (type(value) == bytes or type(value) == int or type(value) == str):
            if self.fieldLengths[field_name] == 0:  # if field length is not predefined
                if type(value) == int:  # this field can't accept type int because of the undefined length
                    print('Invalid type for VALUE (must be bit string or bytes)')
                elif type(value) == str:
                    if self.check_bitstring(value):     # if VALUE is binary string
                        self.fieldValues[field_name] = value
                    else:
                        print('VALUE must be a bit string.')
                else:
                    self.fieldValues[field_name] = self.bytes_to_bits(value)

            else:   # if a normal field
                if type(value) == int:
                    # check if VALUE is in acceptable range for the field length
                    if -(2 ** (self.fieldLengths[field_name] - 1)) + 1 <= value <= 2 ** self.fieldLengths[field_name] - 1:
                        if value >= 0:  # unsigned VALUE
                            bits = bin(value)[2:]
                            self.fieldValues[field_name] = (self.fieldLengths[field_name] - len(bits)) * '0' + bits
                        else:   # negative VALUE
                            bits = bin(value)[3:]
                            self.fieldValues[field_name] = (self.fieldLengths[field_name] - len(bits)) * '1' + bits
                    else:
                        print('Error: VALUE is out of range for the specified length of this field')
                elif type(value) == str:
                    if self.check_bitstring(value):     # if VALUE is binary string
                        if len(value) == self.fieldLengths[field_name]:     # check if lengths match
                            self.fieldValues[field_name] = value
                        else:
                            print('Length of VALUE must equal field length')
                    else:
                        print('VALUE must be a bit string.')
                else:   # if VALUE type is bytes
                    if len(value) * 8 == self.fieldLengths[field_name]:     # check if lengths match
                        self.fieldValues[field_name] = self.bytes_to_bits(value)
                    else:
                        print('Length of VALUE in bit must equal field length specified in format')

        else:
            print('Invalid argument type or invalid field name')
```

<br>

#### Function: get_field(self, field_name)

*get_field* retrieves the value of the specified field if it exists. 
*field_name* is a string and it is case sensitive. A string value of field is returned. 
None is returned if no such field exists.

| Type           | Variable       |
| :------------- | :------------- |
| String         | field_name     |

```python
    def get_field(self, field_name):

        if not isinstance(field_name, str):
            print('Invalid field_name type')
            return None

        try:
            return self.fieldValues[field_name]
        except KeyError:
            print('Field not found')
            return None
```
<br>

#### Function: to_byte(self)

*to_byte* concatenate the values of all fields in the dictionary into a byte object, essentially creating the packet.
It returns a bytes object.
```python
    def to_byte(self):
        # initiate byte string
        string = ''
        # iterate through all fields to get values
        for field in self.fieldValues:
            string += self.fieldValues[field]

        if len(string) % 8 == 0:    # if the whole packet length in bit is divisible by 8
            return int(string, 2).to_bytes(len(string) // 8, byteorder='big')
        else:
            print('The total length of all fields in this packet are not divisible into whole bytes, please check again.')
            return None
```
<br>

#### Function: from_byte(self, packet, index)

*from_byte* takes a bytes object (section/packet) and saves the value of each field into the internal dictionary based on the internal format dictionary. 
Make sure to update the format of your packet before using this function.<br>
The argument *index* can be used to specify where in the packet the parsing should begin (counted in byte).
```python
    def from_byte(self, packet, index):
        """
            Takes a bytes object (section/packet) and save the value of each field into the internal dictionary according to the internal format dictionary

            :param packet: (Bytes) A byte string
            :param index: (int) the index of the byte from which the dictionary starts reading (index starts from 0)
            :return: None
        """
        if type(packet) == bytes and type(index) == int:
            bit_index = index * 8   # keeps track of bit index
            bitstring = self.bytes_to_bits(packet)  # the string of bits from packet
            self.fieldValues.clear()    # flush value dictionary

            # Iterate through each field and extract n = field length, number of bits until done
            for field in self.fieldLengths:
                try:
                    self.fieldValues[field] = bitstring[bit_index:bit_index+self.fieldLengths[field]]
                except IndexError:  # out of bound index
                    self.fieldValues.clear()  # flush value dictionary
                    print("ERROR: Out of bound index when accessing the packet. Make sure the format dictionary matches the format of the packet.")
                    return None
                bit_index += self.fieldLengths[field]
        else:
            print('Invalid argument type')
```
<br>

#### Function: validate_format(format_dict)
*validate_format* checks dictionary validity. The criteria for dictionary validity are:
1) Has to be a dictionary
2) Dictionary length > 0
3) No value in the dictionary < 0
Return value is boolean - true or false. True is valid.
```python
    def validate_format(format_dict):

        if isinstance(format_dict, dict) and len(format_dict) > 0:
            for field in format_dict:
                if format_dict[field] < 0:
                    print('Invalid format... Terminating process call: {}'.format(format_dict))
                    return False
        else:
            return False

        return True
```
<br>

#### Function: bytes_to_bits(packet):
*bytes_to_bits* is used to convert a bytes object to a string of binary. 
Returns the bitstring representation of the input. 
```python
    def bytes_to_bits(packet):

        bitstring = ''
        for i in range(0, len(packet)):
            bits = bin(packet[i])[2:]  # remove prefix '0b'
            bitstring += (8 - len(bits)) * '0' + bits  # add padding 0 in front to make a byte
        return bitstring
```
<br>

#### Function: check_bitstring(string):
*check_bitstring* checks if a string is in binary format (only contains 0 and/or 1). 
Input parameter is a string. True is returned if binary, false if otherwise.
```python
    def check_bitstring(string):
        
        digits = {'0', '1'}
        s = set(string)
        if s == digits or s == {'0'} or s == {'1'}:  # if only contains 0 and/or 1
            return True
        return False
```
