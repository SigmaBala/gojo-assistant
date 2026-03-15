

import asyncio
import os, urllib, uuid, random, base64, re, aiohttp

from aiohttp import FormData
from nandha import aiohttpsession as session, BOT_USERNAME, telegraph, app, LOGGER, LOGS_CHANNEL
from nandha.helpers.decorator import Command, send_action, Callbacks, spam_control, only_premium
from nandha.helpers.scripts import AiChats, paste, Gemini, GPTGeneration
from nandha.helpers.utils import get_ua, UserId, get_as_document
from telegram import Update, constants, helpers, error
from telegram.ext import CallbackContext
from telegram import InputMediaPhoto, constants, InlineKeyboardMarkup, InlineKeyboardButton

         



__module__ = 'AI'

__help__ = '''
*Commands*:
/gojo, /gpt, /draw, 
/imagine, /art, /google,
/groq

```
- /gojo <query>: Use Gojo AI (supports photos and stickers).
- /gpt <query>: Get a response from ChatGPT.
- /groq <query>: Get a response from Groq AI.
- /draw <query>: Generate an image from text description.
- /imagine <query>: Generate an image from text description.
- /art <query>: Generate an image from text description.
- /google or /gemini <query>: Get a response from Gemini AI.
```

*Examples*:
`/gojo Hey, what is x^x?`
`/draw A cute anime girl`
`/imagine a cute anime girl`
'''


ai = AiChats()

async def generate_ai_image(prompt, key="Anime"):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url="https://aiimagegenerator.io/api/model/predict-peach",
            json={
                "prompt": prompt,
                "negativePrompt": "",
                "key": key,
                "width": 512,
                "height": 768,
                "quantity": 5,
                "size": "512x768"
            }
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result.get('data', {}).get('url', '❌ *ERROR "url" not found!*').strip()
            else:
                return f"❌ *ERROR status*: `{response.status}`"
                





art_users = {}
@Command('art')
@send_action(constants.ChatAction.UPLOAD_PHOTO)
async def art_Img_func(update, context):
    m = update.effective_message
    user = update.effective_user
    bot = context.bot

    if len(m.text.split()) < 2:
        return await m.reply_text("🙋 Where is the prompt? e.g., /art anime gojo")

    if art_users.get(user.id, None):
        return await m.reply_text('😉 *Please wait already a process on-going!*', parse_mode=constants.ParseMode.MARKDOWN)
    
    art_users[user.id] = True

    prompt = m.text.split(maxsplit=1)[1]
    msg = await m.reply_text("⚡ *Generating Image...*", parse_mode=constants.ParseMode.MARKDOWN)

    try:
        # Generate the image
        image_url = await generate_ai_image(prompt)
        if not image_url.startswith('https'):
            return await msg.edit_text(image_url, parse_mode=constants.ParseMode.MARKDOWN)

        # Download the image
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as image_response:
                if image_response.status == 200:
                    image_data = await image_response.read()
                else:
                    return await msg.edit_text('❌ Failed to download the generated image.')

        # Save the image locally
        image_filename = f"{uuid.uuid4()}.jpeg"
        with open(image_filename, "wb") as file:
            file.write(image_data)

        # Send the image as a photo and document
        await m.reply_photo(image_filename)
        okay = await m.reply_document(image_filename, caption=f"*⚡ By @{bot.username}*", parse_mode=constants.ParseMode.MARKDOWN)
        await okay.copy(LOGS_CHANNEL, caption=f"*By* `{user.id}`", parse_mode=constants.ParseMode.MARKDOWN)
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f'❌ *ERROR*: `{str(e)}`', parse_mode=constants.ParseMode.MARKDOWN)
    finally:
        art_users.pop(user.id, None)
        import os
        if 'image_filename' in locals() and os.path.exists(image_filename):
            os.remove(image_filename)                




@Command('imagine')
@send_action(constants.ChatAction.UPLOAD_PHOTO)
@spam_control
async def DrawImg(update: Update, context: CallbackContext):
    m = update.effective_message
    bot = context.bot

    if len(m.text.split()) < 2:
        return await m.reply_text("🙋 where prompt ? e.g /imagine anime gojo")

    prompt = urllib.parse.quote(m.text.split(maxsplit=1)[1])
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true&model=flux-anime"
    msg = await m.reply_text("⚡ *Generating Image...*", parse_mode=constants.ParseMode.MARKDOWN)

    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36 OPR/86.0.0.0'}
    image_data = None

    async with aiohttp.ClientSession() as session:
        for attempt in range(5):  # Retry up to 5 times
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        break
                    else:
                        await asyncio.sleep(2.5)  # Wait before retrying
            except (aiohttp.ClientConnectionError, aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == 4:  # Last attempt
                    return await msg.edit_text(f'❌ Failed to generate image after multiple attempts: {str(e)}')
                await asyncio.sleep(4.5)  # Wait before retrying

    if not image_data:
        return await msg.edit_text('❌ Failed to generate image. Please try again later.')

    image = str(uuid.uuid4()) + ".png"
    with open(image, "wb") as file:
        file.write(image_data)

    try:
        await m.reply_photo(image)
        await m.reply_document(image, caption=f"*⚡ By @{bot.username}*", parse_mode=constants.ParseMode.MARKDOWN)
        await msg.delete()
    except Exception as e:
        return await msg.edit_text(f'❌ Error when uploading: {str(e)}')

            
          
      

async def get_output(prompt: str, negprompt: str):

    '''
    
    Objective:
         generate text to image.
    Parameter: 
          prompt - str
          negprompt - str
    Return: 
         list of generated image url
         

    By @NandhaBots
    '''
    
    url = "https://api.monsterapi.ai/v1/generate/txt2img"

    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IjQ0MDU5ZWRmMDJhYWFhNjNiYzk5MWU1NjAxYzc2OTZjIiwiY3JlYXRlZF9hdCI6IjIwMjQtMDctMTFUMDg6NTQ6MzguMDI0Nzk1In0.WAYiUA6McRCYtVDpZxKZ7kwm5LcapLz7k6GzKiG3O7Q"
}

    payload = {
    "safe_filter": False,
    "prompt": prompt,
    "negprompt": negprompt,
    "style": "anime",
    "samples": 2,
    "guidance_scale": 8
}
  
    async with session.post(url, headers=headers, json=payload) as response:
        results = await response.json()
      
        status_url = results.get('status_url')
        headers = {
             "accept": "application/json",
             "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IjQ0MDU5ZWRmMDJhYWFhNjNiYzk5MWU1NjAxYzc2OTZjIiwiY3JlYXRlZF9hdCI6IjIwMjQtMDctMTFUMDg6NTQ6MzguMDI0Nzk1In0.WAYiUA6McRCYtVDpZxKZ7kwm5LcapLz7k6GzKiG3O7Q"
        }

        await asyncio.sleep(30)
        async with session.get(status_url, headers=headers) as response:
            results = await response.json()
          
            outputs = results.get('result')
            return outputs.get('output')
              
        


@Command(('draw'))
@spam_control
@only_premium
@send_action(constants.ChatAction.UPLOAD_PHOTO)
async def imageDraw(update, context):
    ''' Example: /draw anime girl neg: bad quality '''
    m = update.effective_message
    bot = context.bot
  
    if len(m.text.split()) == 1:
        return await m.reply_text(
           text='🙋 Write some text to draw. e.g. `/draw anime girl neg: bad quality`',
          parse_mode=constants.ParseMode.MARKDOWN
        )

    text = m.text.split(maxsplit=1)[1].lower()
    prompt = ''
    negprompt = ''

    if 'neg:' in text.split():
        negprompt += text.split('neg:')[1]
         
    else:
        prompt += text
         
    msg = await m.reply_text(
        text='*✨ Drawing please wait some seconds..*',
        parse_mode=constants.ParseMode.MARKDOWN
     )

   
    images = await get_output(prompt, negprompt)
    
    if images:
         media = []
         for image_url in images:
             media.append(
                 InputMediaPhoto(image_url)
             )
         try:
           is_send = await bot.send_media_group(
             chat_id=m.chat.id,
             media=media, 
             reply_to_message_id=m.message_id
             )
           if is_send:
               return await msg.delete()
         except Exception as e:
             return await msg.edit_text(f'❌ Error: {str(e)}')
    else:
      return await msg.edit_text('❌ No media Generated!')
       




gemini = Gemini(api_key="AIzaSyAXUaQHnCwTddJqlFF7FLM4istz2_rIJT8")

@Command(('google', 'gemini'))
@spam_control
async def _gemini(update, context):
    m = update.effective_message
    user = m.from_user
    bot = context.bot
    r = m.reply_to_message
    msg = await m.reply_text("🔎")
    if r and r.photo:
        file_id = r.photo[-1].file_id
        path = await (await bot.get_file(file_id)).download_to_drive()
        prompt = m.text.split(maxsplit=1)[1] if len(m.text.split()) > 2 else r.caption if r.caption else "describe this picture"
        await msg.edit_text("📩 *Image processing ...*", parse_mode=constants.ParseMode.MARKDOWN)
        file = await gemini.upload_image(path)
        if "error" in file: return await msg.edit_text(f"❌ ERROR: {file['error']}")
        else:
             output = await gemini.ask(prompt, file)
             if "error" in output: return await msg.edit_text(f"❌ ERROR: {output['error']}")
             text = output.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response found 😓')
             try:
                 return await msg.edit_text(text, parse_mode=constants.ParseMode.MARKDOWN)
             except Exception as e:
                 return await msg.edit_text(text)
    else:
        if r and (r.text or r.caption):
              prompt = "Replied text:" + f"\n{(r.text or r.caption)}"
              if len(m.text.split()) > 2:
                  prompt += "\nQuestion:" + m.text.split(maxsplit=1)[1]
        else:
             if len(m.text.split()) < 2:
                  return await msg.edit_text("*Ask Something !D* 😓", parse_mode=constants.ParseMode.MARKDOWN)
             prompt = m.text.split(maxsplit=1)[1]
        output = await gemini.ask(prompt)
        if "error" in output: return await msg.edit_text(f"❌ ERROR: {output['error']}")
        else:
            text = output.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response found 😓')
            try:
               return await msg.edit_text(text, parse_mode=constants.ParseMode.MARKDOWN)
            except Exception as e:
               return await msg.edit_text(text)
         
                

@Command(('gojo', 'ask'))
@send_action(constants.ChatAction.TYPING)
@spam_control
async def GojoAI(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
         
    bot = context.bot
    user_id = UserId()
    msg = await message.reply_text("✨ *Gojo Thinking....*", parse_mode=constants.ParseMode.MARKDOWN
)

    if len(message.text.split()) == 1:
        return await msg.edit_text(
            text="*Gojo*:\n`/gojo recommend anime to watch`", 
            parse_mode=constants.ParseMode.MARKDOWN
        )
             
    else:
        prompt = message.text.split(maxsplit=1)[1]
        image = None
        reply = message.reply_to_message
      
        if reply and (reply.photo or (reply.sticker and not reply.sticker.is_video)):
             await msg.edit_text(text="🔎 *Analyzing image ...*", parse_mode=constants.ParseMode.MARKDOWN)
             photo = reply.photo[-1] if reply.photo else reply.sticker
             file = await bot.get_file(photo.file_id)
             path = await file.download_to_drive()
             result = await ai.image_to_text(open(path, 'rb'))
             error = result.get('error')
             if error:
                 await msg.edit_text('😓 *Failed to process image ...*', parse_mode=constants.ParseMode.MARKDOWN)  
                      
             prompt = f"OLD CONVERSATION:\n\n#{result if not error else '❌ Failed To Analyze Image.'}\n\n#{reply.caption if reply.caption else ''}\n\nQuestion:\n{prompt}"
             os.remove(path)
             messages = [{"role": "user", "content": prompt}]
             
        else:
            reply = message.reply_to_message
            if reply and (reply.text or reply.caption):
                prompt = f"OLD CONVERSATION:\n{reply.text or reply.caption}\n\nQuestion:\n{prompt}"
            messages = [{"role": "user", "content": prompt}]

             
        data = await ai.groq(messages)
        reply_text = data['reply'] if data.get("reply") else "I'm Gojo Saturo."
        
        if len(reply_text) > 4000:
             file_path = f'{user_id}_chat.txt'
                 
             paste_src = await paste(reply_text)
             return await msg.edit_text(text=paste_src['paste_url'], disable_web_page_preview=False)
             
        try:
             return await msg.edit_text(
               text=reply_text,
               parse_mode=constants.ParseMode.MARKDOWN
       )
        except Exception as e:
              if "can't find end of the entity" in str(e):
                  return await msg.edit_text(
                        text=reply_text
                  )
              else:
                  return await msg.edit_text(text=f"❌ ERROR: {str(e)}")
          


@Command('gpt')
@send_action(constants.ChatAction.TYPING)
@spam_control
async def ChatGpt(update, context):
     '''
     Purpose:
        -: ask questions to chat gpt
     Required:
        -: Prompt - str
     Returns:
        -: chat gpt response
     '''
     m = update.effective_message
     reply = m.reply_to_message
    
     if len(m.text.split()) == 1: return await m.reply_text(
        text="⚡ Enter some prompt", parse_mode=constants.ParseMode.MARKDOWN
     )

     prompt = urllib.parse.quote(m.text.split(maxsplit=1)[1])   
     if reply and reply.text:
         prompt = f"Old conversation:\n{reply.text}\n\nQuestion:\n{prompt}"
         
     msg = await m.reply_text('🔍')
     gpt = GPTGeneration()
     try:
        gptReply = await gpt.create(prompt)
        if len(gptReply) > 4000:
            document = get_as_document(gptReply)
            await m.reply_document(document)
            await msg.delete()
        else:
            await msg.edit_text(text=gptReply, parse_mode=constants.ParseMode.MARKDOWN)
     except Exception as e:
         return msg.edit_text("*❌ Unkown Error*\n" + str(e), parse_mode=constants.ParseMode.MARKDOWN)
        
     
   

@Command('groq')
@send_action(constants.ChatAction.TYPING)
@only_premium
async def groq(update, context):
    '''
    Info: 
       Access to the fast generative AI Groq.
       Website https://groq.com.
    '''
    
    message = update.effective_message
    reply = message.reply_to_message
    
    if len(message.text.split()) == 1:
        return await message.reply_text(
            "*Enter some query*. ⚡",
            parse_mode=constants.ParseMode.MARKDOWN
        )
      
    msg = await message.reply_text("⚡")
    
    user_prompt = message.text.split(maxsplit=1)[1]
    if reply and reply.text:
        user_prompt = f"Old conversation:\n{reply.text}\n\nQuestion:\n{user_prompt}"
        
    headers = {"Authorization": "Bearer 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"}
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    data = {
         "model": "llama3-70b-8192",
         "messages": [
           {"role": "user", "content": user_prompt}
         ]
     }
  
    async with session.post(api_url, headers=headers, json=data) as response:
         if response.status == 200:
              response_json = await response.json()
              botReply = response_json.get("choices", [])[0].get("message", {}).get("content", "*Sorry i can't answer that question!*")
              if len(botReply) > 3500:
                  document = get_as_document(botReply)
                  await message.reply_document(document)
                  await msg.delete()
              else:
                  await msg.edit_text(
                      text=botReply, parse_mode=constants.ParseMode.MARKDOWN
                   )
         else:
             return await msg.edit_text(
                 text=f"❌ *Request*: `{str(response.reason)}`",
                 parse_mode=constants.ParseMode.MARKDOWN
             )

