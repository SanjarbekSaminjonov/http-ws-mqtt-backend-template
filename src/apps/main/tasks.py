"""
Celery tasks for main app
"""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def example_task(message: str):
    """
    Example Celery task

    Usage:
        from main.tasks import example_task
        example_task.delay("Hello from Celery!")
    """
    logger.info(f"Running example task: {message}")
    return f"Task completed: {message}"
