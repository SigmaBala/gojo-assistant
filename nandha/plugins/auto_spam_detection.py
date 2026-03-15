from pyrogram import filters, types, enums
from nandha import pbot as Client, LOGGER as log

import re

# List of spam-related regex patterns
CONTEXT = [
    r"crypto",
    r"cash",
    r"win",
    r"bonus",
    r"spins",
    r"sell",
    r"bet",
    r"usdt",
    r"regist",
    r"profit",
    r"invest",
    r"reward",
    r"score",
    r"money",
    r"\d+x",
    r"price",
    r"promot",
    r"premium",
    r"digital",
    r"asset",
    r"nude",
    r"porn",
    r"sex",
    r"airdrop",
    r"referral",
    r"earn",
    r"withdrawal",
    r"buy",
    r"fuck",
]

PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in CONTEXT]

async def check_spam(text: str):
    """
    Checks if the provided text matches spam patterns.

    Returns:
        A list of matched keywords if more than 2 patterns match; otherwise, False.
    """
    if not text:
        return False

    matched = [pattern.pattern for pattern in PATTERNS if pattern.search(text)]
    return matched if len(matched) > 2 else False

def censor_word(word: str) -> str:
    """
    Replaces every second character of a word with an asterisk (e.g., 'cash' -> 'c*s*').
    """
    return ''.join(c if i % 2 == 0 else '*' for i, c in enumerate(word))

@Client.on_message(
    (filters.text | filters.caption) & filters.group, group=-4
)
async def auto_detect_spammers(client: Client, message: types.Message):
    """
    Automatically deletes messages that are detected as spam and notifies the user.
    """
    # Check if the user is an admin
    user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user_status.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return  # Ignore if the user is an admin or owner

    # Use either text or caption (if one is missing, default to an empty string)
    text = message.text or message.caption or ""
    spammers = await check_spam(text)

    if spammers:
        try:
            await message.delete()
        except Exception as e:
            log.error(f"Error deleting message: {e}")

        # Censor the keywords
        censored_keywords = [censor_word(keyword) for keyword in spammers]
        keywords = ", ".join(censored_keywords)
        mention = ""

        async for i in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if not (i.user.is_deleted or i.privileges.is_anonymous or i.user.is_bot):
                mention += f"<a href='tg://user?id={i.user.id}'>\u2063</a>"

        warning_text = (
            f"{mention}⚠️ <b>User {message.from_user.mention(style='html')}'s message has been deleted "
            f"due to spam detection. Detected keywords</b>: <code>{keywords}</code>"
        )
        await message.reply_text(warning_text, parse_mode=enums.ParseMode.HTML)