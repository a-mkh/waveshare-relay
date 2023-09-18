#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# https://www.waveshare.com/wiki/Modbus_POE_ETH_Relay

import socket
import logging
import argparse
import json

COM_ON = 0xFF
COM_OFF = 0
COM_FLIP = 0x55

COM_FLASH_ON = 0x02
COM_FLASH_OFF = 0x04

# Table of CRC values for high–order byte
CRCTableHigh = [
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
    0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40
]

# Table of CRC values for low–order byte
CRCTableLow = [
    0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
    0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
    0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
    0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
    0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7,
    0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
    0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
    0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
    0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
    0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
    0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
    0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
    0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
    0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
    0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
    0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
    0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
    0x40
]


def ModbusCRC(data):
    crcHigh, crcLow = 0xff, 0xff
    for byte in data:
        index = crcLow ^ byte
        crcLow = crcHigh ^ CRCTableHigh[index]
        crcHigh = CRCTableLow[index]
    return (crcHigh << 8 | crcLow)


def sign_cmd(cmd):
    crc = ModbusCRC(cmd[0:6])
    cmd[6] = crc & 0xFF
    cmd[7] = crc >> 8
    return cmd


def relay_cmd(n, command) -> bytearray:
    cmd = [0] * 8
    cmd[0] = 0x01  # Device address
    cmd[1] = 0x05  # command
    cmd[2] = 0
    cmd[3] = n
    cmd[4] = command
    cmd[5] = 0
    return bytearray(sign_cmd(cmd))


def relay_flash_cmd(n, command, duration) -> bytearray:
    cmd = [0] * 8
    cmd[0] = 0x01  # Device address
    cmd[1] = 0x05  # command
    cmd[2] = command
    cmd[3] = n
    # cmd[4] = 0
    # cmd[5] = duration
    cmd[4:6] = duration.to_bytes(2, byteorder='big')
    return bytearray(sign_cmd(cmd))


def state_cmd() -> bytearray:
    cmd = [0] * 8
    cmd[0] = 0x01  # Device address
    cmd[1] = 0x01  # command
    cmd[2] = 0
    cmd[3] = 0
    cmd[4] = 0
    cmd[5] = 0x08
    return bytearray(sign_cmd(cmd))


def send_cmd(s: socket.socket, cmd: bytearray):
    cmd_hex = ' '.join(f'{byte:02x}' for byte in cmd)
    logging.debug(f">>>: {cmd_hex}")
    s.sendall(cmd)
    response = s.recv(1024)
    response_hex = ' '.join(f'{byte:02x}' for byte in response)
    logging.debug(f"<<<: {response_hex}")
    return response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="192.168.1.44", help="Relay host IP address.")
    parser.add_argument("--port", type=int, default=4196, help="Port number.")
    parser.add_argument("--loglevel", default="INFO", help="Log level.")

    subparsers = parser.add_subparsers(dest="command")

    relay_parser = subparsers.add_parser("relay")
    relay_parser.add_argument("number", type=int, choices=list(range(1, 9)) + [256], help="Relay number 1-8, "
                                                                                          "256 for all relays.")
    relay_parser.add_argument("action", choices=["on", "off", "flip"], help="Relay action.")

    flash_parser = subparsers.add_parser("flash")
    flash_parser.add_argument("number", type=int, choices=list(range(1, 9)), help="Relay number 1-8.")
    flash_parser.add_argument("action", choices=["on", "off"], help="Flash action.")

    def duration_type(value):
        ivalue = int(value)
        if ivalue < 1 or ivalue > 65535:
            raise argparse.ArgumentTypeError("Duration must be between 1 and 65535")
        return ivalue

    flash_parser.add_argument("duration", type=duration_type,
                              help="Duration of the flash action in 100ms increments. `10` equals 1 second. (1-65535)")

    state_parser = subparsers.add_parser("state")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    logging.basicConfig(level=getattr(logging, args.loglevel.upper()))
    logging.debug(f"Args received: {args}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))

        if args.command == "state":
            response = send_cmd(s, state_cmd())
            relay_state_byte = response[3]
            relay_states = [(relay_state_byte & (1 << i)) != 0 for i in range(8)]
            print(json.dumps(relay_states))

        elif args.command == "relay":
            coms = {
                'on': COM_ON,
                'off': COM_OFF,
                'flip': COM_FLIP
            }
            send_cmd(s, relay_cmd(args.number - 1, coms.get(args.action)))

        elif args.command == "flash":
            coms = {
                'on': COM_FLASH_ON,
                'off': COM_FLASH_OFF,
            }
            send_cmd(s, relay_flash_cmd(args.number - 1, coms.get(args.action), args.duration))


if __name__ == "__main__":
    main()