# Raito Sync

This server should not be used alone. Check this repository [Raito-Manga](https://github.com/nohackjustnoobb/Raito-Manga) for more information.

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

## Manual Setup (Not Recommended)

Make sure that you have `GoLang` installed before setting up.

```bash
# 1. Clone this repository
git clone https://github.com/nohackjustnoobb/Raito-Sync.git
cd Raito-Sync

# 2. Create and Edit the config file
cp config_template.json config.json
nano config.json

# 3. Install the dependencies
go mod download

# 4. Run the server
go run .
```

You can execute the commands one by one or copy all of them at once and create a shell script.
