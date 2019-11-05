from requests import get
from tests.utils import AsyncManager, server


def test_async_manager_results_collection():
    m = AsyncManager()
    m.log.clear()

    @m.log.task(exceptions=Exception)
    def task():
        with server() as (host, port):
            r = get(f'http://{host}:{port}')
        r.raise_for_status()
        return r

    m.run([task for _ in range(20)])

    assert not m.log.log['task']['fail']
    assert len(m.log.log['task']['pass']) == 20
    assert len(m.results) == 20
    for r in m.results: assert r.status_code == 200
    m.log.report()
