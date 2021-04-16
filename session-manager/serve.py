from typing import Dict
from flask import Flask, Response, request


app = Flask("session manager")

sessions: Dict[str, dict] = {}


@app.route("/session/<session_id>", methods=["PUT"])
def create_session(session_id):
    if request.json is not None:
        sessions[session_id] = request.json
        return Response(status=202)
    else:
        return Response(status=400)


@app.route("/session/<session_id>", methods=["GET"])
def get_session(session_id):
    return sessions[session_id], 200 if session_id in sessions else Response(status=404)


app.run(port=8888, debug=True)
