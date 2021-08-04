# TitCHack
Title Checksum Hack for CGB in DMG mode.

Fixes given header byte to match given checksum.

Palettes can be seletced with the [correct checksum](https://tcrf.net/Notes:Game_Boy_Color_Bootstrap_ROM) if licensee is set to 1 (Nintendo).

## Example
Set palette of ROM `myrom.cgb` to "Link's Awakening" (`0x70`) via title byte `0x142`:

```sh
./titchack.py myrom.cgb '$142' '0x70'
```
## Notice
This only changes the specified byte from the title (0x134-0x143), which makes the checksums in the header incorrect. Palettes use the title checksum, which has nothing to do with the header checksum or global checksum.

You still need to run `rgbfix -f h` (only header, will boot) or `rgbfix -f hg` (header and global) to fix those.

Some original roms had checksums collision, those are distinguished by the 4th character of the title, which has to be set beforehand.
