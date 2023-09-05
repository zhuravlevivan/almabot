from aiogram.dispatcher.filters import Text
from handlers.user import start_cmd, help_cmd, files_cmd, my_id
from handlers.admin import admin_cmd, remove_cmd, rename_cmd,\
    users_cmd, \
    give_or_del_access, process_god_user_id, process_god_file_name, \
    cancel_handler, process_new_name_step, process_old_name_step,\
    process_file_remove_step,  process_get_file,\
    process_text_mailing, voice_processing, handle_audio_or_document,\
    go_back, mailing, get_file,\
    RenameFile, RemoveFile, AccessToFilesStates, MailingState,\
    GetFile, types, RemoveUser, remove_user_cmd, process_remove_user_step,\
    show_user_access, process_user_access_id,\
    FileCaption, add_caption_to_file, process_file_caption_step, process_file_name_caption_step

from create_bot import Dispatcher


def register_handlers_user(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(help_cmd, commands=['help'])
    dp.register_message_handler(files_cmd, Text(equals='files', ignore_case=True))
    dp.register_message_handler(my_id, Text(equals='my id', ignore_case=True))


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admin_cmd, Text(equals='admin', ignore_case=True))

    dp.register_message_handler(rename_cmd, Text(equals='rename', ignore_case=True), state=None)
    dp.register_message_handler(cancel_handler, Text(equals='cancel', ignore_case=True), state='*')
    dp.register_message_handler(process_old_name_step, state=RenameFile.OldName)
    dp.register_message_handler(process_new_name_step, state=RenameFile.NewName)

    dp.register_message_handler(users_cmd, Text(equals='users', ignore_case=True))

    dp.register_message_handler(remove_cmd, Text(equals='remove', ignore_case=True), state=None)
    dp.register_message_handler(process_file_remove_step, state=RemoveFile.FileRemoveName)

    dp.register_message_handler(remove_user_cmd, Text(equals='del_user', ignore_case=True), state=None)
    dp.register_message_handler(process_remove_user_step, state=RemoveUser.UserIDTORemove)

    dp.register_message_handler(give_or_del_access, Text(equals='del_accept', ignore_case=True))
    dp.register_message_handler(give_or_del_access, Text(equals='give_accept', ignore_case=True))
    dp.register_message_handler(process_god_user_id, state=AccessToFilesStates.waiting_for_user_id)
    dp.register_message_handler(process_god_file_name, state=AccessToFilesStates.waiting_for_file_name)

    dp.register_message_handler(go_back, Text(equals='go_back', ignore_case=True))

    dp.register_message_handler(mailing, Text(equals='mailing', ignore_case=True))
    dp.register_message_handler(process_text_mailing, state=MailingState.waiting_text_mailing)

    dp.register_message_handler(get_file, Text(equals='getfile', ignore_case=True))
    dp.register_message_handler(process_get_file, state=GetFile.FileName)

    dp.register_message_handler(voice_processing, content_types=types.ContentType.VOICE)
    dp.register_message_handler(handle_audio_or_document, content_types=[types.ContentType.AUDIO,
                                                                         types.ContentType.DOCUMENT])

    dp.register_message_handler(add_caption_to_file, Text(equals='caption', ignore_case=True))
    dp.register_message_handler(process_file_name_caption_step, state=FileCaption.FileCaptionName)
    dp.register_message_handler(process_file_caption_step, state=FileCaption.FileCaption)

    # dp.register_message_handler(show_user_access, Text(equals='show_acc', ignore_case=True))
    # dp.register_message_handler(process_user_access_id, state=AccessToFilesStates.waiting_for_user_access_id)
