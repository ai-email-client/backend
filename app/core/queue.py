# app/core/queue.py
import asyncio
import logging
from app.schemas.request import DataInsertSummaryRequest

logger = logging.getLogger(__name__)

WORKER_BATCH_SIZE  = 3
BATCH_DELAY_SECONDS = 3

_summary_queue: asyncio.Queue = asyncio.Queue()
_queued_ids: set[str] = set()


def is_queued(source_email_id: str) -> bool:
    return source_email_id in _queued_ids


async def enqueue_summary(task_fn, req: DataInsertSummaryRequest) -> bool:
    task_id = str(req.id)

    if task_id in _queued_ids:
        logger.info(f"[Queue] msg_id={task_id} already queued.")
        return False

    _queued_ids.add(task_id)
    await _summary_queue.put((task_fn, req))
    logger.info(f"[Queue] Enqueued msg_id={task_id}. Queue size={_summary_queue.qsize()}")
    return True

async def summary_worker():
    logger.info("[Worker] Started.")
    while True:
        batch = []
        try:
            batch.append(await _summary_queue.get())
            for _ in range(WORKER_BATCH_SIZE - 1):
                if _summary_queue.empty():
                    break
                batch.append(_summary_queue.get_nowait())
        except asyncio.QueueEmpty:
            pass

        if not batch:
            continue

        logger.info(f"[Worker] Processing batch of {len(batch)}")
        await asyncio.gather(*[_run_task(fn, req) for fn, req in batch])

        if not _summary_queue.empty():
            logger.info(f"[Worker] Waiting {BATCH_DELAY_SECONDS}s before next batch...")
            await asyncio.sleep(BATCH_DELAY_SECONDS)


async def _run_task(task_fn, req):
    task_id = str(req.id)
    loop = asyncio.get_event_loop()
    try:
        import inspect
        if inspect.iscoroutinefunction(task_fn):
            await task_fn(req)
        else:
            await loop.run_in_executor(None, task_fn, req)
        logger.info(f"[Worker] Done msg_id={task_id}")
    except Exception as e:
        logger.error(f"[Worker] Error msg_id={task_id}: {e}")
    finally:
        _queued_ids.discard(task_id)
        _summary_queue.task_done()