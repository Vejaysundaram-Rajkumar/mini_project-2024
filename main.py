from twilio.rest import Client
import keys

def request_sms(my_no,ms):
    client=Client(keys.acc_sid,keys.auth_token)
    message=client.messages.create(
        body=ms,
        from_=keys.twilio_no,
        to=my_no
    )
    print(message.body)

def request_call(my_no,message):
    client=Client(keys.acc_sid,keys.auth_token)
    call=client.calls.create(
        twiml='<Responce><Say>'+message+' This is an request alert!</Say></Responce>',
        to=my_no,
        from_=keys.twilio_no
    )

    print(call.sid)