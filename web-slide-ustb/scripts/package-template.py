"""Create the complete share ZIP, excluding unselected source photos and QA files."""
from pathlib import Path
import hashlib
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    required = ['README.md', 'preview.png', 'template.html', 'template.pdf', '安装Skill.cmd', '导出PDF.cmd', '新国标参考文献要求.md']
    entry = root / 'SKILL.md'
    if not entry.is_file():
        entry = root / 'skill.md'
    files = [root / name for name in required] + [entry] + sorted(root.glob('*规范.pdf'))
    for folder in ('assets', 'scripts', 'references'):
        files += sorted(p for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    if any(not p.is_file() for p in files):
        raise SystemExit('Package is incomplete: generate the HTML/PDF and required assets first.')
    archive = root.parent / 'web-slide-ustb.zip'
    digests = {}
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for file in files:
            relative = 'SKILL.md' if file == entry else file.relative_to(root).as_posix()
            name = 'web-slide-ustb/' + relative
            data = file.read_bytes()
            output.writestr(name, data)
            digests[name] = hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(archive) as check:
        if check.testzip() is not None or any(hashlib.sha256(check.read(name)).hexdigest() != digest for name, digest in digests.items()):
            raise SystemExit('ZIP validation failed.')
    print(f'Verified {len(digests)} files; {archive.stat().st_size:,} bytes')
    print(archive)


if __name__ == '__main__':
    main()
