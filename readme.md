# Mini event driven syste
This toy project uses docker compose and a few simple python scripts to emulate a pub sub system with kafka streaming in the middle.
A postgres database is connected to the kafka stream and records transactions.
An airflow module emulates a small orchestration system which creates reports about aggregate transaction data.
We use docker compose to run a localhost server with a few ports open to simulate a cloud architecture.
All the passwords are stored in clear text because this thing is should run locally.

# System setup
Key requirements:
- Docker desktop
- Python 3.9 env
- kafka-python
- airflow
- psycopg2

## Setup instructions
1. Create a new python env satisfying the requireemnts
2. Create the docker image
3. Start the system with docker up -d or docker 
At that stage, the system works without the database: running the producer will populate the kafka topic, and the consumer will display incoming transactions collectetd from said topic.

4. Run setup_db.py


## Useful commands

```bash
## system
docker info
# Start the docker containers
docker-compose up -d
# check they are running
docker-compose up -d
# stop docker containers
docker-compose down

# Get into a service's container
docker-compose exec kafka bash

## logs
# All containers
docker-compose logs
# Specific container
docker-compose logs kafka | tail -n 50

## Kafka CLI
kafka-topics --list --bootstrap-server localhost:9092
kafka-topics --describe --topic transactions --bootstrap-server localhost:9092


```

### Network Configuration
- Internal container networking
- Exposed ports for development:
  - Kafka: 9092
  - PostgreSQL: 5432
  - Airflow PostgreSQL: 5433
  - Airflow UI: 8080
  - Zookeeper: 2181





