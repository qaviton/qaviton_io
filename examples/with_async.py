from time import time
from typing import List
from requests import get, Response  # lets make use of requests to make async http calls
from qaviton_io import AsyncManager

# we can save the responses here
rs: List[Response] = []

# let's create an async manager
m = AsyncManager()


# first we make a simple function to make an http call.
# we want to log the result,
# and make sure that in case of an exception
# the manager won't stop
@m.log.task(exceptions=Exception)
def task():
    r = get("https://qaviton.com")
    r.raise_for_status()
    rs.append(r)


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

# let's view the results in the log report
m.log.report()
