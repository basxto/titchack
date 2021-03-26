# TitCHack
Title Checksum Hack for CGB in DMG mode.

Fixes given header byte to match given checksum.

Palettes can be seletced with the [correct checksum](https://tcrf.net/Notes:Game_Boy_Color_Bootstrap_ROM) if licensee is set to 1 (Nintendo).

## Example
Set palette of ROM `myrom.cgb` to "Link's Awakening" (`0x70`) via title byte `0x142`:

```sh
./titchack.py myrom.cgb '$142' '0x70'
```
