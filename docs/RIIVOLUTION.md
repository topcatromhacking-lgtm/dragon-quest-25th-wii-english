# Riivolution conversion

Status: preparation, pending the current xdelta and a comparison of the reconstructed game files. This document describes the intended workflow, not a tested patch.

## Local reconstruction

Apply the release xdelta to the matching original ISO with `scripts/apply_xdelta.py`. Extract the original and reconstructed game partitions locally, preserving their internal paths. Compare file hashes to identify changed and added files. Disc header and partition metadata changes must be assessed separately from ordinary game files.

The source metadata below comes from the existing release draft. It must be reconciled with the uploaded xdelta before release:

| Image | Size in bytes | SHA-256 |
| --- | ---: | --- |
| Original Japanese ISO | 4699979776 | 35f1f53687c4976fb80ca087133dcbaae426bf4fad1f5163426f7e890454876c |
| Documented English ISO | 4699979776 | 44027eec9ebd2ad6b421dbf30406991e03da3f5d480462442e8b6dc6554a6ea2 |

Read the disc ID, revision and disc number from the source image. Do not substitute an embedded Virtual Console game ID for the collection's disc ID.

## XML and replacement files

Riivolution uses an XML in `/riivolution/` to match a disc, expose selectable options and map external files to disc paths. File replacements can change file size. The generated package should use explicit mappings for each changed file so every replacement can be reviewed.

The planned layout is `/riivolution/DQCollectionEnglish.xml` alongside `/dq25-english/files/`, with original internal paths preserved under the latter. The XML will contain the confirmed disc identity and one English translation option. This layout is a proposal; no functional XML is committed until the mappings are known.

Collection resources, emulator executables, embedded game payloads, startup notices and HOME resources must be accounted for together. Executables stored as ordinary disc files and loaded later may be candidates for file replacement, but their launch behavior must be tested. Changes to the initial main DOL require separate investigation and may need memory patches. An ISO's translated disc header does not automatically become a runtime Riivolution change.

No save redirection is planned by default. Preserve and test the collection's established save behavior.

Format reference: [Riivolution Patch Format](https://riivolution.github.io/wiki/Patch_Format/).

## Validation before release

Compare every generated replacement with the reconstructed ISO and confirm that all changed resources are covered. Launch the original game with the XML in Dolphin, then check the collection interface and all five game launches, controller warnings, SRAM saving/loading, suspend/resume, HOME and return-to-collection behavior. Confirm English menus, credits and video changes against the ISO build.

Test real Wii Riivolution separately, especially the transitions into the embedded emulators. Report Dolphin and real-console results independently. Successful ISO tests do not establish Riivolution compatibility.

## Release packaging

Keep the original ISO, reconstructed ISO and extracted ROMs local. Attach the xdelta, verified metadata and reconstruction tools to a release. A local generator can produce the Riivolution replacement files from that reconstruction. Publish a direct replacement-file package only after its contents and distribution approach have been reviewed.
