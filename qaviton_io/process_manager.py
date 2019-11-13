from time import time
from typing import List
from qaviton_io.logger import Log
from qaviton_io.types import Tasks
from qaviton_processes import Task
from multiprocessing import cpu_count, Manager, Queue
from qaviton_io.async_manager import AsyncManager
from qaviton_io.utils.log import log as default_log
from logging import Logger


def worker(tasks, queue: Queue):
    m = AsyncManager()
    m.log.clear()
    for i, task in enumerate(tasks):
        if isinstance(task, tuple):
            tasks[i] = lambda: task[0](*task[1:])
    try:
        m.run(tasks)
    finally:
        queue.put(m.log())


class ProcessManager:
    def __init__(self, worker=worker):
        self.log = Log()
        self.queue = Manager().Queue()  # https://stackoverflow.com/questions/11442892/python-multiprocessing-queue-failure?rq=1 the mp.queue gets the processes stuck
        self.log.queue = self.queue
        self.CPUs = cpu_count()
        self.worker = worker

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def merge(self):
        self.log.merge(self.queue)
        return self

    def analyze(
        self,
        analyze_pass=True,
        analyze_fail=False,
        analyze_all=False,
    ): self.log.analyze(
        analyze_pass=analyze_pass,
        analyze_fail=analyze_fail,
        analyze_all=analyze_all,
        queue=self.queue,
    ); return self

    def report(
        self,
        analyze_pass=True,
        analyze_fail=False,
        analyze_all=False,
        show_errors=True,
        logger: Logger = default_log,
    ): self.log.report(
        analyze_pass=analyze_pass,
        analyze_fail=analyze_fail,
        analyze_all=analyze_all,
        show_errors=show_errors,
        logger=logger,
        queue=self.queue,
    ); return self

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
            else:
                try:
                    for session in tasks:
                        if session.is_finished(timeout=timeout):
                            finished_sessions += 1
                        if time() - t > timeout:
                            raise TimeoutError
                except TimeoutError as e:
                    for session in tasks:
                        try:
                            session.kill()
                        except:
                            pass
                    raise e
