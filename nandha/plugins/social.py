

import aiohttp
import config
import os
import re
import random

from mimetypes import guess_type
from bs4 import BeautifulSoup

from nandha import pbot, aiohttpsession as session
from nandha.helpers.utils import get_ua
from nandha.helpers.decorator import Command, send_action, Callbacks
from nandha.helpers.scripts import pinterest_link2download, pinterest_video_search, XDownloader, Instagram_dl, mediafire_dl
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaVideo, InputMediaPhoto, InputMediaAudio, constants, error, InputMedia
from pyrogram import filters



__module__ = "Social"

__help__ = """
*Commands*:
/pinvideo, /xdl
/igdl, /spotify, /pinterest

```
- /pinvideo <query>: downloader for pinterest.com by qurry.
- /xdl <url>: downloader for x.com by video url.
- /igdl <instagram post url>: downloader for Instagram.com by url.
- /spotify <url>: downloader for spotify.com by url.
- /pinterest <url>: downloader for pinterest.com by url.
```

"""


@pbot.on_message(filters.command("coub") & ~filters.forwarded)
async def coub(_, message):
    m = message
    if len(m.command) == 1:
        await m.reply_text("usage: /coub cat")
        return

    rjson = {}
       
    text = m.text.split(maxsplit=1)[1]
    async with aiohttp.ClientSession() as s:
        async with s.get("https://coub.com/api/v2/search/coubs", params={"q": text}) as res:
            rjson = await res.json()

    if not rjson:
        return await m.reply('Response not found!')
           
    try:
        content = random.choice(rjson["coubs"])
        links = content["permalink"]
        title = content["title"]
    except IndexError:
        await m.reply_text('Results not found!')
    else:
        await m.reply_text(f'<b><a href="https://coub.com/v/{links}">{title}</a></b>')


@pbot.on_message(filters.command('pinterest') & ~filters.forwarded)
async def pinterest(_, message):
       m = message
       text = m.text
       url_re = re.search(r'https:\/\/(pin\.it|in\.pinterest\.com\/pin)\/[^\s]+', text)

       if not url_re:
          return await m.reply('✋ Not a pinterest url, e.g format https://pin.it/xxxxx or https://in.pinterest.com/pin/xxxxx')
              
       url = url_re.group().strip()
       
       try:
          data = await pinterest_link2download(url)
          image_url = data.get('image_url', None)
          video_urls = data.get('video_urls', [])
          txt = f"**❤️ By {config.BOT_USERNAME}**"
          if image_url:
              await m.reply_photo(image_url, caption=txt)
          if video_urls:
              for video_url in video_urls:
                 try:
                   await m.reply_video(video_url, thumb=image_url, caption=txt)
                   await asyncio.sleep(2.5)
                 except:
                    pass
       except Exception as e:
            return await m.reply(f'Error: {e}')
              
              
          
       
       
       
       

@pbot.on_message(filters.command('spotify') & ~filters.forwarded)
async def spotifyer(_, message):
       m = message
       url = m.text.split()[1] if len(m.text.split()) > 1 else False
       if not url:
           return await m.reply('**Provide me url to download!**')
         
       msg = await m.reply_text('**Trying to download ...**')
       
       try:
           api = f"https://api.fabdl.com/spotify/get?url={url}"
           async with session.get(api) as response:
                data = await response.json()
                error = data.get('error')
                if error:
                   return await msg.edit(f"❌ **ERROR**: `{error['message']}`")
                d = data['result']
                id = d['id']
                name = d['name']
                image = d['image']
                gid = d['gid']
                artists = d.get('artists', 'Unknown')
                async with session.get(f'https://api.fabdl.com/spotify/mp3-convert-task/{gid}/{id}') as response:
                      data = await response.json()
                      result = data.get('result')
                      if not result: return await msg.edit("Couldn't download 🤷")
                      url = result['download_url']
                      async with session.get(f'https://api.fabdl.com{url}') as r:
                             data = await r.read()
                        
                      path = f"spotify_{m.id}.mp3"
                      with open(path, 'wb+') as file:
                           file.write(data)
                      
                      caption_txt = (
                        f"🎵 **Song Name**: `{name}`"
                        f"\n\n❤️ **By {config.BOT_USERNAME}**"
                      )
                      await m.reply_photo(image, caption=caption_txt)
                      await m.reply_audio(
                          audio=path, 
                          title=name,
                          performer=artists, 
                          caption=caption_txt
                      )
                      await msg.delete()
                      os.remove(path)
       except Exception as e:
             return await msg.edit_text(f'❌ ERROR: `{e}`')
          


@pbot.on_message(filters.command(['instadl', 'igdl']) & ~filters.forwarded)
async def instagramDL(_, message):
    try:
        # Get URL from message
        if len(message.text.split()) <= 1:
            return await message.reply('**Please provide an Instagram URL to download** ✋')
        
        url_txt = message.text.split(maxsplit=1)[1]
        
        # Validate Instagram URL
        ig_pattern = r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[\w-]+/?'
        ig_match = re.match(ig_pattern, url_txt)
        
        if not ig_match:
            return await message.reply('✋ **Invalid Instagram URL. Please provide a valid post/reel URL.**')
        
        Instagram_url = ig_match.group()
        msg = await message.reply('📩 **Downloading please wait ...**')
        
        # Download process
        async with aiohttp.ClientSession() as session:
            # Send request to API
            api_url = f"https://insta-dl.hazex.workers.dev/?url={Instagram_url}"
            
            try:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        return await msg.edit("❌ **API request failed. Please try again later.**")
                    
                    results = await response.json()
                    
                    if results.get('error'):
                        return await msg.edit(f"❌ **Error: {results['error']}**")
                    
                    if not results.get('result') or not results['result'].get('url'):
                        return await msg.edit("❌ **Failed to get download URL.**")
                    
                    dl_url = results['result']['url']
                    
                    # Determine file type and path
                    mime_type = guess_type(dl_url)[0] or ''
                    file_extension = '.jpg' if mime_type.startswith('image') else '.mp4'
                    path = f"instagramDL_{message.id}{file_extension}"
                    
                    # Download media
                    async with session.get(dl_url) as dl_res:
                        if dl_res.status != 200:
                            return await msg.edit("❌ **Failed to download media.**")
                        
                        src_data = await dl_res.read()
                        
                        # Save file
                        with open(path, 'wb') as file:
                            file.write(src_data)
                        
                        # Send media
                        try:
                            if mime_type.startswith('image'):
                                await message.reply_photo(
                                    path,
                                    caption=f"❤️ **Downloaded by {config.BOT_USERNAME}**"
                                )
                            else:
                                await message.reply_video(
                                    path,
                                    caption=f"❤️ **Downloaded by {config.BOT_USERNAME}**"
                                )
                        finally:
                            # Cleanup
                            if os.path.exists(path):
                                os.remove(path)


                            await msg.delete()
                                
            except aiohttp.ClientError as e:
                return await msg.edit(f"❌ **Network error: {str(e)}**")
            
    except Exception as e:
        return await msg.edit(f"❌ **An error occurred: {str(e)}**")      
                       


             
                   


pin_data = {}
@Callbacks('(^pin_dl|^pin_next|^pin_back)')
async def PinterestVideoCQ(update, context):
    query = update.callback_query
    m = update.effective_message
    user = query.from_user
    _, video_id, user_id = query.data.split("#")
    video_id = int(video_id)  # Convert to int early
    
    if user.id != int(user_id):
        return await query.answer("This is not your request!", show_alert=True)
    
    data = pin_data.get(user.id)
    if not data:
        return await query.answer("This query was expired!", show_alert=True)
    
    search_query, videos = data

    async def edit_msg(video_id):
        video = videos[video_id]
        text = (
            f"🔎 *Results for {search_query}.*\n"
            f"📌 *Current page*: `{video_id+1}` of `{len(videos)}`\n"  # Add 1 for user-friendly display
            f"🎥 *Duration*: `{round(video['duration']/60, 2)} Min`\n\n"
            f"*By {config.BOT_USERNAME}*"
        )
        
        button = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Back ◀️', callback_data=f'pin_back#{video_id}#{user.id}'),
                InlineKeyboardButton('Next ⏭️', callback_data=f'pin_next#{video_id}#{user.id}'),
            ],
            [
                InlineKeyboardButton('Download 📩', callback_data=f'pin_dl#{video_id}#{user.id}')
            ],
            [
                InlineKeyboardButton('Close ❌', callback_data=f'delete#{user.id}')
            ]
        ])
        
        await m.edit_media(
            media=InputMediaPhoto(
                media=video['thumbnail'],
                caption=text,
                parse_mode=constants.ParseMode.MARKDOWN
            ),
            reply_markup=button
        )

    if _ == "pin_next":
        if video_id >= len(videos) - 1:  # Fix index check
            return await query.answer("Maximum results reached, you can only go back!", show_alert=True)
        await edit_msg(video_id + 1)
    
    elif _ == "pin_back":
        if video_id <= 0:  # Fix index check
            return await query.answer("Minimum results reached, you can only go next!", show_alert=True)
        await edit_msg(video_id - 1)
    
    else:  # pin_dl case
        video = videos[video_id]
        video_url = video['url']
        duration = video['duration']
        thumb = video['thumbnail']
        
        if video_url.endswith('.mp4'):
            return await m.reply_video(video_url, duration=duration, thumbnail=thumb)
        
        msg = await m.reply_text(
            "📩 *Video Downloading ...*",
            parse_mode=constants.ParseMode.MARKDOWN
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        path = f"video_{query.id}.mp4"
                        with open(path, "wb") as file:
                            file.write(content)
                        
                        await msg.edit_media(
                            media=InputMediaVideo(
                                media=path,
                                duration=duration,
                                thumbnail=thumb
                            )
                        )
                        # Clean up the file after sending
                        import os
                        os.remove(path)
                    else:
                        await msg.edit_text("Failed to download video. Please try again later.")
        except Exception as e:
            await msg.edit_text(f"Error downloading video: {str(e)}")


@Command(['pinvideo', 'pinterestvideo'])
async def PinterestVideoSearch(update, context):
    m = update.effective_message  # Fixed typo
    user = m.from_user
    
    if len(m.text.split()) < 2:  # Fixed condition
        return await m.reply_text("Provide query to search videos in pinterest.")
    
    query = m.text.split(maxsplit=1)[1]
    msg = await m.reply_text(
          text="🔎 *Searching for videos ...*",
          parse_mode=constants.ParseMode.MARKDOWN
    )
    
    try:
        results = await pinterest_video_search(query)
        error = results.get('error')
        if error:
            return await msg.edit_text(error)    
        videos = results['results']
        if not videos:
            return await msg.edit_text("No videos found for your query.")
        
        pin_data[user.id] = query, videos
        video_id = 0  # Start from index 0
        first_video = videos[video_id]
        
        button = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Back ◀️', callback_data=f'pin_back#{video_id}#{user.id}'),
                InlineKeyboardButton('Next ⏭️', callback_data=f'pin_next#{video_id}#{user.id}'),
            ],
            [
                InlineKeyboardButton('Download 📩', callback_data=f'pin_dl#{video_id}#{user.id}')
            ],
            [
                InlineKeyboardButton('Close ❌', callback_data=f'delete#{user.id}')
            ]
        ])

        text = (
            f"🔎 *Results for {query}.*\n"
            f"📌 *Current page*: `{video_id+1}` of `{len(videos)}`\n"
            f"🎥 *Duration*: `{round(first_video['duration']/60, 2)}`\n\n"
            f"❤️ *By {config.BOT_USERNAME}*"
        )

        await msg.edit_media(
            media=InputMediaPhoto(
                media=first_video['thumbnail'],
                caption=text,
                parse_mode=constants.ParseMode.MARKDOWN
            ),
            reply_markup=button
        )
    except Exception as e:
        await msg.edit_text(f"An error occurred: {str(e)}")




@pbot.on_message(filters.command(['xdl', 'xdownload']) & ~filters.forwarded)
async def XDl(_, message):
    text = message.text
    if not len(text.split()) > 1:
        return await message.reply_text("🧐 You haven't give me any X url yet.")
          
    pattern = r"https:\/\/(www\.)?(x|twitter)\.com\/.*"
    url = re.search(pattern, text)
      
    if not url:
        return await message.reply_text("🤔 Looks like not a vali x/twitter url.")      
          
    msg = await message.reply_text(
          f"**🧏 Downloading pls wait a minute....**",
          
    )
      
    results = await XDownloader(url.group())
      
    if results.get('error'):
        return await msg.edit_text(
            "❌ ERROR:\n" + results['error']
        )        
      
    video_url = results['medias'][-1]['url']
      
    await message.reply_video(
                 video_url,
                 caption=(
                 f"📛 **Title**: {results.get('title')}\n"
                 f"⏱️ **Duration**: {results.get('duration')}\n"
                 f"🎥 **Quality**: {results['medias'][-1]['quality']}\n"
                 f"🗂️ **FormattedSize**: {results['medias'][-1]['formattedSize']}\n"
              )
    )
    await msg.delete()      




