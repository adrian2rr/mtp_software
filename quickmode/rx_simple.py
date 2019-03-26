from __future__ import print_function
import time
from RF24 import *

from utils.radio import configure_radios
from utils.config import get_args, process_config

irq_gpio_pin = None

########### USER CONFIGURATION ###########
# See https://github.com/TMRh20/RF24/blob/master/pyRF24/readme.md

# CE Pin, CSN Pin, SPI Speed

# Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 8Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

#RPi B
# Setup for GPIO 15 CE and CE1 CSN with SPI Speed @ 8Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

#RPi B+
# Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
#radio = RF24(RPI_BPLUS_GPIO_J8_15, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

# RPi Alternate, with SPIDEV - Note: Edit RF24/arch/BBB/spi.cpp and  set 'this->device = "/dev/spidev0.0";;' or as listed in /dev


# Setup for connected IRQ pin, GPIO 24 on RPi B+; uncomment to activate
#irq_gpio_pin = RPI_BPLUS_GPIO_J8_18
#irq_gpio_pin = 24

try:
    args = get_args()
    config = process_config(args.config)

except:
    print("missing or invalid arguments")
    exit(0)

millis = lambda: int(round(time.time() * 1000))

print('Quick Mode script! ')

print('RX Role:Pong Back, awaiting transmission')

channel_RX = 0x60
channel_TX = 0x65
payload_size = config.payload_size

radio_tx, radio_rx = configure_radios(channel_TX, channel_RX)

radio_rx.startListening()

frames = {}

last_packet = False
num_packets = 0

# forever loop
while 1:
    # Pong back role.  Receive each packet, dump it out, and send ACK
    if radio_rx.available():
        while radio_rx.available():
            #len = radio_rx.getDynamicPayloadSize()
            receive_payload = radio_rx.read(payload_size)
            print('Got payload size={} value="{}"'.format(payload_size, receive_payload.decode('utf-8')))

            # Insert the frame with its respective id
            frame_id = int(receive_payload[:7], 2)

            # if the frame is consecutive with the last one
            # if not frames
            if frame_id == 1 or frames[len(frames)-1] == frame_id - 1:
                frames.update({str(frame_id): receive_payload})
            else:
                while frames[len(frames)-1] != frame_id - 1:
                    if frames.get(str(frame_id)) is None:
                        frames.update({str(frame_id): receive_payload})
                    else:
                        frames.update({str(len(frames)+1): None})

            # sorted(frames)

            # First, stop listening so we can talk
            #radio_rx.stopListening()

            # Check if it is last packet
            if receive_payload[8] is 1:
                last_packet = True

            # If it is the last packet it sends the ack
            if not last_packet:
                # TODO: stop and wait
                pass
            else:
                # Check all packets are sent correctly
                for id_frame, value in frames:
                    if frames[id_frame] is None:
                        # if it finds some value None it asks for this packet
                        # TODO: ask for the packet missing
                        radio_tx.write("")
                        print('Some packet missing.')
                        break
                    else:
                        num_packets += 1

            if len(frames) == num_packets:
                # Send the final one back.
                radio_tx.write("ACK")
                print('Sent response.')

            # Now, resume listening so we catch the next packets.
            #radio_rx.startListening()
