

from nandha import BOT_ID, BOT_USERNAME
from nandha.helpers.utils import search_text
from nandha.db.chatbot import CHAT_IDS
from telegram import constants
from telegram.ext.filters import MessageFilter


class ReplyToBot(MessageFilter):
    def filter(self, message):
        reply = message.reply_to_message
        result = (
        (message.text and 
        ((message.from_user and reply and reply.from_user and reply.from_user.id == BOT_ID) 
        or search_text(BOT_USERNAME, message.text) 
        or search_text("(@|#)Gojo", message.text)))
        or message.sticker ) and message.chat.id in CHAT_IDS
  
        return result
      
ChatBotReply = ReplyToBot()
