from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetHistoryRequest

import asyncio
from loguru import logger
from time import sleep
import os

# auth
def get_env(name, message, cast=str):
    if name in os.environ:
        return cast(os.environ[name])
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            sleep(1)

api_id = get_env('api_id', 'Enter your API ID: ', int)
api_hash = get_env('api_hash', 'Enter your API HASH: ')
sesrt = get_env('sesrt', "Enter string session: ")

async def main():
    client = TelegramClient(StringSession(sesrt), api_id, api_hash)
    await client.connect()
    userbot_info = await client(GetFullUserRequest('me'))
    logger.info(userbot_info.user.username+" started srapping!")
    logger.info("ID: "+str(userbot_info.user.id))
    await client(JoinChannelRequest("ChatWarsDigest"))
    ent = await client.get_entity("ChatWarsDigest")
    posts = await client(GetHistoryRequest(peer=ent,
    limit=int(5),
    offset_date=None,
    offset_id=0,
    max_id=0,
    min_id=0,
    add_offset=0,
    hash=0))
    for post in posts.messages:
        if "была успешно атакована" in post.message:
            atck_msg = post.date.strftime("%D\n%H:%M\n")
            atck_msg += post.message
            await client.send_message("vaarvind", atck_msg)
        elif post.message.startswith("😴 Скучавшие защитники - на них никто не напал"):
            def_msg = post.date.strftime("%D\n%H:%M\n")
            def_msg += "Ги в дефе но не битые:\n"
            arr = post.message.split("\n")
            defenders_arr = arr.index('')
            for d in arr[1:defenders_arr]:
                def_msg += d
            await client.send_message("vaarvind", def_msg)
            nondef_msg = post.date.strftime("%D\n%H:%M\n")
            nondef_msg += "Не дефали и не битые:\n"
            for nd in arr[defenders_arr+2:]:
                nondef_msg += nd
            await client.send_message('vaarvind',nondef_msg)
        else:
            pass
    await client.disconnect()


asyncio.run(main())
