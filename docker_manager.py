import docker

class DockerManager:
    def __init__(self, base_url="unix:///var/run/docker.sock"):
        self.client = docker.DockerClient(base_url=base_url)
        try:
            self.client.ping()
        except Exception as e:
            raise Exception(f"Docker connection failed: {e}")

    def list_containers(self):
        containers = self.client.containers.list(all=True)
        result = []
        for c in containers:
            ports = []
            port_info = c.attrs.get("NetworkSettings", {}).get("Ports", {})
            for container_port, bindings in port_info.items():
                if bindings:
                    for b in bindings:
                        ports.append(f"{b.get('HostIp','0.0.0.0')}:{b.get('HostPort')}->{container_port}")
                else:
                    ports.append(container_port)
            result.append({
                "id": c.short_id,
                "name": c.name,
                "status": c.status,
                "image": c.image.tags,
                "ports": ports
            })
        return result

    def start_container(self, cid):
        self.client.containers.get(cid).start()

    def stop_container(self, cid):
        self.client.containers.get(cid).stop()

    def remove_container(self, cid):
        self.client.containers.get(cid).remove(force=True)

    def get_logs(self, cid, tail=200):
        return self.client.containers.get(cid).logs(tail=tail).decode()

    def create_container(self, image, version=None, name=None, ports=None):
        full_image = f"{image}:{version}" if version else image
        port_bindings = {}
        if ports:
            for p in ports.split(","):
                host, container = p.strip().split(":")
                port_bindings[container] = int(host)
        container = self.client.containers.run(full_image, name=name or None, detach=True, ports=port_bindings or None)
        return container

    def list_images(self):
        images = self.client.images.list()
        containers = self.client.containers.list(all=True)
        container_tags = set()
        for c in containers:
            container_tags.update(c.image.tags)

        result = []
        for img in images:
            in_use = any(tag in container_tags for tag in img.tags)
            result.append({
                "id": img.id[:12],
                "tags": img.tags if img.tags else ["<none>:<none>"],
                "in_use": in_use
            })
        return result

    def remove_image(self, tag):
        containers = self.client.containers.list(all=True)
        for c in containers:
            if tag in c.image.tags:
                raise Exception("Cannot remove image, container still using it")
        self.client.images.remove(tag)
