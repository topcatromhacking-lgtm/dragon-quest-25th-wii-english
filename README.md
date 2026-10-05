# Dragon Quest 25th Anniversary Collection: English Translation

An unofficial English translation project for the Nintendo Wii collection, integrating five fan-translated releases and an English collection interface.

Assembly and general translation by **TopCatHack (2026)**.

## Included translations

| Game | Translation | Credits |
| --- | --- | --- |
| Dragon Quest (NES) | Delocalized v1.19 | Translation Quest (2026) |
| Dragon Quest II (NES) | Delocalized v1.21 | Translation Quest (2026) |
| Dragon Quest III (NES) | Delocalized v1.13 | Translation Quest (2026) |
| Dragon Quest I & II (SNES) | Addendum v1.053rtm | Rod Merida (2021), original translation by RPGOne (2002) |
| Dragon Quest III (SNES) | Addendum v1.0c | Rod Merida (2022), original translation by DQTranslations (2009) |

The underlying game translations belong to their respective authors. This project adapts them to the Wii collection and translates its surrounding interface.

## Status

The development builds have been reported working across all five games, including SRAM saving/loading, controller warnings and HOME menu behavior. Release reconstruction and Riivolution compatibility need separate testing.

**The Riivolution package is in preparation. There is no ready-to-use Riivolution release yet.** The current repository contains documentation and a local xdelta reconstruction tool. The [v0.95 beta xdelta](https://github.com/topcatromhacking-lgtm/dragon-quest-25th-wii-english/releases/tag/v0.95) is available as a pre-release asset. The local converter can generate an experimental Riivolution package or a report identifying changes that need separate handling.

The interface work described in the release draft includes collection menus, emulator notices, HOME menus, extras labels, English collection logos, translation credits and subtitles for the Dragon Quest X bonus video. Original archived artwork, manuals, maps and packaging remain Japanese. The final package's coverage will be confirmed against its actual files.

## Downloads and setup

Check [Releases](https://github.com/topcatromhacking-lgtm/dragon-quest-25th-wii-english/releases) for patch downloads. A clean, matching Japanese disc image is required for xdelta reconstruction. Keep your disc image on your own computer.

The documented ISO build can be reconstructed with Python 3.9 or newer and [xdelta3](https://github.com/jmacd/xdelta/releases):

```text
python scripts/apply_xdelta.py "original.iso" "translation.xdelta" "DQ_Collection_English.iso"
```

Install xdelta3 on PATH, or add `--xdelta-bin "C:\path\to\xdelta3.exe"`. The script checks the original ISO against the documented source hash and the xdelta against GitHub's v0.95 asset digest. It prints the reconstructed ISO hash; an independently confirmed output hash can also be supplied with `--expected-output-sha256`. The old release-draft output hash is not assumed to describe v0.95. The script preserves the source and refuses to overwrite an existing output.

To generate the experimental Riivolution package from your original and patched ISO, install [Wiimms ISO Tools](https://wit.wiimm.de/) and run:

```text
python scripts/build_riivolution.py "original.iso" "DQ_Collection_English.iso" "build/riivolution-v0.95"
```

Use `--wit-bin "C:\path\to\wit.exe"` if wit is not on PATH. Extracted data-partition directories are also accepted. Keep enough disk space for both extracted data partitions and the replacement files. Send `build-report.json` for review. If unsupported system changes are found, the converter produces the report and withholds the launchable XML. A generated package still needs Dolphin and real Wii testing.

See [the Riivolution build plan](docs/RIIVOLUTION.md) for the remaining conversion and compatibility work. The rebuilt ISO is an intermediate local file, not a repository download.

## Report a bug

Open an [issue](https://github.com/topcatromhacking-lgtm/dragon-quest-25th-wii-english/issues/new/choose). Include the build, affected game or screen, steps to reproduce, console or Dolphin version, and whether you started fresh, loaded SRAM or resumed a suspend state. Screenshots are helpful.

## Credits and distribution

Collection adaptation and asset work were developed with Codex-assisted coding and editing, user review and iterative testing. The game translation credits are listed above. Original game notices are retained.

This is a free, unofficial fan translation, unaffiliated with the original rights holders. Do not upload disc images or extracted game ROMs to this repository. Release artifacts should contain patches and tools; generated replacement files can be built locally from the user's own source.
