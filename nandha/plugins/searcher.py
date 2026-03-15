 
 
import re
import html
from nandha import pbot as bot
from pyrogram import filters, types, enums
from nandha.helpers.scripts import search_gfg, search_youtube, search_wikipedia
import aiohttp
import os
import config

__help__ = '''
*Commands*:
/sof, /wiki,
/ytsearch, /gfg

```
- /sof <query>: search for programming questions or issues. ( Stackoverflow )
- /wiki <query>: search for information about things. ( Wikipedia )
- /gfg <query>: search on greek-for-greeks website.
- /ytsearch <query>: search for youtube videos.
```

*Example*:
`/sof pyrogram`
`/wiki Elon musk`
`/gfg python numpy`
`/ytsearch gojo edits`
'''

__module__ = 'Search'


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)
       
    
@bot.on_message(filters.command('gfg') & ~filters.forwarded)
async def greekforgreeks_func(_, message):
       if len(message.text.split()) == 1:
          return await message.reply('💭 **Example**: `/gfg writing files in python`')
       else:
          query = message.text.split(maxsplit=1)[1]
          data = await search_gfg(query, 10)
          if not data:
             return await message.reply("❌ **No results found!**")
          
          text = "<b>🔎 Greek For Greeks Search</b>:\n\n"
          for idx, d in enumerate(data, start=1):
              text += "<b>{index}, <a href='{link}'>{title}</a></b>\n".format(index=idx, link=d['url'], title=html.escape(d['title']))
          
          text += f"\n<b>By {config.BOT_USERNAME}</b>"
          
          return await message.reply(text, parse_mode=enums.ParseMode.HTML)
           
    
@bot.on_message(filters.command('wiki') & ~filters.forwarded)
async def Wikipedia_func(_, message):
       if len(message.text.split()) == 1:
          return await message.reply('💭 **Example**: `/wiki Elon musk`')
       else:
          query = message.text.split(maxsplit=1)[1]
          data = await search_wikipedia(query, 10)
          if not data:
             return await message.reply("❌ **No results found!**")
          
          text = "<b>🔎 Wikipedia Search</b>:\n\n"
          for idx, d in enumerate(data, start=1):
              text += "<b>{index}, <a href='{link}'>{title}</a></b>\n".format(index=idx, link=d['url'], title=html.escape(d['title']))
          
          text += f"\n<b>By {config.BOT_USERNAME}</b>"
          
          return await message.reply(text, parse_mode=enums.ParseMode.HTML)
           
  

  
     
@bot.on_message(filters.command('ytsearch') & ~filters.forwarded)
async def youtubeSearch_func(_, message):
       if len(message.text.split()) == 1:
          return await message.reply('💭 **Example**: `/ytsearch nandhaxd`')
       else:
          query = message.text.split(maxsplit=1)[1]
          data = await search_youtube(query, 10)
          if not data:
             return await message.reply("❌ **No results found!**")
          
          text = "<b>🔎 YouTube Search</b>:\n\n"
          for idx, d in enumerate(data, start=1):
              text += "<b>{index}, <a href='{link}'>{title}</a></b>\n".format(index=idx, link=d['url'], title=html.escape(d['title']))
         
          text += f"\n<b>By {config.BOT_USERNAME}</b>"
           
          return await message.reply(text, parse_mode=enums.ParseMode.HTML)
           
  
 
  
  
@bot.on_message(filters.command("sof") & ~filters.forwarded)
async def stackflow(_, message):
    if len(message.command) == 1:
        return await message.reply("Give a query to search in StackOverflow!")
    
    msg = await message.reply("Getting data..")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.stackexchange.com/2.3/search/excerpts"
            params = {
                "order": "asc",
                "sort": "relevance",
                "q": message.command[1],
                "accepted": "True",
                "migrated": "False",
                "notice": "False",
                "wiki": "False",
                "site": "stackoverflow"
            }
            
            async with session.get(url, params=params) as response:
                r = await response.json()
        
        hasil = "<b>🔎 StackOverFlow Results</b>:\n\n"
        for count, data in enumerate(r["items"], start=1):
            question = data["question_id"]
            title = data["title"]
            snippet = (
                remove_html_tags(data["excerpt"])[:80].replace("\n", "").replace("    ", "")
                if len(remove_html_tags(data["excerpt"])) > 80
                else remove_html_tags(data["excerpt"]).replace("\n", "").replace("    ", "")
            )
            hasil += f"{count}. <a href='https://stackoverflow.com/questions/{question}'>{title}</a>\n<code>{snippet}</code>\n"

        hasil += f"\n\n<b>By {config.BOT_USERNAME}</b>"
      
        try:
            await msg.edit(hasil)
        except Exception as e:
            # If message is too long, save to file
            path = f"{message.from_user.id}_sof.txt"
            with open(path, 'w', encoding='utf-8') as f:
                f.write(hasil)
            await msg.reply_document(document=path)
            # Clean up the file after sending
            os.remove(path)
    
    except Exception as e:
        await msg.edit(f"An error occurred: {str(e)}")
