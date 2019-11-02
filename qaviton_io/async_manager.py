from asyncio import get_event_loop
from qaviton_io.types import Tasks
from qaviton_io.logger import Log


class AsyncManager:
    def __init__(self):
        self.loop = get_event_loop()
        self.log = Log()

    async def async_run(self, tasks: Tasks):
        progress = [self.loop.run_in_executor(None, task) for task in tasks]
        for task in progress:
            await task

    def run(self, tasks: Tasks):
        self.loop.run_until_complete(self.async_run(tasks))
