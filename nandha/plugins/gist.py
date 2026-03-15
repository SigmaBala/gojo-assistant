
import os
import json
import config
import aiohttp
from pyrogram import filters, types
from nandha import pbot as bot
from nandha.helpers.utils import UserId, get_size


# add ptb mime_type here for text documents

EXTENSION = {
     "application/javascript": "js",
     "application/json": "json",
     "text/x-python": "py",
     "text/python": "py",
     "text/html": "html",
     "text/plain": "txt",
     "text/css": "css",
     "text/x-c": "cpp",
}


__module__ = "Gist"


__help__ = (
    "*Commands*:\n"
    "/gist\n\n"
    "```\n"
    "/gist <Language: (text/plain)>: reply to text or text document for get gist post url.\n"
    "(alternative code paster using GitHub Gist Account)\n"
    "```\n\n"
    "*Language*:\n" +
    ''.join(f'`{lang}`,\n' for lang in list(EXTENSION.keys())) +
    "\n*Example*:\n"
    "`/gist text/html`\n"
    "`/gist reply to document`\n"
)




@bot.on_message(filters.command('gist') & ~filters.forwarded)
async def gist(_, m: types.Message):

      r = m.reply_to_message
      allowed = (r.document or r.text or r.caption) if r else None
      if not allowed:
          return await m.reply("Reply to message text or document ...")

      msg = await m.reply_text("Analysis Gist ...")
  
      if r and r.document and r.document and int(r.document.file_size/1024**2) < 2:
            path = await r.download()
            with open(path, 'r') as file:
                  content = file.read()
            os.remove(path)
            mime_type = getattr(r.document, 'mime_type', 'text/plain')
            
      else:
            content = (r.text or r.caption)
            mime_type = m.text.split()[1] if len(m.text.split()) > 1 else "text/plain"


      if not content:
           return await msg.edit_text("❌ *No content found to paste*", parse_mode=constants.ParseMode.MARKDOWN)
           
      api_url = "https://api.github.com/gists/e08f0a195acf449983815ee7bc3fde4e"
      headers = {
        "Authorization": f"Bearer {config.GIST_TOKEN}",
        "accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
      }


      ext = EXTENSION.get(mime_type, 'txt')
      id = f"{UserId()}.{ext}"
      payload = {        
          "files": {
              id: {
                 "content": str(content)
              }
          }
      }
      try:
         async with aiohttp.ClientSession() as session:
              async with session.post(api_url, headers=headers, data=json.dumps(payload)) as response:
                      if response.status != 200:
                           return await msg.edit(f'❌ ERROR: `{response.reason}`')
                      results = await response.json()
                      files = results['files']
                      paste = files.get(id, None)
                      file_url = f"https://gist.github.com/NandhaxD/e08f0a195acf449983815ee7bc3fde4e#file-{id.replace('.', '-')}"
                      if not paste:
                           return await msg.edit('Pasted File Not Found ❌')
                      else:
                           buttons = types.InlineKeyboardMarkup([[
                               types.InlineKeyboardButton("RAW", url=paste['raw_url']),
                               types.InlineKeyboardButton("URL", url=file_url)
                           ]])
                           text = (
                              "```\n\n"
                              f"Language: {paste['language']}\n"
                              f"Type: {paste['type']}\n"
                              f"Size: {get_size(paste['size'])}\n"
                              "\n\n```"
                           )
                           await msg.edit(text, reply_markup=buttons)
      except Exception as e:
           return await msg.edit(f'❌ ERROR: {str(e)}')
      

