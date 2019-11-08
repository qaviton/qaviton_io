from time import time
from requests import get
from qaviton_io.types import Tasks
from qaviton_io import ProcessManager, task
from traceback import format_exc
from tests.utils import server


@task(exceptions=Exception)
def task1():
    with server() as (host, port):
        r = get(f'http://{host}:{port}')
    r.raise_for_status()


@task(exceptions=Exception)
def multi_task1():
    for _ in range(4):
        with server() as (host, port):
            r = get(f'http://{host}:{port}')
        r.raise_for_status()


@task()
def task2(url):
    with server() as (host, port):
        if url is None:
            url = f'http://{host}:{port}'
        r = get(url)
    r.raise_for_status()


@task(exceptions=Exception)
def multi_task2():
    for url in [
        None,
        "https://qaviton.co.il",
        "https://qaviton.com1",
    ]:
        task2(url)


def execute_tasks(manager: ProcessManager, tasks: Tasks, timeout):
    t = time()
    try:
        manager.run_until_complete(tasks, timeout=timeout)
    except TimeoutError:
        print(format_exc())
    t = time() - t
    print(f'took {round(t, 3)}s')


def test_simple_requests_with_multi_processing():
    manager = ProcessManager()
    manager.log.clear()
    execute_tasks(manager, [task1 for _ in range(1)], timeout=3)
    execute_tasks(manager, [task1 for _ in range(20)], timeout=6)
    execute_tasks(manager, [task1 for _ in range(80)], timeout=9)
    execute_tasks(manager, [task1 for _ in range(400)], timeout=20)
    manager.log.report()


def test_multi_requests_with_multi_processing():
    manager = ProcessManager()
    manager.log.clear()
    execute_tasks(manager, [multi_task1 for _ in range(1)], timeout=12)
    execute_tasks(manager, [multi_task1 for _ in range(20)], timeout=24)
    execute_tasks(manager, [multi_task1 for _ in range(80)], timeout=36)
    execute_tasks(manager, [multi_task1 for _ in range(400)], timeout=80)
    manager.log.report()


def test_nested_requests_with_log_decorator():
    manager = ProcessManager()
    manager.log.clear()
    execute_tasks(manager, [multi_task2 for _ in range(1)], timeout=9)
    execute_tasks(manager, [multi_task2 for _ in range(20)], timeout=18)
    execute_tasks(manager, [multi_task2 for _ in range(80)], timeout=27)
    execute_tasks(manager, [multi_task2 for _ in range(400)], timeout=60)
    manager.log.report(show_errors=False, analyze_fail=True)
