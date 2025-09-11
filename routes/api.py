from flask import Blueprint, jsonify, request, session
from docker_manager import DockerManager

api = Blueprint('api', __name__)
docker_mgr = DockerManager()

@api.route("/containers")
def containers():
    if "token" not in session:
        return jsonify({"msg": "Unauthorized"}), 401
    return jsonify(docker_mgr.list_containers())

@api.route("/containers/<cid>/start", methods=["POST"])
def start_container(cid):
    docker_mgr.start_container(cid)
    return jsonify({"msg":"started"})

@api.route("/containers/<cid>/stop", methods=["POST"])
def stop_container(cid):
    docker_mgr.stop_container(cid)
    return jsonify({"msg":"stopped"})

@api.route("/containers/<cid>/remove", methods=["DELETE"])
def remove_container(cid):
    if session.get("role") != "admin":
        return jsonify({"msg":"Forbidden"}), 403
    docker_mgr.remove_container(cid)
    return jsonify({"msg":"removed"})

@api.route("/containers/<cid>/logs")
def logs_container(cid):
    logs = docker_mgr.get_logs(cid)
    return jsonify({"logs": logs})

@api.route("/containers/create", methods=["POST"])
def create_container():
    if session.get("role") != "admin":
        return jsonify({"msg":"Forbidden"}), 403
    data = request.json
    try:
        cont = docker_mgr.create_container(
            image=data.get("image"),
            version=data.get("version"),
            name=data.get("name"),
            ports=data.get("ports")
        )
        return jsonify({"id": cont.short_id, "name": cont.name})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@api.route("/images")
def images():
    if "token" not in session:
        return jsonify({"msg": "Unauthorized"}), 401
    return jsonify(docker_mgr.list_images())

@api.route("/images/<path:tag>/remove", methods=["DELETE"])
def remove_image(tag):
    if session.get("role") != "admin":
        return jsonify({"msg":"Forbidden"}), 403
    try:
        docker_mgr.remove_image(tag)
        return jsonify({"msg":"removed"})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
