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
