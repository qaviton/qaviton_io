from time import time
from requests import get
from qaviton_io.async_manager import AsyncManager


def test_simple_requests():
    def execute_tasks(number_of_tasks: int):
        errors = {}
        rs = []

        def task():
            try:
                r = get("https://google.com")
                r.raise_for_status()
                rs.append(r)
            except Exception as e:
                name = f'{e.__traceback__}{e}'
                if name in errors:
                    errors[name] += 1
                else:
                    errors[name] = 1

        tasks = [task for _ in range(number_of_tasks)]
        manager = AsyncManager()

        t = time()
        manager.run(tasks)
        t = time() - t
        print(f'took {round(t, 3)}s')
        for e, n in errors.items():
            print(f'{e} this error occurred {n} times')
        assert not errors
        return t

    print("")
    t1 = execute_tasks(1)
    t2 = execute_tasks(20)
    assert t2 < t1 * 2
