
 

from nandha import pbot as app
from pyrogram import filters, types
import aiohttp
import config


__help__ = '''
*Commands*:
/ud

```
/ud <query>: this urban dictionary.
and you know this have exact meaning of urban slangs.
for eg. stfu, fr, like them ( it may contain abuse words meaning too).
```

*Example*:
`/ud lol`
`/ud imao`
'''

__module__ = 'UD'

@app.on_message(filters.command("ud"))
async def urban(_, m):  
    user_id = m.from_user.id
    if len(m.text.split()) == 1:
        return await m.reply("Enter the text for which you would like to find the definition.")
    
    text = m.text.split(None,1)[1]
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.urbandictionary.com/v0/define?term={text}") as response:
            api = await response.json()
    
    mm = api["list"]
    if 0 == len(mm):
        return await m.reply("=> No results Found!")
    
    string = f"🔍 **Ward**: {mm[0].get('word')}\n\n📝 **Definition**: {mm[0].get('definition')}\n\n✏️ **Example**: {mm[0].get('example')}\n\n**By {config.BOT_USERNAME}**"
    
    if 1 == len(mm):
        return await m.reply(text=string, quote=True)
    else:
        num = 0
        return await m.reply(
            text=string, 
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton('next', callback_data=f"udnxt:{user_id}:{text}:{num}")]
            ]), 
            quote=True
        )
              
@app.on_callback_query(filters.regex("^udnxt"))   
async def udnext(_, query):
    user_id = int(query.data.split(":")[1])
    text = str(query.data.split(":")[2])
    num = int(query.data.split(":")[3])+1
    
    if not query.from_user.id == user_id:
        return await query.answer("This is not for You!")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.urbandictionary.com/v0/define?term={text}") as response:
            api = await response.json()
    
    mm = api["list"]
    uwu = mm[num]
    
    if num == len(mm)-1:
        string = f"🔍 **Ward**: {uwu.get('word')}\n\n📝 **Definition**: {uwu.get('definition')}\n\n✏️ **Example**: {uwu.get('example')}\n\n"
        string += f"Page: {num+1}/{len(mm)}\n\n**By {config.BOT_USERNAME}**"
        return await query.message.edit(
            text=string, 
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton('➡️ Back', callback_data=f"udbck:{query.from_user.id}:{text}:{num}")]
            ])
        )
    else:
        string = f"🔍 **Ward**: {uwu.get('word')}\n\n📝 **Definition**: {uwu.get('definition')}\n\n✏️ **Example**: {uwu.get('example')}\n\n"
        string += f"Page: {num+1}/{len(mm)}\n\n**By {config.BOT_USERNAME}**"
        buttons = [[
            types.InlineKeyboardButton("Back ⏮️", callback_data=f"udbck:{query.from_user.id}:{text}:{num}"),
            types.InlineKeyboardButton("Next ⏭️", callback_data=f"udnxt:{query.from_user.id}:{text}:{num}") 
        ]]
        return await query.message.edit(
            text=string, 
            reply_markup=types.InlineKeyboardMarkup(buttons)
        )

@app.on_callback_query(filters.regex("^udbck"))   
async def udback(_, query):
    user_id = int(query.data.split(":")[1])
    text = str(query.data.split(":")[2])
    num = int(query.data.split(":")[3])-1
    
    if not query.from_user.id == user_id:
        return await query.answer("This is not for You!")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.urbandictionary.com/v0/define?term={text}") as response:
            api = await response.json()
    
    mm = api["list"]
    uwu = mm[num]
    
    if num == 0:
        string = f"🔍 **Ward**: {uwu.get('word')}\n\n📝 **Definition**: {uwu.get('definition')}\n\n✏️ **Example**: {uwu.get('example')}\n\n"
        string += f"Page: {num+1}/{len(mm)}\n\n**By {config.BOT_USERNAME}**"
        return await query.message.edit(
            text=string, 
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton('➡️ Next', callback_data=f"udnxt:{query.from_user.id}:{text}:{num}")]
            ])
        )
    else:
        string = f"🔍 **Ward**: {uwu.get('word')}\n\n📝 **Definition**: {uwu.get('definition')}\n\n✏️ **Example**: {uwu.get('example')}\n\n"
        string += f"Page: {num+1}/{len(mm)}\n\n**By {config.BOT_USERNAME}**"
        buttons = [[
            types.InlineKeyboardButton("Back ⏮️", callback_data=f"udbck:{query.from_user.id}:{text}:{num}"),
            types.InlineKeyboardButton("Next ⏭️", callback_data=f"udnxt:{query.from_user.id}:{text}:{num}") 
        ]]
        return await query.message.edit(
            text=string, 
            reply_markup=types.InlineKeyboardMarkup(buttons)
        )
