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
- Docker installed and running  
- Add your user to the `docker` group to run Docker without `sudo`:
  ```bash
  sudo groupadd docker   # if not already created
  sudo usermod -aG docker $USER
  newgrp docker          # apply changes without logout
  ```

Log out and log back in (or run `newgrp docker`) to apply changes.


## Installation 
### Option 1
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
> Note: Create a service file to run it in background

### Option 2
Run the following command:  
Option 1: [defaults: port 5000, user: admin, password:admin123]
```
docker run -v /var/run/docker.sock:/var/run/docker.sock tariqul2h2/dockerwebui:latest
```

Option 2: [#DIY]
```
docker run -d -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock -e ADMIN_USER=superuser -e ADMIN_PASS=superpass -e PORT=5000 tariqul2h2/dockerwebui:latest
```


Now open your Browser, manage your containers.

Happy Containering...


>Thank you so much for your attention