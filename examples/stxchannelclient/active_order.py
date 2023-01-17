import asyncio
from pprint import pprint

from examples.stxchannelclient.init import channel_client

"""
What is Consumer?"
It's a function or service that would be triggered by the async client, means that the channels' message will
automatically hand off to a message listener which passes to the consumer that has been registered.
The client consumes the message when a session thread invokes the onMessage() method of the message listener object.
Our ChannelClient accepts different consumers for each event. The available events are the following:
on_open     it triggers when connected with the server
on_message  it triggers when server send any message
on_close    it triggers when connection to the server is closed
on_error    it triggers when any error send by the server or exception occurs
default     all of the above events are optional to be set, if you want a
            generic method to be run as default you can pass as it with default kwarg
"""


async def on_open(response):
    # message passed by the listener of the async client when connect with the server
    # you can perform any initial operation on this event
    print(f"Successfully connected with the server with message, {response}")


async def on_message(response):
    # message passed by the listener of the async client when server send the message
    # you can perform any post operation on this event
    print(response["data"])


async def default(response):
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

# following are the available events that can be passed to the channel:
#    on_open        it triggers when connected with the server
#    on_message     it triggers when server send any message
#    on_close       it triggers when connection to the server is closed
#    on_error       it triggers when any error send by the server or exception occurs
#    default        all of the above events are optional to be set, if you want a
#                   generic method to be run as default you can pass as it with default kwarg
# here you can see that am only passing functions for on_open and on_message events
# with a default function to handle other events
asyncio.run(
    channel_client.active_orders_join(
        on_open=on_open,
        on_message=on_message,
        default=default,
    )
)
