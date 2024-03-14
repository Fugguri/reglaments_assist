import datetime
from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher.handler import ctx_data
from aiogram.dispatcher import FSMContext

from services import create_answer
from database.Database import UserManager
from config.config import Config
from keyboards.keyboards import Keyboards
from .admin import admin
from utils import speech_to_text


async def start(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: UserManager = ctx_data.get()['db']
    # try:
    #     db.add_user(message.from_user.id, message.from_user.username,
    #                 message.from_user.first_name, message.from_user.last_name)
    # except Exception as ex:
    #     print(ex)
    await message.answer(cfg.misc.messages.start)


async def create_response(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']

    wait = await message.answer("Набираю сообщение ответ…")

    if message.content_type == types.ContentType.VOICE:
        path = f"voice/{message.voice.file_id}.ogg"
        await message.voice.download(path)
        text = await speech_to_text(path)

    elif message.content_type == types.ContentType.TEXT:
        text = message.text
    message.text = text
    try:
        answer = await create_answer(message.from_user.id, message.text)
    except:
        await message.answer("К сожалению,я не смогу обработать этот запрос")
        return
    # answer = await gpt.create_answer(message)
    await message.answer(answer)
    await wait.delete()


def register_user_handlers(dp: Dispatcher, kb: Keyboards):

    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_message_handler(create_response, content_types=[
                                types.ContentType.TEXT, types.ContentType.VOICE], state="*")
