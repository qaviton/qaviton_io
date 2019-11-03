from time import time
from typing import List
from qaviton_io.logger import Log
from qaviton_io.types import Tasks
from qaviton_processes import Task
from multiprocessing import cpu_count, Queue
from qaviton_io.async_manager import AsyncManager


def worker(tasks, queue: Queue):
    m = AsyncManager()
    m.log.queue = queue
    tasks = [lambda: task[0](*task[1:]) if isinstance(task, tuple) else task for task in tasks]
    try:
        m.run(tasks)
    finally:
        queue.put(m.log())


class ProcessManager:
    def __init__(self, worker=worker):
        self.log = Log()
        self.queue = Queue()
        self.log.queue = self.queue
        self.CPUs = cpu_count()
        self.worker = worker

    def distribute(self, tasks: Tasks)->List[Tasks]:
        cpus = self.CPUs
        number_of_tasks = len(tasks)
        processes = [list() for _ in range(cpus if cpus < number_of_tasks else number_of_tasks)]
        for i, task in enumerate(tasks): processes[i % cpus].append(task)
        return processes

    def run(self, tasks) -> List[Task]:
        processes = self.distribute(tasks)
        return [Task(target=self.worker, args=(tasks, self.queue)) for tasks in processes]

    def run_until_complete(self, tasks, timeout):
        processes = self.run(tasks)
        self.wait_until_tasks_are_done(processes, timeout=timeout)

    @staticmethod
    def wait_until_tasks_are_done(tasks: List[Task], timeout):
        finished_sessions = 0
        t = time()
        while finished_sessions < len(tasks):
            finished_sessions = 0
            if timeout is None:  # careful! processes get stuck TODO: better handling for stuck processes
                for session in tasks:
                    if session.is_finished():
                        finished_sessions += 1
            try:
                for session in tasks:
                    if session.is_finished(timeout=timeout):
                        finished_sessions += 1
                    if time()-t > timeout:
                        raise TimeoutError
            except TimeoutError as e:
                for session in tasks:
                    try:
                        session.kill()
                    except:
                        pass
                raise e
