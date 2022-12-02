import asyncio
from pprint import pprint

from examples.stxchannelclient.init import channel_client


async def consumer(response):
    if response["closed"]:
        print(response["message"])
    elif response["data"] is None:
        print("No data return from server.")
    else:
        pprint(response["data"][4])


async def read_active_positions():
    await channel_client.active_positions_join(consumer)


asyncio.run(read_active_positions())
