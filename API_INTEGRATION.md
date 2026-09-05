# Veritas Developer API

Veritas exposes a versioned developer API for organization-to-organization integrations.

## Provision an API key

1. Create/sign in to a Veritas account.
2. Obtain the dashboard bearer token from the authenticated session.
3. Call `POST /v1/api-keys`:

```http
POST /v1/api-keys
Authorization: Bearer <dashboard-access-token>
Content-Type: application/json
```

Body:

```json
{"organization_name":"Acme Verification","name":"Production"}
```

The raw API key is returned once. Store it in the integrating organization's server-side secret manager. Do not put it in browser code.

## Image detection

```bash
curl -X POST "https://YOUR_API_HOST/v1/predict/image" \
  -H "X-API-Key: vrs_live_xxx" \
  -F "file=@sample.jpg"
```

## Video and audio detection

Use the same `X-API-Key` header and multipart `file` field with:

- `POST /v1/predict/video`
- `POST /v1/predict/audio`

The video response also includes sampled-frame count and the available auxiliary signal scores.

## Example response

```json
{
  "prediction_id": 123,
  "filename": "sample.jpg",
  "label": "Possibly Fake",
  "real_percent": 23.4,
  "fake_percent": 76.6,
  "raw_fake_probability": 0.766,
  "model": "veritas-mobilenetv2"
}
```

## Usage

`GET /v1/usage` returns request totals and the configured rolling 24-hour API-key limit. The default is 100 requests per API key per 24 hours and can be changed with `API_DAILY_LIMIT`.

## Interactive documentation

The FastAPI OpenAPI UI is available at `/docs` and the schema at `/openapi.json`.
