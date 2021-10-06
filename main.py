from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerUser

import asyncio
from loguru import logger
from time import sleep
import os
from utils import find_word
import sqlite3 as sq

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
battles_counter = get_env('battles_counter', "Enter battles_counter: ", int)

client = TelegramClient(StringSession(sesrt), api_id, api_hash)
#await client(JoinChannelRequest("ChatWarsDigest"))
#ent = await client.get_entity("ChatWarsDigest")

#@client.on(events.NewMessage(chats=(['ChatWarsDigest'])))
@client.on(events.NewMessage(chats=(['kurashh'])))
async def main(event):
    new_msg = event.message.message
    if "была успешно атакована" in new_msg:
        atck_msg = event.message.date.strftime("%D\n%H:%M\n")
        atck_msg += new_msg
        #await client.send_message("vaarvind", atck_msg)
        await client.send_message("kurashh", atck_msg)
    elif new_msg.startswith("😴 Скучавшие защитники - на них никто не напал"):
        def_msg = event.message.date.strftime("%D\n%H:%M\n")
        def_msg += "Кого дефают:\n"
        arr = new_msg.split("\n")
        defenders_arr = arr.index('')
        for d in arr[1:defenders_arr]:
            def_msg += d
        #await client.send_message("vaarvind", def_msg)
        #await client.send_message("kurashh", def_msg)
        #NonDef GI
        nondef_msg = event.message.date.strftime("%D\n%H:%M\n")
        nondef_msg += "Дефали и не битые:\n"
        non_def_gu_arr = arr[-1].split(', ')
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS defenders (guild_name text, date text);''')
        cur.execute('''CREATE TABLE IF NOT EXISTS percents (gi_name  TEXT, count_of_defs  INTEGER, count_of_battles  INTEGER, percentage  INTEGER);''')
        global battles_counter 
        for gi_name in non_def_gu_arr:
            cur.execute(f"INSERT INTO defenders VALUES(\'{gi_name}\', datetime('now', 'localtime'))")

        for gi_name in non_def_gu_arr:
            #logger.debug(gi_name)
            cur.execute(f"INSERT INTO percents VALUES(\'{gi_name}\',(SELECT count (guild_name) as counter from defenders WHERE guild_name = \'{gi_name}\'),{battles_counter},NULL);")

        battles_counter += 1
        #formula = int((count_on_defs/count_of_days)*100)
        """
        for nd in arr[defenders_arr+2:]:
            nondef_msg += nd
        #await client.send_message('vaarvind',nondef_msg)
        await client.send_message('kurashh',nondef_msg)
        """
        await client.send_message('kurashh',"Defenders was scrapped to DB!")
    else:
        pass

"""
@client.on(events.NewMessage())
async def manager(event):
    castles_emoji = ["🌹", "🖤","☘️","🐢","🦇","🍁","🍆"]
    new_msg = event.message.message
    cur = con.cursor()
    if new_msg.startswith('/show_all'):
        try:
            cur.execute("select DISTINCT guild_name from defenders;")
            raw = cur.fetchall()
        except Exception as e:
            logger.error(e)
            sender = await event.get_input_sender()
            await client.send_message(sender, "Упс!\nЧто-то пошло не так...")
        else:
            all_gi = ""
            for i in raw:
                all_gi += i[0] + "\n"
                sender = await event.get_input_sender()
            await client.send_message(sender, all_gi)
    else:
        logger.debug(find_word(new_msg))
        #logger.debug(new_msg)
        print("Castle!")
    #select * from defenders where guild_name = "🖤DEF";
"""

client.start()
userbot_info = client(GetFullUserRequest('me'))
con = sq.connect("guilds.db",isolation_level=None)
client.send_message("kurashh",userbot_info.user.username+" started srapping!")
client.run_until_disconnected()
