"""Partition GitHub REST code searches to work around the 1,000-result ceiling."""
import logging

LOG = logging.getLogger('softcatala-reuse')
# The legacy REST index accepts files smaller than 384 KiB.
INDEX_MAX_BYTES = 384 * 1024
RESULT_LIMIT = 1000


def github_hits(client, query, warnings, *, max_pages=0, stats=None, checkpoint=None):
    stats = stats if stats is not None else {}
    stats.update(query=query, reported_count=None, unique_matches=0, requests=0,
                 partitions=[], complete=True, state='running')
    seen = set()

    def searched(label):
        if checkpoint:
            checkpoint('GitHub: ' + label)

    def request(q, page):
        stats['requests'] += 1
        try:
            result = client.get('/search/code', {'q': q, 'per_page': 100, 'page': page})
            if not isinstance(result, dict) or not isinstance(result.get('items'), list):
                raise ValueError('Invalid code-search response')
            return result
        except Exception as exc:
            stats['complete'] = False
            warnings.append(f'GitHub search failed: {q}, page {page}: {exc}')
            searched(f'{q}, page {page} (failed)')
            return None

    def walk(low, high, unrestricted=False):
        q = query if unrestricted else f'{query} size:{low}..{high}'
        LOG.info('GitHub: %s', q)
        first = request(q, 1)
        if first is None:
            return
        total = first.get('total_count', 0)
        if unrestricted:
            stats['reported_count'] = total
        if total > RESULT_LIMIT and low < high:
            midpoint = (low + high) // 2
            LOG.info('Splitting %s results into sizes %s..%s and %s..%s', total, low, midpoint, midpoint + 1, high)
            searched(q + ' (split)')
            yield from walk(low, midpoint)
            yield from walk(midpoint + 1, high)
            return
        partition = {'query': q, 'reported_count': total, 'returned_count': 0, 'complete': True}
        stats['partitions'].append(partition)
        if total > RESULT_LIMIT:
            partition['complete'] = stats['complete'] = False
            warnings.append(f'GitHub unresolved cap: {q}: {total} matches of the same byte size; first 1000 accessible')
        page, result = 1, first
        while result is not None:
            if result.get('incomplete_results'):
                partition['complete'] = stats['complete'] = False
                warnings.append(f'GitHub incomplete search: {q}, page {page}')
            if result.get('total_count', 0) != total:
                partition['complete'] = stats['complete'] = False
                warnings.append(f'GitHub index changed while paginating: {q}')
            batch = result['items']
            partition['returned_count'] += len(batch)
            for hit in batch:
                key = (hit['repository']['full_name'].casefold(), hit['path'])
                if key not in seen:
                    seen.add(key)
                    stats['unique_matches'] = len(seen)
                    yield hit
            if not batch or partition['returned_count'] >= min(total, RESULT_LIMIT):
                if partition['returned_count'] < min(total, RESULT_LIMIT):
                    partition['complete'] = stats['complete'] = False
                    warnings.append(f'GitHub short result set: {q}: {partition["returned_count"]}/{total}')
                searched(f'{q}, page {page}')
                break
            if max_pages and page >= max_pages:
                partition['complete'] = stats['complete'] = False
                warnings.append(f'Pagination limited: GitHub {q}, {page} pages')
                searched(f'{q}, page {page} (limited)')
                break
            searched(f'{q}, page {page}')
            page += 1
            result = request(q, page)
            if result is None:
                partition['complete'] = False

    yield from walk(0, INDEX_MAX_BYTES, unrestricted=True)
    if stats['reported_count'] is not None and stats['unique_matches'] < stats['reported_count']:
        stats['complete'] = False
        warnings.append(f'GitHub coverage difference: {query}: {stats["unique_matches"]}/{stats["reported_count"]} unique indexed matches retrieved')
    stats['state'] = 'completed' if stats['complete'] else 'partial'
