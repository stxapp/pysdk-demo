from pprint import pprint

from examples.stxclient.init import client
from stxsdk import Selection

email = "<email address>"
password = "<password>"
client.login(
    params={"email": email, "password": password},
)
params = {
    "userOrder": {
        "marketId": "ec202f18-cc6c-4fa2-90cb-f0c9162afced",
        "orderType": "LIMIT",
        "action": "BUY",
        "price": 1,
        "quantity": 5,
    }
}
selections = Selection(
    "errors", order=Selection("id", "totalValue", "status", "action", "clientOrderId")
)
pprint(client.confirmOrder(params=params, selections=selections))
