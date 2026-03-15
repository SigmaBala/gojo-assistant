
import asyncio
from urllib.parse import urlparse, urlunparse

from pyrogram import filters
from nandha import pbot as bot

__help__ = """
*Commands*:
 /copy

/copy <link1> <link2>: for copy files from public username channel's where they restricted us to forward 😄.


*Example*:
`/copy https://t.me/nandhabots/719`
"""

__module__ = 'CopyFile'


@bot.on_message(filters.command('copy') & ~filters.forwarded)
async def copyMsg(bot, message):
    m = message
    args = m.text.split()[1:] if len(m.text.split()) >= 2 else None

    if not args:
        return await m.reply_text(
            'Usage: /copy «telegram_link1» «telegram_link2» https://t.me/nandhabots/719'
        )

    if len(args) > 10:
        return await m.reply_text('🧐 **Only less than 10 link for each call.**')

    msg = await m.reply_text('**Processing...** ⚡')

    failed_links = []
    for idx, link in enumerate(args, start=1):
        if idx % 3 == 0:
            await asyncio.sleep(3)

        try:
            # Normalize link format
            if not link.startswith('https://'):
                link = 'https://' + link

            # Remove query parameters (?single, etc.)
            parsed_url = urlparse(link)
            clean_url = urlunparse(parsed_url._replace(query=""))

            # Split URL and validate
            parts = clean_url.split('/')
            if len(parts) != 5 or 't.me' not in parts[2]:
                failed_links.append(link)
                continue

            # Extract chat_id and message_id
            chat_id = "@" + parts[3]
            msg_id = int(parts[4])

            # Copy the message
            await bot.copy_message(
                chat_id=m.chat.id,
                from_chat_id=chat_id,
                message_id=msg_id
            )

        except (ValueError, IndexError):
            failed_links.append(link)
        except Exception as e:
            failed_links.append(f"{link} (Error: {str(e)})")

    await msg.reply_text("**Processing Done. ✅**")

    if failed_links:
        await msg.edit_text(
            f"❌ Failed to copy from these links:\n" + "\n".join(failed_links),
        )

    await msg.delete()
    