from stxsdk import StxChannelClient

email = "<email address>"
password = "<password>"

channel_client = StxChannelClient()
channel_client.login(params={"email": email, "password": password})
