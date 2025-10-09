export COMPOSE_FILE := "docker-compose.local.yml"
export COMPOSE_PROJECT_NAME := "flashcards"

## Just does not yet manage signals for subprocesses reliably, which can lead to unexpected behavior.
## Exercise caution before expanding its usage in production environments.
## For more information, see https://github.com/casey/just/issues/2473 .

COMPOSE_CMD := "podman-compose"

# Default command to list all available commands.
default:
    @just --list

# build: Build python image.
build:
    @echo "Building python image..."
    @{{COMPOSE_CMD}} build

# up: Start up containers.
up:
    @echo "Starting up containers..."
    @{{COMPOSE_CMD}} --podman-run-args=--replace up -d --remove-orphans

# down: Stop containers.
down:
    @echo "Stopping containers..."
    @{{COMPOSE_CMD}} down

# prune: Remove containers and their volumes.
prune *args:
    @echo "Killing containers and removing volumes..."
    @{{COMPOSE_CMD}} down -v {{args}}

# logs: View container logs
logs *args:
    @{{COMPOSE_CMD}} logs -f {{args}}

# manage: Executes `manage.py` command.
manage +args:
    @{{COMPOSE_CMD}} run --rm django python ./manage.py {{args}}

# compose: Executes `podman-compose` command.
compose +args:
    @{{COMPOSE_CMD}} {{args}}
