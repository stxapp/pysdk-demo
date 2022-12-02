from pprint import pprint

from examples.stxclient.init import client
from stxsdk import Selection

email = "<email address>"
password = "<password>"
client.login(
    params={"email": email, "password": password},
)
params = {"orderId": "85b670f1-19b7-4378-8b91-6b4d7cc4a46b"}
selections = Selection("status")
pprint(client.cancelOrder(params=params, selections=selections))
