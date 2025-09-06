import os, sqlite3, docker
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecret")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET", "change-this")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)
jwt = JWTManager(app)

base_url = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
docker_client = docker.DockerClient(base_url=base_url)
try:
    docker_client.ping()
except Exception as e:
    print("Docker connection failed:", e)
    exit(1)

DB_PATH = "users.db"

# ---------------- DB + Users ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT
                )""")
    conn.commit(); conn.close()

def add_user(username, password, role="user"):
    from passlib.hash import bcrypt
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                  (username, bcrypt.hash(password), role))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def find_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username,password,role FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return {"username": row[0], "password": row[1], "role": row[2]} if row else None

# Ensure admin user exists
init_db()
admin_user = os.environ.get("ADMIN_USER", "admin")
admin_pass = os.environ.get("ADMIN_PASS", "admin123")
if not find_user(admin_user):
    add_user(admin_user, admin_pass, role="admin")

# ---------------- Auth ----------------
@app.route("/login", methods=["GET","POST"])
def login_page():
    from passlib.hash import bcrypt
    if request.method == "POST":
        user = find_user(request.form["username"])
        if user and bcrypt.verify(request.form["password"], user["password"]):
            token = create_access_token(identity=user["username"], additional_claims={"role": user["role"]})
            session["token"] = token
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

# ---------------- Web UI ----------------
@app.route("/")
def root():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if "token" not in session:
        return redirect(url_for("login_page"))
    return render_template("dashboard.html", role=session.get("role"))

# ---------------- API: Containers ----------------
@app.route("/api/containers")
def api_containers():
    if "token" not in session:
        return jsonify({"msg": "Unauthorized"}), 401
    containers = docker_client.containers.list(all=True)
    res = []
    for c in containers:
        ports = []
        port_info = c.attrs.get("NetworkSettings", {}).get("Ports", {})
        for container_port, bindings in port_info.items():
            if bindings:
                for b in bindings:
                    ports.append(f"{b.get('HostIp','0.0.0.0')}:{b.get('HostPort')}->{container_port}")
            else:
                ports.append(container_port)
        res.append({
            "id": c.short_id,
            "name": c.name,
            "status": c.status,
            "image": c.image.tags,
            "ports": ports
        })
    return jsonify(res)

@app.route("/api/containers/<cid>/start", methods=["POST"])
def api_start_container(cid):
    docker_client.containers.get(cid).start()
    return jsonify({"msg":"started"})

@app.route("/api/containers/<cid>/stop", methods=["POST"])
def api_stop_container(cid):
    docker_client.containers.get(cid).stop()
    return jsonify({"msg":"stopped"})

@app.route("/api/containers/<cid>/remove", methods=["DELETE"])
def api_remove_container(cid):
    if session.get("role") != "admin":
        return jsonify({"msg":"Forbidden"}), 403
    docker_client.containers.get(cid).remove(force=True)
    return jsonify({"msg":"removed"})

@app.route("/api/containers/<cid>/logs")
def api_logs_container(cid):
    logs = docker_client.containers.get(cid).logs(tail=200).decode()
    return jsonify({"logs": logs})

@app.route("/api/containers/create", methods=["POST"])
def api_create_container():
    if session.get("role") != "admin":
        return jsonify({"msg":"Forbidden"}), 403
    data = request.json
    image = data.get("image")
    version = data.get("version")
    name = data.get("name")
    ports_str = data.get("ports", "")
    full_image = f"{image}:{version}" if version else image
    port_bindings = {}
    if ports_str:
        for p in ports_str.split(","):
            host, container = p.strip().split(":")
            port_bindings[container] = int(host)
    cont = docker_client.containers.run(full_image, name=name or None, detach=True, ports=port_bindings or None)
    return jsonify({"id": cont.short_id, "name": cont.name})

# ---------------- API: Images ----------------
@app.route("/api/images")
def api_images():
    if "token" not in session:
        return jsonify({"msg": "Unauthorized"}), 401

    images = docker_client.images.list()
    containers = docker_client.containers.list(all=True)

    # Collect all tags in use by containers
    container_tags = set()
    for c in containers:
        container_tags.update(c.image.tags)

    res = []
    for img in images:
        in_use = any(tag in container_tags for tag in img.tags)
        res.append({
            "id": img.id[:12],
            "tags": img.tags if img.tags else ["<none>:<none>"],
            "in_use": in_use
        })
    return jsonify(res)

@app.route("/api/images/<path:tag>/remove", methods=["DELETE"])
def api_remove_image(tag):
    if session.get("role") != "admin":
        return jsonify({"msg":"Forbidden"}), 403

    # Check if any container is using this image
    containers = docker_client.containers.list(all=True)
    for c in containers:
        if tag in c.image.tags:
            return jsonify({"msg":"Cannot remove image, container still using it"}), 400

    try:
        docker_client.images.remove(tag)
        return jsonify({"msg":"removed"})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")   # default listen everywhere
    port = int(os.getenv("PORT", 5000))   # default port 5000
    app.run(host=host, port=port, debug=True)

