

import os
import time
from pyrogram import types, filters, enums
from nandha.helpers.decorator import unavailable
from nandha import pbot

__module__ = "rename"

__help__ = """
*Commands*:
/rename

```
/rename < file_name with extension / None >:
This module will help you to rename documents, photos, stickers,
videos, and files in Telegram and upload them quickly.
```

```Note:
You can set a custom thumbnail for your files, but keep in mind that this thumbnail will be deleted at any time, so you must check if the thumbnail file is present before renaming.
```

*Example*:
`/setthumb: Reply to a photo to set the thumbnail.`
`/clearthumb: Clear the thumbnail photo from the disk.`
`/getthumb: Get the user's currently set custom thumbnail from the disk.`
"""


temp = {}

@pbot.on_message(filters.command(["setthumb", "getthumb", "clearthumb"]) & ~filters.forwarded)
@unavailable
async def thumbnail(_, message):
       m = message
       r = m.reply_to_message
       user = m.from_user
     
       cmd = m.command[0].lower()
       if cmd == "setthumb":
           if r and r.photo:
               path = await r.download()
               temp[user.id] = path
               return await m.reply("✅ **thumbnail saved Successfully.**")
           else:
               return await m.reply("Only reply to photo type.")
       elif cmd == "clearthumb":
             if user.id in temp:
                   del temp[user.id]
                   return await m.reply("✅ **Removed thumbnail from saved!**")
             else:
                   return await m.reply("❌ No thumbnail is currently in disk!")
       else:
            if user.id in temp:
                return await m.reply_photo(photo=temp[user.id], caption="👀 **Your currently saved thumbnail!**")
            else:
                return await m.reply("❌ No thumbnail is currently in disk!")
 

@pbot.on_message(filters.command("rename") & ~filters.forwarded)
@unavailable
async def renamer(_, message):
     m = message
     reply = r = m.reply_to_message
     chat = m.chat
     user = m.from_user

     media = [
         enums.MessageMediaType.ANIMATION,
         enums.MessageMediaType.VIDEO,
         enums.MessageMediaType.STICKER,
         enums.MessageMediaType.PHOTO,
         enums.MessageMediaType.DOCUMENT,
         enums.MessageMediaType.AUDIO
     ]
     if not getattr(reply, 'media', None):
         return await m.reply("**⚠️ Only reply to a media file!**")
     elif reply.media not in media:
         return await m.reply("**⚠️ Not Supported media type!**")
     else:

        def get_ext(doc: str) -> str:
              ext = doc.file_name[-6:]
              if "." in ext:
                  return ext.split(".")[1]
              elif doc.mime_type:
                   return doc.mime_type.split("/")[1]
              else:
                   return "idk"
              
        file_name_formats = {
    enums.MessageMediaType.ANIMATION: lambda r: (f"{r.animation.file_id}.gif", r.animation.file_size, getattr(r.animation, "thumbs", []) if not r.animation.thumbs else r.animation.thumbs[0].file_id),
    enums.MessageMediaType.VIDEO: lambda r: (f"video_{r.video.file_id}.mp4", r.video.file_size, getattr(r.video, "thumbs", []) if not r.video.thumbs else r.video.thumbs[0].file_id),
    enums.MessageMediaType.STICKER: lambda r: (f"sticker_{r.sticker.file_unique_id}.{get_ext(r.sticker)}", r.sticker.file_size, getattr(r.sticker, "thumbs", []) if not r.sticker.thumbs else r.sticker.thumbs[0].file_id),
    enums.MessageMediaType.PHOTO: lambda r: (f"photo_{r.photo.file_id}.jpeg", r.photo.file_size, r.photo.file_id),
    enums.MessageMediaType.DOCUMENT: lambda r: (f"document_{r.document.file_id}.{get_ext(r.document)}", r.document.file_size, getattr(r.document, "thumbs", []) if not r.document.thumbs else r.document.thumbs[0].file_id),
    enums.MessageMediaType.AUDIO: lambda r: (f"audio_{r.audio.file_id}.{get_ext(r.audio)}", r.audio.file_size, getattr(r.audio, "thumbs", []) if not r.audio.thumbs else r.audio.thumbs[0].file_id)
        }
        msg = await m.reply("**📩 Downloading file please wait.....**")
        file_name, file_size, thumb = file_name_formats[reply.media](reply)
        
        if len(m.text.split()) > 1:
             file_name = m.text.split(maxsplit=1)[1]

        await msg.edit_text("⚡ **Downloading thumbnail from the file...**")
        thumb = await pbot.download_media(thumb) if thumb and user.id not in temp else temp[user.id] if user.id in temp else None
              
        start_time = time.perf_counter()
        last_update_time = start_time

        # Open file for writing
        with open(file_name, "wb+") as file:
             download_size = 0
             mb = 1024 * 1024  # 1 MB = 1024 * 1024 bytes
             await msg.edit("📩 **Downloading ...**")
             
             async for chunk in pbot.stream_media(reply):
                   file.write(chunk)
                   download_size += len(chunk)
                   
                   # Calculate progress and current time
                   current_time = time.perf_counter()
                   progress = (download_size / file_size) * 100
                   
                   # Update progress every 6 seconds
                   if current_time - last_update_time >= 6:
                       try:
                           await msg.edit_text(
                              f"⬇️ **Downloaded {progress:.2f}% "
                              f"({download_size/mb:.2f} MB / {file_size/mb:.2f} MB)**"
                           )
                           last_update_time = current_time
                       except Exception:
                           # If edit fails, just continue downloading
                           pass
                        
        downloaded_time = round(time.perf_counter() - start_time, 4)
               
        await msg.edit("⬆️ **Successfully downloaded now trying to upload in telegram takes some minutes...**")

        try:
             
          upload_msg = await pbot.send_document(
               chat_id=chat.id,
               document=file_name,
               thumb=thumb,
               reply_to_message_id=m.id
          )
          uploaded_time = round(time.perf_counter() - start_time, 4)
             
          os.remove(file_name)
          await msg.delete()
             
          await upload_msg.edit_caption(
               f"```python\nDownloaded time: {downloaded_time}\n"
               f"Uploaded time: {uploaded_time}```\n\n"
               f"**⚡ Successfully reamed by @{_.me.username}**!"
          )
             
        except Exception as e:
            await msg.edit(f"❌ **ERROR**: {e}")

