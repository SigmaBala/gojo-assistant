
from bs4 import BeautifulSoup
from urllib.parse import quote
from nandha import aiohttpsession as session, app
from nandha.helpers.decorator import Command, send_action
from nandha.helpers.scripts import gimage_search, pinterest_search_image, zerochan, fetch_wallpapers
from telegram import constants, InputMediaPhoto, error


import random
import asyncio
import config


__module__ = 'Image Search'

__help__ = '''
*Commands*:
/wallpaper, /pimg
/zerochan, /gimg

```
/wall or /wallpaper <query>:
Provide a query to get from wallpapers, or default to anime wallpapers.
/pimg <query>: get images in pinterest.
/zerochan <query>: get anime images in zerochan
/gimg <query>: images from google.
```

*Example*:
`/wallpaper gojo`
`/pimg gojo`
`/zerochan shikimori`
`/gimg gojo`
'''

# for handling time-out & spamming cmds

process = {}







@Command('gimg')
@send_action(constants.ChatAction.UPLOAD_PHOTO)
async def googleImageSearch(update, context):
       m = update.effective_message
       user = m.from_user
       chat = m.chat
       if len(m.text.split()) < 2:
            return await m.reply_text("ℹ️ Needed a query to process.")
       elif process.get(user.id):
            return await m.reply_text("Already a processing ongoing, don't make me sick!")
              
       else:
           process[user.id] = True
           msg = await m.reply_text("🔎 *Search for images ...*", parse_mode=constants.ParseMode.MARKDOWN)
           results = await gimage_search(m.text.split(maxsplit=1)[1], limit=10)
           error = results.get('error')
           if error:
               process[user.id] = False
               return await msg.edit_text(error)
                  
           images = results['results']
           n = 3
           result = [images[i:i + n] for i in range(0, len(images), n)]
              
           for idx, image_list in enumerate(result, start=1):
                 media = []
                 for img in image_list:
                      media.append(InputMediaPhoto(img))
                 try:
                    await msg.edit_text(
                       text=f"ℹ️ *Trying to upload images in group {idx}...*",
                       parse_mode=constants.ParseMode.MARKDOWN
                    )
                    await chat.send_media_group(media)
                    await asyncio.sleep(5)
                 except Exception as e:
                       process[user.id] = False
                       await msg.edit_text(
                         f"❌ *ERROR when uploading group {idx}  images: {str(e)}, skipping ...*",
                         parse_mode=constants.ParseMode.MARKDOWN
                       )
                       await asyncio.sleep(4)

           process[user.id] = False
           return await msg.edit_text(
                text=f"✅ *All images Successfully uploaded by {config.BOT_USERNAME}*",
                parse_mode=constants.ParseMode.MARKDOWN
           )







@Command('zerochan')
@send_action(constants.ChatAction.UPLOAD_PHOTO)
async def ZeroChanImageSearch(update, context):
       m = update.effective_message
       user = m.from_user
       chat = m.chat
       if len(m.text.split()) < 2:
            return await m.reply_text("ℹ️ Needed a query to process.")
       elif process.get(user.id):
            return await m.reply_text("Already a processing ongoing, don't make me sick!")
              
       else:
           process[user.id] = True
           msg = await m.reply_text("🔎 *Search for images ...*", parse_mode=constants.ParseMode.MARKDOWN)
           results = await zerochan(m.text.split(maxsplit=1)[1])
           error = results.get('error')
           if error:
               process[user.id] = False
               return await msg.edit_text(error)
           images = results['results']
           titles = [f"*{idx}, {t['title']}*" for idx, t in enumerate(images, start=1)]
           await chat.send_message('' + '\n'.join(titles), parse_mode = constants.ParseMode.MARKDOWN)
           n = 3
           result = [images[i:i + n] for i in range(0, len(images), n)]
           for idx, image_list in enumerate(result, start=1):
                 media = []
                 for imgs in image_list:
                      media.append(InputMediaPhoto(imgs['url']))
                 try:
                    await msg.edit_text(
                       text=f"ℹ️ *Trying to upload images in group {idx}...*",
                       parse_mode=constants.ParseMode.MARKDOWN
                    )
                    await chat.send_media_group(media)
                    await asyncio.sleep(5)
                 except Exception as e:
                       process[user.id] = False
                       await msg.edit_text(
                         f"❌ *ERROR when uploading group {idx}  images: {str(e)}, skipping ...*",
                         parse_mode=constants.ParseMode.MARKDOWN
                       )
                       await asyncio.sleep(4)

           process[user.id] = False
           return await msg.edit_text(
                text=f"✅ *All images Successfully uploaded by {config.BOT_USERNAME}*",
                parse_mode=constants.ParseMode.MARKDOWN
           )


@Command('pimg')
@send_action(constants.ChatAction.UPLOAD_PHOTO)
async def PinterestImageSearch(update, context):
       m = update.effective_message
       user = m.from_user
       chat = m.chat
       if len(m.text.split()) < 2:
            return await m.reply_text("ℹ️ Needed a query to process.")
       elif process.get(user.id):
            return await m.reply_text("Already a processing ongoing, don't make me sick!")
              
       else:
           process[user.id] = True
           msg = await m.reply_text("🔎 *Search for images ...*", parse_mode=constants.ParseMode.MARKDOWN)
           results = await pinterest_search_image(m.text.split(maxsplit=1)[1])
           error = results.get('error')
           if error:
               process[user.id] = False
               return await msg.edit_text(error)
           images = results['results']
           n = 3
           result = [images[i:i + n] for i in range(0, len(images), n)]
           for idx, image_list in enumerate(result, start=1):
                 media = []
                 for imgs in image_list:
                      media.append(InputMediaPhoto(imgs['url']))
                 try:
                    await msg.edit_text(
                       text=f"ℹ️ *Trying to upload images in {idx} group ...*",
                       parse_mode=constants.ParseMode.MARKDOWN
                    )
                    await chat.send_media_group(media)
                    await asyncio.sleep(5)
                 except Exception as e:
                       process[user.id] = False
                       await msg.edit_text(
                         f"❌ *ERROR when uploading {idx} group images: {str(e)}, skipping ...*",
                         parse_mode=constants.ParseMode.MARKDOWN
                       )
                       await asyncio.sleep(4)

           process[user.id] = False
           return await msg.edit_text(
                text=f"✅ *All images Successfully uploaded by {config.BOT_USERNAME}*",
                parse_mode=constants.ParseMode.MARKDOWN
           )
                   
     


@Command(('wall', 'wallpaper', 'wallpapers'))
@send_action(constants.ChatAction.UPLOAD_PHOTO)
async def Wallpapers_com(update, context):
      message = update.effective_message
      user = message.from_user
      if process.get(user.id):
            return await message.reply_text("Already a process ongoing, don't make me sick!")
       
      process[user.id] = True
      msg = await message.reply_text(
         "🔎 *Searching for images ...*", 
         parse_mode=constants.ParseMode.MARKDOWN
      )
      if len(message.text.split()) == 1:
          data = await fetch_wallpapers()
      else:
          data = await fetch_wallpapers(
              query = message.text.split(maxsplit=1)[1]
          )

      random.shuffle(data) # To shuffle the fetched images.
  
      media = []
      text = ""
    
      if len(data) == 0:
          return await msg.edit_text(
             "*ℹ️ No Images fetched*",
            parse_mode=constants.ParseMode.MARKDOWN
          )
      msg = await msg.edit_text(
              f"*✅ Successfully fetched {len(data)} sending images.*",
            parse_mode=constants.ParseMode.MARKDOWN
      )

      limits = data[:10]
      
      for idx, image_key in enumerate(limits, start=1):
                
                if idx == len(limits):
                    text += f"`{idx}`, *{image_key['title']}*"
                    media.append(
                       InputMediaPhoto(
                         media=image_key['url'],
                         caption=text,
                         parse_mode=constants.ParseMode.MARKDOWN
                       )
                )
                else:
                    text += f"`{idx}`, *{image_key['title']}*\n"
                    media.append(
                       InputMediaPhoto(
                         media=image_key['url']
                       )
                   )
      try:
         await message.reply_media_group(
                  media=media, parse_mode=constants.ParseMode.MARKDOWN
              )
         process[user.id] = False
         await msg.delete()
      except error.TimedOut:
           await asyncio.sleep(3)
      except error.TelegramError as e:
           await msg.delete()
           await message.reply_text(f"❌ Error: {str(e)}")
           process[user.id] = False
      

  


