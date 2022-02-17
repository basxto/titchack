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

# 8 bit inverse
def inv8b(num):
    return 0xFF - ((num-1) & 0xFF)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", "-t", default="title", help="'title' (default), 'header' or 'both' checksums")
    parser.add_argument("--checksum", "-c", help="Target checksum (only for title checksum)")
    parser.add_argument("--offset", default="0x100", help="Offset where header begins (default: 0x100)")
    parser.add_argument("--mirror64", "-6", default="no", help="64b mirrored ROM (default: no)")
    parser.add_argument("--ambiguous", "-a", default="no", help="Set 4th char for ambiguous titles (default: no)")
    parser.add_argument("--print", "-p", default="no", help="Just print the checksums (default: no)")
    parser.add_argument("file", help="ROM file that should be fixed")
    parser.add_argument("address", help="Address of the byte that should be fixed")
    parser.add_argument("--headeraddress", "--haddr", help="Address of the header byte that should be fixed (type 'both')")
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
    # translate address alreaty
    address = (str2int(args.address) - offset) % maxa
    if args.headeraddress:
        haddress = (str2int(args.headeraddress) - offset) % maxa
    
    if args.type != "header" and not args.checksum:
        print('Title checksum needs a taget checksum')
        exit()

    # minimum/maxim wrapped address
    minwa = base % maxa
    maxwa = (base + 16) % maxa
    if args.type == "header":
        maxwa = (base + 26) % maxa
    if maxwa > minwa:
        if (address < minwa or address > maxwa):
            print('Address has to be between 0x{:04x} and 0x{:04x}'.format(offset + minwa, offset + maxwa))
            exit()
    else:
        if (address < minwa and address > maxwa):
            print('Address has to be between 0x{:04x} and 0x{:04x} or 0x{:04x} and 0x{:04x}'.format(offset, offset + maxwa, offset + minwa, offset + maxa))
            exit()
    if args.headeraddress:
        maxwa = (base + 26) % maxa
        if maxwa > minwa:
            if (haddress < minwa or haddress > maxwa):
                print('Address has to be between 0x{:04x} and 0x{:04x}'.format(offset + minwa, offset + maxwa))
                exit()
        else:
            if (haddress < minwa and haddress > maxwa):
                print('Address has to be between 0x{:04x} and 0x{:04x} or 0x{:04x} and 0x{:04x}'.format(offset, offset + maxwa, offset + minwa, offset + maxa))
                exit()

    with open(args.file, "rb+") as infp:
        # fix the fourth char of title
        if len(args.ambiguous) == 1 and args.print == "no":
            infp.seek(offset + base + 4)
            infp.write(bytes(args.ambiguous, "ascii"))

        infp.seek(offset)
        data = infp.read(maxa)
        checksum = 0
        if args.print != "no" and args.type != "title":
            print("[0x{:02x}] Header checksum byte is 0x{:02x} (-0x{:02x})".format(offset + (0x4D % maxa), data[0x4D % maxa],inv8b(data[0x4D % maxa])))
        if args.print != "no" and args.type != "header":
            if chr(data[(base + 4) % maxa]).isprintable():
                print("[0x{0:02x}] Ambiguity char is '{1:c}' (0x{1:02x})".format(offset + ((base + 4) % maxa), data[(base + 4) % maxa]))
            else:
                print("[0x{0:02x}] Ambiguity char is 0x{1:02x}".format(offset + ((base + 4) % maxa), data[(base + 4) % maxa]))

        for i in range(0, 16):
            if ((base + i) % maxa) != address:
                checksum += data[(base + i) % maxa]
        # fix title checksum
        if args.type != "header":
            checksumfix = checksum - str2int(args.checksum)
            if checksumfix < 0:
                checksumfix = 0xFF - checksumfix
            checksumfix = inv8b(checksumfix)
            if args.print == "no":
                checksum += checksumfix
                infp.seek(offset + address)
                infp.write(checksumfix.to_bytes(1, 'little'))
                print("Byte 0x{:02x} set to 0x{:02x}".format(offset + address, checksumfix))
            else:
                checksum += data[address]
                if chr(data[address]).isprintable():
                    print("[0x{0:02x}] Byte is '{1:c}' (0x{1:02x})".format(offset + address, data[address]))
                else:
                    print("[0x{0:02x}] Byte is 0x{1:02x}".format(offset + address, data[address]))
                print("Real title checksum is 0x{:02x}".format(checksum & 0xFF))
        # fix header checksum
        if args.type != "title":
            if args.type == "both" and args.headeraddress:
                address = haddress
            for i in range(16, 26):
                if ((base + i) % maxa) != address:
                    checksum += data[(base + i) % maxa]
            checksum += 25 # bootrom does checksum += data[(base + i) % maxa] + 1
            if args.print == "no":
                checksum = inv8b(checksum)
                infp.seek(offset + address)
                infp.write(checksum.to_bytes(1, 'little'))
                print("Byte 0x{:02x} set to 0x{:02x}".format(offset + address, checksum))
            else:
                checksum += data[address]
                checksum -= data[(base + 25) % maxa]
                if chr(data[address]).isprintable():
                    print("[0x{0:02x}] Byte is '{1:c}' (0x{1:02x})".format(offset + address, data[address]))
                else:
                    print("[0x{0:02x}] Byte is 0x{1:02x}".format(offset + address, data[address]))
                print("Real header checksum is 0x{:02x}".format(checksum & 0xFF))


if __name__=='__main__':
    main()
