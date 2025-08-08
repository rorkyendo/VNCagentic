# CometAPI Integration Guide

## Overview

VNCagentic now supports CometAPI as an Anthropic-compatible provider, allowing you to use Claude models through CometAPI's infrastructure while maintaining the same interface and functionality.

## Configuration

### 1. Environment Variables

Update your `.env` file to use CometAPI:

```bash
# API Provider Configuration
API_PROVIDER=comet
COMET_API_BASE_URL=https://api.cometapi.com

# API Key (use your CometAPI key)
ANTHROPIC_API_KEY=sk-your-cometapi-key-here

# Model Configuration
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### 2. Supported Models

CometAPI supports various Claude models:
- `claude-3-5-sonnet-20241022`
- `claude-3-haiku-20240307`
- `claude-3-opus-20240229`
- And other Anthropic models available on CometAPI

## API Endpoints

### Anthropic Compatible Endpoint

CometAPI provides an Anthropic-compatible endpoint that uses the same request/response format as the official Anthropic API:

```
POST https://api.cometapi.com/v1/messages
```

### Request Format

```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "Hello, world!"
    }
  ]
}
```

### Response Format

```json
{
  "id": "msg_012345",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello! How can I help you today?"
    }
  ],
  "model": "claude-3-5-sonnet-20241022",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 15
  }
}
```

## Testing CometAPI Connection

### Quick Test

Run the provided test script to validate your CometAPI setup:

```bash
python quick_test.py
```

### Comprehensive Test

For detailed testing with error handling:

```bash
python test_api.py
```

## Backend Integration

### Automatic Provider Selection

The backend automatically configures the appropriate API settings based on the `API_PROVIDER` environment variable:

```python
# For CometAPI
if settings.API_PROVIDER == "comet":
    api_config = {
        'base_url': settings.COMET_API_BASE_URL,
        'auth_header': 'Authorization',
        'auth_format': 'Bearer {}'
    }

# For Anthropic (default)
else:
    api_config = {
        'base_url': settings.ANTHROPIC_API_URL,
        'auth_header': 'x-api-key',
        'auth_format': '{}'
    }
```

### Agent Service

The agent service automatically uses the correct API configuration:

```python
agent = ComputerUseAgent(
    session_id=session_id,
    model=settings.ANTHROPIC_MODEL,
    api_provider=settings.API_PROVIDER,  # "comet" or "anthropic"
    api_key=settings.ANTHROPIC_API_KEY,   # CometAPI key
    api_base_url=api_config.get('base_url'),
    # ... other parameters
)
```

## Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 401  | Invalid API key | Check your CometAPI key |
| 402  | Insufficient credits | Add credits to your CometAPI account |
| 429  | Rate limited | Implement retry logic or reduce request rate |
| 500  | Server error | Retry request or contact CometAPI support |

### Automatic Fallback

The test scripts include automatic fallback logic:

1. Try `/v1/messages` (Anthropic compatible)
2. If fails, try `/v1/chat/completions` (OpenAI compatible)
3. Handle both response formats appropriately

## Migration from Anthropic

### Step 1: Get CometAPI Key

1. Visit [CometAPI](https://api.cometapi.com)
2. Sign up and get your API key
3. Add credits to your account

### Step 2: Update Configuration

1. Change `API_PROVIDER` from `anthropic` to `comet`
2. Update `ANTHROPIC_API_KEY` with your CometAPI key
3. Set `COMET_API_BASE_URL=https://api.cometapi.com`

### Step 3: Test Connection

```bash
python quick_test.py
```

### Step 4: Deploy

```bash
docker-compose up -d
```

## Advantages of CometAPI

1. **Cost Effective**: Often more affordable than direct Anthropic API
2. **Same Interface**: Drop-in replacement for Anthropic API
3. **Multiple Models**: Access to various Claude models
4. **Reliable**: Enterprise-grade infrastructure
5. **Global**: Multiple regions for low latency

## Troubleshooting

### Connection Issues

```bash
# Test basic connectivity
curl -X POST https://api.cometapi.com/v1/messages \
  -H "Authorization: Bearer YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":50,"messages":[{"role":"user","content":"test"}]}'
```

### Debug Logs

Enable debug logging in the backend:

```python
import logging
logging.getLogger("app.services.agent_service").setLevel(logging.DEBUG)
```

### Common Issues

1. **Wrong endpoint**: Ensure using `/v1/messages` not `/v1/chat/completions` for best compatibility
2. **Auth header**: Use `Authorization: Bearer` format for CometAPI
3. **Model names**: Use exact model names as provided by CometAPI
4. **Rate limits**: Implement exponential backoff for 429 errors

## Documentation Links

- [CometAPI Official Documentation](https://api.cometapi.com/doc)
- [Anthropic Compatible Endpoint](https://apidoc.cometapi.com/api-13851478.data)
- [Model List and Pricing](https://api.cometapi.com/pricing)

## Support

For CometAPI-specific issues:
- [CometAPI Discord](https://api.cometapi.com/discord)
- [CometAPI Documentation](https://api.cometapi.com/doc)

For VNCagentic integration issues:
- Check the test scripts output
- Review backend logs
- Ensure environment variables are correctly set
