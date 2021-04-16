import uuid
from typing import Dict
from flask import Flask, request, jsonify


app = Flask("vulnerable server")

sessions: Dict[str, str] = {}


@app.route("/", methods=["GET"])
def hello():
    session_id = request.cookies.get("session_id")
    if session_id is not None and session_id in sessions:
        app.logger.info(f"request with cookie {session_id[:10]}...")
        name = sessions[session_id]
    else:
        name = "stranger"
    return jsonify({"message": f"Hello {name}"}), 200


@app.route("/<name>", methods=["PUT"])
def hello_name(name):
    session_id = request.cookies.get("session_id")
    if session_id is None or session_id not in sessions:
        session_id = uuid.uuid4().hex
        app.logger.info(f"setting new cookie {session_id[:10]}...")

    sessions[session_id] = name
    response = jsonify({"message": f"{name} is now logged in!"})
    response.set_cookie(key="session_id", value=session_id)
    return response, 202


app.run(port=8080, debug=True)
