from time import time
from uuid import uuid4
from qaviton_io import AsyncManager, task, Log, ProcessManager


@task()
def st():
    Log().send_message('st', {'id': f'{uuid4()}', 'timestamp': time()})


def test_log_messaging():
    n = 10
    with AsyncManager() as m:
        m.log.clear()
        m.run([st for _ in range(n)])
        msgs = m.log.receive_all_messages()['st']
    assert len(msgs) == n


def test_messaging_with_processes():
    n = 10
    with ProcessManager() as m:
        m.log.clear()
        m.run_until_complete([st for _ in range(n)], timeout=None)
        m.merge()
        msgs = m.log.receive_all_messages()['st']
    assert len(msgs) == n
