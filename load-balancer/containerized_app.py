import datetime
import logging
import os
import uuid

from docker import DockerClient
from docker.errors import APIError
from docker.models.containers import Container

import utils


class ContainerizedApp:

    @classmethod
    def create(cls, client: DockerClient):
        hostname = f"mtd-app-{uuid.uuid4().hex}"
        container = client.containers.run(image="spzc/python",
                                          name=hostname,
                                          volumes={f"mtd-webapp": {"bind": "/app", "mode": "ro"}},
                                          command=["python3", "app/serve.py"],
                                          detach=True,
                                          environment={"SESSION_MGR": "session-manager"},
                                          network=os.environ.get("NETWORK_NAME", "mtd-private"),
                                          hostname=hostname)
        return ContainerizedApp(container, hostname)

    def __init__(self, container: Container, hostname: str):
        self.container: Container = container
        self.hostname: str = hostname if os.environ.get("ENVIRONMENT", "local") == "docker" else "localhost"
        self.initialized: datetime.datetime = datetime.datetime.now()
        self.logger = utils.create_stdout_logger(logging.DEBUG, container.name)
        self.logger.info(f"created new app")

    def remove(self):
        self.logger.info(f"removing app")
        try:
            self.container.stop()
            self.container.remove()
        except APIError as err:
            self.logger.warning(f"could not remove app: {err.explanation}")
        return self
