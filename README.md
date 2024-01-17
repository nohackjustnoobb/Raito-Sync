# Raito Sync

TODO: description

## Quick Start

1. Create a `config.json` file based on the `config_template.json`.

2. Create a `docker-compose.yml` file like this:

```yml
version: "3.7"

services:
  raito-sync:
    image: nohackjustnoobb/raito-sync
    container_name: raito-sync
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./db.sqlite3:/app/db.sqlite3
      - ./config.json:/app/config.json:ro
```

3. Create the container

```bash
sudo docker-compose up -d
```
