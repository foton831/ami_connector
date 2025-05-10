import asyncio
import logging

from panoramisk import Manager, Message
from env_const import EnviromentVariables as ev
from services import ElmaAPI



manager = Manager(
    host=ev.get_ami_host(),
    port=ev.get_ami_port(),
    username=ev.get_ami_username(),
    secret=ev.get_ami_secret(),
    ping_delay=5,  # Delay after start
    ping_interval=5,  # Periodically ping AMI (dead or alive)
    reconnect_timeout=2,  # Timeout reconnect if connection lost
)


def on_connect(mngr: Manager):
    logging.info(
        'Connected to %s:%s AMI socket successfully' %
        (mngr.config['host'], mngr.config['port'])
    )


def on_login(mngr: Manager):
    logging.info(
        'Connected user:%s to AMI %s:%s successfully' %
        (mngr.config['username'], mngr.config['host'], mngr.config['port'])
    )


def on_disconnect(mngr: Manager, exc: Exception):
    logging.info(
        'Disconnect user:%s from AMI %s:%s' %
        (mngr.config['username'], mngr.config['host'], mngr.config['port'])
    )
    logging.debug(str(exc))


async def on_startup(mngr: Manager):
    await asyncio.sleep(0.1)
    while True:        
        # ElmaAPI.send_request(data={'cmd': 'state', 'status': 'UP'})
        await asyncio.sleep(60)


async def on_shutdown(mngr: Manager):
    await asyncio.sleep(0.1)
    #logging.info(
    #    'Shutdown AMI connection on %s:%s' % (mngr.config['host'], mngr.config['port'])
    #)



@manager.register_event('DialBegin')
async def on_dial_begin(mngr: Manager, msg: Message):
    if 'Exten' in msg and 'CallerIDNum' in msg:
        logging.info(f"DialBegin event detected: Channel: {msg['Channel']} CallerID: {msg['CallerIDNum']} Exten: {msg['Exten']}")
        if len(msg['Exten']) == 3:
            logging.info(f"Incoming call detected: CallerID: {msg['CallerIDNum']} Dialed extension: {msg['Exten']}")

            ElmaAPI.send_request(data= {
                'cmd': 'event',
                'type': 'INCOMING',
                'phone': msg['CallerIDNum'],
                'ext': msg['Exten']
                })

@manager.register_event('DialEnd')
async def on_dial_end(mngr: Manager, msg: Message):
    logging.info(f"DialEnd event detected: Channel: {msg['Channel']} CallerID: {msg.get('CallerIDNum', 'Unknown')} Exten: {msg['Exten']} DialStatus: {msg['DialStatus']}")
    if len(msg['Exten']) == 3:
        if msg['DialStatus'] == 'ANSWER':            
            ElmaAPI.send_request(data= {
                'cmd': 'event',
                'type': 'ACCEPTED',
                'phone': msg['CallerIDNum'],
                'ext': msg['Exten']
                })
        elif msg['DialStatus'] == 'CANCEL':            
            ElmaAPI.send_request(data= {
                'cmd': 'event',
                'type': 'CANCELLED',
                'phone': msg['CallerIDNum'],
                'ext': msg['Exten']
                })

    # Add your custom logic here to handle when the call stops ringing, for example:
    # ElmaAPI.send_request(data={'event': 'call_ended', 'channel': msg['Channel'], 'caller_id': msg.get('CallerIDNum', 'Unknown'), 'dial_status': msg['DialStatus']})


@manager.register_event('*')  # Register all events
async def ami_callback(mngr: Manager, msg: Message):
    if msg.Event == 'FullyBooted':
        print("Asterisk has fully booted.")
    # elif msg.Event == 'DialBegin':
    #     print(f"DialBegin")
    # elif msg.Event == 'Hangup':
    #     print(f"Hangup")
    # elif msg.Event == 'Bridge':
    #     print(f"Bridge")
    
    # elif msg.Event == 'Newchannel':
    #     print(f"Создание нового канала: {msg.Channel}, Caller ID: {msg.CallerIDNum}")
        # caller_id_name = msg.get('CallerIDName', '<unknown>')
        # caller_id_num = msg.get('CallerIDNum', '<unknown>')
        # channel = msg.get('Channel', '<unknown>')
        # dest_channel = msg.get('DestChannel', '<unknown>')
        # dest_caller_id_name = msg.get('DestCallerIDName', '<unknown>')
        # dest_caller_id_num = msg.get('DestCallerIDNum', '<unknown>')
        # dial_string = msg.get('DialString', '<unknown>')
        # timestamp = msg.get('Timestamp', '<unknown>')
        # uniqueid = msg.get('Uniqueid', '<unknown>')

        # print(f"DialBegin event received:")
        # print(f"Caller ID Name: {caller_id_name}")
        # print(f"Caller ID Num: {caller_id_num}")
        # print(f"Channel: {channel}")
        # print(f"Destination Channel: {dest_channel}")
        # print(f"Destination Caller ID Name: {dest_caller_id_name}")
        # print(f"Destination Caller ID Num: {dest_caller_id_num}")
        # print(f"Dial String: {dial_string}")
        # print(f"Timestamp: {timestamp}")
        # print(f"Unique ID: {uniqueid}")
    # elif msg.Event == 'Newchannel':
    #     print(f"Создание нового канала: {msg.Channel}, Caller ID: {msg.CallerIDNum}")
    # elif msg.Event == 'Newstate':
    #     print(f"Изменение состояния канала: {msg.Channel}, State: {msg.ChannelStateDesc}")
    # elif msg.Event == 'Dial':
    #     print(f"Начало набора номера: {msg.Channel} -> {msg.Destination}")
    # elif msg.Event == 'Ringing':
    #     print(f"Сигнал звонка: {msg.Channel}")
    # elif msg.Event == 'Link':
    #     print(f"Соединение каналов: {msg.Channel1} <-> {msg.Channel2}")
    # elif msg.Event == 'Bridge':
    #     print(f"Соединение каналов: {msg.BridgedChannel} <-> {msg.Channel}")
    # elif msg.Event == 'Unlink':
    #     print(f"Разъединение каналов: {msg.Channel1} <-> {msg.Channel2}")
    # elif msg.Event == 'Hangup':
    #     print(f"Завершение вызова: {msg.Channel}")
    #     print(msg) 
    # if msg.Event == 'Newchannel' and 'SIP/' in msg.Channel:
    #     print(f"Incoming call detected on channel: {msg.Channel}, Caller ID: {msg.CallerIDNum}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    manager.on_connect = on_connect
    manager.on_login = on_login
    manager.on_disconnect = on_disconnect
    manager.connect(run_forever=True, on_startup=on_startup, on_shutdown=on_shutdown)