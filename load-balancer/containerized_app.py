import datetime
import logging
import os
import uuid

from docker import DockerClient
from docker.errors import APIError
from docker.models.containers import Container


class ContainerizedApp:

    @classmethod
    def create(cls, client: DockerClient):
        running_virtualized = "VIRTUALIZED" in os.environ
        hostname = f"mtd-app-{uuid.uuid4().hex}" if running_virtualized else "localhost"
        port = int(os.environ.get("APP_PORT", 8080))
        container = client.containers.run(image="spzc/python",
                                          name=hostname,
                                          volumes={f"mtd-webapp": {"bind": "/app", "mode": "ro"}},
                                          command=["python3", "app/serve.py"],
                                          detach=True,
                                          environment={"PORT": port, "SESSION_MGR": "session-manager:8888"},
                                          network=os.environ.get("NETWORK_NAME", "default"),
                                          hostname=hostname)
        return ContainerizedApp(container, hostname, port)

    def __init__(self, container: Container, hostname: str, port: int):
        self.container: Container = container
        self.hostname: str = hostname
        self.port: int = port
        self.initialized: datetime.datetime = datetime.datetime.now()
        self.logger = logging.getLogger(container.name)
        self.logger.setLevel(logging.DEBUG)
        h = logging.StreamHandler()
        h.setLevel(logging.DEBUG)
        self.logger.addHandler(h)
        self.logger.info(f"created new app: {self.container.name}")

    def remove(self):
        self.logger.info(f"removing app: {self.container.name}")
        try:
            self.container.stop()
            self.container.remove()
        except APIError:
            self.logger.warning("could not remove app")
        return self
