# Cache Directory (It will be realized in the near future)

This directory stores temporary cached data to improve application performance.

## Structure
- `embeddings/` - Cached text embeddings
- `search_results/` - Cached search results
- `models/` - Cached model data

## Purpose
- **Performance**: Avoid repeated expensive operations
- **Offline Development**: Cache Azure service responses
- **Rate Limiting**: Reduce API calls to Azure services

## Files Created Automatically
- Cache files are created automatically during application usage
- Cache is cleared periodically based on TTL settings
- Manual cache clearing: delete files in this directory

## Configuration
Cache behavior can be configured via environment variables:
```bash
ENABLE_CACHE=true
CACHE_TTL_HOURS=24
MAX_CACHE_SIZE_MB=100
```
