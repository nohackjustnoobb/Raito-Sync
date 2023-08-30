# Better Manga Server

Better Manga App is an open-source project aimed at simplifying the process of reading manga. The project comprises two parts: front-end and back-end. This repository contains the back-end component of the project. The front-end interface can be found in the following repository: [Better-Manga-Web-Client](https://github.com/nohackjustnoobb/Better-Manga-Web-Client).

## Quick Start

### Running with Docker

The easiest way to start with the server is by running it as a Docker container.

1. Create `docker-compose.yml`

The following file is an example of what the files should resemble or look like.

`docker-compose.yml`

```bash
version: "3.7"

services:
  better-manga-server:
    image: nohackjustnoobb/better-manga-server
    container_name: better-manga-server
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=<SECRET KEY>
      # optional
      # key required to create new accounts
      # leave blank to allow everyone to create new accounts
      - REGISTER_KEY=<REGISTER KEY>
      # optional
      # check https://github.com/nohackjustnoobb/Better-Manga-Proxy for more information
      - PROXY_ADDRESS=<PROXY ADDRESS>
    volumes:
      - ./db.sqlite3:/app/db.sqlite3
```

2. Start the server

The following command will pull the docker image and start the server.

```bash
sudo docker-compose up -d
```

### Manual Setup

In order to run the server, it is essential to create a `.env` file. An example of the `.env` file is shown below:

`.env`

```python
SECRET_KEY=<SECRET KEY>

# optional
# key required to create new accounts
# leave blank to allow everyone to create new accounts
REGISTER_KEY=<REGISTER KEY>

#optional
PROXY_ADDRESS=<PROXY ADDRESS>
```

Make sure that you have Python installed.

```bash
# 1. Clone the repository
# 2. Install the dependencies
# 3. Start the server
git clone https://github.com/nohackjustnoobb/Better-Manga-Server
cd Better-Manga-Server && pip install -r requirements.txt
uwsgi --ini uwsgi.ini
```
