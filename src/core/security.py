import time
from fastapi import Request, HTTPException, status
from redis.asyncio import Redis
import os

# Rate Limiter Config
# 60 requests per minute per IP
RATE_LIMIT_DURATION = 60 
RATE_LIMIT_REQUESTS = 60

async def rate_limiter(request: Request):
    # Get Redis URL from environment
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis = Redis.from_url(redis_url, decode_responses=True)
    
    # Simple IP-based key
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    try:
        current_count = await redis.get(key)
        
        if current_count and int(current_count) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again in a minute."
            )
        
        # Increment or initialize
        async with redis.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            if not current_count:
                await pipe.expire(key, RATE_LIMIT_DURATION)
            await pipe.execute()
            
    finally:
        await redis.close()
