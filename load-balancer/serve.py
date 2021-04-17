from flask import Flask, request
from controller import Controller
from containerized_app import ContainerizedApp
import requests as req

app = Flask("load balancer")


@app.route("/", defaults={"path": ""}, methods=["GET", "PUT"])
@app.route("/<path:path>", methods=["GET", "PUT"])
def route(path):
    container: ContainerizedApp = controller.random_app()
    url = f"http://{container.hostname}:{container.port}/{path}"
    app.logger.info(f"routing to {url}")
    response = req.request(method=request.method, url=url, headers=request.headers, cookies=request.cookies)
    return response.json(), response.status_code


controller = Controller()
app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
