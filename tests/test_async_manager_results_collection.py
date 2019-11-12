from requests import get
from tests.utils import AsyncManager, server
from qaviton_io import task


def test_async_manager_results_collection():
    m = AsyncManager()
    m.log.clear()

    @task(exceptions=Exception)
    def task1():
        with server() as (host, port):
            r = get(f'http://{host}:{port}')
        r.raise_for_status()
        return r

    m.run([task1 for _ in range(20)])

    assert not m.log()['task1']['fail']
    assert len(m.log()['task1']['pass']) == 20
    assert len(m.results) == 20
    for r in m.results: assert r.status_code == 200
    m.report()
