from time import time
from qaviton_io import AsyncManager as AM
from tests.testserver.server import Server


# taken from requests library
def server():
    return Server.text_response_server(
        "HTTP/1.1 200 OK\r\n" +
        "Content-Length: 6\r\n" +
        "[\"OK\"]"
    )


class AsyncManager(AM):
    def run(self, tasks):
        t = time()
        AM.run(self, tasks)
        t = time() - t
        print(f'took {round(t, 3)}s')
        return t

