from init import client

# must run login first, you will get code via email, use that code to confirm 2FA

client.confirm2Fa(
    params={
        "code": "865347",
    }
)
