import argparse
import asyncio
import logging
from pprint import pprint

from stxsdk import StxChannelClient
from stxsdk.config.channels import CHANNELS

logger = logging.getLogger(__file__)

CHANNEL_NAMES = list(CHANNELS)
CHANNEL_CLIENT = StxChannelClient()

# Available channels:
#    portfolio
#    market_info
#    active_trades
#    active_orders
#    active_settlements
#    active_positions


async def on_open(message):
    # message passed by the listener of the async client when connect with the server
    # you can perform any initial operation on this event
    print(f"Successfully connected with the server with message, {message}")


async def on_message(message):
    # message passed by the listener of the async client when server send the message
    # you can perform any post operation on this event
    print(message["data"][4])


async def default(message):
    # message passed by the listener of the async client when connect for any other event
    # it's a default function that will be trigger for the events whose relative consumers
    # functions are not passed you can perform any operation on this event as default case
    print(message)


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Initiate connection with STX SDK Channels."
    )
    parser.add_argument(
        "--channel",
        type=str,
        help="Channel Name",
        required=True,
        choices=CHANNEL_NAMES,
    )
    parser.add_argument(
        "--email",
        type=str,
        help="Email Address",
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Password",
    )
    return parser.parse_args()


def main():
    # initializing the arguments' parser to get the user inputs
    args = get_arguments()
    # taking email as input if user doesn't provide it as an argument
    email = args.email or input("Please enter email address: ")
    # taking password as input if user doesn't provide it as an argument
    password = args.password or input("Please enter password: ")
    # both email and password are required fields, either passed as argument or input
    if not email or not password:
        raise Exception("Please provide valid email and password")
    # using StxClient object to initiate the login
    login_response = CHANNEL_CLIENT.login(params={"email": email, "password": password})
    # if the provided credentials are not correct it would get success False flag in response
    # with relative error message
    if not login_response["success"]:
        logger.error(f"Failed to authenticate with the response: {login_response}")
    # if the credentials are correct but 2FA is enabled then user won;t get fully authenticated
    # instead a code will be sent on the email and required to perform 2FA confirmation
    # here checking for confirm2Fa sub-string in the response message because the
    # login response will success flag True but with message to go through confirm2Fa procedure
    if "confirm2Fa" in login_response["message"]:
        logger.info(login_response["message"])
        # taking sent 2FA code as input from the user
        code = input("Please enter the code: ")
        # using StxClient object to confirm the auth
        login_response = CHANNEL_CLIENT.confirm2Fa(params={"code": str(code)})
    if not login_response["success"]:
        logger.error(f"Failed to authenticate with the response: {login_response}")
    # creates method name with the provided channel name
    method_name = f"{args.channel}_join"
    # getting the method attribute from the client object
    method = getattr(CHANNEL_CLIENT, method_name)
    # running the channel method asynchronously using asyncio pool
    # following the available events:
    #    on_open        it triggers when connected with the server
    #    on_message     it triggers when server send any message
    #    on_close       it triggers when connection to the server is closed
    #    on_error       it triggers when any error send by the server or exception occurs
    #    default        all of the above events are optional to be set, if you want a
    #                   generic method to be run as default you can pass as it with default kwarg
    # here you can see that am only passing functions for on_open and on_message events
    # with a default function to handle other events
    asyncio.run(
        method(
            on_open=on_open,
            on_message=on_message,
            default=default,
        )
    )


# It's the start of the file, this commands represents that this file will execute from here
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.error(exc)
