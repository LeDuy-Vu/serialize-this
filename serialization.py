"""
    San José State University, Spring 2021
    CS 158B: Computer Network Management
    Prof. Ben Reed
    Project 1: Serialization API
    Group 7: Team Gilroy
    Authors: Le Duy Vu
             Alvin Jiang
             Muhammad Umer Sheikh
             Xochitl Medina Arreola
"""

from collections import OrderedDict


class Serializer:
    """
        This class allows users to easily encode and decode binary packets provided a format dictionary
    """

    def __init__(self, format_dict):
        """
            Serializer Constructor

            :param format_dict: user's predefined dictionary for section/packet format
        """
        # check format_dict validity
        if self.validate_format(format_dict):
            # initiate ordered dictionary for field len, the format dictionary
            self.fieldLengths = OrderedDict()
            # initiate ordered dictionary for field val, the value dictionary
            self.fieldValues = OrderedDict()

            # Insert all values from format into dictionaries
            for field in format_dict:
                # Set all field lengths to user specified lengths
                self.fieldLengths[field] = format_dict[field]

                # Set all initial field values to empty binary str with specified lengths
                self.fieldValues[field] = self.fieldLengths[field] * '0'
        else:
            print('Invalid format: {}'.format(format_dict))

    def update_format(self, format_dict):
        """
            Updates the format of the section/packet by taking in a new input dictionary of field lengths

            :param format_dict: (Dict) new format to adhere to
            :return: None
        """
        # check format_dict validity
        if self.validate_format(format_dict):
            self.fieldLengths = OrderedDict()
            for field in format_dict:
                self.fieldLengths[field] = format_dict[field]
        else:
            print('Invalid format: {}'.format(format_dict))

    def get_format(self):
        """
            Retrieves the format dictionary of the section/packet.

            :return: (Dict) the format dictionary
        """
        return self.fieldLengths

    def get_data(self):
        """
            Retrieves the field values dictionary of the section/packet.

            :return: (Dict) the data dictionary
        """
        return self.fieldValues

    def refresh_fields(self):
        """
            Flush the content of the value dictionary and generate a new one based on the format dictionary.

            :return: None
        """
        # flush old content
        self.fieldValues.clear()
        # generate new content
        for field in self.fieldLengths:
            self.fieldValues[field] = self.fieldLengths[field] * '0'

    def set_field(self, field_name, value):
        """
            Sets the VALUE of the specified FIELD_NAME if it exists

            :param field_name: (String) Name of the field being changed (case sensitive)
            :param value: (Int/Bitstring/Bytes) Value to set the field to
            :return: None
        """
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

    def get_field(self, field_name):
        """
            Retrieves the value of the specified field if it exists

            :param field_name: (String) Name of desired field (case sensitive)
            :return: (String) Value of field
        """

        # check argument validity: field_name = string
        if not isinstance(field_name, str):
            print('Invalid field_name type')
            return None

        try:
            return self.fieldValues[field_name]
        except KeyError:
            print('Field not found')
            return None

    def to_byte(self):
        """
            Concatenate the values of all fields in the dictionary into a bytes object

            :return: (Bytes) Byte string of the section/packet according to saved data and format
        """

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

    @staticmethod
    def validate_format(format_dict):
        """
            Checks dictionary validity:
            1) has to be a dictionary
            2) dictionary length > 0
            3) no value in the dictionary < 0

            :param format_dict: (Dict) input values and fields
            :return: (Bool) True if valid else False
        """

        if isinstance(format_dict, dict) and len(format_dict) > 0:
            for field in format_dict:
                if format_dict[field] < 0:
                    print('Invalid format... Terminating process call: {}'.format(format_dict))
                    return False
        else:
            return False

        return True

    @staticmethod
    def bytes_to_bits(packet):
        """
            Converts a bytes object to a string of binary

            :param packet: (Bytes) the section/packet
            :return: (str) the bitstring representation of the input
        """
        bitstring = ''
        for i in range(0, len(packet)):
            bits = bin(packet[i])[2:]  # remove prefix '0b'
            bitstring += (8 - len(bits)) * '0' + bits  # add padding 0 in front to make a byte
        return bitstring

    @staticmethod
    def check_bitstring(string):
        """
            Checks if a string is binary

            :param: (str) input string
            :return: (Bool) True if binary, otherwise False
        """
        digits = {'0', '1'}
        s = set(string)
        if s == digits or s == {'0'} or s == {'1'}:  # if only contains 0 and/or 1
            return True
        return False
