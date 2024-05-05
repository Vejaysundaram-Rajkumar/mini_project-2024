from twilio.rest import Client

import keys

client=Client(keys.acc_sid,keys.auth_token)
message=client.messages.create(
    body="Testing the message sending for my mini project",
    from_=keys.twilio_no,
    to=keys.my_no
)
print(message.body)