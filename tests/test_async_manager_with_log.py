from time import time
from typing import List
from requests import get, Response
from qaviton_io import AsyncManager
from tests.utils import server


def test_simple_requests_with_log_decorator():
    rs: List[Response] = []
    m = AsyncManager()
    m.log.clear()

    @m.log.task(exceptions=Exception)
    def task():
        with server() as (host, port):
            r = get(f'http://{host}:{port}')
        r.raise_for_status()
        rs.append(r)

    def execute_tasks(number_of_tasks: int):
        tasks = [task for _ in range(number_of_tasks)]

        t = time()
        m.run(tasks)
        t = time() - t

        print(f'took {round(t, 3)}s')
        return t

    t1 = execute_tasks(1)
    t2 = execute_tasks(20)

    assert not m.log.log['task']['fail']
    assert len(m.log.log['task']['pass']) == 21
    assert len(rs) == 21
    assert t2 < t1 * 2
    for r in rs: assert r.status_code == 200
    m.log.report()


def test_multi_requests_with_log_decorator():
    rs: List[Response] = []
    m = AsyncManager()
    m.log.clear()

    @m.log.task(exceptions=Exception)
    def multi_task():
        for _ in range(4):
            with server() as (host, port):
                r = get(f'http://{host}:{port}')
            r.raise_for_status()
            rs.append(r)

    def execute_tasks(number_of_tasks: int):
        tasks = [multi_task for _ in range(number_of_tasks)]

        t = time()
        m.run(tasks)
        t = time() - t

        print(f'took {round(t, 3)}s')
        return t

    t1 = execute_tasks(1)
    t2 = execute_tasks(20)

    assert not m.log.log['multi_task']['fail']
    assert len(m.log.log['multi_task']['pass']) == 21
    assert len(rs) == 84
    assert t2 < t1 * 2
    for r in rs: assert r.status_code == 200
    m.log.report()


def test_nested_requests_with_log_decorator():
        rs: List[Response] = []
        m = AsyncManager()
        m.log.clear()

        @m.log.task()
        def task(url):
            with server() as (host, port):
                if url is None:
                    url = f'http://{host}:{port}'
                r = get(url)
            r.raise_for_status()
            rs.append(r)

        @m.log.task(exceptions=Exception)
        def multi_task():
            for url in [
                None,
                "https://qaviton.co.il",
                "https://qaviton.com1",
            ]:
                task(url)

        def execute_tasks(number_of_tasks: int):
            tasks = [multi_task for _ in range(number_of_tasks)]

            t = time()
            m.run(tasks)
            t = time() - t

            print(f'took {round(t, 3)}s')
            return t

        execute_tasks(1)
        execute_tasks(20)
        m.log.report(show_errors=False, analyze_fail=True)
