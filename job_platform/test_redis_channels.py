import asyncio
from channels.layers import get_channel_layer
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_platform.settings")

import django
django.setup()

channel_layer = get_channel_layer()

async def test_send():
    await channel_layer.send("test_channel", {"type": "test.message", "message": "hello from test"})

asyncio.run(test_send())
