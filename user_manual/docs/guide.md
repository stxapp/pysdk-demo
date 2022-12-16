# Developer Guide

## Synchronous Client - HTTP requests

### Initialization

To initialize the client:
```python title="examples/stxclient/init.py"
from stxsdk import StxClient

client = StxClient()
```

### Authentication
Before performing any operation you must authenticate first, if the provided credentials are correct the
login API will store the tokens automatically to be used for authenticated APIs otherwise it will return 
authentication failure response.

```python title="examples/stxclient/login.py"
from stxsdk import StxClient

client = StxClient()

email = "<email address>"
password = "<password>"
result = client.login(
    params={"email": email, "password": password},
)
```
The user token and refresh token validity is automatically handled by the client internally, and
you don"t need to worry about handling the authentication and authorization.
For understanding the token expiry is 1 hour and refresh token expiry is 24 hours.

### 2 Factor Authentication
If the 2FA is enabled, you must execute the confirm2fa to authenticate the user before calling any other operation,
otherwise you will get the authentication failure response.
```python title="examples/stxclient/confirm2FA.py"
from stxsdk import StxClient

client = StxClient()

email = "<email address>"
password = "<password>"
client.login(
    params={"email": email, "password": password},
)
# After login, if 2FA is enabled, you will receive the code on the requested email address
client.confirm2Fa(
    params={
        "code": "865347",
    }
)
```
### User Profile
To get the user profile details
```python title="examples/stxclient/user_profile.py"
from stxsdk import StxClient, Selection

client = StxClient()

email = "<email address>"
password = "<password>"
client.login(
    params={"email": email, "password": password},
)

selections = Selection(
    "accountId",
    "city",
    "country",
    "firstName",
    "lastName",
    "username",
    "id",
)
result = client.userProfile(selections=selections)
```
```json title="Response"
{"data": {"userProfile": {"accountId": "6a7fb2e7-1413-4b8b-b126-6a8eaab128a8",
                          "city": "New York",
                          "country": None,
                          "firstName": "Muhamad",
                          "id": "d9988022-037e-4441-8132-69d1bc58343f",
                          "lastName": "Ali",
                          "username": "Ali.Muhamad.86702"}},
 "errors": None,
 "message": "Request Processed Successfully",
 "success": True,
 }
```
### Utilities
Here you can see a **Selection** object is being created to pass as an argument `selections` to the userProfile function.
If you doesn't pass the selections, you will get all the fields in return by default.

Selections parameter is used to pass the fields that you want in return from the APIs.

Now the question is how would you know which fields are available in the response of the API.
We have a utility method `get_return_fields` that takes the name of the operation as a string and returns
all the available response values with their names and types.

```python title="To get the return fields"
from stxsdk import StxClient

client = StxClient()
result = client.get_return_fields("userProfile")
```
```json title="Response"
{
  "accountId": "rID", "address1": "String", "address2": "String",
  "city": "String", "country": "String", "dateOfBirth": "String",
  "firstName": "String!", "id": "rID!", "industry": "String",
  "jobTitle": "String", "lastName": "String!", "optInMarketing": "Boolean",
  "phoneNumber": "String", "ssn": "String", "state": "String",
  "twoFactorAuth": "Boolean", "twoFactorAuthPerDevice": "Boolean",
  "username": "String!", "zipCode": "String"
}
```
Now what about the response with nested fields, checkout the following example:
```python title="To get the return values with nested fields"
from stxsdk import StxClient

client = StxClient()
result = client.get_return_fields("marketInfos")
```
```json title="Response"
{
"archived": "Boolean", "closedAt": "String", "description": "String",
"detailedEventBrief": "String", "homeCategory": "String", "eventId": "rID",
"eventStart": "String", "eventStatus": "String", "title": "String",
"eventType": "String", "eventBrief": "String", "lastProbabilityAt": "DateTime",
"lastTradedPrice": "Int", "manualProbability": "Boolean", "marketId": "rID",
"maxPrice": "Int", "position": "String", "price": "Float", "priceChange24h": "Int",
"probability": "Float", "question": "String", "result": "String", "shortTitle": "String",
"rulesSpecifier": "String", "specifier": "String", "status": "String",
"timestamp": "String", "timestampInt": "Int", "volume24h": "Int", "symbol": "String",
"tradingFilters": {
        "category": "String", "manual": "Boolean",
        "section": "String", "subcategory": "String"
        },
"recentTrades": {
        "liquidityTaker": "String", "price": "Int", "quantity": "Int",
        "timestamp": "String", "timestampInt": "Int"
        },
"offers": {"price": "Int", "quantity": "Int"},
"orderPriceRules": {"from": "Int", "inc": "Int", "to": "Int"},
"filters": {
        "category": "String", "manual": "Boolean", "section": "String", "subcategory": "String"
        },
"bids": {"price": "Int", "quantity": "Int"}
}
```
You will get two types of responses in return from any operation
```json title="Success Response"
{
    # API response, it could be list or dictionary
    "data": {},
    # it would always be None in case of success
    "errors": None,
    # Success Message
    "message": "Request Processed Successfully",
    # A boolean field, would always be True in case of success response
    "success": True,
}
```
```json title="Failure Response"
{
    # it would be None in case of failure 
    "data": None,
    # it would a list of errors
    "errors": [],
    # General failure message
    "message": "Failed to process the request",
    # A boolean field, would always be False in case of success response
    "success": False,
}
```
You can also use the following function to get the list of available operations
```python title="To get the list of avaiable operations"
from stxsdk import StxClient

client = StxClient()
result = client.get_operations()
```

### Market Infos
In the following example code you can see the usage of **Selection** object to set nested values

```python title="examples/stxclient/market_info.py"
from stxsdk import StxClient, Selection
client = StxClient()

email = "<email address>"
password = "<password>"
client.login(
    params={"email": email, "password": password},
)
# you can create separate selection object and set them as keyword argument
# or can create them inline

# here created selection object for the field orderPriceRules and
# pass it as keyword argument
order_price_rules = Selection("from", "inc", "to")

selections = Selection(
    "closedAt",
    "description",
    "eventId",
    "marketId",
    "title",
    "status",
    orderPriceRules=order_price_rules,
    # inline selection object
    bids=Selection("price", "quantity"),
)
result = client.marketInfos(selections=selections)
```
### Confirm Order
```python title="examples/stxclient/confirm_order.py"
from stxsdk import StxClient, Selection

client = StxClient()

email = "<email address>"
password = "<password>"
client.login(
    params={"email": email, "password": password},
)
params = {
    "userOrder": {
        "marketId": "ec202f18-cc6c-4fa2-90cb-f0c9162afced",
        # orderType: LIMIT | MARKET
        "orderType": "LIMIT",
        # action: BUY | SELL
        "action": "BUY",
        "price": 1,
        "quantity": 5,
    }
}
selections = Selection(
    "errors", order=Selection("id", "totalValue", "status", "action", "clientOrderId")
)
result = client.confirmOrder(params=params, selections=selections)
```

### Cancel Order
```python title="examples/stxclient/cancel_order.py"
from stxsdk import StxClient, Selection

client = StxClient()

email = "<email address>"
password = "<password>"
client.login(
    params={"email": email, "password": password},
)
params = {"orderId": "85b670f1-19b7-4378-8b91-6b4d7cc4a46b"}
selections = Selection("status")
result = client.cancelOrder(params=params, selections=selections)
```

### Trade History
```python title="examples/stxclient/trade_history.py"
from stxsdk import StxClient, Selection

client = StxClient()

email = "<email address>"
password = "<password>"
client.login(
    params={"email": email, "password": password},
)
selections = Selection(
    "totalCount",
    orders=Selection(
        "id",
        "orderType",
        "price",
        "quantity",
        "clientOrderId",
        "totalValue",
        "marketId",
        "status",
    ),
)
result = client.myOrderHistory(selections=selections)
```



## Asynchronous Client - Websocket requests
This service provides the functionality to connect with the Sportsx phoenix channel
via websockets.
### Available Channels
| Channel                   | Description                                                                                                                                           |
|:--------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|
| `portfolio_join`          | It delivers updates to users' available balance                                                                                      |
| `market_info_join`        | It gives information about active markets                                                                                            |
| `active_trades_join`      | It delivers information to the subscriber on a trade executed against an order that is filled against an active market in the system |
| `active_orders_join`      | It delivers information to the subscriber on order that are filled against an active market in the system                            |
| `active_settlements_join` | It delivers information to the subscriber on a settlement recorded against on an account for an active market in the system.         |
| `active_positions_join`   | It delivers information to the subscriber on a position an account holds in an active market                                         |

### Initialization

To initialize the client:
```python title="examples/stxchannelclient/init.py"
email = "<email address>"
password = "<password>"

channel_client = StxChannelClient()
channel_client.login(params={"email": email, "password": password})
```

Same as mentioned above you can set environment for StxChannelClient also via Environment variable or by passing as argument

```python
channel_client = StxChannelClient(env="production")
```

!!! note
    First of all, needs to know that the User management is built on singleton approach,
    It means that no matter how many StxClient or StxChannelClient objects you create all of them
    will be sharing the same user object.

It is required to have authentication before initiating the async client for building the connection with the channels.

In the following example you can see I used `asyncio` library for async communication with channels
asyncio is Python's builtin library to write concurrent code using the async/await syntax.
You can learn more about `asyncio` on its [official documentation](https://docs.python.org/3/library/asyncio.html)

!!! question "What is Consumer?"
    It's a function or service that would be triggered by the async client, means that the channels' message will
    automatically hand off to a message listener which passes to the consumer that has been registered.
    The client consumes the message when a session thread invokes the onMessage() method of the message listener object.

#### Response Syntax
```json title="Success Message"
{
  "closed": False,
  "message_received": True,
  "message": "Message received",
  # it would a list containing message of the channel
  "data": [],
}
```

Below is the sample data of the portfolio channel

```json title="Sample Message Response of the Channel"
[
    "3",
    None,
    "portfolio:EY8Zk0HKYbaMsiG8id81MTE0V1D3",
    "summary",
    {
        "account_balance": 2000000, "account_id": "6a7fb2e7-1413-4b8b-b126-6a8eaab128a8",
        "available_balance": 2000000, "buy_order_liability": 0, "escrow": 0,
        "position_premium_liability": 0, "sell_order_liability": 0, "total_deposits": 2000000,
        "total_fees": 0, "total_settlement_pnl": 0, "total_withdrawals": 0,
        "user_id": "ca84fb65-5df2-456b-80ec-903a068bbdd2"
    }
]
```

### Portfolio Channel

```python title="examples/stxchannelclient/portfolio.py"
import asyncio
from examples.stxchannelclient.init import channel_client

async def consumer(response):
    if response["closed"]:
        print(response["message"])
    elif response["data"] is None:
        print("No data return from server.")
    else:
        print(response["data"][4])

async def read_portfolio():
    await channel_client.portfolio_join(consumer)

asyncio.run(read_portfolio())
```

### Market Info Channel

```python title="examples/stxchannelclient/market_info.py"
import asyncio
from examples.stxchannelclient.init import channel_client

async def consumer(response):
    if response["closed"]:
        print(response["message"])
    elif response["data"] is None:
        print("No data return from server.")
    else:
        print(response["data"][4])

async def read_market_info():
    await channel_client.market_info_join(consumer)

asyncio.run(read_market_info())
```

### Active Trades Channel

```python title="examples/stxchannelclient/active_trade.py"
import asyncio
from examples.stxchannelclient.init import channel_client

async def consumer(response):
    if response["closed"]:
        print(response["message"])
    elif response["data"] is None:
        print("No data return from server.")
    else:
        print(response["data"][4])

async def read_active_trades():
    await channel_client.active_trades_join(consumer)

asyncio.run(read_active_trades())
```

### Active Orders Channel

```python title="examples/stxchannelclient/active_order.py"
import asyncio
from examples.stxchannelclient.init import channel_client

async def consumer(response):
    if response["closed"]:
        print(response["message"])
    elif response["data"] is None:
        print("No data return from server.")
    else:
        print(response["data"][4])

async def read_active_orders():
    await channel_client.active_orders_join(consumer)

asyncio.run(read_active_orders())
```

### Active Settlement Channel

```python title="examples/stxchannelclient/active_settlements.py"
import asyncio
from examples.stxchannelclient.init import channel_client

async def consumer(response):
    if response["closed"]:
        print(response["message"])
    elif response["data"] is None:
        print("No data return from server.")
    else:
        print(response["data"][4])

async def read_active_settlements():
    await channel_client.active_settlements_join(consumer)

asyncio.run(read_active_settlements())
```

### Active Positions Channel

```python title="examples/stxchannelclient/active_positions.py"
import asyncio
from examples.stxchannelclient.init import channel_client

async def consumer(response):
    if response["closed"]:
        print(response["message"])
    elif response["data"] is None:
        print("No data return from server.")
    else:
        print(response["data"][4])

async def read_active_positions():
    await channel_client.active_positions_join(consumer)

asyncio.run(read_active_positions())
```
