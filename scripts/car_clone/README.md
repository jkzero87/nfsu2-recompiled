# Car clone scripts

Some NFSU2 copies list cars in `GLOBAL/GlobalB.lzc` (for example `CIVIC` and `RSX`) whose `CARS/<NAME>` folder is missing; the game then waits forever on the loading screen when it picks one. These scripts build a stand-in folder from a car you have. They read and write only your own game files; none are included here.

The game looks up each solid by the bStringHash (`x = 0xFFFFFFFF; x = x*33 + c`) of `<CAR>_<PART>`, stored 148 bytes before the name, and through a hash index at 0xB8 sorted ascending.

1. Copy `CARS/<DONOR>/GEOMETRY.BIN` and a few short-named cars (`TT`, `A3`, `RX7`, `RX8`) as `geo_<CAR>.bin` into one folder.
2. `python resolve_tails.py geo_PEUGOT106.bin PEUGOT106 tails.json` recovers truncated names.
3. `python rename_car.py geo_PEUGOT106.bin PEUGOT106 CIVIC civic_GEOMETRY.bin tails.json` renames solids and hashes.
4. `python sort_index.py geo_PEUGOT106.bin civic_GEOMETRY.bin` re-sorts the index; without it most parts are invisible.
5. Put the result in `CARS/CIVIC/GEOMETRY.BIN` and copy the donor's `TEXTURES.BIN` and `VINYLS.BIN` next to it.

A few long decal solids (`WIDE*_DECAL_*`) may stay unresolved; they only show with those vinyls.
