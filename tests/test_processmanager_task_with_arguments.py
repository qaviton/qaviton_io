from time import time
from requests import get
from qaviton_io import ProcessManager, Log
from traceback import format_exc
from random import choice


log = Log()


@log.task()
def task(url):
    r = get(url)
    r.raise_for_status()


@log.task(exceptions=Exception)
def multi_task(domain):
    for url in [
        f"https://{domain}.com",
        f"https://{domain}.co.il",
        f"https://{domain}.io",
    ]:
        task(url)


def execute_tasks(manager: ProcessManager, tasks, timeout):
    t = time()
    try:
        manager.run_until_complete(tasks, timeout=timeout)
    except TimeoutError:
        print(format_exc())
    t = time() - t
    print(f'took {round(t, 3)}s')


def test_nested_requests_with_log_decorator():
    manager = ProcessManager()
    execute_tasks(manager, [(multi_task, choice(['google', 'youtube', 'netflix'])) for _ in range(20)], timeout=18)
    manager.log.report(show_errors=False, analyze_fail=True)
