"""UTF-8 serialization and atomic writes shared by scanners and exporters."""
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def atomic_write(path, content):
    """Replace one file only after writing successfully; leave no temporary files."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + '.', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content.encode('utf-8') if isinstance(content, str) else content)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_json(path, value, *, indent=2):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=indent) + '\n')


def write_csv(path, rows, fieldnames):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    atomic_write(path, stream.getvalue())


def cache_path(directory, url):
    return Path(directory) / (hashlib.sha256(url.encode('utf-8')).hexdigest() + '.json')
