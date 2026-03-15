
import config
import re
from telegram import constants, helpers
from telegram.ext import filters
from nandha.db.notes import *
from nandha.helpers.decorator import Command, admin_check, Messages
from nandha.helpers.utils import get_media_id, get_media, get_method_by_type



__help__ = """
*Commands*:

```
- /save <tag>: save file or text note in a chat.
- /get #<tag> or index: to get saved note in chat.
- /clear #<tag> or index: to delete saved note.
- /notes: send to your chat to get saved note list.
- /renotes: rearrange notes order index.
```

*Example*:
`/save gojo`
`/get #gojo or 1` or just `#gojo`
`/clear #gojo or 1`
"""

__module__ = "Notes"



CHATS = set()
CHATS.update(CHAT_IDS)

@Messages(filters=(filters.Regex(r'.*#\w+') & ~filters.COMMAND), group=6)
async def SendNoteHashtag(update, context):
    m = update.effective_message
    chat = m.chat
    bot = context.bot
    
    if not chat.id in CHATS:
        return
        
    # Extract hashtag using regex pattern
    hashtag_match = re.search(r'#([\w-]+)', m.text)
    if not hashtag_match:
        return
        
    tag = hashtag_match.group(1).lower()  # Get the captured group (text after #)
    
    _note = await get_note_by_tag(chat.id, tag)
    if not _note:
        return await m.reply_text('🔴 *Note not found!*', parse_mode=constants.ParseMode.MARKDOWN)
        
    NOTE = _note[0]  # get first result
    file_type = NOTE['type']
    reply = m.reply_to_message if m.reply_to_message else m
    method = get_method_by_type(bot, file_type)
    
    if file_type == "text":
        await reply.reply_text(NOTE['text'], parse_mode=constants.ParseMode.MARKDOWN)
    else:
        await method(
            chat.id,
            NOTE['file_id'],
            caption=NOTE.get('text'),
            parse_mode=constants.ParseMode.MARKDOWN,
            reply_to_message_id=reply.id
        )

       
@Command('renotes')
async def ReNotes(update, context):
       m = update.effective_message
       changes = await reindex_notes(m.chat.id)
       if changes:
            return await m.reply_text(
                   text='📝 *Rearranged notes order index.*', 
                   parse_mode=constants.ParseMode.MARKDOWN
            )
       else:
           return await m.reply_text(
                  text='🟢 *All are already ordered.*',
                  parse_mode=constants.ParseMode.MARKDOWN
           )


@Command('notes')
async def GetNotes(update, context):
       m = update.effective_message
       chat = m.chat     
  
       chats = await get_all_chats()
       CHATS.update(chats) # update chats

       notes = await get_notes_by_chat(chat.id)
  
       if not notes:
            return await chat.send_message('🔴 Notes not found', parse_mode=constants.ParseMode.MARKDOWN)

       txt = f"📝 *Notes in {chat.title or chat.full_name}* — (`{chat.id}`)\n\n"
       txt += "*NOTE INDEX, NOT TAG*\n\n"
       for note in notes:
           txt += f"{note['index']}, `#{note['tag']}`\n"

       txt += "\n\n```\nGet notes by using #name or /get <index>```\n\n"
       txt += f"*By {config.BOT_USERNAME}*"
       return await chat.send_message(txt, parse_mode=constants.ParseMode.MARKDOWN)
            

            

@Command('get')
async def GetNote(update, context):
       m = update.effective_message
       chat = m.chat
       bot = context.bot
       
       pattern = m.text.split()[1] if len(m.text.split()) > 1 else None
       if not pattern:
            return await m.reply_text('*I want note note tag or index ..*', parse_mode=constants.ParseMode.MARKDOWN)

       chats = await get_all_chats()
       CHATS.update(chats) # update chats
       
       async def send_note(m, chat, pattern, is_tag):
  
              if is_tag:
                    _note = await get_note_by_tag(chat.id, (pattern.lower()))
                    note = _note[0] if _note else _note
              else:
                    _note = await get_note_by_index(chat.id, pattern)
                    note = _note
                
              if not note:
                  return await chat.send_message('🔴 *Note not found*.', parse_mode=constants.ParseMode.MARKDOWN)
                     
              file_type = note['type']
              reply = m.reply_to_message if m.reply_to_message else m
              method = get_method_by_type(bot, file_type)

              if file_type == "text":
                    await reply.reply_text(note['text'], parse_mode=constants.ParseMode.MARKDOWN)
              else:
                    await method(chat.id, note['file_id'], caption=note.get('text'), parse_mode=constants.ParseMode.MARKDOWN, reply_to_message_id=reply.id)
                
       if pattern.startswith('#'):
             tag = pattern.split('#')[1]
             await send_note(m, chat, tag, is_tag=True)
       elif pattern.isdigit():
             await send_note(m, chat, int(pattern), is_tag=False)
         
       else:
            return await m.reply_text('*You can only get note by /note <index> or /note <#name>*', parse_mode=constants.ParseMode.MARKDOWN)
            
             


@Command('clear')
@admin_check()
async def ClearNote(update, context):
       m = update.effective_message
       chat = m.chat
       r = m.reply_to_message
       pattern = m.text.split()[1] if len(m.text.split()) > 1 else None
       if not pattern:
            return await m.reply_text('*You have to provide me tag for clear the note.*', parse_mode=constants.ParseMode.MARKDOWN)

       if pattern.isdigit():
              note = int(pattern)
              if await delete_note_by_index(chat.id, note):
                    return await chat.send_message('🗑️ *Deleted Note!*', parse_mode=constants.ParseMode.MARKDOWN)
              else:
                    return await chat.send_message('🔴 *Note not found!*', parse_mode=constants.ParseMode.MARKDOWN)     
                
       elif pattern.startswith('#'):
             tag = pattern.split('#')[1]
             if await delete_note_by_tag(chat.id, (tag.lower())):
                  return await chat.send_message('🗑️ *Deleted Note!*', parse_mode=constants.ParseMode.MARKDOWN)
             else:
                  return await chat.send_message('🔴 *Note not found!*', parse_mode=constants.ParseMode.MARKDOWN)
       else:
             return await m.reply_text('*Not a valid note index or tag either.*', parse_mode=constants.ParseMode.MARKDOWN)
            


@Command('save')
@admin_check()
async def SaveNote(update, context):
       m = update.effective_message
       chat = m.chat
       r = m.reply_to_message
       tag = '-'.join(m.text.split(maxsplit=1)[1].strip().split()) if len(m.text.split()) > 1 else None

       chats = await get_all_chats()
       CHATS.update(chats) # update chats

       tags = await get_notes_name_by_chat(chat.id)
       
       if not tag:
            return await m.reply_text('*You have to provide me tag for save the note.*', parse_mode=constants.ParseMode.MARKDOWN)
       elif '#' in tag:
            return await m.reply_text('*please remove the "#" word in your note name.*', parse_mode=constants.ParseMode.MARKDOWN)
       elif tag in tags:
            return await m.reply_text('*This note tag already used!*', parse_mode=constants.ParseMode.MARKDOWN)
       text = None
       file_id = None

       if r:
            file_type, file_id = get_media_id(r)
              
       if r and (r.text or r.caption):
            text = helpers.escape_markdown((r.text or r.caption))
            if file_type is None:
                   file_type = "text"

       if not (text or file_id):
           return await m.reply_text('*What you want to save ? reply to it.*', parse_mode=constants.ParseMode.MARKDOWN)
              
       is_saved = await save_note(chat.id, tag=(tag.lower()), type=file_type, text=text, file_id=file_id)
  
       if is_saved:
           return await chat.send_message(f'🟢 *Note #{tag} saved!*\n*—› Use:* `/get #{tag}`', parse_mode=constants.ParseMode.MARKDOWN)
       else:
           return await m.reply_text(f'🔴 *Note #{tag} failed to save!*', parse_mode=constants.ParseMode.MARKDOWN)




       
