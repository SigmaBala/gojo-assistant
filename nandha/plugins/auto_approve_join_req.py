
import random

from pyrogram import filters, types, enums
from nandha import pbot, LOGGER as log, STICKERS

@pbot.on_chat_join_request(filters.channel, group=-11)
async def join_reqs(pbot, join_req: types.ChatJoinRequest):

      user = join_req.from_user
      chat = join_req.chat    
      invite = join_req.invite_link
      
      
      TEXT = f"✋ <b>Hello {user.full_name}!\n\nYour request for join in the channel ( {chat.title} ) has been accepted!</b>"
      
      if not invite.is_revoked:
          TEXT += f"\n\n📢 <b>Join link: {invite.invite_link}</b>"
         
      try:
          await pbot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
          await pbot.send_sticker(chat_id=user.id, sticker=random.choice(list(STICKERS)))
          await pbot.send_message(chat_id=user.id, text=TEXT, parse_mode=enums.ParseMode.HTML)
      except Exception as e:
           log.error(f'❌ error when accepting join request: {e}')
   
      
     
     
         
