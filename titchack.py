#!/usr/bin/env python3
"""
Previously: Title Checksum Hack
Copyright 2021-2022 Sebastian "basxto" Riedel
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", "-t", default="title", help="'title' (default) or 'header' checksum")
    parser.add_argument("--checksum", "-c", help="Target checksum (only for title checksum)")
    parser.add_argument("--offset", default="0x100", help="Offset where header begins (default: 0x100)")
    parser.add_argument("--mirror64", "-6", default="no", help="64b mirrored ROM (default: no)")
    parser.add_argument("--ambiguous", "-a", default="no", help="Set 4th char for ambiguous titles (default: no)")
    parser.add_argument("--print", "-p", default="no", help="Just print the checksums (default: no)")
    parser.add_argument("file", help="ROM file that should be fixed")
    parser.add_argument("address", help="Address of the byte that should be fixed")
    global args
    args = parser.parse_args()
    if args.type != "header" and args.print == "no":
        if not args.checksum:
            sys.stderr.write("error: 'title' type needs a checksum\n")
            sys.exit(2)

    offset = str2int(args.offset)
    maxa = 0x80 # maximum address at which to wrap
    if args.mirror64 != "no":
        maxa = 0x40
    base = 0x34 # base address for the checksum
    if args.type != "header":
        amount = 16
    else:
        amount = 26
    # translate address alreaty
    address = (str2int(args.address) - offset) % maxa

    # minimum/maxim wrapped address
    minwa = base % maxa
    maxwa = (base + amount) % maxa
    if maxwa > minwa:
        if (address < minwa or address > maxwa):
            print('Address has to be between 0x{:04x} and 0x{:04x}'.format(offset + minwa, offset + maxwa))
            exit()
    else:
        if (address < minwa and address > maxwa):
            print('Address has to be between 0x{:04x} and 0x{:04x} or 0x{:04x} and 0x{:04x}'.format(offset, offset + maxwa, offset + minwa, offset + maxa))
            exit()

    with open(args.file, "rb+") as infp:
        # fix the fourth char of title
        if len(args.ambiguous) == 1 and args.print == "no":
            infp.seek(offset + base + 4)
            infp.write(bytes(args.ambiguous, "ascii"))

        infp.seek(offset)
        data = infp.read(maxa)
        if args.type != "header" and args.print == "no":
            checksum = -str2int(args.checksum)
        else:
            checksum = 0x19
        if args.print != "no":
            checksum = data[0x4D % maxa]
            print("[0x{:02x}] Header checksum byte is 0x{:02x} (-0x{:02x})".format(offset + (0x4D % maxa), checksum,0xFF - ((checksum-1) & 0xFF)))
            if chr(data[(base + 4) % maxa]).isprintable():
                print("[0x{0:02x}] Ambiguity char is '{1:c}' (0x{1:02x})".format(offset + ((base + 4) % maxa), data[(base + 4) % maxa]))
            else:
                print("[0x{0:02x}] Ambiguity char is 0x{1:02x}".format(offset + ((base + 4) % maxa), data[(base + 4) % maxa]))
            if chr(data[address]).isprintable():
                print("[0x{0:02x}] Byte is '{1:c}' (0x{1:02x})".format(offset + address, data[address]))
            else:
                print("[0x{0:02x}] Byte is 0x{1:02x}".format(offset + address, data[address]))
            # we want to calculate the checksum, not the fix for it
            checksum = 0
            for i in range(0, 16):
                checksum += data[(base + i) % maxa]
            print("Real title checksum is 0x{:02x}".format(checksum & 0xFF))
            for i in range(16, 25):
                checksum += data[(base + i) % maxa]
            print("Real header checksum is 0x{:02x}".format((checksum+0x19) & 0xFF))
        else:
            # substract the wanted checksum from the real one
            #checksum = -checksum
            for i in range(0, amount):
                if ((base + i) % maxa) != address:
                    checksum += data[(base + i) % maxa]
            # fix up if still negative
            if checksum < 0:
                checksum = 0xFF - checksum

            # calculate the 8b inverse in two's complement
            checksum = 0xFF - ((checksum-1) & 0xFF)

            infp.seek(offset + address)
            infp.write(checksum.to_bytes(1, 'little'))

            print("Byte 0x{:02x} set to 0x{:02x}".format(offset + address, checksum))


if __name__=='__main__':
    main()
