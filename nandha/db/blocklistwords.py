

from nandha import database2 as database

db = database['blocklist']


async def count_chats() -> int:
      count = await db.count_documents({})
      return count

async def get_words(chat_id: int) -> list:
    chat_f = {"chat_id": chat_id}
    chat = await db.find_one(chat_f)
    if chat:
        return chat["words"]
    return []

async def add_word(chat_id: int, word: str) -> bool:
    chat_f = {'chat_id': chat_id}
    update_f = {"$addToSet": {"words": word}}  # Use $addToSet to avoid duplicates
    result = await db.update_one(chat_f, update_f, upsert=True)
    return result.modified_count > 0 or result.upserted_id is not None


async def update_mode(chat_id: int, switch: bool) -> bool:
      chat_f = {'chat_id': chat_id}
      chat = await db.find_one(chat_f)
      if chat:
          update_f = {"$set": {"mode": switch}}
          await db.update_one(chat_f, update_f)
          return True


async def get_mode(chat_id: int) -> bool:
      chat_f = {'chat_id': chat_id}
      chat = await db.find_one(chat_f)
      return chat.get('mode', False) if chat else False

async def remove_word(chat_id: int, word: str) -> bool:
    chat_f = {'chat_id': chat_id}
    chat = await db.find_one(chat_f)
    if chat:
        update_f = {"$pull": {"words": word}}
        result = await db.update_one(chat_f, update_f, upsert=True)
        return result.modified_count > 0
      


async def get_all_chats() -> list:
    try:
        chats = await db.find().to_list(length=1000)
        return [chat['chat_id'] for chat in chats]
    except Exception as e:
        return []
    
