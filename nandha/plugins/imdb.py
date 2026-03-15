

import config
import asyncio
from nandha import pbot
from nandha.helpers.scripts import IMDBScraper
from pyrogram import filters

imdb = IMDBScraper()


__help__ = '''
*Commands*:
/imdb

```
- /imdb <query>: search movies through imdb.
```
'''

__module__ = 'ImDb'


async def search_imdb(name: str):
        result = await imdb.search_by_name(name)
        results = result.get('results')
        if results:
             return [
               {
                 'url': 'https://m.imdb.com/title/{}'.format(m['id']),
                 'title': m.get('titlePosterImageModel', {}).get('caption', 'not available'),
                 'id': m['id'],
                 'media': m.get('titlePosterImageModel', {}).get('url', 'https://i.imgur.com/5wWF99I.jpeg')
               } for m in results if m.get('titlePosterImageModel', {}).get('caption', None) and m.get('id')
             ]
        return []
        

@pbot.on_message(filters.command('imdb') & ~filters.forwarded)
async def imdb_search(_, message):
     m = message
     query = m.text.split(maxsplit=1)[1] if len(m.text.split()) > 1 else None
     if not query: return await m.reply_text('**Movie name ??**')
     data = await search_imdb(query)
     if not data:
          return await m.reply_text('❌ **Movie not found.**')
     for d in data:
         caption = (
            f"**🎥 Movie**: `{d['title']}`\n"
            f"**🆔 Movie imdb**: `{d['id']}`\n"
            f"**🖇️ Movie Link**: {d['url']}\n"      
         )
         await m.reply_document(d['media'], caption=caption)
         await asyncio.sleep(1.3)
  
     