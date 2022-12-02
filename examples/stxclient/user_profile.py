from pprint import pprint

from examples.stxclient.init import client
from stxsdk import Selection

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
pprint(client.userProfile(selections=selections))
