# Qaviton IO  
![logo](https://www.qaviton.com/wp-content/uploads/logo-svg.svg)  
[![version](https://img.shields.io/pypi/v/qaviton_io.svg)](https://pypi.python.org/pypi)
[![license](https://img.shields.io/pypi/l/qaviton_io.svg)](https://pypi.python.org/pypi)
[![open issues](https://img.shields.io/github/issues/yehonadav/qaviton_io)](https://github/issues-raw/yehonadav/qaviton_io)
[![downloads](https://img.shields.io/pypi/dm/qaviton_io.svg)](https://pypi.python.org/pypi)
![code size](https://img.shields.io/github/languages/code-size/yehonadav/qaviton_io)
-------------------------  
  
Qaviton IO  
is a package with a simple API, making use of python's async & multiprocessing  
to enable fast execution of many asyncable operations.  
  
## Installation  
```sh  
pip install qaviton-io -U
```  
  
### Requirements  
- Python 3.6+  
  
## Features  
* async task manager  
* process task manager  
* task logger  
  
## Usage  
  
#### async manager:  
  
```python
from time import time
from requests import get  # lets make use of requests to make async http calls
from qaviton_io import AsyncManager, task


# let's create an async manager
m = AsyncManager()


# first we make a simple function to make an http call.
# we want to log the result,
# and make sure that in case of an exception
# the manager won't stop
@task(exceptions=Exception)
def task(): return get("https://qaviton.com")


# this will run async tasks and measure their duration
def run(tasks):
    t = time()
    m.run(tasks)
    t = time() - t
    print(f'took {round(t, 3)}s')


# let's run our task once and see how long it takes
run([task for _ in range(1)])

# now let's run our task 20 times and see how long it takes
run([task for _ in range(20)])

# we can assert the collected results here
assert len(m.results) == 21
for r in m.results:
    assert r.status_code == 200

# let's view the results in the log report
m.report()
```  
   
#### process manager:  
  
```python
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
    manager.report()
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
```  
  
## notes:  
  
* for good performance and easy usage  
you should probably stick with using the AsyncManager  
  
* The ProcessManager uses async operations as well as multi-processing.  
It distributes tasks across cpus, and those tasks are executed using the AsyncManager  
if you want maximum efficiency you should consider using the ProcessManager  
  
* The ProcessManager uses the multiprocessing module  
and should be treated with it's restrictions & limitations accordingly  
  
* The ProcessManager gets stuck easily,  
make sure to use timeouts when using it  
