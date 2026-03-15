import html
import re
from pyrogram import Client, filters
from pyrogram.types import Message
from nandha import pbot


__module__ = "Sed"

__help__ = """
*Use the following format for search-and-replace*:
`s/pattern/replacement/flags`

*Flags*:
- i: case-insensitive
- g: global replacement
- s: dot matches newline

*Explanation*:
text: 'Hi Gojo'
user repaid that text with `s/gojo/Nandha/i` now the text was replaced with 'Hi Nandha'
"""



@pbot.on_message(filters.regex(r"^s/(.+)?/(.+)?(/.+)?") & filters.reply)
async def sed(c: Client, m: Message):
    # Split the command into parts using regular expression
    try:
        parts = m.text.split('/')
        # Remove the 's' prefix
        parts = parts[1:]
        
        # Extract pattern, replacement and flags
        pattern = parts[0]
        replace_with = parts[1]
        flags = parts[2] if len(parts) > 2 else ""
        
        # Convert flags to re module flags
        rflags = 0
        if 'i' in flags:
            rflags |= re.IGNORECASE
        if 's' in flags:
            rflags |= re.DOTALL
            
        # Get the text to perform replacement on
        text = m.reply_to_message.text or m.reply_to_message.caption
        
        if not text:
            return await m.reply('No text to perform :D')
            
        # Perform the replacement
        if 'g' in flags:
            # Global replacement
            res = re.sub(pattern, replace_with, text, flags=rflags)
        else:
            # Replace first occurrence only
            res = re.sub(pattern, replace_with, text, count=1, flags=rflags)
            
        # Send the result
        await c.send_message(
            m.chat.id,
            f"<pre>{html.escape(res)}</pre>",
            reply_to_message_id=m.reply_to_message.id,
        )
            
    except re.error as e:
        await m.reply_text(f"Regular expression error: {str(e)}")
    except Exception as e:
        await m.reply_text(f"An error occurred: {str(e)}")

  
