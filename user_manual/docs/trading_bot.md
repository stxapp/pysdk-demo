# Trading Bot

This document will guide you on the usage of SportsX SDK with an example to create a Trading Bot.

Let's just set some requirements of the bot, what is the target of this bot what features this bot would have etc.

The objective of this bot is to perform the following routine:

     - Get all the available markets from the API.
     - Pick a random market.
     - Extract the probability of the selected market.
     - Generate a random probability cap between 0 and 10 to add into the market current probability.
       probability = current_probability + (current_probability * random.choice(range(11)) / 100)
     - Generate the price using the generated probability and market's current max price.
       price = max market price * probability
     - Pick random quantity between 1 and 10
       quantity = random.choice(range(11))
     - Place an order with market id, price and quantity.
     - Initiate market channel and check if price shifts 5% either up down for that market.
       - Cancel the created order.
       - Post new order with new price.

Before the implementation we are going to need the SDK.
### Installation

Install the latest release via pip:

    pip install stx-pysdk

The SDK is built for python 3 only.
If your system has both python2 and python3 manager installed then by default "pip" refers to python2 manager,
so in order to install for python3 "pip3" would be used

    pip3 install stx-pysdk

### Implementation

We will start with the creating a project with name `trading_bot`.
And create a python file with name `bot.py` in which we are creating a class `TradingBot`.
This class will contain all the operations of the bot.
```python title="trading_bot/bot.py"

class TradingBot:
    pass
```
Now let's create a method called `initiate` that will be called to initiate the bot,
this method will be responsible for calling the required operations as defined in the requirements.

Before doing any operation it is required to have a valid authentication so the first step would be performing the authentication.
We'll add an auth method `__authenticate` that will be called here to perform the authentication.

After the auth the next step is to get the available markets, so we'll add a method `__populate_markets` that will be
responsible for storing the market data to the bot object.

Next step would be picking up the random market from previously stored markets data.

After selecting the market we'll perform some computation based on our requirements and algorithms.

`__compute_price` to compute the price at which we'll be placing the order.

`__get_quantity` to get the quantity of the shares to be purchased.

```python
class TradingBot:
    def initiate(self):        
        # Starts the bot by preforming the authentication for the APIs.
        self.__authenticate()
        # Populates the available markets using the market API.
        self.__populate_markets()
        # Randomly pick a market to which the order will be placed
        self.__pick_random_market()
        # compute the price on which the order will be placed
        price = self.__compute_price()
        # get the quantity of the shares for the order
        quantity = self.__get_quantity()
```

For the authentication of the bot we need username and password, lets just update the authentication method to accept
username and password as parameters to perform the authentication now the function would be.

```python
class TradingBot:
    def initiate(self):        
        # Starts the bot by preforming the authentication for the APIs.
        self.__authenticate(username, password)
        ...
```

Now its time to define these methods. We'll now use the provided StxClient by importing it from the installed SDK.

```python
from stxsdk import StxClient

CLIENT = StxClient()
```

Now that we have the client object, we'll be using it to interact with the SportsX APIs.

So the authentication method would be:
```python
class TradingBot:
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
```
This is only a sample code for the authentication API usage, you can perform your own operations in case of success and failures.

Market population method would be like:
```python
class TradingBot:
    def __populate_markets(self):
        """
        This function is populating the bot markets by executing the marketInfos API
        """
        print("Initiating to populate the market data")
        # making selection object of the required response fields
        # You can have your own list of selections as per your requirements
        # To learn more about what Selection is you can check out the guide section.
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
```
This is sample code for populating the markets, you can define your own operation for markets extractions,
and different approaches for handling success and failure cases.
Here we are storing markets in the object, you can use any database to store them as per your requirements.

Next step is to define the market picking method:
```python
class TradingBot:
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
```
This is sample code for picking up the market on which we'll be placing order, you can have your own algorithm
for picking the right market to place order on.

Once you picked the market now lets define the methods that will be calculating the parameters for placing the order.
Order required 5 parameters, `marktetId`, `orderType`, `action`, `quantity` and `price`.

We can get the `marketId` from the picked market object.

For this example we'll be using `LIMIT` as `orderType`, you can have your own logic for deciding the order type,
available order types are `LIMIT` and `MARKET`

Setting `action` as `BUY` because this bot will be buying the shares, you can have your own logic to decide the action
based on you requirements.

For `quantity`, as per our requirement we will be randomly choosing the value between 1 and 10, you can have your own
logic to decide the quantity of the shares.

```python
class TradingBot:
    @staticmethod
    def __get_quantity():
        # returns random quantity between 1 and 10
        return random.choice(range(1, 11))
```

For `price` we have a defined formula that will be using to compute the price to place the order on.
You can have your own algorithm, logic to compute the price.

```python
class TradingBot:
    def __extract_market_probability(self):
        """
        This function is returning the probability of the selected market
        """
        print("Getting the market probability.")
        # returns the market's probability
        return self.market["probability"]

    def __compute_price(self):
        """
        This function is computing the price using the market's current probability
        on which the order would be placed.
        """
        # extract the current probability of the picked market
        probability = self.__extract_market_probability()
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
```

Once we get the values of all the required parameters we'll move to place the order.
Following is an example code for placing the order, you can have your own logic for placing the order and perform
different operations on success and failure cases.

```python
class TradingBot:
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
```

As you can see am storing the placed order information in the object, you can store it in the database or something as
per your requirements.

Now that we have placed the order, our next target is to keep checkout the market's price change and whenever price
shifts 5% up or down, cancel the order and place new one with different prices.

We have to define a method to cancel the order.
```python
class TradingBot:
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
```
You can have your own logic of cancelling the order this is just an example usage on how you can cancel the order using SDK.

Now the question is how we can track the market prices or any other updates to the market. We have another client class
available in the SDK that allow us to connect with the SportsX channels (Websocket Channels).
You can learn more about what channels are, what channels are available in the guide section.

Here we will be using the market info channel, this channel asynchronously sends the updates to our passed consumers
which then can be used to perform any required operations.

In order to connect with the channel you have to create a StxChannelClient object by importing from the SDK.
```python
from stxsdk import StxChannelClient
CHANNEL_CLIENT = StxChannelClient()
```

Now this channel client will be used to connect with the SportsX market info channel.
We have to define a method that will be initiating the connection with channel and pass our defined consumers.

```python
import asyncio
class TradingBot:
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
```

As you can see we are passing 3 methods, `on_market_info_update`, `on_market_close` and `on_market_error`.
These are the consumer methods, you can learn more about consumers on the guide section.
Quick introduction is that we can pass different consumer methods to each available events to be triggered on.

| Event         | Description                                                                  |
|:--------------|:-----------------------------------------------------------------------------|
| `on_open`     | It triggers when connected with the server                                   |
| `on_message`  | It triggers when connection to the server is closed                          |
| `on_close`    | It triggers when connection to the server is closed                          |
| `on_error`    | It triggers when any error send by the server or exception occurs            |
| `default`     | all of the above events are optional to be set, if you want a generic method to be run as default you can pass as it with default kwarg|

We are using asyncio to connect with channels, you can use any other asynchronous libraries to connect with the channels.

Following is the sample code of the consumer methods, you can have your own logic to be performed based on the requirements
```python
class TradingBot:
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
```

After including the order creation and market channel connection methods the bot `initiate` method could use them as following:
```python
class TradingBot:
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
        # compute the price on which the order will be placed
        price = self.__compute_price()
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
```


you can check out the whole sample code of Trading Bot on the [trading_bot package](../../trading_bot)
