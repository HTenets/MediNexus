import logging
from fastapi import Request

logger = logging.getLogger("medinexus")


async def logging_middleware(request: Request, call_next):
    logger.info("%s %s", request.method, request.url.path)
    return await call_next(request)
