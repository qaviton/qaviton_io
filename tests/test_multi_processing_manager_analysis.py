import json
from time import time
from requests import get
from traceback import format_exc
from qaviton_io import ProcessManager, task, AsyncManager
from tests.utils import server
from os import remove


class Login:
    def __init__(self):
        self.login()
        self.sessions = []

    @task()
    def login(self):
        with server() as (host, port):
            url = f'http://{host}:{port}'
            r = get(url)
        r.raise_for_status()
        return r

    @task()
    def _create_new_session(self):
        with server() as (host, port):
            url = f'http://{host}:{port}'
            r = get(url)
        r.raise_for_status()
        return r

    def create_session(self, number_of_sessions=1):
        if number_of_sessions == 1:
            self.sessions.append(
                self._create_new_session()
                    .text)
        else:
            def async_call():
                r = self._create_new_session()
                r.raise_for_status()
                self.sessions.append(r.text)

            async_calls = []
            max_sessions_per_request = 1

            while number_of_sessions > 0:
                if number_of_sessions > max_sessions_per_request:
                    number_of_sessions -= max_sessions_per_request
                else:
                    number_of_sessions = 0
                async_calls.append(lambda: async_call())

            AsyncManager().run(async_calls)

    @task()
    def create_session_locally(self):
        self.sessions.append(self._create_new_session().text)


class Shop:
    def __init__(self, session: Login):
        self.r = session.sessions.pop()

    @task()
    def get(self):
        with server() as (host, port):
            url = f'http://{host}:{port}'
            r = get(url)
        r.raise_for_status()
        return r

    @task()
    def bad_request(self):
        raise


def store_workflow(session: Login):
    try:
        session.create_session_locally()
        shop = Shop(session)
    except:  # don't stop the async loop
        print(format_exc())
    else:
        try:
            shop.get()
            shop.get()
            try:
                shop.bad_request()
            except:
                pass
            else:
                raise
        finally:
            shop.get()



def test_multi_processing_manager_analysis():
    report_file = 'report_logs.json'

    session = Login()
    manager = ProcessManager()
    t = time()
    try:
        manager.run_until_complete([(store_workflow, session) for _ in range(100)], timeout=50)
    except TimeoutError:
        print(format_exc())
    t = time() - t

    manager.report(show_errors=False)
    print(f'took {round(t, 3)}s\n')

    with open(report_file, 'w') as f:
        json.dump(manager.log(), f, indent=2)

    try:
        manager.log.clear()

        with open(report_file) as f:
            analysis = json.load(f)

        assert isinstance(analysis, dict)
        assert 'login'                  in analysis
        assert 'create_session_locally' in analysis
        assert '_create_new_session'    in analysis
        assert 'get'                    in analysis
        assert 'bad_request'            in analysis

        assert len(analysis['login']                 ['pass']) == 1
        assert len(analysis['create_session_locally']['pass']) == 100
        assert len(analysis['_create_new_session']   ['pass']) == 100
        assert len(analysis['get']                   ['pass']) == 300
        assert len(analysis['bad_request']           ['pass']) == 0

        assert not analysis['login']                 ['fail']
        assert not analysis['create_session_locally']['fail']
        assert not analysis['_create_new_session']   ['fail']
        assert not analysis['get']                   ['fail']
        assert len(analysis['bad_request']['fail']) == 1

        assert analysis['login']                 ['err'] == 0
        assert analysis['create_session_locally']['err'] == 0
        assert analysis['_create_new_session']   ['err'] == 0
        assert analysis['get']                   ['err'] == 0
        assert analysis['bad_request']           ['err'] == 100

        assert len(analysis['login']                 ['fails']) == 0
        assert len(analysis['create_session_locally']['fails']) == 0
        assert len(analysis['_create_new_session']   ['fails']) == 0
        assert len(analysis['get']                   ['fails']) == 0
        assert len(analysis['bad_request']           ['fails']) == 100

        assert len(analysis['login']                 ['all']) == 1
        assert len(analysis['create_session_locally']['all']) == 100
        assert len(analysis['_create_new_session']   ['all']) == 100
        assert len(analysis['get']                   ['all']) == 300
        assert len(analysis['bad_request']           ['all']) == 100

        assert analysis['login']                 ['ok'] == 1
        assert analysis['create_session_locally']['ok'] == 100
        assert analysis['_create_new_session']   ['ok'] == 100
        assert analysis['get']                   ['ok'] == 300
        assert analysis['bad_request']           ['ok'] == 0

        assert analysis['login']                 ['total'] == 1
        assert analysis['create_session_locally']['total'] == 100
        assert analysis['_create_new_session']   ['total'] == 100
        assert analysis['get']                   ['total'] == 300
        assert analysis['bad_request']           ['total'] == 100

        assert 'max' in analysis['login']
        assert 'max' in analysis['create_session_locally']
        assert 'max' in analysis['_create_new_session']
        assert 'max' in analysis['get']
        assert 'max' in analysis['bad_request']
        assert 'min' in analysis['login']
        assert 'min' in analysis['create_session_locally']
        assert 'min' in analysis['_create_new_session']
        assert 'min' in analysis['get']
        assert 'min' in analysis['bad_request']
        assert 'avg' in analysis['login']
        assert 'avg' in analysis['create_session_locally']
        assert 'avg' in analysis['_create_new_session']
        assert 'avg' in analysis['get']
        assert 'avg' in analysis['bad_request']
        assert 'med' in analysis['login']
        assert 'med' in analysis['create_session_locally']
        assert 'med' in analysis['_create_new_session']
        assert 'med' in analysis['get']
        assert 'med' in analysis['bad_request']
    finally:
        remove(report_file)
