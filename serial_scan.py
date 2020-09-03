#!/usr/bin/env python3
import argparse
import logging
import serial
import sys
import time

# *** Build Logger ***
logger = logging.getLogger("Scanner")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[*] - %(message)s")

fh = logging.FileHandler("scan.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.WARN)
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)

known_good = ["login", "error", "invalid", "command", "not", "found"]

class SerialClient:

    def __init__(self, DEV, BAUD, TIMEOUT=.5):
        self.dev = DEV
        self.baud = BAUD
        self.timeout = TIMEOUT

    def __connect(self):
        logger.debug(f"Testing baud rate {self.baud}")
        self.serial = serial.Serial(self.dev, self.baud, timeout=self.timeout)

    def send(self, message):
        self.__connect()
        logger.debug(f"Sending message: {message}")
        self.serial.write(message)

    def recv(self):
        data = self.serial.read(1024).decode("utf-8").split("\n")
        for line in data:
            for word in line.split(" "):
                if word in known_good:
                    logger.warn(f"Found known good clear text word: {word}")
                    logger.warn(f"Exiting...")
                    sys.exit(0)
            logger.debug(f"Received: {line}")

    def close(self):
        logger.debug(f"Closing Serial connection for baud rate: {self.baud}")
        self.serial.close()

if __name__ == "__main__":


    parser = argparse.ArgumentParser("Serial Baud Rate Scanner.")
    parser.add_argument("-d", dest="dev", default="/dev/ttyUSB0",
                        help="Set device. default=/dev/ttyUSB0")
    parser.add_argument("-v", dest="verbose", action="store_true",
                        help="Verbose mode.")

    args = parser.parse_args()

    if args.verbose:
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    for baud in range(1100, 256000, 100):
        try:
            client = SerialClient(args.dev, baud)
            client.send("test\n")
            client.recv()
            client.close()
        except Exception as error:
            logger.error("Exception raised:")
            logger.error(error)
            sys.exit(1)

