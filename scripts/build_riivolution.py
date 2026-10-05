"""Build an experimental file-replacement package from two local Wii images."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symbolic links are not supported in extracted inputs')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = {
                'size': path.stat().st_size, 'sha256': digest(path)}
    return result


def partition_root(root):
    candidates = [p.parent.parent for p in root.rglob('boot.bin')
                  if p.parent.name == 'sys' and (p.parent.parent / 'files').is_dir()]
    if len(candidates) != 1:
        raise ValueError('Expected exactly one extracted data partition with sys/boot.bin and files/')
    return candidates[0]


def prepare(source, target, wit):
    if source.is_dir():
        return partition_root(source)
    if not source.is_file():
        raise ValueError(f'Input does not exist: {source}')
    if wit is None:
        raise ValueError('Install wit on PATH or specify --wit-bin for ISO extraction')
    subprocess.run([wit, 'extract', str(source), '--dest', str(target), '--psel', 'data'], check=True)
    return partition_root(target)


def build(original, translated, output, version):
    if output.exists():
        raise ValueError('Output directory already exists; choose a new directory')
    boot = (original / 'sys/boot.bin').read_bytes()
    if len(boot) < 0x440:
        raise ValueError('Original boot.bin is truncated')
    game_id = boot[:6].decode('ascii')
    if not re.fullmatch(r'[A-Z0-9]{6}', game_id):
        raise ValueError('Invalid disc ID in original boot.bin')
    old, new = inventory(original / 'files'), inventory(translated / 'files')
    changes = []
    blockers = []
    notes = []
    for name in sorted(set(old) | set(new)):
        if old.get(name) == new.get(name):
            continue
        kind = 'removed' if name not in new else ('added' if name not in old else 'replaced')
        changes.append({'path': name, 'kind': kind, 'original': old.get(name), 'translated': new.get(name)})
        if kind == 'removed':
            blockers.append(f'File deletion requires review: {name}')
    old_sys, new_sys = inventory(original / 'sys'), inventory(translated / 'sys')
    system_changes = []
    for name in sorted(set(old_sys) | set(new_sys)):
        if old_sys.get(name) == new_sys.get(name):
            continue
        system_changes.append({'path': name, 'original': old_sys.get(name), 'translated': new_sys.get(name)})
        if name == 'fst.bin':
            notes.append('FST differences are handled through explicit file mappings, not a raw FST replacement.')
        elif name == 'boot.bin' and name in new_sys:
            after = (translated / 'sys/boot.bin').read_bytes()
            # Title and physical DOL/FST offsets are ISO metadata. Other differences need review.
            before_mask, after_mask = bytearray(boot), bytearray(after)
            for start, end in [(0x20, 0x60), (0x420, 0x430)]:
                before_mask[start:end] = b'\x00' * (end - start)
                after_mask[start:end] = b'\x00' * (end - start)
            if before_mask != after_mask:
                blockers.append('boot.bin has changes beyond the title and physical DOL/FST offsets.')
            else:
                notes.append('Disc-header title and physical DOL/FST offsets are not runtime file patches.')
        else:
            blockers.append(f'System-file change needs separate handling: sys/{name}')
    if not changes:
        blockers.append('No game-file replacements found; check that the translated input is correct.')
    report = {'version': version, 'disc_id': game_id, 'disc_number': boot[6], 'revision': boot[7],
              'status': 'blocked' if blockers else 'experimental-unplayed', 'files': changes,
              'system_changes': system_changes, 'blockers': blockers, 'notes': notes,
              'validation': 'File hashes checked; no emulator or console playback performed.'}
    output.mkdir(parents=True)
    (output / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if blockers:
        return report
    xml = ET.Element('wiidisc', version='1', root='/dq25-english')
    identity = ET.SubElement(xml, 'id', game=game_id[:3], developer=game_id[4:],
                             disc=str(boot[6]), version=str(boot[7]))
    ET.SubElement(identity, 'region', type=game_id[3])
    options = ET.SubElement(xml, 'options')
    section = ET.SubElement(options, 'section', name='Dragon Quest Collection')
    option = ET.SubElement(section, 'option', name='English translation', default='1')
    choice = ET.SubElement(option, 'choice', name=f'English {version} (experimental)')
    ET.SubElement(choice, 'patch', id='dq25_english')
    patch = ET.SubElement(xml, 'patch', id='dq25_english')
    for item in changes:
        name = item['path']
        destination = output / 'dq25-english/files' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(translated / 'files' / name, destination)
        if digest(destination) != item['translated']['sha256']:
            raise ValueError(f'Replacement copy failed verification: {name}')
        ET.SubElement(patch, 'file', disc='/' + name, external='files/' + name,
                      resize='true', create='true' if item['kind'] == 'added' else 'false')
    (output / 'riivolution').mkdir()
    ET.indent(xml, space='  ')
    ET.ElementTree(xml).write(output / 'riivolution/DQCollectionEnglish.xml', encoding='utf-8', xml_declaration=True)
    (output / 'TESTING.txt').write_text(
        'EXPERIMENTAL, NOT YET PLAYED THROUGH RIIVOLUTION\n\n'
        'Copy riivolution and dq25-english to the SD root for a real Wii.\n'
        'In Dolphin, launch the ORIGINAL game with this Riivolution XML enabled.\n'
        'Test all five game launches, warnings, SRAM, suspend/resume, HOME and return to collection.\n'
        'Keep generated replacement files local. Share build-report.json for review.\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path, help='Clean ISO or extracted data partition')
    parser.add_argument('translated', type=Path, help='Patched ISO or extracted data partition')
    parser.add_argument('output', type=Path, help='New output directory')
    parser.add_argument('--wit-bin', default='wit')
    parser.add_argument('--version', default='v0.95')
    args = parser.parse_args()
    try:
        original, translated, output = (p.resolve() for p in (args.original, args.translated, args.output))
        if output.exists():
            raise ValueError('Output directory already exists')
        for path in (original, translated):
            if path.is_dir() and (output == path or path in output.parents):
                raise ValueError('Keep output outside the extracted input directories')
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='dq25-extract-', dir=output.parent) as work:
            original_root = prepare(original, Path(work) / 'original', shutil.which(args.wit_bin))
            translated_root = prepare(translated, Path(work) / 'translated', shutil.which(args.wit_bin))
            report = build(original_root, translated_root, output, args.version)
        print(f"{report['status']}: {len(report['files'])} changed game files")
        print(f'Report: {output / "build-report.json"}')
        if report['blockers']:
            parser.exit(2, 'Separate handling is needed. No launchable XML was generated.\n')
        print('Experimental package generated. Runtime testing is still required.')
    except (OSError, ValueError, UnicodeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
