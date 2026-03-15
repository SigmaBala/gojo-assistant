
from telegram.ext import filters
from nandha.helpers.decorator import Command, only_users, Messages, Callbacks, admin_check, devs_only, only_groups
from nandha.helpers.utils import autofilter_send_file, check_membership, generate_random_string, auto_delete, encode_to_base64, get_size, fixed_file_name, decode_to_base64, file_best_name
from nandha.db.autofilter import ( update_filename_by_file_unique_id, CHAT_IDS, get_file_by_index, update_chat_type, get_chat_type, get_chat_imdb, update_chat_imdb, remove_chat, add_file, delete_file_by_index, get_files_by_name)
from nandha.helpers.misc import arrange_buttons
from nandha.helpers.scripts import IMDBScraper, fetch_and_resize_image
from telegram import SwitchInlineQueryChosenChat, constants, InlineKeyboardMarkup, InlineKeyboardButton
from nandha import pbot as bot, LOGGER as logger

import re, random, config, math, asyncio, json, time, html




__module__ = "AutoFilter"

__help__ = """
*Commands*:
/filters, /autofilter, /afrequest,
/addfile, /delfile, /afindex,
/afuname, /haf

```
A Superb Module for Piracy Movies.
```

```
Type: anime, movies, songs, all, apps


/haf: get tutorial for ( how to use autofilter).

/autofilter only groups: 
Select your chat desired filter type then query for files.
Supports ( video, document and so audio ), use it wisely.

/filters <query> <type>: 
This command can be used in both private/public.

/afrequest reply to media:
if requested file not found in our db,
you can help us by doing reply a media and add content name to caption for request.

/addfile auto/[name1,name2] #types: for add specific file.

/afindex start, end, chat, forward: for indexing files from channel.

/delfile <index>: to delete file.

/afuname [name1, name2]: reply to file for update file name.
```

*Example*:
`/filters anime #anime` 
`/filters movie #all`
"""


temp = {}
index_data = {}
indexing = []
REQ_DEL_TIME = 900
PER_PAGE = 10
MAX_QUERY_LENGTH = 8
MAX_QS_BTN_LENGTH = 3


PHOTOS = config.AF_PHOTOS
imdb = IMDBScraper()


valid_filters = [
 'anime', 'movies', 
 'songs', 'apps'
]

ALLOWED_MIME_TYPES = [
 'audio/mp3', 'audio/mp4', 'application/x-subrip',
 'application/vnd.android.package-archive', 'audio/mpeg', 'video/x-msvideo',
 'video/mp4', 'video/x-matroska'
]


QUICK_SEARCH_KEYS = {
    'Video': ['mp4', 'video', 'avi', 'mov', 'wmv', 'flv', 'm4v', 'webm'],
    'Song': ['audio', 'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a'],
    'Document': ['document', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'odt', 'ods', 'odp', 'mkv'],
    'Tamil': ['tamil', 'tam', 'தமிழ்',],
    'English': ['english', 'eng',],
    'Malayalam': ['malayalam', 'mal', 'മലയാളം'],
    'Hindi': ['hindi', 'hin', 'हिन्दी',],
    'Japanese': ['japanese', 'jap', '日本語',],
    'Kannada': ['kannada', 'kan', 'ಕನ್ನಡ',],
    'Telegu': ['telugu', 'tel', 'తెలుగు',],
    'Korean': ['korean', 'kor', '한국어',],
    'French': ['french', 'fra', 'français',],
    'Spanish': ['spanish', 'spa', 'español',],
    'German': ['german', 'ger', 'deutsch',],
    'Italian': ['italian', 'ita', 'italiano',],
    'Low Quality': ['280P', '360P', '480P'],
    'High Quality': ['720P', '1080P', '4K', 'hd', '2160P']
}




def clean_text(text: str):
    text = re.sub(r"[,`';!\?\[\]\(\)\.&\-:]", ' ', text)
    text = re.sub(r"\bmovies?\b|\bthe\b", ' ', text, flags=re.IGNORECASE)
    return ' '.join(text.strip().split())

async def clear_user_task(user_id: int):
    async def clear_user():
        if temp.get(user_id, None):
            del temp[user_id]         
    loop = asyncio.get_running_loop()
    loop.call_later(REQ_DEL_TIME, lambda: loop.create_task(clear_user()))
 



async def correct_name_by_imdb(name: str):
        result = await imdb.search_by_name(name)
        results = result.get('results')
        if results:
             return [             
                m.get('titlePosterImageModel', {}).get('caption', None) for m in results if m.get('titlePosterImageModel', {}).get('caption', None)
            ]
        return []


async def send_files(query, context, data: list, user_id: int, page: int = 1, is_send_all:bool = False):
      bot = context.bot
      pages = math.ceil(len(data)/PER_PAGE)
      start_idx = (page - 1) * PER_PAGE
      end_idx = start_idx + PER_PAGE
      files = data[start_idx:end_idx]
      if is_send_all:
           files = data
      is_user_member = await check_membership(config.UPDATE_CHANNEL, int(user_id))
      if not is_user_member:
           return await query.answer(f"You have to Join my {config.UPDATE_CHANNEL} to Use this feature.", show_alert=True)

      await query.answer(url=f"https://t.me/{config.BOT_USERNAME[1:]}?start=help")
      for idx, file in enumerate(files, start=1):
            if idx % 5 == 0:
                 await asyncio.sleep(5)
            code = "afFile-" + encode_to_base64(f"{user_id}&{file['index']}")
            await autofilter_send_file(bot, code, int(user_id), file)




async def get_keyboard(data:list, user_id:int, page:int = 1, add_home:bool = False):
    buttons = []
    pages = math.ceil(len(data)/PER_PAGE)

    # Fix the pagination calculation
    start_idx = (page - 1) * PER_PAGE
    end_idx = start_idx + PER_PAGE
    
    # Calculate the starting index for the current page
    # This ensures continuous numbering across pages
    idx_start = 1 + (page - 1) * PER_PAGE
    
    # Slice the data correctly
    c_results = len(data[start_idx:end_idx])
 
    TEXT = (
        f"📦 <b><u>Found {len(data)} Files | Showing Page {page} of {pages}</u></b>\n\n"
    )
 
    # Use idx_start and increment for each file                     
    for i, file in enumerate(data[start_idx:end_idx], start=idx_start):
        file_name = html.escape(file_best_name(file['file_name']).capitalize() if len(file['file_name']) > 1 else file['file_name'][0].capitalize())

        index = file['index']
        encoded_string = encode_to_base64(f"{user_id}&{index}")
        encoded_url = f"https://t.me/{config.BOT_USERNAME[1:]}?start=afFile-{encoded_string}"
        TEXT += f"📄 {i}. <b><a href='{encoded_url}'>{file_name}</a></b>\n\n"

    TEXT += f"\n👤 <b>Requested by</b>: <code>{user_id}</code>"

    # Navigation buttons
    nav_buttons = []
 
    if page > 1:
        nav_buttons.append(
              InlineKeyboardButton(text=f'🔙 Back', callback_data=f"autofilter_back#{page}#{user_id}"),
        )
    if page < pages:
        nav_buttons.append(
              InlineKeyboardButton(text=f'Next ⏭️', callback_data=f"autofilter_next#{page}#{user_id}"),
        )

    # Buttons array
    buttons = []
    
    # Extra action buttons
    send_btns = [
        InlineKeyboardButton(text='📨 Send Page', callback_data=f"autofilter_sendpage#{page}#{user_id}"),
        InlineKeyboardButton(text='📨 Send All', callback_data=f"autofilter_sendall#{page}#{user_id}"),
    ]
    extra_btns = [
        InlineKeyboardButton(text='🔎 Qucik Search', callback_data=f"autofilter_quicksearch#{page}#{user_id}"),     
    ]
    
    # Add navigation and extra buttons
    if nav_buttons:
        buttons.append(nav_buttons)
     
    if (page > 1 or add_home):
        extra_btns.append(InlineKeyboardButton(text='🏡 Home', callback_data=f"autofilter_home#1#{user_id}"))
     
    buttons.append(send_btns)
    buttons.append(extra_btns)
    
    # Close button
    buttons.append([
        InlineKeyboardButton('Close ❌', callback_data=f"delete#{user_id}")
    ])

    return TEXT, InlineKeyboardMarkup(buttons)




@Command('haf')
async def HowToUseAf(update, context):
     m = update.effective_message
     r = m.reply_to_message
     m_id = r.id if r else m.id
     TEXT = f"""
⁉️<b> How to Use Movie Search Features</b>:

🔍<b>Search Types</b>:
- #anime #movies #songs #apps #all

✨ <b>Inline Query</b>:
Quickly find and share files using our inline search feature.
• Usage: <code>{config.BOT_USERNAME} autofilter komi</code>
• Supports All Types: ✅

✨ <b>Filters Command</b>:
Perform private searches with enhanced results.
• Usage: <code>/filters komi #all</code>
• More Comprehensive Than Autofilter: ✅
• Supports All Types: ✅

✨ <b>Autofilter</b>:
Automatically find content in your group by simply sending movie names.
• Recommended Type: "All Types"
• Easy Group Integration: ✅
• Supports All Types: ✅

👀 <b>Didn't understand? no worries!</b>
—» <b>Watch our tutorial video</b>:
 https://t.me/nandhabots/610

🎥 <b>Movies Request</b>: @A2K_Movies
🆘 <b>Support Chat</b>: {config.SUPPORT_CHAT}
"""  
     await m.chat.send_message(
          text=TEXT,
          reply_to_message_id=m_id,
          parse_mode=constants.ParseMode.HTML
     )



@Command('afrequest')
async def AfRequest(update, context):
     m = update.effective_message
     user = m.from_user
     r = m.reply_to_message
     if r and (r.photo or r.video or r.document or r.audio) and r.caption:
          text = r.caption + f"\n\n<b>Request by {user.mention_html()}</b>"
          await r.copy(
              chat_id=config.LOGS_CHANNEL,
              caption=text,
              parse_mode=constants.ParseMode.HTML
          )
          await m.reply_text("✓ *Successful request sent.*", parse_mode=constants.ParseMode.MARKDOWN)
     else:
         await m.reply_text("? *Reply to media and add file names in the caption !*", parse_mode=constants.ParseMode.MARKDOWN)




@Callbacks('^af_QS')
async def afQuickSearchCQ(update, context):
    query = update.callback_query
    m = update.effective_message
    user = query.from_user
    cmd, qs_key, user_id = query.data.split('#')

    if user.id != int(user_id):
        return await query.answer('This is not your request!', show_alert=True)

    unique_id = m.chat.id + user.id
    data = temp.get(unique_id)
 
    if not data:
        return await query.answer("This request was expired, make new request (:", show_alert=True)

    search_keys = QUICK_SEARCH_KEYS[qs_key]
    matching_documents = []

    for doc in data:
        file_name_str = ' '.join(doc['file_name'])

        for keyword in search_keys:
            if re.search(keyword, file_name_str, re.IGNORECASE):
                matching_documents.append(doc)
                break  # No need to check more keywords if a match is found
             
    if not matching_documents:
        return await query.answer(f'🧐 Quick Search for {qs_key} not found!', show_alert=True)
     
    af_text, buttons = await get_keyboard(matching_documents, user.id, add_home=True)
    return await m.edit_text(text=af_text, reply_markup=buttons, parse_mode=constants.ParseMode.HTML)
 
    
    

@Callbacks('^autofilter')
async def autoFilterCQ(update, context):
    query = update.callback_query
    m = update.effective_message
    user = query.from_user
    cmd, type, user_id = query.data.split("#")

    user_id = int(user_id)
    if user.id != int(user_id):
        return await query.answer('This is not your request!', show_alert=True)

    async def edit_text(text, add = True):
        if add:
            if m.chat.id not in CHAT_IDS:
                CHAT_IDS.append(m.chat.id)
        else:
            if m.chat.id in CHAT_IDS:
                CHAT_IDS.remove(m.chat.id)
        return await m.edit_text(text, parse_mode = constants.ParseMode.MARKDOWN)

    async def edit_settings():
          imdb = await get_chat_imdb(m.chat.id)
          buttons = InlineKeyboardMarkup(
            [[

              InlineKeyboardButton(f"📒 IMDB currently {'Enabled ✅' if imdb else 'Disable ❌'}", callback_data=f"autofilter_imdb#{imdb}#{user.id}"),
            ],[
              InlineKeyboardButton("Close ❌", callback_data=f"delete#{user.id}")

            ]]
          )
          return await m.edit_text(
              text="```\nSettings for autofilter```",
              parse_mode=constants.ParseMode.MARKDOWN,
              reply_markup=buttons
          )

    if cmd == "autofilter_settings":
          return await edit_settings()

    elif cmd == "autofilter_imdb":
          mode = not eval(type)
          imdb = await update_chat_imdb(m.chat.id, mode)
          return await edit_settings()

    elif cmd in ["autofilter_home", "autofilter_quicksearch", "autofilter_next", "autofilter_back", "autofilter_sendpage", "autofilter_sendall"]:
        unique_id = m.chat.id + user.id
        data = temp.get(unique_id)

        if not data:
            return await query.answer("This request was expired, make new request (:", show_alert=True)

        current_page = int(type)
        pages = math.ceil(len(data)/PER_PAGE)

        if cmd == "autofilter_quicksearch":
             buttons_data = [
                 InlineKeyboardButton(text=data, callback_data=f"af_QS#{data}#{user.id}") for data in  list(QUICK_SEARCH_KEYS)
             ]
             buttons = arrange_buttons(buttons_data, MAX_QS_BTN_LENGTH)
             buttons.append([InlineKeyboardButton(text='🏡 Home', callback_data=f"autofilter_home#1#{user.id}")])
             return await m.edit_text(text=config.AF_QS_TEXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=constants.ParseMode.HTML)
       
        elif cmd == "autofilter_sendpage":
             return await send_files(query, context, data, user_id, current_page)

        elif cmd == "autofilter_sendall":
             return await send_files(query, context, data, user_id, current_page, is_send_all=True)

        elif cmd == "autofilter_home":
             new_page = 1
         
        elif cmd == "autofilter_next":
            if current_page >= pages:
                return await query.answer("This is the last page.", show_alert=True)
            new_page = current_page + 1
        else:  # autofilter_back
            if current_page <= 1:
                return await query.answer("This is the first page.", show_alert=True)
            new_page = current_page - 1

        af_text, buttons = await get_keyboard(data, user.id, new_page)
        return await m.edit_text(text=af_text, reply_markup=buttons, parse_mode=constants.ParseMode.HTML)

    # Handle other filter types
    if type == "anime":
        await update_chat_type(m.chat.id, type)
        text = f"★ *Successfully #{type} type mode activated!*"
        return await edit_text(text)
    elif type == "movies":
        await update_chat_type(m.chat.id, type)
        text = f"★ *Successfully #{type} type mode activated!*"
        return await edit_text(text)
    elif type == "apps":
        await update_chat_type(m.chat.id, type)
        text = f"★ *Successfully #{type} type mode activated!*"
        return await edit_text(text)
    elif type == "songs":
         await update_chat_type(m.chat.id, type)
         text = f"★ *Successfully #{type} type mode activated!*"
         return await edit_text(text)

    elif type == "disable":
        await update_chat_type(m.chat.id, False)
        text = "∅ *Autofilter mode deactivated!*"
        return await edit_text(text, False)
    else:
        await update_chat_type(m.chat.id, type)
        text = f"★ *Successfully #{type} type mode activated!*"
        return await edit_text(text)



 
@Command('filters')
async def filtersSearch(update, context):
    m = update.effective_message
    r = m.reply_to_message
    user = m.from_user
    chat = m.chat
    text = " ".join(m.text.split()[1:])  # Get everything after command

    if not text:
        return await m.reply_text(
            "🔎 *Enter a search query with a filter type*\n"
            "Example: `/filters anime #anime`",
            parse_mode=constants.ParseMode.MARKDOWN
        )

    # Look for hashtag in the entire text
    pattern = re.compile(r'#(\w+)', re.IGNORECASE)

    tag = pattern.search(text)
    filter_type = tag.group(1).lower() if tag else None

    if not filter_type or ((filter_type not in valid_filters) and filter_type != "all"):
        return await m.reply_text(
            "⚠️ *Please select a valid filter type:*\n"
            "• #anime - Anime content\n"
            "• #songs - Music tracks\n"
            "• #movies - Movies & Shows\n"
            "• #apps - Applications\n"
            "• #all - Search everything\n\n"
            "📝 Format: `/filters query #type`",
            parse_mode=constants.ParseMode.MARKDOWN
        )

    # Remove the hashtag from the query
    query = pattern.sub('', text).strip()
    query = clean_text(query)
    if len(query.split()) > MAX_QUERY_LENGTH:
         return await m.reply_text(f"⁉️ *That query is pretty long, request query limit only [{MAX_QUERY_LENGTH}] words!*", parse_mode=constants.ParseMode.MARKDOWN)

    files = await get_files_by_name(query, filter_type, limit=100)
    if not files:
        text=f"❌ *No '{filter_type}' files found for '{query}'*\n\n"
        if not filter_type in ['apps', 'songs', 'all']:
            names = await correct_name_by_imdb(query)
            if names:
                 text += (
                    "⁉️ *Do you mean one of these*:\n"
                    + '\n'.join(f'› `{n}`' for n in names)
                  )

        return await m.reply_text(
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN
        )

    unique_id = chat.id + user.id
    temp[unique_id] = files
    af_text, buttons = await get_keyboard(files, user.id)

    
    msg = await chat.send_message(
        text=af_text,
        reply_markup=buttons,
        reply_to_message_id=(r.id if r else m.id),
        parse_mode=constants.ParseMode.HTML
    )


@Messages(filters=(~filters.COMMAND & filters.TEXT & filters.ChatType.GROUPS), group=5)
async def autoFilterHandler(update, context):
    m = update.effective_message
    chat = m.chat
    user = m.from_user
    r = m.reply_to_message
    message_id = (r.id if r else m.id)
 
    if chat.id in CHAT_IDS and user:
        type = await get_chat_type(chat.id)
        if type and (type in valid_filters or type == 'all'):
            filter_type = type
            query = clean_text(m.text)
            if len(query.split()) > MAX_QUERY_LENGTH:
                 return await m.reply_text(f"⁉️ *That query is pretty long, request query limit only [{MAX_QUERY_LENGTH}] words!*", parse_mode=constants.ParseMode.MARKDOWN)

            
            msg = await chat.send_message("<b>🔎 Searching files in database...</b>", parse_mode=constants.ParseMode.HTML, reply_to_message_id=message_id)

            files = await get_files_by_name(query, filter_type)

            if not files:
               text=f"❌ *No '{filter_type}' files found for '{query}'*\n\n"
               if not filter_type in ['apps', 'songs']:

                   names = await correct_name_by_imdb(query)
                   if names:
                        text += (
                    "⁉️ *Do you mean one of these*:\n"
                    + '\n'.join(f'› `{n}`' for n in names)
                 )

               return await msg.edit_text(text, parse_mode=constants.ParseMode.MARKDOWN)

            else:
                unique_id = chat.id + user.id
                temp[unique_id] = files
                af_text, buttons = await get_keyboard(files, user.id)
                is_imdb = await get_chat_imdb(chat.id)
                            
                msg = await msg.edit_text(
                       text=af_text,                                   reply_markup=buttons,
                       parse_mode=constants.ParseMode.HTML
                )
                await auto_delete(msg, REQ_DEL_TIME)
                await clear_user_task(user.id)


@Command('autofilter')
@admin_check('can_change_info')
async def autoFilterMode(update, context):
     m = update.effective_message
     user = m.from_user
     type = m.chat.type

     if type == constants.ChatType.PRIVATE:
           text = "<blockquote><b>\n🔎 Search fils through inline.\n\nUse: /filters for better search results & buttons navigations.</b></blockquote>"
           buttons = InlineKeyboardMarkup(
              [[
                InlineKeyboardButton(text='🔎 Search here', switch_inline_query_current_chat='autofilter')
              ],[
                InlineKeyboardButton(
                  text='🔎 Search on another chat', switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                       query='autofilter', 
                       allow_channel_chats=True,
                       allow_group_chats=True,
                       allow_bot_chats=True,
                       allow_user_chats=True
))]]
           )
           return await m.reply_text(text, reply_markup=buttons, parse_mode=constants.ParseMode.HTML)

     buttons = InlineKeyboardMarkup(
           [[    
              InlineKeyboardButton('🤩 Anime', callback_data=f"autofilter#anime#{user.id}"),
              InlineKeyboardButton('🎥 Movies', callback_data=f"autofilter#movies#{user.id}"),
           ],[
              InlineKeyboardButton('📱 Apps', callback_data=f"autofilter#apps#{user.id}"),
              InlineKeyboardButton('🎵 Songs', callback_data=f"autofilter#songs#{user.id}")
           ],[
              InlineKeyboardButton('📁 All Types', callback_data=f"autofilter#all#{user.id}")
           ],[

              InlineKeyboardButton('⚙️ Settings', callback_data=f"autofilter_settings#settings#{user.id}"),
              InlineKeyboardButton('⛔ Disable', callback_data=f"autofilter#disable#{user.id}")
           ],[
              InlineKeyboardButton('Close ❌', callback_data=f"delete#{user.id}"),

           ]]
     )
     text = "```\nSelect chat autofilter type:```"
     await m.reply_text(text, reply_markup=buttons, parse_mode=constants.ParseMode.MARKDOWN)


####################################################################################################



async def start_indexing(user_id: int, chat_id: int, last_msg_id: int, start_index: int, filter_type: str, file_names: list, m, token):
    current_id = start_index
    empty = 0
    no_name = 0
    duplicate = 0
    not_sup = 0
    added = []
    failed = []

    def create_status_text(status="⚙️ Processing..."):
        return f"""
*📊 Channel Indexing Status*
└ Channel ID: `{chat_id}`

*📈 Progress Details:*
├ ✅ Added Files: `{len(added)}`
├ 📭 Empty Files: `{empty}`
├ 💭 No Name Files: `{no_name}`
├ ‼️ Not Supported: `{not_sup}`
├ 📑 Duplicate Files: `{duplicate}`
└ ❌ Failed Files: `{len(failed)}`

*⚡ Progress:* `{current_id}/{last_msg_id}`
*🕒 Status:* `{status}`
"""

    def create_markup(include_results=False):
        rows = [
            [InlineKeyboardButton('⛔ Cancel Index', callback_data=f"afindex_cancel#{user_id}#{token}")]
        ]
        if include_results:
            rows[0].append(InlineKeyboardButton('📩 Result', callback_data=f"afindex_results#{user_id}#{token}"))
        rows.append([InlineKeyboardButton('❌ Close', callback_data=f"delete#{m.from_user.id}")])
        return InlineKeyboardMarkup(rows)

    try:
        status_message = await m.edit_text(
            create_status_text(),
            reply_markup=create_markup(),
            parse_mode=constants.ParseMode.MARKDOWN
        )

        last_update_time = time.time()
        update_interval = 5

        while current_id < last_msg_id:
            batch_end = min(current_id + 300, last_msg_id)
            message_ids = list(range(current_id, batch_end))

            try:
                msgs = await bot.get_messages(chat_id, message_ids=message_ids)
                await asyncio.sleep(3.5)  # Rate limiting

                for idx, msg in enumerate(msgs, start=current_id):  # Start enumeration from current_id
                    # Update current_id for each message processed
                    current_id = idx + 1

                    current_time = time.time()
                    if current_time - last_update_time >= update_interval:
                        try:
                            await status_message.edit_text(
                                create_status_text(),
                                reply_markup=create_markup(),
                                parse_mode=constants.ParseMode.MARKDOWN
                            )
                            last_update_time = current_time
                        except Exception as edit_error:
                            logger.error(f"Failed to update status: {str(edit_error)}")

                    if not msg or not msg.media or msg.empty:
                        empty += 1
                        continue

                    media_types = {
                        'video': (msg.video, 'video'),
                        'document': (msg.document, 'document'),
                        'audio': (msg.audio, 'audio')
                    }

                    media_obj = None
                    file_type = None

                    for obj, type_name in media_types.values():
                        if obj:
                            media_obj = obj
                            file_type = type_name
                            break

                    if not media_obj:
                        empty += 1
                        continue

                    try:
                        file_id = media_obj.file_id
                        file_name = media_obj.file_name if file_type != 'audio' else f"{getattr(media_obj, 'file_name', '')} - {getattr(msg.audio, 'title', 'songs')}"
                        file_size = media_obj.file_size
                        mime_type = getattr(media_obj, 'mime_type', None)


                        if mime_type and mime_type not in ALLOWED_MIME_TYPES:
                              not_sup += 1
                              continue #skip
                        elif msg.audio and not getattr(msg.audio,'title', None):
                              not_sup += 1
                              continue #skip


                        file_unique_id = media_obj.file_unique_id

                        if not file_name:
                            no_name += 1
                            continue #skip

                        file_size = get_size(file_size)
                        name = fixed_file_name(file_name, file_type, file_size)
                        file_name = file_names.copy()
                        file_name.append(name)

                        try:
                            file = await add_file(file_name, file_type, file_id, file_unique_id, filter_type)
                            if file:
                                added.append(file_id)
                            else:
                                duplicate += 1
                        except Exception as add_error:
                            logger.error(f"Error adding file to database: {str(add_error)}")
                            failed.append(file_id)

                    except Exception as e:
                        logger.error(f"Error processing file {file_id}: {str(e)}")
                        failed.append(file_id)

            except Exception as batch_error:
                logger.error(f"Error processing batch {current_id}-{batch_end}: {str(batch_error)}")

            # Make sure we update current_id even if batch processing fails
            if current_id < batch_end:
                current_id = batch_end

    except asyncio.CancelledError:
        await status_message.edit_text(
            create_status_text("⚫ Cancelled"),
            reply_markup=create_markup(True),
            parse_mode=constants.ParseMode.MARKDOWN
        )
        raise
    except Exception as e:
        logger.error(f"Fatal error in indexing: {str(e)}")
        await status_message.edit_text(
            create_status_text("❌ Failed"),
            reply_markup=create_markup(True),
            parse_mode=constants.ParseMode.MARKDOWN
        )
    else:
        await status_message.edit_text(
            create_status_text("✅ Completed"),
            reply_markup=create_markup(True),
            parse_mode=constants.ParseMode.MARKDOWN
        )
    finally:
        data = {
            'added_count': len(added),
            'no_name_count': no_name,
            'failed_count': len(failed),
            'failed_ids': failed,
            'not_sup_count': not_sup,
            'empty_count': empty,
            'duplicate_count': duplicate
        }
        return data


@Callbacks('^afindex')
async def _cq_indexer(update, context):
    m = update.effective_message
    query = update.callback_query
    cmd, user_id, token = query.data.split("#")

    if query.from_user.id != int(user_id):
         return await query.answer('This Command Not Request By You!', show_alert=True)

    data = index_data.get(token)
    if not data:
        return await query.answer('🤷 This Indexer was expired!', show_alert=True)

    chat_id, message_id, start_index, filter_type, file_names = data

    try:
        if cmd == "afindex_start":
            if indexing:
                await query.answer("Already one indexing process is running.", show_alert=True)
            else:
                # Create and start the indexing task
                task = asyncio.create_task(start_indexing(int(user_id), chat_id, message_id, start_index, filter_type, file_names, m, token))
                indexing.append(task)
                # Don't edit the message here - let start_indexing handle it
                await query.answer("Indexing started!", show_alert=True)

        elif cmd == "afindex_cancel":
            if indexing:
                indexing[0].cancel()
                indexing.clear()
                await query.answer("Indexing cancelled!", show_alert=True)
            else:
                await query.answer("No indexing task is running!", show_alert=True)

        elif cmd == "afindex_results":
            if not indexing:
                return await query.answer("No indexing process is running...", show_alert=True)

            try:
                data = await indexing[0]
                path = 'indexer.json'
                with open(path, 'w+') as file:
                    json.dump(data, file, indent=4)
                await m.reply_document(path)
                await query.answer("Results generated!", show_alert=True)
            except Exception as e:
                logger.error(f"Error generating results: {str(e)}")
                await query.answer("Error generating results!", show_alert=True)

    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        await query.answer("An error occurred!", show_alert=True)


@Command('afindex')
@only_users([6781100064, 5696053228])
async def _indexer(update, context):
    m = update.effective_message
    r = m.reply_to_message
    user = m.from_user
    text = m.text


    message_id = None
    file_names = []
    start_index = 0

    try:
        filter_match = re.search(r'#(\w+)', text, re.IGNORECASE)
        if not filter_match:
            return await m.reply_text(
                "⚠️ *Filter type required!*\n\n"
                "*Available filters:*\n"
                "• #anime - Anime content\n"
                "• #songs - Music files\n"
                "• #movies - Movies/Shows\n"
                "• #apps - Applications",
                parse_mode=constants.ParseMode.MARKDOWN
            )

        filter_type = filter_match.group(1).lower()
        if filter_type not in valid_filters:
            return await m.reply_text(
                "❌ *Invalid filter type!*\n\n"
                "*Please use one of these:*\n"
                "• #apps\n• #anime\n• #songs\n• #movies",
                parse_mode=constants.ParseMode.MARKDOWN
            )

        names_pattern = re.compile(r'\[(.*?)\]', flags=re.IGNORECASE)
        names_match = names_pattern.search(text)
        if names_match:
            file_names = [name.strip() for name in names_match.group(1).split(',')]


        end_pattern = re.compile(r'end\s(\d+)', flags=re.IGNORECASE)
        end_index_match = end_pattern.search(text)
        if end_index_match:
             message_id = int(end_index_match.group(1))

        sidx_pattern = re.compile(r'\s+start\s(\d+)', re.IGNORECASE)
        start_index_match = sidx_pattern.search(m.text)
        if start_index_match:
             start_index = int(start_index_match.group(1))

        chat_filter = re.compile(r'chat\s(.*)', flags=re.IGNORECASE)
        is_chat = chat_filter.search(text)

        if r and r.forward_origin and r.forward_origin.chat.type == constants.ChatType.CHANNEL:
              chat_id = r.forward_origin.chat.id
              message_id = r.forward_origin.message_id
        elif is_chat:
              chat_id = int(is_chat.group(1)) if is_chat.group(1).isdigit() else is_chat.group(1)
        else:
             return await m.reply_text("Give me chat id or reply to forwarded msg id from channel!")

        if not message_id:
            return await m.reply_text("index Ends Message id not Found!")

        # save them in temp data
        token = generate_random_string(6)
        index_data[token] = [
              chat_id, message_id + 1, start_index, filter_type, file_names
        ]

        if not indexing:
            buttons = InlineKeyboardMarkup([[
                InlineKeyboardButton('✨ Start Index', callback_data=f"afindex_start#{user.id}#{token}"),
                InlineKeyboardButton('❌ Close', callback_data=f"delete#{user.id}")
            ]])
            await m.reply_text(
                "🔍 *Ready to Index*\n\n"
                "Press the button below to begin indexing files.\n"
                f"Filter: `#{filter_type}`\n"
                f"Start Index: `{start_index}`",
                reply_markup=buttons,
                parse_mode=constants.ParseMode.MARKDOWN
            )
        else:
            buttons = InlineKeyboardMarkup([[
                InlineKeyboardButton('⛔ Cancel Index', callback_data=f"afindex_cancel#{user.id}#{token}"),
                InlineKeyboardButton('❌ Close', callback_data=f"delete#{user.id}")
            ]])
            await m.reply_text(
                "⚠️ *Indexing in Progress*\n\n"
                "Another indexing process is currently running.\n"
                "Please cancel it before starting a new one.",
                reply_markup=buttons,
                parse_mode=constants.ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Command error: {str(e)}")
        await m.reply_text(
            "❌ *Error Occurred*\n\n"
            "Failed to process your request.\n"
            "Please try again or contact admin.",
            parse_mode=constants.ParseMode.MARKDOWN
        )

####################################################################################################



@Command('afuname')
@only_users(config.AF_USERS)
async def updateFileName(update, context):
    m = update.effective_message
    r = m.reply_to_message

    # Ensure the user replied to a valid message containing a file
    if not r or not (r.video or r.document or r.audio):
        return await m.reply_text("» Must reply to a video, document, or audio message!")

    # Use a non-greedy regex pattern to extract the file names
    file_name_re = re.search(r'\[(.*?)\]', m.text)
    if not file_name_re:
        return await m.reply_text('❌ Use a valid file name format!\nExample: /afuname [name1, name2]')

    # Extract and clean the file names
    file_names_raw = file_name_re.group(1).split(',')
    file_names = [name.strip() for name in file_names_raw if name.strip()]

    if not file_names:
        return await m.reply_text('❌ No valid file names found. Please provide at least one file name.')

    # Get file details from the replied message
    if r.document:
        file_unique_id = r.document.file_unique_id
        file_size = get_size(r.document.file_size)
        file_type = "document"
    elif r.video:
        file_unique_id = r.video.file_unique_id
        file_size = get_size(r.video.file_size)
        file_type = "video"
    else:  # r.audio
        file_unique_id = r.audio.file_unique_id
        file_size = get_size(r.audio.file_size)
        file_type = "audio"

    # Apply fixed_file_name to each file name
    file_names_fixed = [fixed_file_name(name, file_type, file_size) for name in file_names]

    await m.reply_text(f"✓ File name(s) received: {', '.join(file_names_fixed)}\nProceeding to update...")

    # Update the file name(s) in the database
    update_successful = await update_filename_by_file_unique_id(file_unique_id, file_names_fixed)

    if update_successful:
        return await m.reply_text('✨ *File Name successfully updated!*', parse_mode=constants.ParseMode.MARKDOWN)
    else:
        return await m.reply_text('❌ *File name failed to update.*', parse_mode=constants.ParseMode.MARKDOWN)



@Command('addfile')
@only_users(config.AF_USERS)
async def addFile(update, context):
    m = update.effective_message
    r = m.reply_to_message

    if indexing:
      return await m.reply_text('❌<b> Stop! running indexing process...</b>', parse_mode=constants.ParseMode.HTML)

    if not r or (r and not (r.video or r.document or r.audio)):
        return await m.reply_text("» Must reply to a video or document or audio!")

    # Determine file type and get file details
    file_type = "video" if r.video else "document" if r.document else "audio"
    file_id = r.document.file_id if r.document else r.video.file_id if r.video else r.audio.file_id
    file_size = get_size(r.document.file_size if r.document else r.video.file_size if r.video else r.audio.file_size)
    file_name = r.document.file_name if r.document else r.video.file_name if r.video else r.audio.file_name
    file_unique_id = r.document.file_unique_id if r.document else r.video.file_unique_id if r.video else r.audio.file_unique_id

    # Get the command text without the command itself
    text = " ".join(m.text.split()[1:])
    if not text:
        return await m.reply_text("∅ File name or filter type missing ...")

    # Handle auto naming
    if text.lower().startswith("auto"):
        filter_match = re.search(r'#(\w+)', text, re.IGNORECASE)
        if not filter_match:
            return await m.reply_text("» Filter type missing. Use #anime, #movies, or #songs or #apps")

        filter_type = filter_match.group(1).lower()
        if filter_type and filter_type not in valid_filters:
            return await m.reply_text("» Unsupported filter type. Use #anime, #movies, #apps, or #songs")

        if not file_name:
            return await m.reply_text("This file has no name, I can't auto generate file name.")

        fname = fixed_file_name(file_name, file_type, file_size)
        file_names = [fname]

    # Handle manual naming
    else:
        pattern = re.compile(r'\[(.*?)\]\s*#(\w+)', re.IGNORECASE)
        match = pattern.search(text)

        if not match:
            return await m.reply_text("∅ Invalid format. Use: /addfile [name1, name2] #filtertype")

        filter_type = match.group(2).lower()
        file_names = [
    fixed_file_name(name.strip(), file_type, file_size)
    for name in match.group(1).split(',')
    if name.strip()  # This filters out any empty strings
]

        if filter_type not in valid_filters:
            return await m.reply_text("» Unsupported filter type. Use #anime, #movies, or #songs, #apps")

    await m.reply_text(f"✓ File name(s) received: {', '.join(file_names)}\nProceeding to update...")



    # Add file to database
    file = await add_file(file_names, file_type, file_id, file_unique_id, filter_type)
    if file:
        await m.reply_text("✓ File added successfully")
    else: 
        await m.reply_text("👀 File maybe already stored.")


@Command('delfile')
@only_users(config.AF_USERS)
async def delFile(update, context):
      m = update.effective_message
      index = int(m.text.split()[1]) if len(m.text.split()) == 2 and m.text.split()[1].isdigit() else None
      if not index:
          return await m.reply_text("Invalid Index given! or not given!")
      else:
          if await delete_file_by_index(index):
               await m.reply_text("✓ File is deleted.")
          else:
               await m.reply_text("∅ File Not found")


@Command('afclear')
@only_users(config.AF_USERS)
async def autofilter_req_clear(update, context):
       m = update.effective_message
       temp.clear()
       await m.reply_text('🗑️*Cleared all autofilter requestes.*', parse_mode=constants.ParseMode.MARKDOWN)
 

@Command('afchk')
@only_users(config.AF_USERS)
async def AfCheck(update, context):
    m = update.effective_message
    r = m.reply_to_message
    text = (r.text or r.caption or "") + " " + (m.text or "") if r else (m.text or "")
    pattern = r'afFile-(.*)'
    code = re.search(pattern, text, re.IGNORECASE)
    if not code:
        return await m.reply_text(
            "⚠️ *Error: File code not found!*\n"
            "Please make sure to reply to a message containing a valid file code.",
            parse_mode=constants.ParseMode.MARKDOWN
        )

    try:
        user_id, index = decode_to_base64(code.group(1).encode()).split("&")
        index_num = int(index)
        file = await get_file_by_index(index_num)

        if not file:
            return await m.reply_text(
                "⚠️ *Error: File not found!*\n"
                "The requested file index does not exist.",
                parse_mode=constants.ParseMode.MARKDOWN
            )

        file_unique_id = file.get('file_unique_id', 'N/A')
        filter_type = file.get('filter_type', 'N/A')
        file_type = file.get('file_type', 'N/A')
        file_id = file.get('file_id', 'N/A')
        file_names = file.get('file_name', [])

        # Ensure file_names is always a list
        if isinstance(file_names, str):
            file_names = [file_names]

        names_text = '\n'.join(f'• `{name}`' for name in file_names)

        return await m.reply_text(
            f"""📋 *File Information*
━━━━━━━━━━━━━━━
🔢 *Index:* `{index_num}`
📁 *Type:* `{file_type}`
🏷️ *Category:* `{filter_type}`

*📝 Available Names:*
{names_text}

🔍 *Technical Details*
━━━━━━━━━━━━━━━
📌 *File ID:* `{file_id}`
🆔 *Unique ID:* `{file_unique_id}`

👤 *Requested by:* `{user_id}`""",
            parse_mode=constants.ParseMode.MARKDOWN
        )

    except Exception as e:
        return await m.reply_text(
            f"⚠️ *Error: Something went wrong!*\n`{str(e)}`",
            parse_mode=constants.ParseMode.MARKDOWN
        )
