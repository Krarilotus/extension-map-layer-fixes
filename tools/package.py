"""Build a deterministic UCP module ZIP; never include original game binaries."""
from pathlib import Path
import hashlib
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def build(destination):
    definition = (ROOT / 'definition.yml').read_text(encoding='utf-8')
    version = re.search(r'^version: (\d+\.\d+\.\d+)$', definition, re.MULTILINE)
    if not version:
        raise ValueError('Expected a semantic module version')
    name = 'map-layer-fixes-' + version.group(1)
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / (name + '.zip')
    files = [ROOT / path for path in ('definition.yml','options.yml','init.lua','README.md','CHANGELOG.md','LICENSE')]
    files += sorted((ROOT / 'code').glob('*.lua'))
    files += sorted((ROOT / 'docs').glob('*.md'))
    files += sorted((ROOT / 'locale').glob('*.md'))
    files += sorted((ROOT / 'locale').glob('*.yml'))
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for path in sorted(files):
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), (2026,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            output.writestr(info, path.read_bytes())
    with zipfile.ZipFile(archive) as check:
        assert check.testzip() is None
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (destination / 'SHA256SUMS').write_text(digest + '  ' + archive.name + '\n', encoding='ascii')
    return archive

if __name__ == '__main__':
    print(build(ROOT / 'dist'))
