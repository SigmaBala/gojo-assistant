
import aiohttp
import re
import os
import config

from nandha import pbot
from nandha.helpers.scripts import anime_quote
from nandha.helpers.decorator import spam_control
from pyrogram import filters


__module__ = "AniQuote"

__help__ = """
*Commands*:

```
- /aniquote <query> & page 1 (optional):
Search anime quotes of character with audio.
you can change page value to get different results.
```

*Example*:
`/aniquote`
`/aniquote wow page 2`
`/aniquote cool`
"""




@pbot.on_message(filters.command('aniquote') & ~filters.forwarded)
@spam_control
async def AniQuote(_, message):
    m = message
    search = m.text.split(maxsplit=1)[1] if len(m.text.split()) > 1 else None
    random = True if not search else False
    page = 1

    if search:
        page_re = re.compile(r'page (\d+)', re.IGNORECASE)
        page_s = page_re.search(search)
        if page_s:
            page = int(page_s.group(1))
            search = page_re.sub('', search).strip()

    quote_data = await anime_quote(
        search=search,
        random=random,
        page=page
    )
  
    if not quote_data:
         return await m.reply_text('❌ **No results found**.')
      
    if isinstance(quote_data, dict):
        return await m.reply_text(
            text=f'❌ **ERROR**: `{quote_data["error"]}`'
        )
    else:
        msg = await m.reply_text('✨ **Uploading Quotes...**')
        async with aiohttp.ClientSession() as session:
            for data in quote_data:
                audio_path = data['quote'] + '.mp3'
                async with session.get(data['audio_url']) as response:
                    with open(audio_path, 'wb+') as file:
                        file.write(await response.read())
                text = f"""
<blockquote>
<b>Quote:</b>
{data['quote']}
</blockquote>


ℹ️ <b>Character</b>:
<by code>{data['character']}</code> — {data['image_url']}
"""

                await m.reply_audio(audio_path, caption=text)

                os.remove(audio_path)

            return await msg.edit_text(f'✨ **Uploaded by {config.BOT_USERNAME}**')
                
