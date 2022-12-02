from stxsdk import StxChannelClient, StxClient

email = "<email address>"
password = "<password>"
client = StxClient()
client.login(params={"email": email, "password": password})

channel_client = StxChannelClient()
