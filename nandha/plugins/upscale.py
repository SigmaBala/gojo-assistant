import aiohttp
import random
import config
import os
from io import BytesIO
from PIL import Image
from pyrogram import filters
from nandha import pbot


__help__ = """
*Commands*:
/upscale

```
Reply to photo with /upscale

also support pattern:
/upscale anime ( for anime upscale ).
/upscale lvl-high ( for high resolution ).
e.g /upscale anime lvl-high
```
"""

__module__ = "Upscaler"



# Dictionary to track active user processes
users = {}

# Helper function to generate a random number
def generate_random_number(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)

# Upscale function using aiohttp
async def upscale(buffer: bytes, anime: bool = False, level: str = None) -> str:
    try:
        # Generate a random number for the request
        random_number = generate_random_number(1_000_000, 999_292_220_822)

        # Determine image dimensions using PIL
        with Image.open(BytesIO(buffer)) as img:
            width, height = img.size

        # Prepare form data
        form_data = aiohttp.FormData()
        form_data.add_field("image_file", buffer, filename="image.jpg", content_type="image/jpeg")
        form_data.add_field("name", str(random_number))
        form_data.add_field("desiredHeight", str(height * 4))
        form_data.add_field("desiredWidth", str(width * 4))
        form_data.add_field("outputFormat", "png")
        if level:
            form_data.add_field("compressionLevel", level)
        form_data.add_field("anime", str(anime).lower())

        # Send the POST request using aiohttp
        api_url = "https://api.upscalepics.com/upscale-to-size"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://upscalepics.com",
            "Referer": "https://upscalepics.com/",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Timezone": "Africa/Cairo",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data=form_data, headers=headers) as response:
                if response.status == 200:
                    json_response = await response.json()
                    return json_response.get("bgRemoved", "").strip()
                else:
                    raise Exception(f"API request failed with status code: {response.status}")

    except Exception as error:
        print(f"An error occurred during upscaling: {error}")
        return None

## Pyrogram handler for the /upscale command
@pbot.on_message(filters.command('upscale') & ~filters.forwarded)
async def upscale_func(_, message):
    user = message.from_user
    is_photo = message.reply_to_message and message.reply_to_message.photo

    # Check if the user already has an active process
    if users.get(user.id, False):
        return await message.reply('😉 <b>Already one process going on, wait!</b>')

    users[user.id] = True

    if not is_photo:
        users.pop(user.id, None)
        return await message.reply('❌ <b>Reply to a photo message!</b>')

    loading_msg = await message.reply('⚡ **Upscaling Image ...**')

    try:
        # Extract optional parameters from the command
        pattern_text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        anime = "anime" in pattern_text
        level = pattern_text.split('lvl-')[1] if 'lvl' in pattern_text else None

        # Download the photo
        path = await message.reply_to_message.download()
        with open(path, 'rb') as image_file:
            image_buffer = image_file.read()

        # Upscale the image
        image_url = await upscale(image_buffer, anime=anime, level=level)

        if image_url and image_url.startswith('http'):
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        img_path = f"upscaled_{message.id}.png"
                        with open(img_path, 'wb') as file:
                            file.write(content)

                        # Send the upscaled image
                        await message.reply_document(img_path, caption=f"**By {config.BOT_USERNAME}**")
                    else:
                        raise Exception("Failed to download the upscaled image")
        else:
            return await message.reply(f'❌ **ERROR**: `{image_url}`')

    except Exception as e:
        return await message.reply(f'❌ **ERROR**: `{e}`')

    finally:
        # Clean up
        if 'path' in locals() and os.path.exists(path):
            os.remove(path)
        if 'img_path' in locals() and os.path.exists(img_path):
            os.remove(img_path)
        if 'loading_msg' in locals():
            await loading_msg.delete()

        users.pop(user.id, None)