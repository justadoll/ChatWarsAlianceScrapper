from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageTextIsEmpty
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram import types
from asyncio import run
from environs import Env

env = Env()
env.read_env()

from loguru import logger
import sqlite3 as sq

token = env.str("BOT_TOKEN")

castles_btn = InlineKeyboardMarkup()
castles_btn.add(InlineKeyboardButton(callback_data="s_🌹",text="🌹"),InlineKeyboardButton(callback_data="s_🖤",text="🖤"),
        InlineKeyboardButton(callback_data="s_🦇",text="🦇"), InlineKeyboardButton(callback_data="s_☘️",text="☘️"),
        InlineKeyboardButton(callback_data="s_🐢",text="🐢"),InlineKeyboardButton(callback_data="s_🍁",text="🍁"),
        InlineKeyboardButton(callback_data="s_🍆",text="🍆")
        )
bot=Bot(token=token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
con = sq.connect("guilds.db",isolation_level=None)
cur = con.cursor()

class GetPercent(StatesGroup):
    stiker = State()
    gi_name = State()

class GetLastDefs(StatesGroup):
    stiker = State()
    gi_name = State()

@dp.message_handler(CommandStart())
async def main(message):
    await message.answer("Привет!")

@dp.message_handler(commands=["show_all"])
async def show_all_proc(message):
    await message.answer("Собираю все ги...")
    cur.execute("select DISTINCT guild_name from defenders;")
    raw = cur.fetchall()
    if not raw:
        logger.error("GI not found")
    else:
        all_gi = ""
        for i in raw:
            all_gi += i[0] + "\n"
        await message.answer(all_gi)


@dp.message_handler(commands=["get_percents"])
async def get_percents_st_proc(message):
    await message.answer("<b>Замок гильдии:</b>", reply_markup=castles_btn)
    await GetPercent.stiker.set()

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("s_"), state=GetPercent.stiker)
async def cb_get_stiker(callback_data:types.CallbackQuery, state:FSMContext):
    await bot.answer_callback_query(callback_data.id)
    await bot.edit_message_text(chat_id=callback_data.message.chat.id, message_id=callback_data.message.message_id, text="<b>Введите название ги:</b>")
    await state.update_data(stiker=callback_data.data.split("_")[1])
    await GetPercent.gi_name.set()

@dp.message_handler(state=GetPercent.gi_name)
async def get_percents_proc(message:types.Message, state=FSMContext):
    async with state.proxy() as data:
        request_data = f"SELECT * FROM percents WHERE gi_name = \'{data['stiker']}{message.text}\'"
    logger.debug(request_data)
    cur.execute(request_data)
    raw = cur.fetchall()
    if not raw:
        logger.error(f"{message.text} guild not found from {message.chat.username}:{message.chat.id}")
        await message.answer("<i>Гильдия не найдена...</i>🤨")
    else:
        data = raw[0]
        result = f"""<b>Название ги:</b> {data[0]}\n<b>Количество дефов:</b> {data[1]}\n<b>Кол-во битв:</b>{data[2]}\n<b>Процент защиты:</b> {data[3]}"""
        logger.debug(result)
        await message.answer(result)

    await state.finish()

@dp.message_handler(commands=["get_last_def"])
async def get_last_def_st_proc(message):
    await message.answer("<b>Замок гильдии:</b>", reply_markup=castles_btn)
    await GetLastDefs.stiker.set()

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("s_"), state=GetLastDefs.stiker)
async def get_last_def_st_proc(callback_data:types.CallbackQuery, state=FSMContext):
    await bot.answer_callback_query(callback_data.id)
    await bot.edit_message_text(chat_id=callback_data.message.chat.id, message_id=callback_data.message.message_id, text="<b>Введите название ги:</b>")
    await state.update_data(stiker=callback_data.data.split("_")[1])
    await GetLastDefs.gi_name.set()

@dp.message_handler(state=GetLastDefs.gi_name)
async def get_last_def_st_proc(message:types.Message, state=FSMContext):
    async with state.proxy() as data:
        request_data = f"SELECT * from defenders where guild_name = \'{data['stiker']}{message.text}\' LIMIT 10;"
    logger.debug(request_data)
    cur.execute(request_data)
    raw = cur.fetchall()
    if not raw:
        logger.error(f"{message.text} last_def guild not found from {message.chat.username}:{message.chat.id}")
        await message.answer("<i>Гильдия не найдена...</i>🤨")
    else:
        logger.debug(raw)
        result = ""
        for i in raw:
            result += f"<code>{i[0]}</code>:\t<code>{i[1]}</code>\n"
        await message.answer(result)

    await state.finish()

if __name__ == "__main__":
    try:
        executor.start_polling(dp,skip_updates=True)
    except Exception as e:
        logger.error(e)
