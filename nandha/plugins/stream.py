import config

from pyrogram import filters, types
from nandha.helpers.pyro_utils import gen_link
from nandha.helpers.decorator import unavailable
from nandha import pbot as bot

__module__ = 'Stream'

__help__ = """
*Commands*:
/stream

```
This feature is disabled and only 
used by premium users now due to the hosting problem.
```

```
- /stream: reply to a video, audio, or document to get a stream link.
```
*Example*:
`/stream reply to video`
"""


@bot.on_message(filters.command('stream') & ~filters.forwarded)
@unavailable
async def Stream(_, message):
    m = message
    r = m.reply_to_message
    if r and (r.video or r.document or r.audio):
        log_msg = await r.forward(config.FILE_DB_CHANNEL)
        page_link, dl_link = gen_link(log_msg)
        text = (
          '✨ **Your stream link has been generated**:\n\n'
            f'📺 **Watch link**: {page_link}\n'
            f'📩 **Download link**: {dl_link}\n\n'
            f'❤️ **By {_.me.username}**'
        )
        buttons = [[
            types.InlineKeyboardButton('Watch 📺', url=page_link),
            types.InlineKeyboardButton('Download 📩', url=dl_link)
          
        ]]
        await m.reply_text(
            text=text,
            reply_markup=types.InlineKeyboardMarkup(buttons)
        )
    else:
        return await m.reply(
          'Please reply to a document, audio, or video only. ⚠️'
        )

  
