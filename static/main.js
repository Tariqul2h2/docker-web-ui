let currentRole = "{{ role }}"; // set role from Flask

// ---------------- Containers ----------------
async function loadContainers() {
    const res = await fetch("/api/containers");
    const data = await res.json();
    const tbody = document.querySelector("#container-table tbody");
    tbody.innerHTML = "";

    data.forEach(c => {
        const row = document.createElement("tr");
        const ports = c.ports.length ? c.ports.join(", ") : "";
        const images = c.image.length ? c.image.join(", ") : "";
        row.innerHTML = `
            <td>${c.id}</td>
            <td>${c.name}</td>
            <td>${c.status}</td>
            <td>${images}</td>
            <td>${ports}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="startContainer('${c.id}')">Start</button>
                <button class="btn btn-sm btn-warning" onclick="stopContainer('${c.id}')">Stop</button>
                ${userRole === "admin" ? `<button class="btn btn-sm btn-danger" onclick="removeContainer('${c.id}')">Remove</button>` : ''}
            </td>
        `;
        tbody.appendChild(row);
    });
}

// ---------------- Images ----------------
async function loadImages() {
    const res = await fetch("/api/images");
    const data = await res.json();
    const tbody = document.querySelector("#images-table tbody");
    tbody.innerHTML = "";

    data.forEach(img => {
        const displayTag = img.tags.join(", ");
        const canRemove = userRole === "admin" && !img.in_use && !displayTag.includes("<none>");

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${img.id}</td>
            <td>${displayTag}</td>
            <td>
                ${canRemove 
                  ? `<button class="btn btn-sm btn-danger" onclick="removeImage('${encodeURIComponent(img.tags[0])}')">Remove</button>` 
                  : (img.in_use ? "<span class='text-muted'>In use</span>" : "")}
            </td>
        `;
        tbody.appendChild(row);
    });
}
// ---------------- Actions ----------------
async function createContainer() {
    const image = document.getElementById("image").value;
    const version = document.getElementById("version").value;
    const name = document.getElementById("name").value;
    const ports = document.getElementById("ports").value;

    if (!image) { alert("Image name is required!"); return; }

    await fetch("/api/containers/create", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({image, version, name, ports})
    });

    document.getElementById("image").value = "";
    document.getElementById("version").value = "";
    document.getElementById("name").value = "";
    document.getElementById("ports").value = "";

    loadContainers();
}

async function startContainer(id) {
    await fetch(`/api/containers/${id}/start`, {method:"POST"});
    loadContainers();
}

async function stopContainer(id) {
    await fetch(`/api/containers/${id}/stop`, {method:"POST"});
    loadContainers();
}

async function removeContainer(id) {
    await fetch(`/api/containers/${id}/remove`, {method:"DELETE"});
    loadContainers();
}


async function removeImage(tag) {
    if (!tag) return;

    const res = await fetch(`/api/images/${tag}/remove`, { method: "DELETE" });

    if (res.status === 400) {
        const data = await res.json();
        alert(data.msg || "Forbidden: Remove containers using this image first");
    } else if (res.status === 403) {
        alert("Forbidden: Only admin can remove images");
    } else if (res.status === 200) {
        loadImages();
    }
}

// ---------------- Load on page ----------------
document.addEventListener("DOMContentLoaded", loadImages);
document.addEventListener("DOMContentLoaded", () => {
    loadContainers();
});

