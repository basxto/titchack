# TitCHack
Title and Header Checksum Hack for CGB in DMG mode. It’s pronouced “tight check”.

Fixes given header byte ([0x134-0x143](https://gbdev.io/pandocs/The_Cartridge_Header.html#0134-0143---title)) to match given title checksum.

Or fixes given header byte (0x134-0x14C) to match [header checksum](https://gbdev.io/pandocs/The_Cartridge_Header.html#014d---header-checksum).

# Title Checksum
Palettes can be seletced with the [correct checksum](https://tcrf.net/Notes:Game_Boy_Color_Bootstrap_ROM) if [old licensee](https://gbdev.io/pandocs/The_Cartridge_Header.html#014b---old-licensee-code) is set to 1 (Nintendo).

## Example
Set palette of ROM `myrom.cgb` to "Link's Awakening" (`0x70`) via title byte `0x142`:

```sh
rgbfix -l 1 myrom.cgb
./titchack.py myrom.cgb '$142' -c'0x70'
rgbfix -f h myrom.cgb
```

The makebin equivalent to [`rgbfix -l 1`](https://rgbds.gbdev.io/docs/v0.5.1/rgbfix.1#l_2) would be `makebin -Z -yl 1` (`-Wm-yl` if wrapped through lcc)
## Notice
This only changes the specified byte from the title (0x134-0x143), which makes the checksums in the header incorrect. Palettes use the title checksum, which has nothing to do with the header checksum or global checksum.

You still need to run [`rgbfix -f h`](https://rgbds.gbdev.io/docs/v0.5.1/rgbfix.1#f) (only header, will boot) or `rgbfix -f hg` (header and global) to fix those. Or perform a header checksum hack with another run.

Some original roms had checksum collision, those are distinguished by the [4th character of the title](https://github.com/ISSOtm/gb-bootroms/blob/6232573bc6592df17cdbce878c418e79d8355b68/src/cgb.asm#L1273), which has to be set beforehand.

Be warned that [0x143](https://gbdev.io/pandocs/The_Cartridge_Header.html#0143---cgb-flag) set to the wrong number can screw up your ROM. If it enables CGB mode, predefined palettes are not used and you have to define colors yourself. If it enables PGB mode, you basically end up with a white on white palette.

# Header Checksum

You can reduce the space occupied by the header and use unused bytes for the header. Like `$144/$145`(New Licensee Code), `$14A` (Destination Code) or unused characters of the title.

## Example

```sh
./titchack.py -theader myrom.cgb '#0x13F'
```

## Notice
The header checksum can’t be fixed with a title byte if you also want to hack the title checksum.