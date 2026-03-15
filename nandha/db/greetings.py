
from nandha import database2 as database

welcome_db = database['welcome']
goodbye_db = database["goodbye"]


async def get_all_goodbye_chats() -> list:
      chats = await goodbye_db.find().to_list()
      return [chat['chat_id'] for chat in chats ] if chats else []


async def count_goodbye_chats() -> int:
      count = await goodbye_db.count_documents({})
      return count

async def set_goodbye_time(chat_id: int, time: int = 300):
       chat = {'chat_id': chat_id}
       data = {
            "$set": {
             'time': time
            }
       }
       result = await goodbye_db.update_one(chat, data)
       return result.modified_count > 0


async def clear_goodbye(chat_id: int):
      chat = {'chat_id': chat_id}
      chat_db = await goodbye_db.find_one(chat)
      if chat_db:
           await goodbye_db.delete_one(chat_db)
           return True
            
async def check_goodbye(chat_id: int):
      chat = {'chat_id': chat_id}
      chat_db = await goodbye_db.find_one(chat)
      if chat_db:
           return True
      return False

async def get_goodbye(chat_id: int):
      chat = {'chat_id': chat_id}
      chat_db = await goodbye_db.find_one(chat)
      if chat_db:
           return chat_db

async def set_goodbye(
      chat_id: int,
      file_id: str = None,
      file_type: str = None,  
      text: str = None,
      keyboard: dict = None
):
     chat = {'chat_id': chat_id}
     chat_db = await goodbye_db.find_one(chat)
     update = {
         "$set": {
         "file_type": file_type,
         "file_id": file_id,
         "text": text,
         "keyboard": keyboard
         }
     }
     result = await goodbye_db.update_one(chat, update, upsert=True)
     return result.modified_count > 0 or result.upserted_id is not None




async def check_welcome(chat_id: int):
      chat = {'chat_id': chat_id}
      chat_db = await welcome_db.find_one(chat)
      if chat_db:
           return True
      return False
        
async def clear_welcome(chat_id: int):
      chat = {'chat_id': chat_id}
      chat_db = await welcome_db.find_one(chat)
      if chat_db:
           await welcome_db.delete_one(chat_db)
           return True


async def get_welcome(chat_id: int):
      chat = {'chat_id': chat_id}
      chat_db = await welcome_db.find_one(chat)
      if chat_db:
           return chat_db
             

async def count_welcome_chats() -> int:
      count = await welcome_db.count_documents({})
      return count
      
async def get_all_welcome_chats() -> list:
      chats = await welcome_db.find().to_list()
      return [chat['chat_id'] for chat in chats ] if chats else []



async def set_welcome_time(chat_id: int, time: int = 300):
       chat = {'chat_id': chat_id}
       data = {
            "$set": {
             'time': time
            }
       }
       result = await welcome.update_one(chat, data)
       return result.modified_count > 0


async def set_welcome(
      chat_id: int,
      file_id: str = None,
      file_type: str = None,  
      text: str = None,
      keyboard: dict = None
):
     chat = {'chat_id': chat_id}
     chat_db = await welcome_db.find_one(chat)
     update = {
         "$set": {
         "file_type": file_type,
         "file_id": file_id,
         "text": text,
         "keyboard": keyboard
         }
     }
     result = await welcome_db.update_one(chat, update, upsert=True)
     return result.modified_count > 0 or result.upserted_id is not None


