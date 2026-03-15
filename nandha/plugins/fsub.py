import uuid
import asyncio

from pyrogram import types, errors, filters, enums
from pyrogram.types import InlineKeyboardButton
from nandha import pbot, pbot as bot
from nandha.db.fsub import *
from nandha.helpers.pyro_utils import check_membership, is_admin, check_admin_rights

refresh = {}


__module__ = "Fsub"

__help__ = """
/fsub, /rmfsub

```
- /fsub <username or chat id>: to enable force subscription in your chat only used by admin with restrictions rights.
- /rmfsub: remove force subscription in the chat.
```

*Example*:
`/fsub @NandhaBots`
"""




@pbot.on_callback_query(filters.regex('^fsub_refresh'))
async def refresh_fsub_user(bot, query):
    data = query.data
    user = query.from_user
    m = query.message
    _, user_id, force_chat_id = data.split('#')
    user_id, force_chat_id = int(user_id), int(force_chat_id)

    if user.id != user_id:
        return await query.answer(f'💀 This is not for you, {user.full_name}!', show_alert=True)

    if refresh.get(user.id, None):
        return await query.answer(f"🧐 Don't spam the button, {user.full_name}!", show_alert=True)

    refresh[user.id] = str(uuid.uuid4())

    is_member = await check_membership(force_chat_id, user.id)
    if not is_member:
        await query.answer(f"😌 Don't be so smart, {user.full_name}. Join our channel to continue chatting here.", show_alert=True)
        return

    member = await bot.get_chat_member(m.chat.id, user.id)
    if member.status != enums.ChatMemberStatus.RESTRICTED:        
        await query.answer(f"🧐 Nah! You're not restricted, {user.full_name}!", show_alert=True)
        await asyncio.sleep(5)
        if user.id in list(refresh.keys()):
            del refresh[user.id]   
        await m.delete()
        return

    try:
        chat_permissions = (await bot.get_chat(m.chat.id)).permissions  # Get chat permissions to restore all necessary permissions back to the restricted user
        await bot.restrict_chat_member(m.chat.id, user.id, chat_permissions)
        await asyncio.sleep(5)
        await m.delete()
        del refresh[user.id]
    except Exception as e:
        await m.edit_text(f'❌ **Error when unrestricting user {user.mention} (ID: {user.id})**: `{e}`')
        await asyncio.sleep(5)
        del refresh[user.id]


@pbot.on_message(group=-100)
async def force_user(_, message):
    m = message
    user = m.from_user
    chat = m.chat

    if chat.id in CHAT_IDS:
        fsub = await get_chat_fsub(chat.id)
        if fsub and fsub.get('switch', False):
            force_chat_id = fsub['force_chat_id']

            invite_link = (await pbot.get_chat(force_chat_id)).invite_link
            if not invite_link:
                return await m.reply(f"🤨 **I can't generate invite link for force chat {chat.title} (ID: {chat.id}), please checkout and give me rights.**")

            is_member = await check_membership(force_chat_id, user.id)

            if not is_member:
                try:
                    await bot.restrict_chat_member(chat.id, user.id, types.ChatPermissions())
                except errors.ChatAdminRequired:
                    return await m.reply_text(f'🧐 **I need admin rights to restrict users who are not joined in the fsub group/channel {chat.title} (ID: {chat.id})!**')
                except errors.UserAdminInvalid:
                    return  # Skip the user
                except Exception as e:
                    return await m.reply_text(f'❌ **Error when restricting user {user.mention} (ID: {user.id})**: `{e}`')

                buttons = [
                    [InlineKeyboardButton("📢 Join", url=invite_link),
                     InlineKeyboardButton("🔄 Refresh", callback_data=f"fsub_refresh#{user.id}#{force_chat_id}")]
                ]

                await m.reply_text(
                    f"<blockquote><b>Hello {user.mention} (ID: {user.id})! This chat {chat.title} (ID: {chat.id}) has enabled force subscription. To chat here, please join the channel/group below and then click refresh.</b></blockquote>",
                    reply_markup=types.InlineKeyboardMarkup(buttons))


@pbot.on_message(filters.command('rmfsub') & ~filters.forwarded)
async def remove_force_sub(_, message):
    m = message
    chat = m.chat
    user = m.from_user

    if chat.type == enums.ChatType.PRIVATE:
        return await m.reply(f'🤨 **This feature only works for groups, {user.full_name}!**')

    can_do = await check_admin_rights(chat.id, user.id, 'can_restrict_members')
    if not can_do:
        return await m.reply(f"**You don't have enough rights to cancel force subscription, {user.full_name}!**")

    if chat.id in CHAT_IDS:
        CHAT_IDS.remove(chat.id)

    await remove_chat(chat.id)

    return await m.reply(f'✅ **Force Subscription Removed from {chat.title} (ID: {chat.id})!**')


@pbot.on_message(filters.command('fsub') & ~filters.forwarded)
async def force_sub(_, message):
    m = message
    chat = m.chat
    user = m.from_user

    if chat.type == enums.ChatType.PRIVATE:
        return await m.reply(f'🤨 **This feature only works for groups, {user.full_name}!**')

    query = m.text.split(maxsplit=1)[1].strip().split()[0] if len(m.text.split()) > 1 else False

    if not query:
        return await m.reply(f'**Provide a username or chat Telegram ID, {user.full_name}...**')

    verify_admin = await is_admin(chat.id, user.id)
    if not verify_admin:
        return await m.reply_text(f'**Only admins can do this, {user.full_name}.**')

    if query.startswith('-100'):
        chat_id = int(query)
    elif query.startswith('@'):
        chat_id = query
    else:
        return await m.reply(f'**Only accepts @username or Telegram ID, {user.full_name}...**')

    try:
        info = await bot.get_chat(chat_id)
    except Exception as e:
        return await m.reply(f'❌ **Error when checking force chat info for {chat.title} (ID: {chat.id})**: `{e}`')

    if (await is_admin(info.id, bot.me.id)) and (await check_admin_rights(chat.id, bot.me.id, 'can_restrict_members')):
        if chat.id not in CHAT_IDS:
            CHAT_IDS.append(chat.id)
        await update_fsub(chat.id, force_chat_id=info.id)
        await m.reply(f'✅ **Enabled force subscription for {chat.title} (ID: {chat.id}) to {info.title}** (`{info.id}`) ...')
    else:
        await m.reply_text(f'🧐 **I need restrict rights to enable this feature in {chat.title} (ID: {chat.id}), {user.full_name}!**')

  
