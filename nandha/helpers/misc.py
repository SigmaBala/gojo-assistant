import config


from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from nandha import MODULE, font


def arrange_buttons(buttons_list, columns=2):
    arranged = []
    row = []

    for i, button in enumerate(buttons_list):
        row.append(button)

        if len(row) == columns or i == len(buttons_list) - 1:
            arranged.append(row)
            row = []

    return arranged
      

def dict_to_keyboard(data):
      keyboard = [[
        InlineKeyboardButton(**button) for button in row]
             for row in data['inline_keyboard']
      ]
      return InlineKeyboardMarkup(keyboard)



def help_keyboard_data(user_id: int, rows: int = 10, columns: int = 3):
    modules = sorted(MODULE.items(), key=lambda x: x[0])
    pages = []
    page = []
    row = []
    
    for i, (module_name, module_help) in enumerate(modules):
        button = InlineKeyboardButton(text=font(module_name.capitalize()), callback_data=f"help_{module_name}_{user_id}")
        row.append(button)
        
        if len(row) == columns:
            page.append(row)
            row = []
        
        if len(page) == rows:
            pages.append(page)
            page = []

    if row:
        page.append(row)
    if page:
        pages.append(page)
    
    return pages        


def help_button(user_id):
    buttons = []
    row = []
  
    sorted_modules = sorted(MODULE.items(), key=lambda x: x[0])

    for i, (module, help) in enumerate(sorted_modules):
        button = InlineKeyboardButton(text=font(module.capitalize()), callback_data=f"help_{module}_{user_id}")
        row.append(button)
        if (i+1) % 3 == 0 or i == len(sorted_modules) - 1:
            buttons.append(row)
            row = []
    return InlineKeyboardMarkup(buttons)




async def get_help_button(message, user):
    buttons = help_keyboard_data(user_id=user.id, rows=config.BTN_ROWS, columns=config.BTN_COLUMNS)
    if not buttons:
         await message.reply_text("❌ *No help module is provided to repository.*", parse_mode=constants.ParseMode.MARKDOWN)
          
    page_number = 0
    if len(buttons) > 1:
         buttons[page_number].append(
             [
               InlineKeyboardButton(font('❌ Close'), callback_data=f"delete#{user.id}"),
               InlineKeyboardButton(font('➡️ Next'), callback_data=f"helpcq_next#{user.id}#{page_number}"),
               
             ]
         )
    else:
          buttons[page_number].append(
             [
               InlineKeyboardButton(font('❌ Close'), callback_data=f"delete#{user.id}"),
             ]
          )
    return buttons[page_number]

