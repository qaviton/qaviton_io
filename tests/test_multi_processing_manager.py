from time import time
from typing import List
from requests import get, Response
from qaviton_io.logger import Log
from qaviton_io.process_manager import ProcessManager

rs: List[Response] = []
manager = ProcessManager()
log = Log()


@log.task(exceptions=Exception)
def task1():
    r = get("https://google.com")
    r.raise_for_status()
    rs.append(r)


def execute_tasks1(number_of_tasks: int):
    tasks = [task1 for _ in range(number_of_tasks)]

    t = time()
    manager.run_until_complete(tasks)
    t = time() - t

    print(f'took {round(t, 3)}s')
    return t


def test_simple_requests_with_log_decorator():
    t1 = execute_tasks1(1)
    t2 = execute_tasks1(20)
    t3 = execute_tasks1(80)
    execute_tasks1(400)
    assert t2 < t1 * 2 and t3 < t2 * 2
    log.queue = manager.queue
    log.report()


# def test_multi_requests_with_log_decorator():
#     rs: List[Response] = []
#     manager = AsyncManager()
#     log = Log()
#
#     @log.task(exceptions=Exception)
#     def multi_task():
#         for _ in range(4):
#             r = get("https://google.com")
#             r.raise_for_status()
#             rs.append(r)
#
#     def execute_tasks(number_of_tasks: int):
#         tasks = [multi_task for _ in range(number_of_tasks)]
#
#         t = time()
#         manager.run(tasks)
#         t = time() - t
#
#         print(f'took {round(t, 3)}s')
#         return t
#
#     t1 = execute_tasks(1)
#     t2 = execute_tasks(20)
#
#     assert not log.log['multi_task']['fail']
#     assert len(log.log['multi_task']['pass']) == 21
#     assert len(rs) == 84
#     assert t2 < t1 * 2
#     for r in rs: assert r.status_code == 200
#     log.report()
#
#
# def test_nested_requests_with_log_decorator():
#     rs: List[Response] = []
#     manager = AsyncManager()
#     log = Log()
#
#     @log.task()
#     def task(url):
#         r = get(url)
#         r.raise_for_status()
#         rs.append(r)
#
#     @log.task(exceptions=Exception)
#     def multi_task():
#         for url in [
#             "https://google.com",
#             "https://google.co.il",
#             "https://google.com1",
#         ]:
#             task(url)
#
#     def execute_tasks(number_of_tasks: int):
#         tasks = [multi_task for _ in range(number_of_tasks)]
#
#         t = time()
#         manager.run(tasks)
#         t = time() - t
#
#         print(f'took {round(t, 3)}s')
#         return t
#
#     execute_tasks(1)
#     execute_tasks(20)
#     log.report(show_errors=False, analyze_fail=True)
