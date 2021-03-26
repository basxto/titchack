#!/usr/bin/env python
"""
Title Checksum Hack
Copyright 2021 Sebastian "basxto" Riedel
[License: MIT]

Fixes the title to match the given checksum
"""
import sys
import argparse


# convert str to integer and accept rgbds syntax
def str2int(x):
    y = 0
    x = x.replace('$', "0x", 1).replace('%', "0b", 1).replace('&', "0", 1).replace('#0', "0", 1).lower()
    if (x[0] == '0' and x[1] == 'x'):
        y = int(x, base=16)
    elif (x[0] == '0' and x[1] == 'b'):
        y = int(x, base=2)
    elif (x[0] == '0'):
        y = int(x, base=8)
    else:
        y = int(x, base=10)
    return y

def parse_argv(argv):
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("address")
    p.add_argument("checksum")
    return p.parse_args(argv[1:])

def main(argv=None):
    args = parse_argv(argv or sys.argv)
    address = str2int(args.address)
    checksum = str2int(args.checksum)

    if (address < 0x134 or address > 0x143):
        print('Address has to be between 0x134 and 0x143')
        exit()

    with open(args.file, "rb+") as infp:
        infp.seek(0x134)
        data = infp.read(25)

        # substract the wanted checksum from the real one
        checksum = -checksum
        for i in range(0, 16):
            if (0x134+i) != address:
                checksum += data[i]
        # fix up if still negative
        if checksum < 0:
            checksum = 0xFF - checksum

        # calculate the 8b inverse in two's complement
        checksum = 0xFF - ((checksum-1) & 0xFF)

        infp.seek(address)
        infp.write(checksum.to_bytes(1, 'little'))

    print("Byte 0x{:02x} set to 0x{:02x}".format(address, checksum))


if __name__=='__main__':
    main()