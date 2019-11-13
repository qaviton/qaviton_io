from time import time
from logging import Logger
from functools import wraps
from statistics import median
from colorama import init, Fore
from traceback import format_exc
from multiprocessing import Queue
from typing import List, Dict, Callable
from qaviton_io.utils.log import log as default_log


init()


class Log:
    _log = {}

    def __call__(self)->dict:
        return self.log

    @property
    def log(self):
        return Log._log

    @staticmethod
    def clear():
        Log._log = {}

    def send_message(self, name, *args):
        assert args
        log = self.log
        if name not in log:
            log[name] = {'fail': {}, 'pass': [], 'msg': [*args]}
        elif 'msg' not in log[name]:
            log[name]['msg'] = [*args]
        else:
            log[name]['msg'].extend(args)

    def has_message(self, name):
        return 'msg' in self.log[name]

    def receive_messages(self, name) -> list:
        if self.has_message(name):
            return self.log[name]['msg']

    def receive_all_messages(self):
        log = self.log
        return {name: log[name]['msg'] for name in log if 'msg' in log[name]}

    def merge(self, queue: Queue):
        results: List[Dict] = []
        append = results.append
        result = queue.get
        not_empty = queue.qsize

        while not_empty():
            append(result())

        for logs in results:
            for name, log in logs.items():
                if name not in self.log:
                    self.log[name] = log
                else:
                    for error, durations in log["fail"].items():
                        if error not in self.log[name]["fail"]:
                            self.log[name]["fail"][error] = []
                        self.log[name]["fail"][error].extend(durations)
                    self.log[name]["pass"].extend(log["pass"])
                    if 'msg' in log:
                        if 'msg' not in self.log[name]:
                            self.log[name]['msg'] = log['msg']
                        else:
                            self.log[name]['msg'].extend(log['msg'])
        return self

    def analyze(
        self,
        analyze_pass=True,
        analyze_fail=False,
        analyze_all=False,
        queue: Queue = None,
    ):
        if queue:
            self.merge(queue)
        for name, log in self.log.items():
            log["err"] = 0
            log["fails"] = []
            for error_durations in log['fail'].values():
                log["err"] += len(error_durations)
                log["fails"].extend(error_durations)
            log["all"] = log["pass"] + log["fails"]
            log["ok"] = len(log["pass"])
            log["total"] = len(log["all"])

            if analyze_pass:
                log["max"] = max(log["pass"]) if log["pass"] else None
                log["min"] = min(log["pass"]) if log["pass"] else None
                log["avg"] = sum(log["pass"]) / log["ok"] if log["pass"] else None
                log["med"] = median(log["pass"]) if log["pass"] else None
            if analyze_fail:
                log["max-err"] = max(log["fails"]) if log["fails"] else None
                log["min-err"] = min(log["fails"]) if log["fails"] else None
                log["avg-err"] = sum(log["fails"]) / log["err"] if log["fails"] else None
                log["med-err"] = median(log["fails"]) if log["fails"] else None
            if analyze_all:
                log["max-all"] = max(log["all"])
                log["min-all"] = min(log["all"])
                log["avg-all"] = sum(log["all"]) / log["total"]
                log["med-all"] = median(log["all"])
        return self

    def report(
        self,
        analyze_pass=True,
        analyze_fail=False,
        analyze_all=False,
        show_errors=True,
        logger: Logger = default_log,
        queue: Queue = None,
    ):
        self.analyze(analyze_pass, analyze_fail, analyze_all, queue)
        errors_detected = False
        logger.info("REPORT STATISTICS")
        logger.info("")
        for name, log in self.log.items():
            if log["fails"]:
                printlog = logger.error
                errors_detected = True
            else:
                printlog = logger.info
            space = " "*(30-len(name) if len(name) < 35 else 0)
            analyze_msg = [f'{name}:{space}']
            if analyze_pass:
                analyze_msg.append(
                    f'  max: {round(log["max"], 3) if log["max"] else None}s'
                    f'  min: {round(log["min"], 3) if log["min"] else None}s'
                    f'  avg: {round(log["avg"], 3) if log["avg"] else None}s'
                    f'  med: {round(log["med"], 3) if log["med"] else None}s'
                )
            if analyze_fail:
                analyze_msg.append(
                    f'  max-err: {round(log["max-err"], 3) if log["max-err"] else None}s'
                    f'  min-err: {round(log["min-err"], 3) if log["min-err"] else None}s'
                    f'  avg-err: {round(log["avg-err"], 3) if log["avg-err"] else None}s'
                    f'  med-err: {round(log["med-err"], 3) if log["med-err"] else None}s'
                )
            if analyze_all:
                analyze_msg.append(
                    f'  max-all: {round(max(log["all"]), 3)}s'
                    f'  min-all: {round(min(log["all"]), 3)}s'
                    f'  avg-all: {round(sum(log["all"]) / len(log["all"]), 3)}s'
                    f'  med-all: {round(median(log["all"]), 3)}s'
                )
            analyze_msg.append(
                f'  ok: {log["ok"]}'
                f'  total: {log["total"]}'
                f'  err: {log["err"]}'
            )
            printlog(''.join(analyze_msg))

        if errors_detected and show_errors:
            logger.info("")
            logger.info("REPORT ERRORS")
            logger.info("")
            for name, log in self.log.items():
                if log["fail"]:
                    logger.error(f'{Fore.RED}{name} with {len(log["fail"])} errors:\n')
                    for e, n in log["fail"].items():
                        logger.error(f'{Fore.RED}{e}, this error occurred {len(n)} times\n')
        return self


def task(exceptions=tuple()):
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if f.__name__ not in Log._log:
                Log._log[f.__name__] = {"pass": [], "fail": {}}
            t = time()
            try:
                r = f(*args, **kwargs)
            except exceptions:
                t = time() - t
                e = format_exc()
                if e not in Log._log[f.__name__]["fail"]:
                    Log._log[f.__name__]["fail"][e] = []
                Log._log[f.__name__]["fail"][e].append(t)
            except Exception as error:
                t = time() - t
                e = format_exc()
                if e not in Log._log[f.__name__]["fail"]:
                    Log._log[f.__name__]["fail"][e] = []
                Log._log[f.__name__]["fail"][e].append(t)
                raise error
            else:
                t = time() - t
                Log._log[f.__name__]["pass"].append(t)
                return r
        return wrapper
    return decorator
