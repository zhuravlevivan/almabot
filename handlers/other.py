import config
from create_bot import bot
from keyboards import user_kb, admin_menu_kb
from aiogram.dispatcher.filters import Text
from aiogram import Dispatcher


async def sending_file(file_name, user_id):
    doc = open(f'files/{file_name}', 'rb')
    try:
        if user_id in config.ADMINS:
            await bot.send_audio(user_id, doc,
                                 protect_content=True,
                                 caption="{SOME TEXT}",
                                 reply_markup=admin_menu_kb)
        else:
            await bot.send_audio(user_id, doc,
                                 protect_content=True,
                                 caption="{SOME TEXT}",
                                 reply_markup=user_kb)
    except Exception as e:
        await bot.send_message(user_id, str(e))

    doc.close()


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(sending_file, commands=['getfile'])
    dp.register_message_handler(sending_file, Text(equals='getfile', ignore_case=True))
