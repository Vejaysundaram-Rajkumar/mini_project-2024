from twilio.rest import Client
import keys

def request(my_no):
    client=Client(keys.acc_sid,keys.auth_token)
    message=client.messages.create(
        body="Testing the message sending for my mini project and will be calling for intimation",
        from_=keys.twilio_no,
        to=my_no
    )
    print(message.body)

    call=client.calls.create(
        twiml='<Responce><Say>Hello this is an blood request alert from bloodline community</Say></Responce>',
        to=my_no,
        from_=keys.twilio_no
    )

    print(call.sid)