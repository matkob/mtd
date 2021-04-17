import logging
import os
import random
import signal
from typing import List

import docker
from apscheduler.schedulers.background import BackgroundScheduler
from docker import DockerClient
from containerized_app import ContainerizedApp


class Controller:
    LIVE_APPS = int(os.environ.get("REPLICAS", 1))

    def __init__(self):
        self.docker: DockerClient = docker.from_env()
        self.apps: List[ContainerizedApp] = []

        self.logger = logging.getLogger("controller")
        self.logger.setLevel(logging.DEBUG)
        h = logging.StreamHandler()
        h.setLevel(logging.DEBUG)
        self.logger.addHandler(h)

        self.initialize()

        self.scheduler: BackgroundScheduler = BackgroundScheduler()
        self.scheduler.add_job(func=lambda: self.rotate_apps(),
                               trigger="interval",
                               seconds=10,
                               max_instances=1,
                               replace_existing=False)
        self.scheduler.start()
        signal.signal(signal.SIGTERM, lambda signum, frame: self.shutdown())
        signal.signal(signal.SIGINT, lambda signum, frame: self.shutdown())

    def initialize(self):
        for i in range(self.LIVE_APPS):
            app = ContainerizedApp.create(self.docker)
            self.apps.append(app)

    def rotate_apps(self):
        self.logger.info("rotating apps")

    def remove_apps(self):
        [app.remove() for app in self.apps]
        self.apps = []

    def shutdown(self):
        [app.remove() for app in self.apps]  # needs open client
        self.docker.close()
        self.scheduler.shutdown(wait=False)
        exit(0)

    def random_app(self) -> ContainerizedApp:
        return random.choice(self.apps)
