# TitCHack
Title and Header Checksum Hack for CGB in DMG mode. It’s pronouced “tight check”.

Fixes given title byte ([0x134-0x143](https://gbdev.io/pandocs/The_Cartridge_Header.html#0134-0143---title)) to match given title checksum.

Or fixes given header byte (0x134-0x14C) to match [header checksum](https://gbdev.io/pandocs/The_Cartridge_Header.html#014d---header-checksum).

# Title Checksum
Palettes can be selected with the [correct checksum](https://tcrf.net/Notes:Game_Boy_Color_Bootstrap_ROM) if [old licensee](https://gbdev.io/pandocs/The_Cartridge_Header.html#014b---old-licensee-code) is set to 1 (Nintendo) or if [new licensee](https://gbdev.io/pandocs/The_Cartridge_Header.html#0144-0145---new-licensee-code) is used and set to '01' (Nintendo). The licensee can be fixed with `--fixlicensee`.

## Example
Set palette of ROM `myrom.cgb` to "Kirby's Block Ball (USA, Europe)" (`0x27`) via title byte `0x142` and with ambiguity char `'B'`:

(This example is for standard UNIX shells. Other command line interpreters might need other kinds of quotes.)

```sh
$ ./titchack.py myrom.cgb '$142' --checksum '0x27' --ambiguous 'B' --fixlicensee yes --headeraddress '#0x14D' --type both
```

We also fixed the header checksum and the licensee byte(s) to create a working rom.

## Notice
This only changes the specified byte from the title (0x134-0x143), which makes the checksums in the header incorrect. Palettes use the title checksum, which has nothing to do with the header checksum or global checksum.

You still need to fix the header checksum with `-tboth` or `-theader`.

Some original roms had checksum collision, those are distinguished by the [4th character of the title](https://github.com/ISSOtm/gb-bootroms/blob/6232573bc6592df17cdbce878c418e79d8355b68/src/cgb.asm#L1273), which can be set with `--ambiguous`.

Be warned that [0x143](https://gbdev.io/pandocs/The_Cartridge_Header.html#0143---cgb-flag) set to the wrong number can screw up your ROM. If it enables CGB mode, predefined palettes are not used and you have to define colors yourself. If it enables PGB mode, you basically end up with a white on white palette.

# Header Checksum

You can reduce the space occupied by the header and use unused bytes for the header. Like `$144/$145`(New Licensee Code), `$14A` (Destination Code) or unused characters of the title.

## Example

(This example is for standard UNIX shells. Other command line interpreters might need other kinds of quotes.)

```sh
$ ./titchack.py -theader myrom.cgb '0447'
```

## Notice
The header checksum can’t be fixed with a title byte if you also want to hack the title checksum.
