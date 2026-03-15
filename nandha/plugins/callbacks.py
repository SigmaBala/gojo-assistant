
import config

from nandha.helpers.pyro_utils import gen_link
from nandha import font, MODULE, HELP_CMD_IMG, HELP_MODULE_IMG, pbot
from nandha.helpers.decorator import Callbacks, admin_check
from nandha.helpers.misc import help_button,  help_keyboard_data, get_help_button
from telegram import ChatPermissions, constants, helpers, InlineKeyboardButton, InlineKeyboardMarkup, InputMedia, InputMediaPhoto
from pyrogram import filters as pfilters, types as ptypes



@pbot.on_callback_query(pfilters.regex('^stream'))
async def Cq(_, query):
       data = query.data
       user = query.from_user
       user_id = int(data.split('#')[1])
       if user.id != user_id:
           return await query.answer('💀 This is not yours!', show_alert=True)

       msg = query.message
     
       log_msg = await msg.forward(config.FILE_DB_CHANNEL)
       watch, download = gen_link(log_msg)
       caption = f"```\n{msg.caption}```"
       caption += (
          '\n\n✨ **Your stream link has been generated**:\n\n'
            f'📺 **Watch link**: {watch}\n'
            f'📩 **Download link**: {download}\n\n'
            f'❤️ **By {_.me.username}**'
       )

       buttons = [[
            ptypes.InlineKeyboardButton('Watch 📺', url=watch),
            ptypes.InlineKeyboardButton('Download 📩', url=download)
          
        ]]
       await query.edit_message_caption(caption, reply_markup=ptypes.InlineKeyboardMarkup(buttons))
              


@Callbacks('helpcq')
async def help_callback(update, context):
     query = update.callback_query
     quser = query.from_user
     quser_id = quser.id
     quser_name = quser.first_name
     cmd, user_id, page_num = query.data.split('#')
     user_id, page_num = int(user_id), int(page_num)
     
     if quser_id != user_id:
          return await query.answer("Don't trigger others commands!")
          
     pages = help_keyboard_data(user_id=user_id, columns=config.BTN_COLUMNS, rows=config.BTN_ROWS)
     
     if cmd == "helpcq_next":
           page_num += 1
           if page_num == (len(pages) -1):
                 pages[page_num].append(
                      [
                           InlineKeyboardButton(font('❌ Close'), callback_data=f"delete#{quser.id}"),
                           InlineKeyboardButton(font('⬅️ Back'), callback_data=f"helpcq_back#{quser.id}#{page_num}"),
                      ]
                  
           )
           else:
                 pages[page_num].append(
                        [
                             InlineKeyboardButton(font('⬅️ Back'), callback_data=f"helpcq_back#{quser.id}#{page_num}"),
                             InlineKeyboardButton(font('➡️ Next'), callback_data=f"helpcq_next#{quser.id}#{page_num}"),
               
                        ]
                 )
                
     elif cmd == "helpcq_back":
           page_num -= 1
           
           if 0 == page_num:
                 pages[page_num].append(
                        [
                             InlineKeyboardButton(font('❌ Close'), callback_data=f"delete#{quser.id}"),
                             InlineKeyboardButton(font('➡️ Next'), callback_data=f"helpcq_next#{quser.id}#{page_num}"),
               
                        ]
                 )          
              
           else:
                 pages[page_num].append(
                      [
                           InlineKeyboardButton(font('⬅️ Back'), callback_data=f"helpcq_back#{quser.id}#{page_num}"),
                           InlineKeyboardButton(font('➡️ Next'), callback_data=f"helpcq_next#{quser.id}#{page_num}"),
                      ]
                  
                 )
                 
     buttons = pages[page_num]
     
     await query.edit_message_reply_markup(
             reply_markup=InlineKeyboardMarkup(buttons)
     )
     


@Callbacks('^help')
async def module_help(update, context):
     query = update.callback_query
     quser = query.from_user
     quser_id = quser.id
     quser_name = quser.first_name     
     user_id = int(query.data.split("_")[-1])
     
     if quser_id != user_id:
          return await query.answer("Don't trigger others commands!!")
          
     await query.message.edit_media(
          media=InputMediaPhoto(
               HELP_CMD_IMG
          )
     )
     
     if len(query.data.split("_")) == 2:
           buttons = await get_help_button(query.message, quser)
           if not buttons: return # it will handle itself.
                
           mention = helpers.mention_markdown(quser_id, quser_name)
          
           caption = (
f"""
*Hey* {mention}!

*Need help or want to support us?*

• `/donate`: keep our bot alive and kicking!
• `/support`: get in touch with our official support team.
• `/privacy`: learn how we protect your privacy.

*Ready to explore? Click the button below to discover my commands!*
"""
           )                
           return await query.edit_message_caption(
                caption=caption, 
                parse_mode=constants.ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(buttons)
          )

     else:
        _, module_key, user_id = query.data.split("_")
        help_text = MODULE[module_key]

        photo_url = HELP_MODULE_IMG
          
        await query.message.edit_media(
          media=InputMedia(
               media_type='photo',
               media=photo_url
          )
     )
     
        text = f'*⚡ Help for the module*: *{module_key.upper()}*\n\n' + help_text
          
        buttons = InlineKeyboardMarkup(
           [[
                InlineKeyboardButton(
                    text='🔄 Back', callback_data=f'help_{query.from_user.id}'
                     )

           ]]
      )
        return await query.edit_message_caption(
              caption=text, 
              parse_mode=constants.ParseMode.MARKDOWN,
              reply_markup=buttons
      )
 



@Callbacks('^delete')
async def DeleteMsg(update, context):
     """ Delete An CallbackQuery Message """
     message = update.effective_message
     query = update.callback_query
     user_id = int(query.data.split("#")[1])
     if (query.from_user.id == user_id) or (message.chat.type == constants.ChatType.PRIVATE):
          await message.delete()
          await query.answer("Deleted!")
     else:
          info = await message.chat.get_member(query.from_user.id)
          if info.status in (constants.ChatMemberStatus.ADMINISTRATOR, constants.ChatMemberStatus.OWNER):
               await message.delete()
               await query.answer("Deleted!")
          else:
               return await query.answer('❌ You can\'t delete this.')
          




@Callbacks('^unmute')
@admin_check('can_restrict_members')
async def UnbanBtn(update, context):
   
   query = update.callback_query
   _, member_id = query.data.split("_")
   admin_id = query.from_user.id
     
   admin = await query.message.chat.get_member(int(admin_id))
   try:
       member = await query.message.chat.get_member(int(member_id))
       permissions = ChatPermissions.all_permissions()
       await query.message.chat.restrict_member(int(member.user.id), permissions=permissions)
       mention = helpers.mention_html(member.user.id, member.user.first_name)
       await query.message.edit_text(
                f"""⚡ <b>{"Bot" if member.user.is_bot else "User"} {mention} Successfully Unmuted!</b>""",
                parse_mode=constants.ParseMode.HTML
           )
   except Exception as e:
      return await query.message.edit_text(
              "❌ ERROR: " + str(e),
           parse_mode=constants.ParseMode.MARKDOWN
             )
   



@Callbacks('^unban')
@admin_check('can_restrict_members')
async def UnbanBtn(update, context):
   ''' Unban Chat Member Callback keyboard Button '''
     
   query = update.callback_query
   _, member_id = query.data.split("_")
   admin_id = query.from_user.id
     
   admin = await query.message.chat.get_member(int(admin_id))
   try:
       member = await query.message.chat.get_member(int(member_id))
       await query.message.chat.unban_member(int(member.user.id))
       mention = helpers.mention_html(member.user.id, member.user.first_name)
             
       await query.message.edit_text(
                f"""⚡ <b>{"Bot" if member.user.is_bot else "User"} {mention} Successfully Unbanned!</b>""",
                parse_mode=constants.ParseMode.HTML
           )
   except Exception as e:
      return await query.message.edit_text(
           "❌ *Error*: " + str(e),
           parse_mode=constants.ParseMode.MARKDOWN
             )
   


