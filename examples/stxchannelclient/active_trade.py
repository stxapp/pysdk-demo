import asyncio
from pprint import pprint

from examples.stxchannelclient.init import channel_client

"""
What is Consumer?"
It's a function or service that would be triggered by the async client, means that the channels' message will
automatically hand off to a message listener which passes to the consumer that has been registered.
The client consumes the message when a session thread invokes the onMessage() method of the message listener object.
"""


async def consumer(response):
    # Here response would be the response passed by the listener of the async client
    if response["closed"]:
        print(response["message"])
    elif response["data"] is None:
        print("No data return from server.")
    else:
        pprint(response["data"][4])


# StxChannelClient provides the channel function as an asynchronous tasks, in order to execute
# them async in a continuous loop using the asyncio module's event loop,
# asynio is Python's built-in package that provides a foundation and API for running and managing coroutines.

asyncio.run(channel_client.active_trades_join(consumer))
