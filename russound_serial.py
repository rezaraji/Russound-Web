"""
Russound RNT serial interface (used by models CAS44, CAA66, CAM6.6, CAV6.6)

Heavily modified by Reza Raji to work with the serial port instead on IP gateway
Based on code from Neil Lathwood <https://github.com/laf/ http://www.lathwood.co.uk/>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.  Please see LICENSE.txt at the top level of
the source code distribution for details.

The Russound RNET protocol is documented in cav6.6_rnet_protocol_v1.01.00.pdf, and russound-rs-232-V01_00_01.pdf
which are stored in the source code repo.
"""

import logging
import time
import threading
import serial

_LOGGER = logging.getLogger(__name__)
# Recommendation is that this should be at least 100ms delay to ensure subsequent commands
# are processed correctly (pg 35 on russound-rs-232-V01_00_01.pdf).
COMMAND_DELAY = 0.1
KEYPAD_CODE = '70'  # For an external system this is the required value (pg 28 of cav6.6_rnet_protocol_v1.01.00.pdf)


class Russound:
    """ Implements a python API for selected commands to the Russound system using the RNET protocol.
    The class is designed to maintain a connection to the Russound controller, and reads the controller state
    directly from using RNET"""

    _sem_comm = 0

    def __init__(self, port, baud):
        """ Initialise Russound class """

        self.ser = serial.Serial(port=port, baudrate=baud, timeout=1)

        self._last_send = time.time()  # Use this to keep track of when the last send command was sent
        self.lock = threading.Lock()   # Used to ensure only one thread sends commands to the Russound

    def set_power(self, controller, zone, power):
        """ Switch power on/off to a zone
        :param controller: Russound Controller ID. For systems with one controller this should be a value of 1.
        :param zone: The zone to be controlled. Expect a 1 based number.
        :param power: 0 = off, 1 = on
        """
        send_msg = self.create_send_message("F0 @cc 00 7F 00 00 @kk 05 02 02 00 00 F1 23 00 @pr 00 @zz 00 01",
                                            controller, zone, power)
        self.send_data(send_msg)
        self.get_response_message()  # Clear response buffer

    def set_volume(self, controller, zone, volume):
        """ Set volume for zone to specific value.
        Divide the volume by 2 to translate to a range (0..50) as expected by Russound (Even thought the
        keypads show 0..100).
        """
        send_msg = self.create_send_message("F0 @cc 00 7F 00 00 @kk 05 02 02 00 00 F1 21 00 @pr 00 @zz 00 01",
                                            controller, zone, volume // 2)

        self.send_data(send_msg)
        self.get_response_message()  # Clear response buffer
        """
        try:
            self.lock.acquire()
            #_LOGGER.debug('Zone %s - acquired lock for ', zone)
            self.send_data(send_msg)
            #_LOGGER.debug("Zone %s - sent message %s", zone, send_msg)
            self.get_response_message()  # Clear response buffer
        finally:
            self.lock.release()
            #_LOGGER.debug("Zone %s - released lock for ", zone)
            #_LOGGER.debug("End - controller %s, zone %s, volume set to %s.\n", controller, zone, volume)
        """

    def set_source(self, controller, zone, source):
        """ Set source for a zone - 0 based value for source """

        _LOGGER.info("Begin - controller= %s, zone= %s change source to %s.", controller, zone, source)
        send_msg = self.create_send_message("F0 @cc 00 7F 00 @zz @kk 05 02 00 00 00 F1 3E 00 00 00 @pr 00 01",
                                            controller, zone, source)

        self.send_data(send_msg)
        self.get_response_message()  # Clear response buffer
        """
        try:
            self.lock.acquire()
            _LOGGER.debug('Zone %s - acquired lock for ', zone)
            self.send_data(send_msg)
            _LOGGER.debug("Zone %s - sent message %s", zone, send_msg)
            # Clear response buffer in case there is any response data(ensures correct results on future reads)
            self.get_response_message()
        finally:
            self.lock.release()
            _LOGGER.debug("Zone %s - released lock for ", zone)
            _LOGGER.debug("End - controller= %s, zone= %s source set to %s.\n", controller, zone, source)
        """

    def all_on_off(self, power):
        """ Turn all zones on or off
        Note that the all on function is not supported by the Russound CAA66, although it does support the all off.
        On and off are supported by the CAV6.6.
        Note: Not tested (acambitsis)
        """

        send_msg = self.create_send_message("F0 7F 00 7F 00 00 @kk 05 02 02 00 00 F1 22 00 00 @pr 00 00 01",
                                            None, None, power)
        self.send_data(send_msg)
        self.get_response_message()  # Clear response buffer

    def toggle_mute(self, controller, zone):
        """ Toggle mute on/off for a zone
        Note: Not tested (acambitsis) """

        send_msg = self.create_send_message("F0 @cc 00 7F 00 @zz @kk 05 02 02 00 00 F1 40 00 00 00 0D 00 01",
                                            controller, zone)
        self.send_data(send_msg)
        self.get_response_message()  # Clear response buffer

    def get_zone_info(self, controller, zone, return_variable):
        """ Get all relevant info for the zone
            When called with return_variable == 4, then the function returns a list with current
             volume, source and ON/OFF status.
            When called with 0, 1 or 2, it will return an integer with the Power, Source or Volume """

        # Define the signature for a response message, used later to find the correct response from the controller.
        # FF is the hex we use to signify bytes that need to be ignored when comparing to response message.
        # resp_msg_signature = self.create_response_signature("04 02 00 @zz 07 00 00 01 00 0C", zone)

        # _LOGGER.debug("Begin - controller= %s, zone= %s, get status", controller, zone)
        resp_msg_signature = self.create_response_signature("04 02 00 @zz 07", zone)
        send_msg = self.create_send_message("F0 @cc 00 7F 00 00 @kk 01 04 02 00 @zz 07 00 00", controller, zone)
        try:
            #self.lock.acquire()
            #_LOGGER.debug('Acquired lock for zone %s', zone)
            self.send_data(send_msg)
            #_LOGGER.debug("Zone: %s Sent: %s", zone, send_msg)
            # Expected response is as per pg 23 of cav6.6_rnet_protocol_v1.01.00.pdf
            matching_message = self.get_response_message(resp_msg_signature)
            if matching_message is not None:
                # Offset of 11 is the position of return data payload is that we require for the signature we are using.
                #_LOGGER.debug("matching message to use= %s", matching_message)
                #_LOGGER.debug("matching message length= %s", len(matching_message))
                if return_variable == 4:
                    return_value = [matching_message[11], matching_message[12], matching_message[13]]
                else:
                    return_value = matching_message[return_variable + 11]
            else:
                return_value = None
                #_LOGGER.warning("Did not receive expected Russound power state for controller %s and zone %s.", controller, zone)
        finally:
            #self.lock.release()
            #_LOGGER.debug("Released lock for zone %s", zone)
            #_LOGGER.debug("End - controller= %s, zone= %s, get status \n", controller, zone)
            return return_value

    def get_power(self, controller, zone):
        """ Gets the power status as a 0 or 1 which is located on a 0 byte offset """
        return self.get_zone_info(controller, zone, 0)

    def get_source(self, controller, zone):
        """ Gets the selected source as a 0 based index - it is located on a 1 byte offset """
        return self.get_zone_info(controller, zone, 1)

    def get_volume(self, controller, zone):
        """ Gets the volume level which needs to be doubled to get it to the range of 0..100 -
        it is located on a 2 byte offset """
        volume_level = self.get_zone_info(controller, zone, 2)
        if volume_level is not None:
            volume_level *= 2
        return volume_level

    def create_send_message(self, string_message, controller, zone=None, parameter=None):
        """ Creates a message from a string, substituting the necessary parameters,
        that is ready to send to the socket """

        if controller is not None:
            cc = hex(int(controller) - 1).replace('0x', '')  # RNET requires controller value to be zero based
        else:
            cc = ''
        if zone is not None:
            zz = hex(int(zone) - 1).replace('0x', '')  # RNET requires zone value to be zero based
        else:
            zz = ''
        if parameter is not None:
            pr = hex(int(parameter)).replace('0x', '')
        else:
            pr = ''

        string_message = string_message.replace('@cc', cc)  # Replace controller parameter
        string_message = string_message.replace('@zz', zz)  # Replace zone parameter
        string_message = string_message.replace('@kk', KEYPAD_CODE)  # Replace keypad parameter
        string_message = string_message.replace('@pr', pr)  # Replace specific parameter to message

        # Split message into an array for each "byte" and add the checksum and end of message bytes
        send_msg = string_message.split()
        send_msg = self.calc_checksum(send_msg)
        return send_msg

    def create_response_signature(self, string_message, zone):
        """ Basic helper function to keep code clean for defining a response message signature """

        zz = ''
        if zone is not None:
            zz = hex(int(zone)-1).replace('0x', '')  # RNET requires zone value to be zero based
        string_message = string_message.replace('@zz', zz)  # Replace zone parameter
        return string_message

    def send_data(self, data, delay=COMMAND_DELAY):
        """ Send data to Russound controller """

        time_since_last_send = time.time() - self._last_send
        delay = max(0, delay - time_since_last_send)
        time.sleep(delay)  # Ensure minim recommended delay since last send

        for item in data:
            data = bytes.fromhex(str(item.zfill(2)))
            self.ser.write(data)
            #print(data)
        self._last_send = time.time()

    def get_response_message(self, resp_msg_signature=None, delay=COMMAND_DELAY):
        """ Receive data from connected gateway and if required seach and return a stream that starts at the required
        response message signature.  The reason we couple the search for the response signature here is that given the
        RNET protocol and TCP comms, we don't have an easy way of knowing that we have received the response.  We want to
        minimise the time spent reading the socket (to reduce user lag), hence we use the message response signature
        at this point to determine when to stop reading."""

        matching_message = None  # Set intial value to none (assume no response found)
        if resp_msg_signature is None:
            no_of_socket_reads = 1  # If we are not looking for a specific response do a single read to clear the buffer
        else:
            no_of_socket_reads = 20 # Try 20x (= approx 2s at default)if we are looking for a specific response

        time.sleep(delay)  # Insert recommended delay to ensure command is processed correctly

        data = B''
        for i in range(0, no_of_socket_reads):
            data += self.ser.read(512)
            if resp_msg_signature is not None:  # If we are looking for a specific response
                matching_message, data = self.find_signature(data, resp_msg_signature)
            if matching_message is not None:  # Required response found
                break
            time.sleep(delay)  # Wait before reading again - default of 100ms

        return matching_message

    def find_signature(self, data_stream, msg_signature):
        """ Takes the stream of bytes received and looks for a message that matches the signature
        of the expected response """

        signature_match_index = None  # The message that will be returned if it matches the signature
        msg_signature = msg_signature.split()  # Split into list
        # convert to bytearray in order to be able to compare with the messages list which contains bytearrays
        msg_signature = bytearray(int(x, 16) for x in msg_signature)
        # loop through each message returned from Russound
        index_of_last_f7 = None
        for i in range(len(data_stream)):
            if data_stream[i] == 247:
                index_of_last_f7 = i
            # the below line checks for the matching signature, ensuring ALL bytes of the response have been received
            if (data_stream[i:i + len(msg_signature)] == msg_signature) and (len(data_stream) - i >= 24):
                signature_match_index = i
                break
        if signature_match_index is None:
            # Scrap bytes up to end of msg (to avoid searching these again)
            data_stream = data_stream[index_of_last_f7:len(data_stream)]
            matching_message = None
        else:
            matching_message = data_stream[signature_match_index:len(data_stream)]

        _LOGGER.debug("Message signature found at location: %s", signature_match_index)
        return matching_message, data_stream

    def calc_checksum(self, data):
        """ Calculate the checksum we need """

        output = 0
        length = len(data)
        for value in data:
            output += int(value, 16)

        output += length
        checksum = hex(output & int('0x007F', 16)).lstrip("0x")
        data.append(checksum)
        data.append('F7')
        return data
