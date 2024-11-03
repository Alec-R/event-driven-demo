# Event-Driven Transaction Processing System

## System Components

### Infrastructure (Docker)
- Kafka + Zookeeper: Message broker
- PostgreSQL: Transaction storage
- Airflow: Scheduling and monitoring

### Core Services
- Transaction Producer: Generates random financial transactions
- Transaction Consumer: Processes transactions and generates alerts
- Airflow DAGs: Reporting and monitoring

## System Workflow

1. **Transaction Generation**
   - Producer creates random transactions
   - Publishes to Kafka topic 'transactions'

2. **Transaction Processing**
   - Consumer reads from Kafka topic
   - Stores transactions in PostgreSQL
   - Generates alerts based on rules
   - Stores alerts in PostgreSQL

3. **Monitoring & Reporting**
   - Airflow DAGs run scheduled tasks:
     - Daily transaction reports
     - System health monitoring
     - Data cleanup
     - Alert analysis

## Data Flow
```
Producer → Kafka → Consumer → PostgreSQL → Airflow → Reports/Metrics
```

## Generic User Workflow

1. **Setup Phase**
   ```bash
   # Start infrastructure
   docker-compose up -d
   
   # Initialize Airflow
   docker-compose run airflow-webserver airflow db init
   docker-compose run airflow-webserver airflow users create [...]
   ```

2. **Operation Phase**
   - Start producer to generate transactions
   - Start consumer to process transactions
   - Monitor via:
     - Kafka CLI tools
     - PostgreSQL queries
     - Airflow UI (http://localhost:8080)

3. **Maintenance Phase**
   - Kafka topic cleanup (automated)
   - Database cleanup (via Airflow DAG)
   - System health monitoring (via Airflow DAG)
