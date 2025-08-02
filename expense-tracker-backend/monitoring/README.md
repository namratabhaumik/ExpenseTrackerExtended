# Google Cloud Operations Suite Monitoring

This directory contains the monitoring configuration for the Expense Tracker application using Google Cloud Operations Suite (formerly Stackdriver).

## Overview

The monitoring setup provides:

- **Structured JSON Logging**: All application logs are formatted as JSON for easy parsing and analysis
- **Request/Response Tracking**: Automatic logging of all HTTP requests with performance metrics
- **Error Monitoring**: Comprehensive error tracking with context and stack traces
- **Performance Monitoring**: Detection and alerting for slow requests
- **Dashboard**: Pre-configured dashboard with key metrics
- **Alerts**: Automated alerting for critical issues

## Files

- `dashboard.json`: Google Cloud Operations Suite dashboard configuration
- `alerts.json`: Alerting policy configuration
- `../scripts/setup_monitoring.py`: Setup script for deploying monitoring configuration

## Setup Instructions

### 1. Prerequisites

- Google Cloud project with Cloud Run enabled
- Google Cloud SDK installed and authenticated
- Application deployed to Cloud Run

### 2. Automatic Setup

Run the setup script to configure monitoring:

```bash
cd expense-tracker-backend
python scripts/setup_monitoring.py
```

### 3. Manual Setup

If the automatic setup fails, you can configure monitoring manually:

#### Dashboard Setup

1. Go to [Google Cloud Console > Monitoring > Dashboards](https://console.cloud.google.com/monitoring/dashboards)
2. Click "Create Dashboard"
3. Import the configuration from `monitoring/dashboard.json`

#### Alert Setup

1. Go to [Google Cloud Console > Monitoring > Alerting](https://console.cloud.google.com/monitoring/alerting)
2. Click "Create Policy"
3. Use the configuration from `monitoring/alerts.json` as a reference

## Dashboard Metrics

The dashboard includes the following key metrics:

### Request Metrics

- **Request Rate**: Requests per second
- **Response Time**: 95th percentile response time
- **Slow Requests**: Count of requests taking >1 second

### Error Metrics

- **Error Rate**: Errors per second
- **Top Error Types**: Breakdown of error types
- **Request Success Rate**: Percentage of successful requests

### Performance Metrics

- **Requests by Endpoint**: Traffic distribution across API endpoints
- **Performance Trends**: Historical performance data

## Alerting

The alerting policy monitors:

- **High Error Rate**: >5% error rate over 5 minutes
- **High Response Time**: >2 second 95th percentile response time
- **Service Unavailability**: No requests received for 1 minute

## Log Structure

All logs are structured as JSON with the following key fields:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "severity": "INFO",
  "service": "expense-tracker-backend",
  "environment": "production",
  "request_id": "uuid",
  "user_id": "user123",
  "method": "GET",
  "path": "/api/expenses",
  "status_code": 200,
  "duration_ms": 150,
  "message": "Request completed"
}
```

## Error Logs

Error logs include additional context:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "severity": "ERROR",
  "service": "expense-tracker-backend",
  "environment": "production",
  "error_type": "ValidationError",
  "error_message": "Invalid expense data",
  "request_id": "uuid",
  "user_id": "user123",
  "method": "POST",
  "path": "/api/expenses"
}
```

## Viewing Logs

### Google Cloud Console

1. Go to [Google Cloud Console > Logging](https://console.cloud.google.com/logs)
2. Filter by resource type: `cloud_run_revision`
3. Filter by service name: `expense-tracker-backend`

### Command Line

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=expense-tracker-backend" --limit=50

# View error logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=expense-tracker-backend AND jsonPayload.severity=ERROR" --limit=20

# View slow requests
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=expense-tracker-backend AND jsonPayload.duration_ms>1000" --limit=10
```

## Custom Queries

### Performance Analysis

```sql
-- Average response time by endpoint
SELECT
  jsonPayload.path,
  AVG(jsonPayload.duration_ms) as avg_duration_ms,
  COUNT(*) as request_count
FROM `project-id.logs.cloud_run_revision`
WHERE resource.labels.service_name = "expense-tracker-backend"
  AND jsonPayload.duration_ms > 0
GROUP BY jsonPayload.path
ORDER BY avg_duration_ms DESC
```

### Error Analysis

```sql
-- Error rate by hour
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
  COUNTIF(jsonPayload.severity = "ERROR") as error_count,
  COUNT(*) as total_requests,
  COUNTIF(jsonPayload.severity = "ERROR") / COUNT(*) as error_rate
FROM `project-id.logs.cloud_run_revision`
WHERE resource.labels.service_name = "expense-tracker-backend"
  AND timestamp >= TIMESTAMP_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY hour
ORDER BY hour
```

## Troubleshooting

### Logs Not Appearing

1. Check that the application is deployed to Cloud Run
2. Verify that the `CLOUD_RUN` environment variable is set to `true`
3. Check that the Google Cloud Logging API is enabled
4. Verify that the service account has logging permissions

### Dashboard Not Loading

1. Ensure the dashboard is created in the correct project
2. Check that the metric filters match your service name
3. Verify that logs are being generated with the expected structure

### Alerts Not Triggering

1. Check that the alert policy is active
2. Verify that the metric filters are correct
3. Ensure that notification channels are configured
4. Check that the threshold values are appropriate for your traffic

## Best Practices

1. **Monitor Regularly**: Check the dashboard daily for trends and issues
2. **Set Appropriate Thresholds**: Adjust alert thresholds based on your application's normal behavior
3. **Use Structured Logging**: Always use the structured logging functions for consistency
4. **Include Context**: Add relevant context to error logs for easier debugging
5. **Review Performance**: Regularly analyze slow requests and optimize accordingly

## Support

For issues with Google Cloud Operations Suite:

- [Google Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [Google Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Google Cloud Support](https://cloud.google.com/support)
