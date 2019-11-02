from time import time
from requests import get
from qaviton_io.types import Tasks
from qaviton_io import ProcessManager, Log


log = Log()


@log.task(exceptions=Exception)
def task1():
    r = get("https://google.com")
    r.raise_for_status()


@log.task(exceptions=Exception)
def multi_task1():
    for _ in range(4):
        r = get("https://google.com")
        r.raise_for_status()


@log.task()
def task2(url):
    r = get(url)
    r.raise_for_status()


@log.task(exceptions=Exception)
def multi_task2():
    for url in [
        "https://google.com",
        "https://google.co.il",
        "https://google.com1",
    ]:
        task2(url)


def execute_tasks(manager: ProcessManager, tasks: Tasks):
    t = time()
    manager.run_until_complete(tasks)
    t = time() - t
    print(f'took {round(t, 3)}s')


def test_simple_requests_with_multi_processing():
    manager = ProcessManager()
    execute_tasks(manager, [task1 for _ in range(1)])
    execute_tasks(manager, [task1 for _ in range(20)])
    execute_tasks(manager, [task1 for _ in range(80)])
    execute_tasks(manager, [task1 for _ in range(400)])
    manager.log.report()


def test_multi_requests_with_multi_processing():
    manager = ProcessManager()
    execute_tasks(manager, [multi_task1 for _ in range(1)])
    execute_tasks(manager, [multi_task1 for _ in range(20)])
    execute_tasks(manager, [multi_task1 for _ in range(80)])
    execute_tasks(manager, [multi_task1 for _ in range(400)])
    manager.log.report()


def test_nested_requests_with_log_decorator():
    manager = ProcessManager()
    execute_tasks(manager, [multi_task2 for _ in range(1)])
    execute_tasks(manager, [multi_task2 for _ in range(20)])
    execute_tasks(manager, [multi_task2 for _ in range(80)])
    execute_tasks(manager, [multi_task2 for _ in range(400)])
    manager.log.report(show_errors=False, analyze_fail=True)
