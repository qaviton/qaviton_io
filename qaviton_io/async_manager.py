from asyncio import get_event_loop
from qaviton_io.types import Tasks
from qaviton_io.logger import Log
from qaviton_io.utils.log import log as default_log
from logging import Logger


class AsyncManager:
    def __init__(self):
        self.loop = get_event_loop()
        self.log = Log()
        self.results = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def analyze(
        self,
        analyze_pass=True,
        analyze_fail=False,
        analyze_all=False,
    ):  self.log.analyze(
        analyze_pass=analyze_pass,
        analyze_fail=analyze_fail,
        analyze_all=analyze_all,
        queue=None,
    ); return self

    def report(
        self,
        analyze_pass=True,
        analyze_fail=False,
        analyze_all=False,
        show_errors=True,
        logger: Logger = default_log,
    ):  self.log.report(
        analyze_pass=analyze_pass,
        analyze_fail=analyze_fail,
        analyze_all=analyze_all,
        show_errors=show_errors,
        logger=logger,
        queue=None,
    ); return self

    async def async_run(self, tasks: Tasks):
        progress = [self.loop.run_in_executor(None, task) for task in tasks]
        self.results.extend([await task for task in progress])

    def run(self, tasks: Tasks):
        self.loop.run_until_complete(self.async_run(tasks))
