
import config

from nandha.helpers.decorator import Messages, Command, admin_check, only_groups, devs_only
from nandha.db.blocklistwords import get_words, get_mode, update_mode, add_word, remove_word, get_all_chats
from telegram import constants
from telegram.ext import filters
from nandha.helpers.utils import search_text, get_as_document


CHATS = []



__module__ = "blwords"


__help__ = '''
*Commands*:
/addblword, /rmblword, /blwordslist, /blwords

```
- /addblword <word>: Add a word to the chat's blocklist
- /rmblword <word>: Remove a word from the chat's blocklist
- /blwordslist: View all blocked words in the chat
- /blwords <on/off>: Enable or disable the blocklist feature in the chat
- /blchats ( only special user ).
```

*Note*:
You must enable the blocklist feature using `/blwords on` for the bot to delete blocked words in the chat.

*Examples*:
`/blwords on`
`/addblword spam`
`/rmblword spam`
'''


@Messages(filters=((filters.TEXT | filters.CAPTION) & filters.ChatType.GROUPS), group=3)
async def _findAndDelete(update, context):

      m = update.effective_message
      user = update.effective_user

      if len(CHATS) == 0:
          my_chats = await get_all_chats()
          CHATS.extend(my_chats)
            
      if m.chat.id in CHATS:
           mode = await get_mode(m.chat.id)
           if not mode: return
           words = await get_words(m.chat.id)
           if words:
               pattern = "|".join(words)
               text = (m.text or m.caption)
               ok = search_text(pattern, text)
               if ok and (m.from_user.id != config.BOT_ID):
                   member = await m.chat.get_member(user.id)
                   status = constants.ChatMemberStatus
                   if member.status not in [status.OWNER, status.ADMINISTRATOR]:
                        await m.delete()


      

@Command("rmblword")
@admin_check("can_delete_messages")
@only_groups
async def _removeBlockListWord(update, context):

     m = update.effective_message
     if len(m.text.split()) < 2:
         return await m.reply_text("*Bro* you gotta gimme word to delete it instant.")
     else:
         word = m.text.split(maxsplit=1)[1]
         bl_words = await get_words(m.chat.id)
         if not word in bl_words:
             return await m.reply_text("*Bro* that word is not in blocklist!")
         else:
             await remove_word(m.chat.id, word)
             if m.chat.id in CHATS:
                 CHATS.remove(m.chat.id)
             mode = await get_mode(m.chat.id)
             mode = "on" if mode else "off"
             return await m.reply_text(
                   f"*Removed the word from blocklist!* and currently blocklist words is {mode} in this chat.",
                   parse_mode=constants.ParseMode.MARKDOWN
             )
             
@Command("addblword")
@admin_check("can_delete_messages")
@only_groups
async def _addBlockListWord(update, context):

     m = update.effective_message
     if len(m.text.split()) < 2:
         return await m.reply_text("*Bro* you gotta gimme word to delete it instant.")
     else:
         word = m.text.split(maxsplit=1)[1]
         bl_words = await get_words(m.chat.id)
         if len(bl_words) == 50:
               return await m.reply_text("You can't add more than 50 words! contact /support if you want to add more.")             
         elif word in bl_words:
              return await m.reply_text("*Bro* that word is already in blocklist!")
         else:
             await add_word(m.chat.id, word)
             if not m.chat.id in CHATS:
                 CHATS.append(m.chat.id)
             mode = await get_mode(m.chat.id)
             mode = "on" if mode else "off"
             return await m.reply_text(
                   f"*Added the word to blocklist and currently blocklist words is {mode} in this chat.*",
                   parse_mode=constants.ParseMode.MARKDOWN
             )



@Command("blwords")
@admin_check('can_delete_messages')
@only_groups
async def _blocklistWords(update, context):
     user = update.effective_user
     m = update.effective_message
     mode = await get_mode(m.chat.id)
     mode = 'on' if mode else 'off'
     if len(m.text.split()) < 2:         
         return await m.reply_text(f"on/off pattern ? and currently blocklist words is {mode}")
     else:
         q = m.text.split()[1].lower()
         if not q in ['on', 'off']:
             return await m.reply_text("Only on/off can be used as argument!")
         else:
             if q == 'on':
                await update_mode(m.chat.id, True)
                return await m.reply_text("*Yes* I'll delete all unnecessary words for you.")
             else:
                await update_mode(m.chat.id, False)
                return await m.reply_text("*Okay*, I'm stopping deleting blocked words here.")


@Command("blwordslist")
@admin_check('can_delete_messages')
@only_groups
async def _blocklistWords(update, context):
     user = update.effective_user
     m = update.effective_message
     chat = m.chat
     chats = await get_all_chats()
     if m.chat.id in chats:
         words = await get_words(m.chat.id)
         if not words:
             return await m.reply_text("No words currently blocked!")
         text = f"*{m.chat.title}'s blocklist words*:\n"
         text += "\n".join(f"—» `{word}`" for word in words)
         if len(text) >= 4000:
                file = get_as_document(text)
                await chat.send_document(file)
         else:
                await chat.send_message(text, parse_mode=constants.ParseMode.MARKDOWN)
     else:
         return await chat.send_message("No Blocklist words!")
         
@Command("blchats")
@devs_only
async def _blocklistChats(update, context):
     user = update.effective_user
     m = update.effective_message
     users = list(map(str, CHATS))
     if not users:
         return await m.reply_text("Currently no blocklist words chats.")
     text = "\n".join(f"–› `{user}`" for user in users)
     file = get_as_document(text)
     return await m.reply_document(
       document=file, 
       parse_mode=constants.ParseMode.MARKDOWN
     )

