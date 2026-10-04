"""Read GitHub content and its pinned provenance for all review entry points."""
import base64
from urllib.parse import quote


def decode_contents(data):
    if data.get('encoding', 'base64') != 'base64':
        raise ValueError('API file content is not base64 encoded')
    return base64.b64decode(data['content']).decode('utf-8', errors='replace')


def fetch_file(client, repository, path, revision):
    data = client.get(f'/repos/{repository}/contents/{quote(path, safe="/")}', {'ref': revision})
    return dict(path=path, content=decode_contents(data),
                url=f'https://github.com/{repository}/blob/{revision}/{path}')
