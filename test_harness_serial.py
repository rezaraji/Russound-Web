""" Used for adhoc testing.  in time can create formal tests. """

import logging
import russound_serial
import time

CONTROLLER_COUNT=2  #how many Russound controllers are daisy chained. Russound allows max of 6

#Zone names in order (control 1 then 2, ...)
ZONE_NAMES = ['Guest Bath', 'Dining Room', 'Kitchen', 'Master Bed', 'Master Bath', 'Nick', 'Office', 'Play Room', 'Alex', 'Living Room', 'Patio', 'Pool']

SOURCE_NAMES = ['Sonos', 'Apple']   #Source names in order. Russound allows max of 6

SERIAL_PORT = '/dev/ttyUSB0'       # for RPi
#SERIAL_PORT = '/dev/tty.URT2'           # for MBP?
BAUD = 19200
logging.basicConfig(filename='russound_debugging.log', level=logging.DEBUG,
                    format='%(asctime)s:%(name)s:%(levelname)s:%(funcName)s():%(message)s')
_LOGGER = logging.getLogger(__name__)


def test1():
    zone = '1'
    print("Turn off zone", zone)
    x.set_power('1', zone, '0')
    print("Power status zone", zone, "=", x.get_power('1', zone))

    print("Turn on zone", zone)
    x.set_power('1', zone, '1')
    print("Power status zone", zone, "=", x.get_power('1', zone))

    print("Source on zone", zone, "is", x.get_source('1',zone))
    x.set_source('1', zone, '0')
    print("Source on zone", zone, "is", x.get_source('1',zone))

    print("Volume on zone", zone, "is", x.get_volume('1',zone))
    x.set_volume('1', zone, 20)
    print("Volume on zone", zone, "is", x.get_volume('1',zone))


def test2():
    """ Used this approach to determine what responses are returned from Russound """
    controller = '1'
    zone = '1'
    sequence = []
    for i in range(0,51):
        sequence.append(None)

    #sequence[5] = ('set_power_off', x.create_message("F0 @cc 00 7F 00 00 @kk 05 02 02 00 00 F1 23 00 @pr 00 @zz 00 01", controller, zone, 0))
    sequence[5] = ('get_power', x.create_send_message("F0 @cc 00 7F 00 00 @kk 01 04 02 00 @zz 06 00 00", controller, zone))
    sequence[10] = ('get_source', x.create_send_message("F0 @cc 00 7F 00 00 @kk 01 04 02 00 @zz 02 00 00", controller, zone))
    sequence[15] = ('get_source', x.create_send_message("F0 @cc 00 7F 00 00 @kk 01 04 02 00 @zz 01 00 00", controller, zone))
    #sequence[15] = ('set_power_on', x.create_message("F0 @cc 00 7F 00 00 @kk 05 02 02 00 00 F1 23 00 @pr 00 @zz 00 01", controller, zone, 1))
    #sequence[20] = ('get_power', x.create_message("F0 @cc 00 7F 00 00 @kk 01 04 02 00 @zz 06 00 00", controller, zone))
    #sequence[50] = ('get_power', x.create_message("F0 @cc 00 7F 00 00 @kk 01 04 02 00 @zz 06 00 00", controller, zone))

    t = 0
    for item in sequence:
        if item is not None:
            print(round(t, 1), item[0], "...")
            x.send_data(item[1])
        else:
            response = x.receive_data0()
            print(round(t, 1), "Receiving message...", list(response))
            print(x.get_received_messages(response))
            #if len(response) > 0:
            #    print(response)
        time.sleep(0.1)
        t += 0.1


def test3():
    """ All zones on, change sound and then all off """

    for zone in range(1, 5):
        x.set_power('1', zone, '1')
        print("Power status zone", zone, "is", x.get_power('1', zone))

    for zone in range(1,5):
        x.set_volume('1', zone, 34)
        print("Volume on zone", zone, "is", x.get_volume('1', zone))

    time.sleep(5)
    for zone in range(1, 5):
        x.set_power('1', zone, '0')


def test4():
    zone = '1'

    print("For zone 1, read power status, turn zone on and read volume and source")
    _LOGGER.debug("Zone %s power status=%s", zone, x.get_power('1', zone))
    x.set_power('1', zone, '1')
    _LOGGER.debug("Zone %s power status=%s", zone, x.get_power('1', zone))
    _LOGGER.debug("Zone %s source=%s", zone, x.get_source('1',zone))
    _LOGGER.debug("Zone %s volume=%s", zone, x.get_volume('1',zone))

    print("Set volume to 35 and source to 2nd source")
    x.set_volume('1', zone, 35)
    x.set_source('1', zone, 1)

    print("Read the source and volume levels from the controller")
    _LOGGER.debug("Zone %s source=%s", zone, x.get_source('1',zone))
    _LOGGER.debug("Zone %s volume=%s", zone, x.get_volume('1',zone))

    time.sleep(2)
    x.set_power('1', zone, '0')
    _LOGGER.debug("Zone %s source=%s", zone, x.get_source('1',zone))


def all_on():     #All zones ON
    for controller in range(1, CONTROLLER_COUNT+1):
        for zone in range(1, 7):
            x.set_power(controller, zone, '1')
            print(controller, zone)


def all_off():   #All zones OFF
    for controller in range(1, CONTROLLER_COUNT+1):
        for zone in range(1, 7):
            x.set_power(controller, zone, '0')
            print(controller, zone)


def controller_ID (zone_name):  #return the controller ID string based on the name of the zone (returns a number between 1-6)
    return str(int((ZONE_NAMES.index(zone_name)/6)+1))


def zone_ID(zone_name):         #return the zone ID string based on the name of the zone (returns a number between 1-6)
    return str((ZONE_NAMES.index(zone_name)%6)+1)


def source_ID(source_name):     #return the source ID string based on the name of the zone (returns a number between 1-6)
    return str(SOURCE_NAMES.index(source_name))


def print_all_zones():
    # Print all the Zone names with their control and zone IDs
    for x in range(len(ZONE_NAMES)):
        print(ZONE_NAMES[x], controller_ID(ZONE_NAMES[x]), zone_ID(ZONE_NAMES[x]))
    for x in range(len(SOURCE_NAMES)):
        print(SOURCE_NAMES[x], int(source_ID(SOURCE_NAMES[x])) + 1)



x = russound_serial.Russound(SERIAL_PORT, BAUD)

print_all_zones()

#x.set_power(controller_ID('Office'), zone_ID('Office'), '1')
#x.set_volume(controller_ID('Office'), zone_ID('Office'), 30)
#x.set_source(controller_ID('Office'), zone_ID('Office'), source_ID('Sonos'))

#time.sleep(1)

#x.set_power(controller_ID('Patio'), zone_ID('Patio'), '1')
#x.set_volume(controller_ID('Patio'), zone_ID('Patio'), 50)
#x.set_source(controller_ID('Patio'), zone_ID('Patio'), source_ID('Sonos'))

"""
print(x.get_zone_info(1, 1, 4))
print(x.get_zone_info(1, 2, 4))
print(x.get_zone_info(1, 3, 4))
print(x.get_zone_info(1, 4, 4))
print(x.get_zone_info(1, 5, 4))
print(x.get_zone_info(1, 6, 4))
print(x.get_zone_info(2, 1, 4))
print(x.get_zone_info(2, 2, 4))
print(x.get_zone_info(2, 3, 4))
print(x.get_zone_info(2, 4, 4))
print(x.get_zone_info(2, 5, 4))
print(x.get_zone_info(2, 6, 4))
"""