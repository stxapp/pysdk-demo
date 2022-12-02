from pprint import pprint

from examples.stxclient.init import client
from stxsdk import Selection

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
pprint(client.myOrderHistory(selections=selections))
