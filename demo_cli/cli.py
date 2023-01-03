import argparse
import logging
import sys
from pprint import pprint

from stxsdk import StxClient, Selection

logger = logging.getLogger(__file__)

# globally initiated StxClient object
CLIENT = StxClient()

# globally initiated a variable to store the markets data to reuse for market detail operation
# checkout get_markets function for further details
MARKETS = {}


# we have two separate functions for market, one for getting all the markets from API
# and second for getting the details of the requested market
# this function is responsible for executing the marketinfos API and store details in the
# MARKET variable as short title to market details mapper.
# eg. {"BHL @ MPH": {<detailed dictionary of the market>}}
def get_markets():
    # making selection object of the required response fields
    selections = Selection(
        "title",
        "shortTitle",
        "marketId",
        "eventType",
        "status",
        "maxPrice",
        "probability",
        "question",
        "eventStatus",
        "position",
        "price",
        bids=Selection("price", "quantity"),
        offers=Selection("price", "quantity"),
    )
    # executing the marketinfos API with the generated selection object
    market_data = CLIENT.marketInfos(selections=selections)
    if not market_data["success"]:
        logger.error(f"Failed to get markets with error: {market_data['errors']}")
    else:
        # clearing the MARKET in order to avoid duplication or expired data
        MARKETS.clear()
        markets = []
        # generating the markets mapper as mentioned above and a
        # list of market short titles to be sent in the response
        for market in market_data["data"]["marketInfos"]:
            MARKETS[market["shortTitle"]] = market
            markets.append(market["shortTitle"])
        return markets


def get_market_details():
    short_code = input("Enter Market Short Title: ")
    return MARKETS.get(short_code, "Market with this Short Title not exist.")


def create_order():
    # this function takes market id as input to pass in confirmOrder API
    market_id = input("Enter Market ID: ")
    # here taking order type as input and the loop will continuously ask for order type
    # until the valid input is provided
    while True:
        order_type = input("Enter Order Type [MARKET | LIMIT]: ")
        if order_type in ["MARKET", "LIMIT"]:
            break
        else:
            logger.error("Invalid Order Type, Please select MARKET or LIMIT")
    quantity = input("Enter Quantity: ")
    params = {
        "userOrder": {
            "marketId": market_id,
            "orderType": order_type,
            "action": "BUY",
            "quantity": quantity,
        }
    }
    # if the order type is LIMIT then price is required
    if order_type == "LIMIT":
        price = input("Enter Price: ")
        params["userOrder"]["price"] = price
    return CLIENT.confirmOrder(params=params)


def get_order_trades():
    # this function takes order id as input and pass it as param in myTradesForOrder API
    order_id = input("Enter Order ID: ")
    params = {"orderId": order_id}
    return CLIENT.myTradesForOrder(params=params)


def get_market_settlements():
    # this function takes market id as input and pass it as param in marketSettlements API
    market_id = input("Enter Market ID: ")
    params = {"marketId": market_id}
    return CLIENT.marketSettlements(params=params)


def cancel_order():
    # this function takes order id as input and pass it as param in cancelOrder API
    order_id = input("Enter Order ID: ")
    params = {"orderId": order_id}
    return CLIENT.cancelOrder(params=params)


def exit_session():
    sys.exit()


# operation to option map
METHOD_MAP = {
    "1": CLIENT.userProfile,
    "2": get_markets,
    "3": get_market_details,
    "4": create_order,
    "5": CLIENT.myOrderHistory,
    "6": get_order_trades,
    "7": CLIENT.myTradesHistory,
    "8": CLIENT.mySettlementsHistory,
    "9": get_market_settlements,
    "10": cancel_order,
    "11": CLIENT.logout,
    "12": exit_session,
}


def print_menu():
    print(
        """
    Please select any option:
    1. Get Profile
    2. Get Available Markets
    3. Get Market Details
    4. Create Order
    5. Get Orders
    6. Get Order Trades
    7. Get All Trades
    8. Get All Settlements
    9. Get Market Settlements
    10. Cancel Order
    11. Logout
    12. Exit
    """
    )


def get_arguments():
    parser = argparse.ArgumentParser(description="Initiate connection with STX SDK.")
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
    login_response = CLIENT.login(params={"email": email, "password": password})
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
        login_response = CLIENT.confirm2Fa(params={"code": str(code)})
    if not login_response["success"]:
        logger.error(f"Failed to authenticate with the response: {login_response}")
    # infinitely looping to provide continuous options availability
    # and can only be exited on user's command
    while True:
        # printing out the available commands options on each iteration
        print_menu()
        # taking input from the user for the option selection
        option = input("Select Option: ")
        # a mapper is defined with all the options with their relative operations
        method = METHOD_MAP.get(option)
        # if the provided option is not in the mapper it responds with error log
        if not method:
            logger.error("Invalid Option.")
        else:
            # executing the relative operation and printing the response
            response = method()
            pprint(response)


# It's the start of the file, this commands represents that this file will execute from here
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.error(exc)
