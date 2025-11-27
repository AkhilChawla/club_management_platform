# Event & Club Management Platform with RabbitMQ

This project demonstrates a microservice‑based architecture for managing university clubs, their events and associated ticketing.  Each bounded context lives in its own Django service and they communicate over HTTP as well as asynchronously via a RabbitMQ message broker.  The core logic is encapsulated in the services themselves.

## Architecture

The solution is split into three core services and one message broker:

| Service                    | Purpose                                                                                                                                                         | Port                            |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| **Clubs Service**    | Manages student clubs: create clubs (pending approval), approve clubs, list clubs and manage club memberships.                                                  | 8001                            |
| **Events Service**   | Lets club officers create events; students can list events and RSVP.                                                                                            | 8002                            |
| **Payments Service** | Provides ticket types for events and accepts orders (simulated payments).                                                                                       | 8003                            |
| **RabbitMQ Broker**  | Acts as a message bus for inter‑service communication.  Events are published to the `events` queue whenever a club or event is created, approved or updated. | 5672 (AMQP), 15672 (management) |

Each service maintains its own SQLite database; there is **no shared database**.  Synchronous interactions use RESTful HTTP APIs defined in the `views.py` of each service.  Asynchronous notifications are emitted via RabbitMQ when key actions occur (e.g. a club is created or approved, a member joins a club, an event is created, a user RSVPs or places an order).  These messages can be consumed by additional services (e.g. an email notification service or analytics pipeline) without coupling the producers to the consumers.

## Message Broker Integration

RabbitMQ is configured as an additional container in `docker-compose.yml`.  The services obtain connection details from the environment variables `RABBITMQ_HOST`, `RABBITMQ_USER` and `RABBITMQ_PASS`.  A helper function in each service uses the [`pika`](https://pika.readthedocs.io/) client library to publish JSON messages to a durable queue named `events`.  The payload structure follows this shape:

```json
{
  "type": "club_created",   // or club_approved, member_added, event_created, rsvp_created, order_created
  "data": {                   // domain‑specific fields for the event
    "id": "…",              // UUID of the resource
    "name": "…",            // Additional properties depending on the event type
    …
  }
}
```

Running the project with RabbitMQ lets you inspect the messages via the RabbitMQ Management UI at http://localhost:15672 (default credentials are `user` / `password` as set in `docker-compose.yml`).

## Prerequisites

* Python 3.10+
* [Docker](https://www.docker.com/) and [docker‑compose](https://docs.docker.com/compose/) (recommended for a quick setup)
* Alternatively, you can run each service locally without containers (see below).

## Quick start with Docker Compose

The easiest way to run the whole stack is via docker-compose.  From the project root:

```bash
docker-compose up --build
```

This command builds the Docker images for each service, starts the RabbitMQ broker and launches all containers.  Services will be available at the following ports on your host machine:

* Clubs Service: http://localhost:8001
* Events Service: http://localhost:8002
* Payments Service: http://localhost:8003
* RabbitMQ Management UI: http://localhost:15672 (login with `user` / `password`)

Each Django service automatically applies migrations and loads sample data (from `seed_data.json`) when started via the supplied `entrypoint.sh` scripts.

## Running services locally without Docker

If you prefer to run the services directly on your machine, you can do so in separate terminals.  First install the Python dependencies:

```bash
pip install -r requirements.txt
```

Then open three terminals and start each service:

```bash
# Terminal 1 – start RabbitMQ (requires RabbitMQ installed locally)
rabbitmq-server

# Terminal 2 – Clubs Service
cd services/clubs_service
export RABBITMQ_HOST=localhost
export RABBITMQ_USER=user
export RABBITMQ_PASS=password
python manage.py migrate
python manage.py loaddata seed_data.json  # optional sample data
python manage.py runserver 0.0.0.0:8001

# Terminal 3 – Events Service
cd services/events_service
export RABBITMQ_HOST=localhost
export RABBITMQ_USER=user
export RABBITMQ_PASS=password
python manage.py migrate
python manage.py loaddata seed_data.json
python manage.py runserver 0.0.0.0:8002

# Terminal 4 – Payments Service
cd services/payments_service
export RABBITMQ_HOST=localhost
export RABBITMQ_USER=user
export RABBITMQ_PASS=password
python manage.py migrate
python manage.py loaddata seed_data.json
python manage.py runserver 0.0.0.0:8003

```

If you run without Docker, you must supply your own RabbitMQ server listening on `localhost:5672` and create the user/password specified in the environment variables.  Using Docker Compose is recommended to avoid manual setup.
