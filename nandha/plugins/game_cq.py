

import random

from telegram import constants, InputMedia, InlineKeyboardButton, InlineKeyboardMarkup
from nandha.helpers.decorator import Callbacks
from nandha.db.characters import get_character
from nandha.db.user_characters import user_character_exists, add_user_character
from nandha.db.game import get_cash, update_cash



@Callbacks("^chealth")
async def characterHealth(update, context):
     query = update.callback_query
     user_id = query.from_user.id
     _, character_id, fuser_id = query.data.split("#")

     if user_id != int(fuser_id):
          return await query.answer("This is not your request *bro* 😉", show_alert=True)
     
     else:
         return await query.answer("We're updating this module.... 😉", show_alert=True)


@Callbacks("^cattack")
async def characterAttack(update, context):
     query = update.callback_query
     user_id = query.from_user.id
     _, character_id, fuser_id = query.data.split("#")

     if user_id != int(fuser_id):
          return await query.answer("This is not your request *bro* 😉", show_alert=True)
     
     else:
         return await query.answer("We're updating this module.... 😉", show_alert=True)


@Callbacks("^chome")
async def characterHome(update, context):
     query = update.callback_query
     user_id = query.from_user.id
     _, character_id, fuser_id = query.data.split("#")

     if user_id != int(fuser_id):
          return await query.answer("This is not your request *bro* 😉", show_alert=True)
     
     else:
          character = await get_character(character_id)
          character_id = character['character_id']
          name = character['character_name']
          health = character['health']
          attack = character['attack']
          rarity_type = character['rarity_type']
          cash = character['cash']
          image = random.choice(character['images'])
          buttons = InlineKeyboardMarkup([[
               InlineKeyboardButton(text="Shop 🛒", callback_data=f"cshop#{character_id}#{user_id}")
          ]])
          
          text = \
f"""
🌀 *Name*: `{name}`
🆔 *Character id*: `{character_id}`

💚 *Health*: `{health} HP`
🏅 *Rarity*: `type {rarity_type}`
💸 *Cash*: `{cash} dollar`
"""
          await query.edit_message_media(
                media=InputMedia(
                     media_type='photo',
                     media=image,
                     caption=text,
                     parse_mode=constants.ParseMode.MARKDOWN
                ),
                reply_markup=buttons
          )
          

          

@Callbacks("^cshop")
async def characterShop(update, context):
     query = update.callback_query
     user_id = query.from_user.id
     _, character_id, fuser_id = query.data.split("#")

     if user_id != int(fuser_id):
          return await query.answer("This is not your request *bro* 😉", show_alert=True)
          
     elif await user_character_exists(user_id, character_id):
          buttons = InlineKeyboardMarkup([[
               InlineKeyboardButton(text="Health 💚", callback_data=f"chealth#{character_id}#{user_id}"),
               InlineKeyboardButton(text="Attack 🔴", callback_data=f"cattack#{character_id}#{user_id}")
          ],[
               InlineKeyboardButton(text=" 🏡 Home 🏡", callback_data=f"chome#{character_id}#{user_id}")
          ]])
          text = \
"""
```
What do you want to upgrade? Choose below option given.
```
"""
          await query.edit_message_text(
               text=text,
               parse_mode=constants.ParseMode.MARKDOWN,
               reply_markup=buttons
          )
     else:
          return await query.answer("Yo, you ain't got this character yet! first buy.", show_alert=True)



@Callbacks("^cbuy")
async def characterBuy(update, context):
     query = update.callback_query
     user_id = query.from_user.id

     _, character_id, fuser_id = query.data.split("#")

     if user_id != int(fuser_id):
          return await query.answer("This is not your request *bro* 😉", show_alert=True)
          
     elif await user_character_exists(user_id, character_id):
          return await query.answer("You already have this character, *baka* 🥴", show_alert=True)
     else:
         character_info = await get_character(character_id)
         user_cash = await get_cash(user_id)
         character_cash = character_info['cash']
         if user_cash < character_cash:
              return await query.answer(f"You don't have enough cash to purchase {character_info['character_name']}, *pathetic* 🤧", show_alert=True)
         else:             
             await add_user_character(
                 user_id=user_id,
                 character_name=character_info['character_name'],
                 character_id=character_info['character_id'],
                 attack=character_info['attack'],
                 health=character_info['health'],
                 images=character_info['images'],
                 rarity_type=character_info['rarity_type']
             )
             await update_cash(user_id, -character_cash)
             await query.answer(f"Congratulations, you purchased {character_info['character_name']}! *You're one step closer to being like me* 🥳", show_alert=True)
               
             
         
     
     
