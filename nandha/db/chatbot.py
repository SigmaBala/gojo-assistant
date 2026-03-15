
from nandha import database2 as database

collection = database['chatbot']

CHAT_IDS = []

async def count_chats() -> int:
      count = await collection.count_documents({})
      return count

async def add_chat(chat_id):
    try:
        chat_id = int(chat_id)  # Ensure chat_id is an integer
        chat = await collection.find_one({'chat_id': chat_id})
        if not chat:
            chat = {
                'chat_id': chat_id
            }
            await collection.insert_one(chat)
    except Exception as e:
        print(f"Error adding chat: {e}")


async def remove_chat(chat_id):
    try:
        chat_id = int(chat_id)  # Ensure chat_id is an integer
        await collection.delete_one({'chat_id': chat_id})
    except Exception as e:
        print(f"Error removing chat: {e}")


async def get_all_chats():
    try:
        chats = await collection.find().to_list(length=1000)
        return [chat['chat_id'] for chat in chats]
    except Exception as e:
        print(f"Error getting all chats: {e}")
        return []


async def initialize_db_chats():
     users = await get_all_chats()
     CHAT_IDS.extend(users)
     
