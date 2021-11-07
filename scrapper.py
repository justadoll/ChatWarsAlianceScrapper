from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerUser

import asyncio
from loguru import logger
from utils import find_word
from environs import Env
import sqlite3 as sq

env = Env()
env.read_env()
logger.add("debug.json", format="{time} {level} {message}", level="DEBUG", rotation="5 MB", compression="zip", serialize=True)

api_id = env.int('API_ID')
api_hash = env.str('API_HASH')
sesrt = env.str('SESTR')
battles_counter = env.int('BATTLE_COUNTER')

client = TelegramClient(StringSession(sesrt), api_id, api_hash)
#await client(JoinChannelRequest("ChatWarsDigest"))
#ent = await client.get_entity("ChatWarsDigest")

@client.on(events.NewMessage(chats=(['ChatWarsDigest'])))
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

        #NonDef GI
        nondef_msg = event.message.date.strftime("%D\n%H:%M\n")
        nondef_msg += "Дефали и не битые:\n"
        def_gu_arr = arr[-1].split(', ')
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS defenders (guild_name text, date text);''')
        cur.execute('''CREATE TABLE IF NOT EXISTS percents (gi_name  TEXT, count_of_defs  INTEGER, count_of_battles  INTEGER, percentage  INTEGER);''')
        global battles_counter 
        for gi_name in def_gu_arr:
            cur.execute(f"INSERT INTO defenders VALUES(\'{gi_name}\', datetime('now', 'localtime'))")

        for gi_name in def_gu_arr:
            cur.execute(f"SELECT * FROM percents WHERE gi_name = \'{gi_name}\'")
            raw = cur.fetchall()
            if not raw:
                logger.debug(f"{gi_name} not found in percents table, adding!")
                cur.execute(f"INSERT INTO percents VALUES(\'{gi_name}\',(SELECT count (guild_name) as counter from defenders WHERE guild_name = \'{gi_name}\'),{battles_counter},NULL);")
            else:
                logger.info(f"{gi_name} was found, updating!")
                cur.execute(f"""UPDATE percents set count_of_defs = (SELECT count (guild_name) as counter from defenders WHERE guild_name = \'{gi_name}\'), count_of_battles = {battles_counter} WHERE gi_name = \'{gi_name}\';""")
                cur.execute(f"""SELECT count_of_battles, count_of_defs from percents WHERE gi_name = \'{gi_name}\';""")
                resp = cur.fetchall()
                count_of_battles = resp[0][1]
                count_of_defs = resp[0][0]
                formula = (count_of_battles/count_of_defs)*100
                cur.execute(f"""UPDATE percents set percentage = {str(formula)} WHERE gi_name = \'{gi_name}\';""")
                logger.info(f"{gi_name} percents was updated to {formula}")



        await client.send_message('kurashh',f"{battles_counter}th battle was played!")
        battles_counter += 1
        await client.send_message('kurashh',"Defenders was scrapped to DB!")
    else:
        pass

@client.on(events.NewMessage())
async def manager(event):
    #castles_emoji = ["🌹", "🖤","☘️","🐢","🦇","🍁","🍆"]
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

client.start()
userbot_info = client(GetFullUserRequest('me'))
con = sq.connect("guilds.db",isolation_level=None)
client.send_message("kurashh",userbot_info.user.username+" started srapping!")
client.run_until_disconnected()
