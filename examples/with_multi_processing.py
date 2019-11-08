"""
make sure your tasks are defined at the module level,
so they can be pickled by multiprocessing
"""
from time import time
from requests import get
from qaviton_io.types import Tasks
from qaviton_io import ProcessManager, task
from traceback import format_exc


# now we make some tasks
# this is a nested task
# we don't want to handle any exceptions
# so in case of failure the parent will not proceed
@task()
def task1(url):
    r = get(url)
    r.raise_for_status()


# this is the prent task
# we want to handle all exceptions
# so in case of failure the next task will execute
@task(exceptions=Exception)
def multi_task():
    for url in [
        "https://qaviton.com",
        "https://qaviton.co.il",  # make sure you enter a valid address
        "https://qaviton.com1",  # make sure you enter a valid address
    ]:
        task1(url)


# let's create a function to execute tasks
def execute_tasks(tasks: Tasks, timeout):
    manager = ProcessManager()
    t = time()
    try:
        manager.run_until_complete(tasks, timeout=timeout)
        timed_out = None
    except TimeoutError:
        timed_out = format_exc()
    t = time() - t
    manager.log.report()
    print(f'took {round(t, 3)}s\n')
    manager.log.clear()
    return timed_out


# now all that's left is to run the tasks
if __name__ == "__main__":
    timeouts = [
        execute_tasks([multi_task for _ in range(1)], timeout=3),
        execute_tasks([multi_task for _ in range(20)], timeout=6),
        execute_tasks([multi_task for _ in range(80)], timeout=9),
    ]
    for timeout in timeouts:
        if timeout:
            print(timeout)
