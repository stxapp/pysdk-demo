import asyncio
import contextlib
import logging
import random

from stxsdk import StxClient, Selection, StxChannelClient
from stxsdk.exceptions import AuthenticationFailedException
from trading_bot.exceptions import MarketsNotFoundException, OrderCreationFailure

logger = logging.getLogger(__file__)

# globally initiated StxClient object
CLIENT = StxClient()

# globally initiated StxChannelClient object
CHANNEL_CLIENT = StxChannelClient()


class TradingBot:
    """
    The objective of this bot is to perform the following routine:
     - Get all the available markets from the API.
     - Pick a random market.
     - Extract the probability of the selected market.
     - Generate a random probability cap between 0 and 10 to add into
       the market current probability.
       probability = current_probability + (current_probability * random.choice(range(11)) / 100)
     - Generate the price using the generated probability and market's current max price.
       price = max market price * probability
     - Pick random quantity between 1 and 10
       quantity = random.choice(range(11))
     - Place an order with market id, price and quantity
     - Initiate market channel and check if price shifts 5% either up down for that market.
       - Cancel the created order.
       - Post new order with new price.
    """

    order = None
    markets = {}
    market = None

    @staticmethod
    def __authenticate(email, password):
        """
        This function is authenticating the client with the provided credentials,
        and will raise the exception if authentication fails
        """
        print("Executing bot user authentication.")
        # using StxClient object to initiate the login
        login_response = CLIENT.login(params={"email": email, "password": password})
        # if the provided credentials are not correct it would get success False flag in response
        # with relative error message
        if not login_response["success"]:
            logger.error(f"Failed to authenticate with the response: {login_response}")
            raise AuthenticationFailedException(login_response["message"])

    def __populate_markets(self):
        """
        This function is populating the bot markets by executing the marketInfos API
        """
        print("Initiating to populate the market data")
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
        print("Executing the marketinfos API.")
        market_data = CLIENT.marketInfos(selections=selections)
        if not market_data["success"]:
            # if for any reason market info API fails, raise the exception
            msg = f"Failed to get markets with error: {market_data['errors']}"
            logger.error(msg)
            raise MarketsNotFoundException(msg)
        else:
            self.markets.clear()
            market_data = market_data["data"]["marketInfos"]
            print(f"Received {len(market_data)} markets.")
            # storing the markets in the bot object to be randomly picked from
            # am making marketId to market data map for quick accessing the market
            # you can define your own data structure or store in database
            # depending on your use case, you can also filter out the markets based
            # on your preferences and requirements
            self.markets = {market["marketId"]: market for market in market_data}

    def __pick_random_market(self):
        """
        This function is randomly picking a market from the available markets
        """
        print("Picking random market with the bids.")
        # infinitely looping to pick the random market with bids available
        while True:
            # random.choice picks any element from the list in uniformly distributed manner
            market = random.choice(list(self.markets.values()))
            # set the picked market to bot object for order creation
            # only if the market has bids available, and probability greater than 0
            # you can set any other conditions based on your requirements
            if market.get("bids") and market.get("probability") > 0:
                self.market = market
                print(
                    f"The picked market is {market['shortTitle']}, having id {market['marketId']}"
                )
                # breaks the loop when the market is picked
                break

    def __extract_market_probability(self):
        """
        This function is returning the probability of the selected market
        """
        print("Getting the market probability.")
        # returns the market's probability
        return self.market["probability"]

    def __compute_price(self, probability):
        """
        This function is computing the price using the market's current probability
        on which the order would be placed.
        :param probability: market's current probability
        """
        print(
            f"Computing the price for order creation, market current probability is {probability}"
        )
        # get random probability cap between 0 and 10 to add into the market current probability
        probability_cap = random.choice(range(11))
        # increasing the probability by the percent of the computed cap
        probability += probability * probability_cap / 100
        print(f"Generated probability is {probability}")
        # get the max price of all the bids
        max_market_price = max(bid["price"] for bid in self.market["bids"])
        # price = integer type (max market price * computed probability)
        # type casting to int, because following command will return as float
        # and the price should be integer type
        price = int(max_market_price * probability)
        print(f"Computed price is {price}")
        return price

    @staticmethod
    def __get_quantity():
        # returns random quantity between 1 and 10
        return random.choice(range(1, 11))

    def __create_order(self, market_id, quantity, price):
        """
        This function is posting a new order with the provided details
        :param market_id: unique ID of the market
        :param quantity: quantity of the shares to be purchased
        :param price: the price at which the shares would be purchased
        """
        print(
            f"Initiating to create the order for market id: {market_id}, "
            f"with price: {price} and quantity: {quantity}."
        )
        # generate the request params for order creation
        params = {
            "userOrder": {
                "marketId": market_id,
                "orderType": "LIMIT",
                "action": "BUY",
                "quantity": quantity,
                "price": price,
            }
        }
        # request the confirmOrder API to post the order
        order_response = CLIENT.confirmOrder(params=params)
        # if the response is not successful raise the exception
        if not order_response["success"]:
            msg = f"Order creating failed with error {order_response['message']}"
            logger.error(msg)
            raise OrderCreationFailure(msg)
        # if order created successfully then set the order data to the bot object
        order = order_response["data"]["confirmOrder"]['order']
        order_total = order['quantity'] * order["price"]
        print(
            f"Order is created with id: {order['id']} and total price is {order_total}"
        )
        self.order = order

    def __cancel_order(self):
        """
        This function is cancelling the order using cancelOrder API
        """
        if not self.order:
            return
        print(f"Cancelling the order with id {self.order['id']}")
        # generate the request params for cancelling the order
        params = {"orderId": self.order["id"]}
        CLIENT.cancelOrder(params=params)
        # resetting the bot current order to None after cancelling the order
        self.order = None

    async def on_market_info_update(self, response):
        """
        This function will be called whenever there is an update to a market.
        It checks if the update is happened to the market which we placed order for
        If market id matches, checkout for the price shift, if the shift is 5% up or down.
        Cancel the order and post new order with new price.

        Sample channel response:
        {
        'closed': False,
        'message_received': True,
        'message': 'Message received',
        'data': [
            None,
            None,
            'market_info',
            'market_updated',
            {
                'd76112d8-2537-4c20-a376-37c74fbe7977': {
                    'market_id': 'd76112d8-2537-4c20-a376-37c74fbe7977',
                    'offers': [
                        {'price': 5400, 'quantity': 10},
                        {'price': 3500, 'quantity': 8},
                        {'price': 3400, 'quantity': 66},
                    ],
                    'price': 3150.0,
                    'timestamp': '2023-01-17T16:53:26.324012Z',
                    'unix_timestamp': 1673974406324012,
                    }
                }
            ]
        }

        the data key contains the server response
        data is a list, where 3rd element is the message event for example when market gets updated
        it will be 'market_updated', when new market created it will be 'market_created'
        the 4th element is the market data, this market data will have mandatory
        'market_id' and 'timestamp' fields indicating what market change and when with only the changed fields
        """
        try:
            data = response["data"]
            market_response_type = data[3]
            market_response_data = data[4]
            # suppressing the StopIteration exception to pass the empty response data
            with contextlib.suppress(StopIteration):
                # getting the market data from the response, response is a dictionary
                # using next with iter to get the first element of the response dict
                # next raises StopIteration exception if empty iter is provided
                # the above context is suppressing this case
                market_data = market_response_data[next(iter(market_response_data))]
                # checking if the server message is for market update
                # also if the update happened for the market we placed order on
                if (
                    market_response_type == "market_updated"
                    and market_data["market_id"] == self.market["marketId"]
                ):
                    print("The market has been updated.")
                    # market data will only have those fields that are updated
                    market_latest_price = market_data.get("price")
                    # if the market data has price field, it means the market price is shifted
                    if market_latest_price:
                        order_price = self.order["price"]
                        print(
                            f"The market price is changed, old price: {order_price}, new price: {market_latest_price}"
                        )
                        # get the 5% max and min price cap of the order's price
                        max_shift = order_price + (order_price * 5 / 100)
                        min_shift = order_price - (order_price * 5 / 100)
                        # checking if the latest price is between the price shift cap
                        if max_shift > market_latest_price < min_shift:
                            print("A price shift of 5% up/down is detected. Cancelling the order.")
                            # cancel the order and post the new order with new price for the same market
                            self.__cancel_order()
                            quantity = self.__get_quantity()
                            print("Posting the new order with the latest market price.")
                            self.__create_order(
                                self.market["marketId"], quantity, market_latest_price
                            )
        except Exception as exc:
            # if any general exception occurs, cancel the order if any posted
            print(f"The bot operation failed with exception: {exc}")
            if self.order:
                self.__cancel_order()

    async def on_market_close(self, response=None):
        print(f"Market channel has been closed with response: {response}")
        print("Cancelling the order.")
        self.__cancel_order()

    async def on_market_error(self, response=None):
        print(f"Faced an exception or error with response: {response}")
        print("Cancelling the order.")
        self.__cancel_order()

    def initiate_market_info_channel(self):
        """
        This function is initiating the market info channel to check for the price shifts
        here we are using asyncio for asynchronous communication with the server
        """
        asyncio.run(
            CHANNEL_CLIENT.market_info_join(
                on_message=self.on_market_info_update,
                on_close=self.on_market_close,
                on_error=self.on_market_error,
            )
        )

    def initiate(self, email, password):
        """
        This function is step by step performing the defined routines
        """
        # Starts the bot by preforming the authentication for the APIs.
        self.__authenticate(email, password)
        # Populates the available markets using the market API.
        self.__populate_markets()
        # Randomly pick a market to which the order will be placed
        self.__pick_random_market()
        # extract the current probability of the picked market
        market_probability = self.__extract_market_probability()
        # compute the price on which the order will be placed
        price = self.__compute_price(market_probability)
        # get the quantity of the shares for the order
        quantity = self.__get_quantity()
        # Post the order with the generated quantity and price
        try:
            self.__create_order(self.market["marketId"], quantity, price)
            # connecting with the market info channel to look out for the price shift
            self.initiate_market_info_channel()
        except Exception as exc:
            # if any general exception occurs, cancel the order if any posted
            print(f"The bot operation failed with exception: {exc}")
            if self.order:
                self.__cancel_order()
