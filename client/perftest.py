import os
import time
import requests as req
import pandas as pd


class PerformanceTest:

    def __init__(self):
        self.iterations = 10000
        self.print_step = int(self.iterations / 100)
        self.payload_size = 128
        self.url = "http://localhost:5000"
        self.times = {"put": [], "get": []}

    def put(self, payload: str):
        s = req.Session()
        url = self.url + "/login/" + payload
        return s.put(url), s

    def get(self, s: req.Session):
        return s.get(self.url)

    @staticmethod
    def random_payload(size):
        return os.urandom(size).hex()

    @staticmethod
    def time_call(func):
        start = time.time_ns()
        ret = func()
        end = time.time_ns()
        return end - start, ret

    def print_progress(self, it: int):
        if it % self.print_step == 0:
            print(f"progress: {it}/{self.iterations}")

    def run(self):
        for it in range(self.iterations):
            self.print_progress(it)
            payload = self.random_payload(self.payload_size)
            put_time, ret = self.time_call(lambda: self.put(payload))
            if ret[0].status_code != 202:
                continue
            get_time, ret = self.time_call(lambda: self.get(ret[1]))
            self.times["put"].append(put_time)
            self.times["get"].append(get_time)

    def print_summary(self):
        df = pd.DataFrame(data=self.times)
        df = df / 1000 / 1000  # nanos to millis
        print("")
        print(f"Number of iterations: {self.iterations}")
        print(f"Size of payload: {self.payload_size}")
        print("")
        print("### Payload is measured in bytes ###")
        print("### Time is measured in ms ###")
        print(df.describe(percentiles=[.5, .9, .99, .999, .9999]))
