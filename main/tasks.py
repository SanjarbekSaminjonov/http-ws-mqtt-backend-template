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


@shared_task
def send_device_command(device_id: int, command: dict):
    """
    Example: Send command to device via MQTT

    Usage:
        from main.tasks import send_device_command
        send_device_command.delay(device_id=1, command={"action": "start"})
    """
    from mqtt_service.commander import publish_mqtt_message

    # TODO: Get device from DB and publish to its MQTT topic
    # device = Device.objects.get(id=device_id)
    # publish_mqtt_message(device.mqtt_topic, command)

    logger.info(f"Command sent to device {device_id}: {command}")
    return True
