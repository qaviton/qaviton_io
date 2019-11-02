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
from typing import List
from requests import get, Response  # lets make use of requests to make async http calls
from qaviton_io import AsyncManager, Log

# we can save the responses here
rs: List[Response] = []

# let's create an async manager & log
manager = AsyncManager()
log = Log()

# first we make a simple function to make an http call
# we want to log the result
# and make sure that in case of an exception
# the manager won't stop
@log.task(exceptions=Exception)
def task():
    r = get("https://google.com")
    r.raise_for_status()
    rs.append(r)

# let's run our task once and see how long it takes
t = time()
manager.run([task for _ in range(1)])
t = time() - t
print(f'took {round(t, 3)}s')

# now let's run our task 20 times and see how long it takes
t = time()
manager.run([task for _ in range(20)])
t = time() - t
print(f'took {round(t, 3)}s')

# let's view the results in the log report
log.report()
```  
  
#### process manager:  
  
```python
# TODO: add timeout
```  
  