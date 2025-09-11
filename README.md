# Docker Web UI

This is a simple web-based dashboard to manage Docker containers and images.

## Features

- Login with admin or user role
- List running/stopped containers
- Create, start, stop, remove containers
- View Docker images and remove unused images
- Notifications if images are in use by containers
- Supports specifying image version and port mapping


Log out and log back in (or run `newgrp docker`) to apply changes.



```bash
git clone git@github.com:Tariqul2h2/docker-web-ui.git
cd docker-web-ui
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
This will run in `0.0.0.0:5000`
> Note: Create a service file to run it in background
