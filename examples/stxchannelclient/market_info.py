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


async def read_market_info():
    await channel_client.market_info_join(consumer)


asyncio.run(read_market_info())
