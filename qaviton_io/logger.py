from time import time
from multiprocessing import Queue
from statistics import median
from typing import List, Dict, Callable
from qaviton_io.utils.log import log as default_log
from colorama import init, Fore
from functools import wraps
from logging import Logger

init()


class Log:
    def __init__(self):
        self.log = {}
        self.queue: Queue = None

    def task(self, exceptions=Exception):
        def decorator(f: Callable):
            @wraps(f)
            def wrapper(*args, **kwargs):
                t = time()
                try:
                    r = f(*args, **kwargs)
                except exceptions as e:
                    should_raise = False
                except Exception as e:
                    should_raise = True

                t = time() - t
                if f.__name__ in self.log:
                    self.log[f.__name__].append(t)
                else:
                    self.log[f.__name__] = [t]
                    State.errors[f.__name__] = {}
                if validate_response is True:
                    try:
                        r.raise_for_status()
                    except Exception as error:
                        e = f'{traceback.format_exc()} {r.text}'
                        if e in State.errors[f.__name__]:
                            State.errors[f.__name__][e] += 1
                        else:
                            State.errors[f.__name__][e] = 1
                        raise error
                elif validate_response is False:
                    try:
                        assert not r.ok
                    except Exception as error:
                        e = traceback.format_exc()
                        if e in State.errors[f.__name__]:
                            State.errors[f.__name__][e] += 1
                        else:
                            State.errors[f.__name__][e] = 1
                        raise error
                elif validate_response is None:
                    pass
                return r
            return wrapper
        return decorator

    def merge_logs(self):
        results: List[Dict] = []
        queue = self.queue
        append_result = results.append
        get_result = queue.get
        hold_results = queue.empty

        while not hold_results():
            append_result(get_result())

        for logs in results:
            for name, log in logs.items():
                if name not in self.log:
                    self.log[name] = log
                else:
                    for error, durations in log["fail"].items():
                        self.log[name]["fail"][error].extend(durations)

                    for durations in log["pass"]:
                        self.log[name]["pass"].extend(durations)

    def report(self, analyze_pass=True, analyze_fail=False, analyze_all=False, logger: Logger = default_log):
        for name, log in self.log.items():
            log["err"] = 0
            log["fails"] = []
            for error_durations in log['fail'].values():
                log["err"] += len(error_durations)
                log["fails"].extend(error_durations)
            log["all"] = log["pass"] + log["fails"]
            log["ok"] = len(log["pass"]) - log["err"]
            log["total"] = len(log["all"])

            if analyze_pass:
                log["max"] = max(log["pass"])
                log["min"] = min(log["pass"])
                log["avg"] = sum(log["pass"]) / log["ok"]
                log["med"] = median(log["pass"])
            if analyze_fail:
                log["max-err"] = max(log["fails"])
                log["min-err"] = min(log["fails"])
                log["avg-err"] = sum(log["fails"]) / log["err"]
                log["med-err"] = median(log["fails"])
            if analyze_all:
                log["max-all"] = max(log["all"])
                log["min-all"] = min(log["all"])
                log["avg-all"] = sum(log["all"]) / log["total"]
                log["med-all"] = median(log["all"])

        if logger:
            logger.info("REPORT STATISTICS")
            for name, log in self.log.items():
                if log["fails"]:
                    printlog = logger.error
                else:
                    printlog = logger.info
                space = " "*(30-len(name) if len(name) < 35 else 0)
                analyze_msg = [f'{name}:{space}']
                if analyze_pass:
                    analyze_msg.append(
                        f'  max: {log["max"]}s'
                        f'  min: {log["min"]}s'
                        f'  avg: {round(log["avg"], 3)}s'
                        f'  med: {round(log["med"], 3)}s'
                    )
                if analyze_fail:
                    analyze_msg.append(
                        f'  max-err: {log["max-err"]}s'
                        f'  min-err: {log["min-err"]}s'
                        f'  avg-err: {round(log["avg-err"], 3)}s'
                        f'  med-err: {round(log["med-err"], 3)}s'
                    )
                if analyze_all:
                    analyze_msg.append(
                        f'  max-all: {max(log["all"])}s'
                        f'  min-all: {min(log["all"])}s'
                        f'  avg-all: {round(sum(log["all"]) / len(log["all"]), 3)}s'
                        f'  med-all: {round(median(log["all"]), 3)}s'
                    )
                analyze_msg.append(
                    f'  ok: {log["ok"]}'
                    f'  total: {log["total"]}'
                    f'  err: {log["err"]}'
                )
                printlog(''.join(analyze_msg))

            logger.info("REPORT ERRORS")
            for name, log in self.log.items():
                if log["fail"]:
                    print(f'{Fore.RED}{name} with {len(log["fail"])} errors:\n')
                    for e, n in log["fail"].items():
                        print(f'{Fore.RED}{e}, this error occurred {len(n)} times\n')
