import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_errors(coro, default_return=None):
    """
    Bắt các ngoại lệ phổ biến như TimeoutError hoặc lỗi hệ thống khác.
    """
    try:
        return await coro
    except asyncio.TimeoutError:
        logger.error("Thao tác quá thời gian chờ (TimeoutError).")
        return {"status": "error", "message": "Task timed out"}
    except Exception as e:
        logger.error(f"Phát hiện lỗi không xác định: {str(e)}")
        return {"status": "error", "message": str(e)}