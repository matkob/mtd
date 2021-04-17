import os
import uuid
import requests as req
from flask import Flask, request, jsonify, Response


app = Flask("vulnerable server")
session_manager = os.environ.get("SESSION_MGR", "localhost")


@app.route("/", methods=["GET"])
def hello():
    session_id = request.cookies.get("session_id")
    generic_message = jsonify({"message": f"Hello stranger"}), 200

    if session_id is None:
        return generic_message

    app.logger.info(f"request with session id {session_id[:10]}...")
    session_data = req.get(f"http://{session_manager}:8888/session/{session_id}")
    if session_data.status_code != 200:
        return generic_message

    user = session_data.json()["user"]
    app.logger.info(f"request from user {user}")
    return jsonify({"message": f"Hello {user}"}), 200


@app.route("/login/<name>", methods=["PUT"])
def login(name):
    session_id = request.cookies.get("session_id")

    if session_id is None:
        session_id = uuid.uuid4().hex
        app.logger.info(f"setting new session id {session_id[:10]}...")

    if req.put(f"http://{session_manager}:8888/session/{session_id}", json={"user": name}).status_code != 202:
        return Response(status=500)

    response = jsonify({"message": f"{name} is now logged in!"})
    response.set_cookie(key="session_id", value=session_id)
    return response, 202


app.run(host="0.0.0.0", port=8080, debug=True)
