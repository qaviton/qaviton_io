from typing import List
from qaviton_io import task
from requests import get, Response
from tests.utils import AsyncManager, server


def test_simple_requests_with_log_decorator():
    rs: List[Response] = []
    m = AsyncManager()
    m.log.clear()

    @task(exceptions=Exception)
    def task1():
        with server() as (host, port):
            r = get(f'http://{host}:{port}')
        r.raise_for_status()
        rs.append(r)

    t1 = m.run([task1 for _ in range(1)])
    t2 = m.run([task1 for _ in range(20)])

    assert not m.log()['task1']['fail']
    assert len(m.log()['task1']['pass']) == 21
    assert len(rs) == 21
    assert t2 < t1 * 2
    for r in rs: assert r.status_code == 200
    m.report()


def test_multi_requests_with_log_decorator():
    rs: List[Response] = []
    m = AsyncManager()
    m.log.clear()

    @task(exceptions=Exception)
    def multi_task():
        for _ in range(4):
            with server() as (host, port):
                r = get(f'http://{host}:{port}')
            r.raise_for_status()
            rs.append(r)

    t1 = m.run([multi_task for _ in range(1)])
    t2 = m.run([multi_task for _ in range(20)])

    assert not m.log()['multi_task']['fail']
    assert len(m.log()['multi_task']['pass']) == 21
    assert len(rs) == 84
    assert t2 < t1 * 2
    for r in rs: assert r.status_code == 200
    m.report()


def test_nested_requests_with_log_decorator():
    rs: List[Response] = []
    m = AsyncManager()
    m.log.clear()

    @task()
    def task1(url):
        with server() as (host, port):
            if url is None:
                url = f'http://{host}:{port}'
            r = get(url)
        r.raise_for_status()
        rs.append(r)

    @task(exceptions=Exception)
    def multi_task():
        for url in [
            None,
            "https://qaviton.co.il",
            "https://qaviton.com1",
        ]:
            task1(url)

    m.run([multi_task for _ in range(1)])
    m.run([multi_task for _ in range(20)])
    m.report(show_errors=False, analyze_fail=True)
