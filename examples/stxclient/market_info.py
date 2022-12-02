from pprint import pprint

from examples.stxclient.init import client
from stxsdk import Selection

email = "<email address>"
password = "<password>"
client.login(
    params={"email": email, "password": password},
)

selections = Selection(
    "closedAt",
    "description",
    "eventId",
    "marketId",
    "title",
    "status",
    bids=Selection("price", "quantity"),
)
pprint(client.marketInfos(selections=selections))
