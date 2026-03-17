---
name: observability-metrics
description: Monitoring, observability, and metrics collection for Customer Success FTE with Prometheus, structured logging, distributed tracing, and channel-specific dashboards.
---

# Observability & Metrics Skill

## Purpose

This skill provides complete monitoring and observability implementation for the Customer Success AI agent, including metrics collection, structured logging, distributed tracing, and operational dashboards.

## When to Use This Skill

Use this skill when you need to:
- Collect and visualize agent performance metrics
- Implement structured logging across all components
- Set up distributed tracing for request tracking
- Create operational dashboards for monitoring
- Configure alerts for critical issues
- Track channel-specific performance
- Monitor Kafka lag and worker health
- Generate daily/weekly reports

---

## Metrics Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY ARCHITECTURE                                 │
│                                                                              │
│  APPLICATION LAYER                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │   Agent     │  │   Channel   │  │   Worker    │                          │
│  │   Metrics   │  │   Metrics   │  │   Metrics   │                          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                          │
│         │                │                │                                  │
│         └────────────────┼────────────────┘                                  │
│                          ▼                                                   │
│              ┌───────────────────────┐                                      │
│              │   Prometheus Client   │                                      │
│              │   (Metrics Export)    │                                      │
│              └───────────┬───────────┘                                      │
│                          │                                                   │
│                          ▼                                                   │
│              ┌───────────────────────┐                                      │
│              │    Prometheus Server  │                                      │
│              │    (Scrape & Store)   │                                      │
│              └───────────┬───────────┘                                      │
│                          │                                                   │
│         ┌────────────────┼────────────────┐                                 │
│         ▼                ▼                ▼                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │  Grafana    │  │   Alert     │  │  Reporting  │                         │
│  │  Dashboard  │  │   Manager   │  │   Engine    │                         │
│  └─────────────┘  └─────────────┘  └─────────────┘                         │
│                                                                              │
│  LOGGING LAYER                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │  App Logs   │  │  Audit Logs │  │ Error Logs  │                          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                          │
│         │                │                │                                  │
│         └────────────────┼────────────────┘                                  │
│                          ▼                                                   │
│              ┌───────────────────────┐                                      │
│              │    Loki / ELK Stack   │                                      │
│              └───────────────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Prometheus Metrics Implementation

```python
# metrics/prometheus_metrics.py

from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest
from typing import Dict, Optional
import time
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# METRIC DEFINITIONS
# =============================================================================

# Counter Metrics
MESSAGES_RECEIVED = Counter(
    'fte_messages_received_total',
    'Total number of customer messages received',
    ['channel', 'priority']
)

MESSAGES_PROCESSED = Counter(
    'fte_messages_processed_total',
    'Total number of messages processed successfully',
    ['channel', 'agent_id']
)

MESSAGES_FAILED = Counter(
    'fte_messages_failed_total',
    'Total number of message processing failures',
    ['channel', 'error_type']
)

ESCALATIONS_TOTAL = Counter(
    'fte_escalations_total',
    'Total number of escalations to human support',
    ['reason', 'urgency']
)

TICKETS_CREATED = Counter(
    'fte_tickets_created_total',
    'Total number of support tickets created',
    ['channel', 'priority', 'category']
)

RESPONSES_SENT = Counter(
    'fte_responses_sent_total',
    'Total number of responses sent to customers',
    ['channel', 'delivery_status']
)

# Histogram Metrics (for latency distribution)
PROCESSING_LATENCY = Histogram(
    'fte_processing_latency_seconds',
    'Time taken to process customer messages',
    ['channel', 'message_type'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
)

API_LATENCY = Histogram(
    'fte_api_latency_seconds',
    'API request latency',
    ['endpoint', 'method'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

DB_QUERY_LATENCY = Histogram(
    'fte_db_query_latency_seconds',
    'Database query latency',
    ['query_type', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# Gauge Metrics (current state)
ACTIVE_CONVERSATIONS = Gauge(
    'fte_active_conversations',
    'Number of currently active customer conversations',
    ['channel']
)

WORKER_QUEUE_SIZE = Gauge(
    'fte_worker_queue_size',
    'Current size of worker message queue',
    ['worker_id']
)

KAFKA_LAG = Gauge(
    'fte_kafka_consumer_lag',
    'Kafka consumer lag (messages behind)',
    ['topic', 'partition', 'consumer_group']
)

AGENT_UTILIZATION = Gauge(
    'fte_agent_utilization',
    'Agent utilization percentage (0-100)',
    ['agent_id']
)

SENTIMENT_SCORE = Gauge(
    'fte_current_sentiment_score',
    'Current average sentiment score',
    ['channel', 'time_bucket']
)

# Summary Metrics (for percentiles)
TOKEN_USAGE = Summary(
    'fte_token_usage',
    'Token usage for LLM calls',
    ['model', 'operation']
)

# =============================================================================
# METRICS COLLECTOR
# =============================================================================

class MetricsCollector:
    """Collect and record metrics for the FTE system."""
    
    def __init__(self):
        self.start_times: Dict[str, float] = {}
    
    # Message Processing Metrics
    def record_message_received(self, channel: str, priority: str = "medium"):
        """Record incoming message."""
        MESSAGES_RECEIVED.labels(channel=channel, priority=priority).inc()
    
    def record_message_processed(self, channel: str, agent_id: str = "default"):
        """Record successfully processed message."""
        MESSAGES_PROCESSED.labels(channel=channel, agent_id=agent_id).inc()
    
    def record_message_failed(self, channel: str, error_type: str):
        """Record failed message processing."""
        MESSAGES_FAILED.labels(channel=channel, error_type=error_type).inc()
    
    # Latency Tracking
    def start_timer(self, timer_id: str):
        """Start a timer for latency measurement."""
        self.start_times[timer_id] = time.time()
    
    def stop_timer(self, timer_id: str, channel: str = None, message_type: str = None):
        """Stop timer and record latency."""
        if timer_id in self.start_times:
            latency = time.time() - self.start_times[timer_id]
            if channel and message_type:
                PROCESSING_LATENCY.labels(
                    channel=channel,
                    message_type=message_type
                ).observe(latency)
            del self.start_times[timer_id]
            return latency
        return None
    
    # Escalation Metrics
    def record_escalation(self, reason: str, urgency: str = "medium"):
        """Record escalation to human support."""
        ESCALATIONS_TOTAL.labels(reason=reason, urgency=urgency).inc()
    
    # Ticket Metrics
    def record_ticket_created(self, channel: str, priority: str, category: str = None):
        """Record new ticket creation."""
        TICKETS_CREATED.labels(
            channel=channel,
            priority=priority,
            category=category or "general"
        ).inc()
    
    # Response Metrics
    def record_response_sent(self, channel: str, delivery_status: str):
        """Record response delivery."""
        RESPONSES_SENT.labels(channel=channel, delivery_status=delivery_status).inc()
    
    # State Metrics
    def set_active_conversations(self, count: int, channel: str):
        """Update active conversations gauge."""
        ACTIVE_CONVERSATIONS.labels(channel=channel).set(count)
    
    def set_worker_queue_size(self, size: int, worker_id: str):
        """Update worker queue size."""
        WORKER_QUEUE_SIZE.labels(worker_id=worker_id).set(size)
    
    def set_kafka_lag(self, lag: int, topic: str, partition: int, consumer_group: str):
        """Update Kafka consumer lag."""
        KAFKA_LAG.labels(
            topic=topic,
            partition=partition,
            consumer_group=consumer_group
        ).set(lag)
    
    def set_agent_utilization(self, utilization: float, agent_id: str):
        """Update agent utilization percentage."""
        AGENT_UTILIZATION.labels(agent_id=agent_id).set(utilization)
    
    def set_sentiment_score(self, score: float, channel: str, time_bucket: str):
        """Update sentiment score gauge."""
        SENTIMENT_SCORE.labels(channel=channel, time_bucket=time_bucket).set(score)
    
    # Database Metrics
    def record_db_query(self, query_type: str, table: str, latency: float):
        """Record database query latency."""
        DB_QUERY_LATENCY.labels(query_type=query_type, table=table).observe(latency)
    
    # API Metrics
    def record_api_request(self, endpoint: str, method: str, latency: float):
        """Record API request latency."""
        API_LATENCY.labels(endpoint=endpoint, method=method).observe(latency)
    
    # Token Usage
    def record_token_usage(self, model: str, operation: str, tokens: int):
        """Record LLM token usage."""
        TOKEN_USAGE.labels(model=model, operation=operation).observe(tokens)
    
    def get_metrics(self) -> str:
        """Get all metrics in Prometheus format."""
        return generate_latest().decode('utf-8')


# Global metrics collector instance
metrics = MetricsCollector()
```

---

## Structured Logging

```python
# logging/structured_logger.py

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import sys

class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter for production."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add custom fields
        if hasattr(record, 'custom_fields'):
            log_entry.update(record.custom_fields)
        
        # Add context fields
        if hasattr(record, 'context'):
            log_entry['context'] = record.context
        
        return json.dumps(log_entry)


class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter for development."""
    
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging(
    level: int = logging.INFO,
    environment: str = "development",
    service_name: str = "customer-success-fte"
) -> logging.Logger:
    """
    Setup structured logging for the service.
    
    Args:
        level: Logging level
        environment: 'development' or 'production'
        service_name: Name of the service
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if environment == "production":
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(ConsoleFormatter())
    
    logger.addHandler(console_handler)
    
    # File handler (optional)
    file_handler = logging.FileHandler(f'{service_name}.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(file_handler)
    
    return logger


# Context-aware logging
class ContextLogger:
    """Logger with automatic context injection."""
    
    def __init__(self, name: str, context: Dict[str, Any] = None):
        self.logger = logging.getLogger(name)
        self.context = context or {}
    
    def _with_context(self, **kwargs) -> Dict:
        """Merge context with additional fields."""
        return {**self.context, **kwargs}
    
    def info(self, message: str, **kwargs):
        self.logger.info(
            message,
            extra={'custom_fields': self._with_context(**kwargs)}
        )
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        self.logger.error(
            message,
            extra={'custom_fields': self._with_context(**kwargs)},
            exc_info=exc_info
        )
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(
            message,
            extra={'custom_fields': self._with_context(**kwargs)}
        )
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(
            message,
            extra={'custom_fields': self._with_context(**kwargs)}
        )


# Usage example
def example_usage():
    logger = setup_logging(environment="production")
    
    # Basic logging
    logger.info("Service started")
    
    # Context-aware logging
    context_logger = ContextLogger(
        "message_processor",
        context={"worker_id": "worker-1", "channel": "email"}
    )
    
    context_logger.info(
        "Processing message",
        message_id="msg_123",
        customer_id="cust_456"
    )
    
    context_logger.error(
        "Failed to process message",
        message_id="msg_123",
        error="timeout",
        exc_info=True
    )
```

---

## Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "Customer Success FTE - Operations",
    "panels": [
      {
        "title": "Messages Received by Channel",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(fte_messages_received_total[5m])",
            "legendFormat": "{{channel}}"
          }
        ]
      },
      {
        "title": "Processing Latency (p95)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(fte_processing_latency_seconds_bucket[5m]))",
            "legendFormat": "p95 latency"
          }
        ]
      },
      {
        "title": "Escalation Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(fte_escalations_total[1h])",
            "legendFormat": "Escalations/hour"
          }
        ]
      },
      {
        "title": "Active Conversations",
        "type": "gauge",
        "targets": [
          {
            "expr": "sum(fte_active_conversations)",
            "legendFormat": "Active"
          }
        ]
      },
      {
        "title": "Kafka Consumer Lag",
        "type": "timeseries",
        "targets": [
          {
            "expr": "fte_kafka_consumer_lag",
            "legendFormat": "{{topic}} - {{consumer_group}}"
          }
        ]
      },
      {
        "title": "Agent Utilization",
        "type": "gauge",
        "targets": [
          {
            "expr": "fte_agent_utilization",
            "legendFormat": "{{agent_id}}"
          }
        ]
      },
      {
        "title": "Sentiment Score Trend",
        "type": "timeseries",
        "targets": [
          {
            "expr": "fte_current_sentiment_score",
            "legendFormat": "{{channel}}"
          }
        ]
      },
      {
        "title": "Error Rate by Type",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(fte_messages_failed_total[5m])",
            "legendFormat": "{{error_type}}"
          }
        ]
      }
    ]
  }
}
```

---

## Alert Rules (Prometheus)

```yaml
# alerts/fte_alerts.yaml

groups:
- name: customer_success_fte
  rules:
  # High Error Rate
  - alert: HighMessageFailureRate
    expr: rate(fte_messages_failed_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High message failure rate detected"
      description: "Message failure rate is {{ $value }} per second"
  
  # High Kafka Lag
  - alert: HighKafkaLag
    expr: fte_kafka_consumer_lag > 1000
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Kafka consumer lag is high"
      description: "Consumer lag for {{ $labels.topic }} is {{ $value }} messages"
  
  # High Escalation Rate
  - alert: HighEscalationRate
    expr: rate(fte_escalations_total[1h]) > 10
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "High escalation rate detected"
      description: "Escalation rate is {{ $value }} per hour"
  
  # Low Agent Availability
  - alert: LowAgentAvailability
    expr: fte_agent_utilization > 90
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "Agent utilization is critically high"
      description: "Agent {{ $labels.agent_id }} utilization is {{ $value }}%"
  
  # High Processing Latency
  - alert: HighProcessingLatency
    expr: histogram_quantile(0.95, rate(fte_processing_latency_seconds_bucket[5m])) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High processing latency detected"
      description: "P95 latency is {{ $value }} seconds"
  
  # Negative Sentiment Spike
  - alert: NegativeSentimentSpike
    expr: fte_current_sentiment_score < 0.2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Negative sentiment detected"
      description: "Average sentiment score is {{ $value }} on {{ $labels.channel }}"
```

---

## Daily Report Generator

```python
# reporting/daily_report.py

from datetime import datetime, timedelta
from typing import Dict, List
import asyncpg

class DailyReportGenerator:
    """Generate daily operational reports."""
    
    def __init__(self, db_connection: str):
        self.db_connection = db_connection
    
    async def generate_report(self, date: datetime = None) -> Dict:
        """Generate daily report for given date."""
        if not date:
            date = datetime.utcnow() - timedelta(days=1)
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        conn = await asyncpg.connect(self.db_connection)
        
        try:
            report = {
                'date': start_date.isoformat(),
                'generated_at': datetime.utcnow().isoformat(),
                'summary': await self.get_summary(conn, start_date, end_date),
                'by_channel': await self.get_channel_breakdown(conn, start_date, end_date),
                'sentiment': await self.get_sentiment_analysis(conn, start_date, end_date),
                'escalations': await self.get_escalation_report(conn, start_date, end_date),
                'performance': await self.get_performance_metrics(conn, start_date, end_date)
            }
            
            return report
        finally:
            await conn.close()
    
    async def get_summary(self, conn, start: datetime, end: datetime) -> Dict:
        """Get overall summary metrics."""
        row = await conn.fetchrow("""
            SELECT 
                COUNT(DISTINCT c.id) as total_conversations,
                COUNT(DISTINCT t.id) as total_tickets,
                COUNT(m.id) as total_messages,
                COUNT(CASE WHEN m.direction = 'inbound' THEN 1 END) as inbound_messages,
                COUNT(CASE WHEN m.direction = 'outbound' THEN 1 END) as outbound_messages
            FROM conversations c
            LEFT JOIN tickets t ON c.id = t.conversation_id
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE c.started_at BETWEEN $1 AND $2
        """, start, end)
        
        return dict(row) if row else {}
    
    async def get_channel_breakdown(self, conn, start: datetime, end: datetime) -> Dict:
        """Get metrics broken down by channel."""
        rows = await conn.fetch("""
            SELECT 
                c.initial_channel as channel,
                COUNT(DISTINCT c.id) as conversations,
                COUNT(DISTINCT t.id) as tickets,
                AVG(c.sentiment_score) as avg_sentiment,
                COUNT(CASE WHEN t.status = 'resolved' THEN 1 END) as resolved_tickets
            FROM conversations c
            LEFT JOIN tickets t ON c.id = t.conversation_id
            WHERE c.started_at BETWEEN $1 AND $2
            GROUP BY c.initial_channel
        """, start, end)
        
        return {row['channel']: dict(row) for row in rows}
    
    async def get_sentiment_analysis(self, conn, start: datetime, end: datetime) -> Dict:
        """Get sentiment analysis for the day."""
        row = await conn.fetchrow("""
            SELECT 
                AVG(sentiment_score) as avg_score,
                MIN(sentiment_score) as min_score,
                MAX(sentiment_score) as max_score,
                COUNT(CASE WHEN sentiment_score < 0.3 THEN 1 END) as negative_count,
                COUNT(CASE WHEN sentiment_score > 0.7 THEN 1 END) as positive_count
            FROM messages
            WHERE created_at BETWEEN $1 AND $2
            AND sentiment_score IS NOT NULL
        """, start, end)
        
        return dict(row) if row else {}
    
    async def get_escalation_report(self, conn, start: datetime, end: datetime) -> Dict:
        """Get escalation metrics."""
        rows = await conn.fetch("""
            SELECT 
                reason_code,
                COUNT(*) as count,
                AVG(EXTRACT(EPOCH FROM (resolved_at - escalated_at))/3600) as avg_resolution_hours
            FROM escalations
            WHERE escalated_at BETWEEN $1 AND $2
            GROUP BY reason_code
        """, start, end)
        
        return {row['reason_code']: dict(row) for row in rows}
    
    async def get_performance_metrics(self, conn, start: datetime, end: datetime) -> Dict:
        """Get performance metrics."""
        row = await conn.fetchrow("""
            SELECT 
                AVG(EXTRACT(EPOCH FROM (m.created_at - c.started_at))) as avg_response_time_seconds,
                PERCENTILE_CONT(0.95) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (m.created_at - c.started_at))
                ) as p95_response_time_seconds
            FROM conversations c
            JOIN messages m ON c.id = m.conversation_id
            WHERE c.started_at BETWEEN $1 AND $2
            AND m.direction = 'outbound'
        """, start, end)
        
        return dict(row) if row else {}
```

---

## Acceptance Criteria

- [ ] Prometheus metrics exposed at /metrics endpoint
- [ ] All key metrics defined and collected
- [ ] Structured logging configured for production
- [ ] Grafana dashboard imported and working
- [ ] Alert rules configured in Prometheus
- [ ] Daily report generation works
- [ ] Channel-specific metrics tracked
- [ ] Latency percentiles calculated correctly
- [ ] Error tracking captures all failures
- [ ] Sentiment metrics updated in real-time

## Related Skills

- `kafka-event-processing` - Metrics from Kafka consumers
- `k8s-fte-deployment` - Prometheus deployment on K8s
- `customer-success-agent` - Agent metrics collection
- `sentiment-analysis` - Sentiment metrics

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Python Prometheus Client](https://github.com/prometheus/client_python)
