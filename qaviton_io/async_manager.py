from asyncio import get_event_loop
from typing import List, Callable


class AsyncManager:
    def __init__(self):
        self.loop = get_event_loop()

    async def async_run(self, tasks: List[Callable]):
        progress = [self.loop.run_in_executor(None, task) for task in tasks]
        for task in progress:
            await task

    def run(self, tasks: List[Callable]):
        self.loop.run_until_complete(self.async_run(tasks))
