from nandha.helpers.decorator import Command, admin_check, only_groups
from telegram import constants, ChatPermissions



__help__ = '''
*Commands*:
/locktypes, /lock, /unlock

```
/locktypes: returns all types chat permission with keyword which used for lock.
/lock <keyword>: use the locktypes keyword for lock chat permission.
/unlock <keyword>: use the locktypes keyword for unlock chat permission.
```

*Example*:
`/lock video`
`/unlock video`
`/lock all`
`/unlock all`
'''

__module__ = 'Locks'


LOCK_TYPES = {
    'message': 'can_send_messages',
    'poll': 'can_send_polls',
    'media': 'can_send_other_messages',
    'preview': 'can_add_web_page_previews',
    'info': 'can_change_info',
    'invite': 'can_invite_users',
    'pin': 'can_pin_messages',
    'topic': 'can_manage_topics',
    'video': 'can_send_videos',
    'photo': 'can_send_photos',
    'audio': 'can_send_audios',
    'document': 'can_send_documents',
    'voice': 'can_send_voice_notes',
    'notes': 'can_send_video_notes'  
}


def get_only_valid_permissions(chat_info):
     permissions = chat_info.permissions.to_dict()
     del permissions['can_send_media_messages'] # deprecated
     return permissions


@Command('locktypes')
@admin_check()
@only_groups
async def GetlockTypes(update, context):
      m = update.effective_message
      txt = "🔐 *LockTypes*:\n\n"
      for key, value in LOCK_TYPES.items():
           txt += f"🟢 *{key}*\n— `{value}`\n\n"
      await m.reply_text(
          txt, 
          parse_mode=constants.ParseMode.MARKDOWN
      )




@Command('unlock')
@admin_check()
@only_groups
async def unlockChats(update, context):
     m = update.effective_message
     chat = m.chat
     bot = context.bot
     permission = m.text.split()[1].lower() if (len(m.text.split()) > 1 and bool(LOCK_TYPES.get(m.text.split()[1].lower()) or m.text.split()[1].lower() == 'all')) else None
     chat_info = await bot.get_chat(chat.id)
     permissions = get_only_valid_permissions(chat_info)
     if permission != 'all' and LOCK_TYPES.get(permission, None) not in permissions:
          return await m.reply_text('🤔 *Given lock type not allowed in this chat.*', parse_mode=constants.ParseMode.MARKDOWN)
     try:
         if permission != 'all':
              permissions[LOCK_TYPES[permission]] = True
         else:
              permissions = {key: True for key in permissions}
         await chat.set_permissions(permissions=ChatPermissions(**permissions))
     except Exception as e:
         return await m.reply_text(f'❌ *ERROR*: `{str(e)}`',  parse_mode=constants.ParseMode.MARKDOWN)
       
     return await m.reply_text(f'🔓 *Unlocked!* `{permission}`', parse_mode=constants.ParseMode.MARKDOWN)



@Command('lock')
@admin_check()
@only_groups
async def lockChats(update, context):
     m = update.effective_message
     chat = m.chat
     bot = context.bot
     permission = m.text.split()[1].lower() if (len(m.text.split()) > 1 and bool(LOCK_TYPES.get(m.text.split()[1].lower()) or m.text.split()[1].lower() == 'all')) else None
     chat_info = await bot.get_chat(chat.id)
     permissions = get_only_valid_permissions(chat_info)
     if permission != 'all' and LOCK_TYPES.get(permission, None) not in permissions:
          return await m.reply_text('🤔 *Given lock type not allowed in this chat.*', parse_mode=constants.ParseMode.MARKDOWN)
     try:
         if permission != 'all':
              permissions[LOCK_TYPES[permission]] = False
         else:
              permissions = {key: False for key in permissions}
         await chat.set_permissions(permissions=ChatPermissions(**permissions))
     except Exception as e:
         return await m.reply_text(f'❌ *ERROR*: `{str(e)}`',  parse_mode=constants.ParseMode.MARKDOWN)
       
     return await m.reply_text(f'🔓 *Locked!* `{permission}`', parse_mode=constants.ParseMode.MARKDOWN)

     
       
