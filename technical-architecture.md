# Technical Architecture Documentation

## Python Modules & Code Structure

### Producer Module
```
producer/
└── transaction_producer.py
    - Creates random transactions
    - Uses Kafka producer
    - Implements error handling and logging
```

### Consumer Module
```
consumer/
└── transaction_processor.py
    - Processes Kafka messages
    - Implements alert logic
    - Handles database operations
    - Includes graceful shutdown
```

### Database Utilities
```
utils/
├── database.py
    - Database connection management
    - Transaction & alert CRUD operations
    - Connection pooling
├── kafka_cleanup.py
    - Topic management
    - Cleanup operations
    - Scaling utilities
```

### Airflow DAGs
```
dags/
├── transaction_reporting_dag.py
    - Daily transaction aggregation
    - Alert analysis
    - Report generation
└── system_monitoring_dag.py
    - Kafka health checks
    - PostgreSQL monitoring
    - System metrics collection
```

## System Design

### Event Flow
1. **Transaction Generation**
   - Random transaction creation
   - JSON serialization
   - Kafka message production

2. **Message Processing**
   - Kafka consumer group management
   - Transaction validation
   - Alert rule evaluation
   - Database persistence

3. **Data Management**
   - PostgreSQL schemas for transactions and alerts
   - Indexed fields for efficient querying
   - Retention policies

4. **Monitoring & Reporting**
   - Scheduled health checks
   - Performance metrics collection
   - Automated reporting
   - Data cleanup routines

### Database Schema
```sql
transactions
├── transaction_id (PK)
├── account_id (Indexed)
├── transaction_type
├── amount
├── timestamp (Indexed)
└── processed_at

alerts
├── alert_id (PK)
├── transaction_id (FK)
├── alert_type
├── alert_message
└── created_at
```

## Docker Infrastructure

### Service Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Kafka     │     │  PostgreSQL │     │   Airflow   │
│  (Broker)   │     │  (Storage)  │     │ (Scheduler) │
└─────────────┘     └─────────────┘     └─────────────┘
      ▲                   ▲                    ▲
      │                   │                    │
      └───────────────────┼────────────────────┘
                         │
                  ┌─────────────┐
                  │  Zookeeper  │
                  │  (Kafka)    │
                  └─────────────┘
```

### Container Configuration
1. **Messaging Layer**
   - Kafka broker
   - Zookeeper for Kafka coordination
   - Configured for local development

2. **Storage Layer**
   - PostgreSQL for transactions
   - Separate PostgreSQL for Airflow
   - Persistent volumes

3. **Orchestration Layer**
   - Airflow webserver
   - Airflow scheduler
   - Local executor setup

### Volume Management
```
Named Volumes:
└── postgres_data: Persistent transaction storage

Bind Mounts:
├── ./dags: Airflow DAG files
└── ./airflow-data: Reports and metrics
```

### Network Configuration
- Internal container networking
- Exposed ports for development:
  - Kafka: 9092
  - PostgreSQL: 5432
  - Airflow PostgreSQL: 5433
  - Airflow UI: 8080
  - Zookeeper: 2181

### Resource Management
- Container health checks
- Service dependencies
- Graceful shutdown handling
- Volume persistence
- Port conflict prevention
