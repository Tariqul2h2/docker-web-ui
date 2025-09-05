# Docker Web UI

This is a simple web-based dashboard to manage Docker containers and images.

## Features

- Login with admin or user role
- List running/stopped containers
- Create, start, stop, remove containers
- View Docker images and remove unused images
- Notifications if images are in use by containers
- Supports specifying image version and port mapping

## Prerequisites
- Python 3.8+  
- Docker installed and running  
- Add your user to the `docker` group to run Docker without `sudo`:
  ```bash
  sudo groupadd docker   # if not already created
  sudo usermod -aG docker $USER
  newgrp docker          # apply changes without logout
  ```

Log out and log back in (or run `newgrp docker`) to apply changes.


## Installation
<!-- Simpley install using apt repository
```
sudo apt update
sudo apt install dockerwebui
``` -->

```bash
git clone git@github.com:Tariqul2h2/docker-web-ui.git
cd docker-web-ui
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
This will run in `0.0.0.0:5000`

Now open your Browser, manage your containers.

Happy Containering...

> Note: Create a service file to run it in background, you can create an issue here if you want me to create the service file.

>Thank you so much for your attention