from time import time
from typing import List
from requests import get, Response
from qaviton_io import AsyncManager


def test_simple_requests_with_log_decorator():
    rs: List[Response] = []
    m = AsyncManager()

    @m.log.task(exceptions=Exception)
    def task():
        r = get("https://qaviton.com")
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

    @m.log.task(exceptions=Exception)
    def multi_task():
        for _ in range(4):
            r = get("https://qaviton.com")
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

    @m.log.task()
    def task(url):
        r = get(url)
        r.raise_for_status()
        rs.append(r)

    @m.log.task(exceptions=Exception)
    def multi_task():
        for url in [
            "https://qaviton.com",
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
