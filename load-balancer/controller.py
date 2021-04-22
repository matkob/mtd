import logging
import os
import random
import signal
import datetime
from typing import List

from apscheduler.job import Job
from pytimeparse.timeparse import timeparse
import docker
from apscheduler.schedulers.background import BackgroundScheduler
from docker import DockerClient

import utils
from containerized_app import ContainerizedApp


class Controller:
    LIVE_APPS = int(os.environ.get("REPLICAS", 1))
    TIME_TO_LIVE = datetime.timedelta(seconds=timeparse(os.environ.get("APP_TTL", "5s")))
    DECOMMISSION_PERIOD = datetime.timedelta(seconds=timeparse(os.environ.get("APP_DECOMMISSION_PERIOD", "10s")))

    def __init__(self):
        self.docker: DockerClient = docker.from_env()
        self.apps: List[ContainerizedApp] = []
        self.next_apps: List[ContainerizedApp] = []
        self.logger = utils.create_stdout_logger(logging.DEBUG, "controller")

        self.create_network()
        self.apps = self.initialize_apps()
        self.next_apps = self.initialize_apps()

        self.scheduler: BackgroundScheduler = BackgroundScheduler()
        self.rotation_job: Job = self.scheduler.add_job(func=lambda: self.rotate_apps(),
                                                        trigger="interval",
                                                        seconds=self.TIME_TO_LIVE.seconds,
                                                        max_instances=1,
                                                        replace_existing=False)
        self.scheduler.start()
        signal.signal(signal.SIGTERM, lambda signum, frame: self.shutdown())
        signal.signal(signal.SIGINT, lambda signum, frame: self.shutdown())

    def create_network(self):
        network_name = os.environ.get("NETWORK_NAME", "mtd-private")
        if len(self.docker.networks.list(names=[network_name])) == 0:
            self.docker.networks.create(name=network_name, driver="bridge")

    def initialize_apps(self):
        return [ContainerizedApp.create(self.docker) for _ in range(self.LIVE_APPS)]

    def rotate_apps(self):
        self.logger.info("rotating apps")
        old_apps = self.apps
        self.scheduler.add_job(func=lambda: [app.remove() for app in old_apps],
                               trigger="date",
                               run_date=datetime.datetime.now() + self.DECOMMISSION_PERIOD)
        self.apps = self.next_apps
        self.next_apps = self.initialize_apps()  # race condition when shutting down during initialization

    def shutdown(self):
        self.rotation_job.remove()
        [c.remove() for c in self.apps + self.next_apps]  # needs open client
        [job.func() for job in self.scheduler.get_jobs()]
        self.scheduler.shutdown(wait=False)
        self.docker.close()
        exit(0)

    def random_app(self) -> ContainerizedApp:
        return random.choice(self.apps)
