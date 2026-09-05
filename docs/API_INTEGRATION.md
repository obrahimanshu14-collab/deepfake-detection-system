# Veritas Developer API

Veritas exposes a versioned `/v1` API for server-to-server integrations.

## Authentication

Developer inference endpoints use `X-API-Key`. Never expose an API key in browser JavaScript, mobile apps, or public repositories.

Provision a key from an authenticated account with:

```http
POST /v1/api-keys
Authorization: Bearer <user-jwt>
Content-Type: application/json

{"organization_name":"Acme Verification","name":"Production"}
```

The returned raw API key is displayed once. Store it in the consuming organization's secret manager.

## Inference

```http
POST /v1/predict/image
X-API-Key: vrs_live_...
Content-Type: multipart/form-data
```

Video and audio use the same contract at `/v1/predict/video` and `/v1/predict/audio`.

A normalized response includes:

```json
{
  "prediction_id": 123,
  "filename": "sample.jpg",
  "label": "Possibly Fake",
  "real_percent": 31.4,
  "fake_percent": 68.6,
  "raw_fake_probability": 0.686,
  "model": "veritas-mobilenetv2"
}
```

Video additionally reports `frames_analyzed` and auxiliary signal details.

## Usage and limits

`GET /v1/usage` returns request usage for the current API key. The rolling 24-hour request limit is configurable with `API_DAILY_LIMIT` and defaults to 100.

## Privacy behavior

Raw media uploaded through the developer API is used for inference and deleted after processing. Only prediction metadata is persisted.

## Production integration pattern

```text
Organization backend
        |
        | X-API-Key
        v
 Veritas /v1/predict/*
        |
        v
 Detection engine
        |
        +--> normalized result
        +--> usage/audit record
```
