# Riivolution conversion

Status: v0.95 xdelta uploaded; comparison and runtime testing still pending. A local experimental converter is available in `scripts/build_riivolution.py`. This document describes the intended workflow, not a tested patch.

## Local reconstruction

Apply the release xdelta to the matching original ISO with `scripts/apply_xdelta.py`. Extract the original and reconstructed game partitions locally, preserving their internal paths. Compare file hashes to identify changed and added files. Disc header and partition metadata changes must be assessed separately from ordinary game files.

The source metadata below comes from the existing release draft. The original source hash is used by the patcher. The older draft's output hash has not been confirmed for v0.95:

| Image | Size in bytes | SHA-256 |
| --- | ---: | --- |
| Original Japanese ISO | 4699979776 | 35f1f53687c4976fb80ca087133dcbaae426bf4fad1f5163426f7e890454876c |
| Documented English ISO | 4699979776 | 44027eec9ebd2ad6b421dbf30406991e03da3f5d480462442e8b6dc6554a6ea2 |

Read the disc ID, revision and disc number from the source image. Do not substitute an embedded Virtual Console game ID for the collection's disc ID.

## XML and replacement files

Riivolution uses an XML in `/riivolution/` to match a disc, expose selectable options and map external files to disc paths. File replacements can change file size. The generated package should use explicit mappings for each changed file so every replacement can be reviewed.

The planned layout is `/riivolution/DQCollectionEnglish.xml` alongside `/dq25-english/files/`, with original internal paths preserved under the latter. The converter reads the original disc identity and generates one English option with explicit file mappings. Generated XML and replacement files stay local and are excluded from the source repository.

Collection resources, emulator executables, embedded game payloads, startup notices and HOME resources must be accounted for together. Executables stored as ordinary disc files and loaded later may be candidates for file replacement, but their launch behavior must be tested. For an initial main DOL with an unchanged loading header and size, the converter maps loaded-section differences into checked memory writes. It verifies that these writes reconstruct the translated executable exactly. Header, layout or non-loaded-byte changes remain blocked. An ISO's translated disc header does not automatically become a runtime Riivolution change.

No save redirection is planned by default. Preserve and test the collection's established save behavior.

Format reference: [Riivolution Patch Format](https://riivolution.github.io/wiki/Patch_Format/).

## Validation before release

Compare every generated replacement with the reconstructed ISO and confirm that all changed resources are covered. Launch the original game with the XML in Dolphin, then check the collection interface and all five game launches, controller warnings, SRAM saving/loading, suspend/resume, HOME and return-to-collection behavior. Confirm English menus, credits and video changes against the ISO build.

Test real Wii Riivolution separately, especially the transitions into the embedded emulators. Report Dolphin and real-console results independently. Successful ISO tests do not establish Riivolution compatibility.

## Release packaging

Keep the original ISO, reconstructed ISO and extracted ROMs local. Attach the xdelta, verified metadata and reconstruction tools to a release. A local generator can produce the Riivolution replacement files from that reconstruction. Publish a direct replacement-file package only after its contents and distribution approach have been reviewed.

## v0.95 release input

Patch asset: `Dragon.Quest.I-II-III.25th.Anniversary.Collection.v0.95.ENG-TopCatHack.xdelta`.

Size: 849667870 bytes. SHA-256 from GitHub release metadata: `10092bad614eb40382d14f0b8fb378489ab1e6fa58207c86b4722169e5d254f0`. This identifies the uploaded patch; it is not a playback validation or a reconstructed-ISO hash.

The converter supports changed and added ordinary files. Unreviewed file deletions, unsupported main-DOL changes, apploader or other unsupported system changes block XML generation and are listed in `build-report.json`. Disc-title and physical DOL/FST offset changes are documented as ISO metadata. It preserves save behavior without adding save redirection.

## Executable review of v0.95

The uploaded diagnostic executables match the main-DOL hashes in the build report. The collection disc ID is `S25JGD`, disc 0, revision 0. The main DOL has an identical loading header and length, with 738 changed bytes. Seven generated memory writes, including original-byte checks, reproduce the translated executable byte for byte. This is a structural check, not a runtime test.

Both reviewed SNES emulator executables now contain `/%s.rom` and `/%s.pcm` instead of the original `/LZH8%s.rom` and `/LZH8%s.pcm` filename formats. Their replacement ROM/audio files are added under the new names. The four obsolete compressed assets remain on the original disc, with no mapping applied. This exception requires the exact reviewed translated emulator hashes and the corresponding new files; arbitrary deletions remain blocked. Normal playback must still confirm that these legacy assets are unused.

The report lists 141 changed game-file entries: four obsolete assets can be retained and 137 entries need file mappings. The five replacement emulator DOLs are ordinary game-file mappings. The initial collection DOL uses the seven memory writes.

Local verification applied the seven writes to the actual original main DOL and compared the complete result with the actual translated main DOL. Package tests combined those actual executables with small asset fixtures to check retained assets and XML generation. Changed-header and unreviewed-deletion cases were also checked. The full replacement assets remain on the user's computer; the full generated package and runtime behavior are not yet verified.
