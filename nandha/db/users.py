
from nandha import database2 as database

import config

collection = database['users']


USER_IDS = []


async def check_user_exists(user_id: int):
      user = await collection.find_one({'user_id': user_id})
      return True if user else False



async def get_all_premium_users():
    filter = {'is_premium': True}
    users = await collection.find(filter).to_list(length=None)
    return [ user['user_id'] for user in users ] if users else []


async def update_user_premium(user_id: int, option: bool) -> bool:
    user_filter = {
        'user_id': user_id
    }
    db_user = await collection.find_one(user_filter)  # Use find_one instead of find
    data = {
        "$set": {
            "is_premium": option
        }
    }
    if db_user:
        result = await collection.update_one(user_filter, data)
        return result.modified_count > 0
    return False



 
async def check_user_premium(user_id: int) -> bool:
    user_filter = {
        'user_id': user_id
    }
    db_user = await collection.find_one(user_filter)
    if db_user:
        return db_user.get("is_premium", False)  # Return the premium status, default to False if not found
    return False


        
  
async def get_user_premium(user_id: int) -> dict:
    user_filter = {
        'user_id': user_id
    }
    db_user = await collection.find_one(user_filter)
    if db_user:
        return {
            "user_id": db_user.get("user_id"),
            "is_premium": db_user.get("is_premium", False)  # Return premium status, default to False if not found
        }
    return False  # Return None if the user is not found
    


async def add_user(obj):
    try:
        user_id = obj['id']
        filter = {'user_id': user_id}
        user_data = {
            "$set": {
                'user_id': user_id,
                'first_name': obj.get('first_name'),
                'username': obj.get('username'),
                'active': True,
            }
        }
        await collection.update_one(filter, user_data, upsert=True)
    except Exception as e:
        print(f"Error adding user: {e}")


async def update_users_status(users_id: list, status=True):
    filter = {'user_id': {'$in': users_id}}
    update = {'$set': {'active': status}}
    result = await collection.update_many(filter, update)
    return result.modified_count > 0


async def remove_user(user_id):
    try:
        await collection.delete_one({'user_id': user_id})
    except Exception as e:
        print(f"Error removing user: {e}")


async def get_user_data(user_id):
    try:
        user = await collection.find_one({'user_id': user_id})
        if user:
            return {key: value for key, value in user.items() if not key.startswith('_')}
        else:
            return {}
    except Exception as e:
        print(f"Error getting user: {e}")
        return {}



async def get_users_by_first_name(first_name):
    try:
        users = await collection.find(
            {'first_name': {'$regex': first_name, '$options': 'i'}}
        ).to_list(None)
        return users
    except Exception as e:
        print(f'Error while searching for user_ids by first_name: {str(e)}')
        return []


async def get_users_by_username(username):
    try:
        users = await collection.find(
            {'username': {'$regex': username, '$options': 'i'}}
        ).to_list(None)
        return users
    except Exception as e:
        print(f'Error while searching for user_ids by first_name: {str(e)}')
        return []




async def get_user_id_by_username(username):
    try:
        user = await collection.find_one(
          {'username': {'$regex': username, '$options': 'i'}}
        )
        return user['user_id'] if user else None
    except Exception as e:
        print(f'Error while searching for user_id by username: {str(e)}')
        return None


async def update_users_status_to_active(users_id: list):
    filter = {'user_id': {'$in': users_id}}
    update = {'$set': {'active': True}}
    result = await collection.update_many(filter, update)
    return result.modified_count > 0

async def update_users_status_to_inactive(users_id: list):
    filter = {'user_id': {'$in': users_id}}
    update = {'$set': {'active': False}}
    result = await collection.update_many(filter, update)
    return result.modified_count > 0


async def get_all_active_users():
    filter = {'active': True}
    users = await collection.find(filter).to_list(length=None)
    return [ user['user_id'] for user in users ] if users else []

async def count_users() -> int:
      count = await collection.count_documents({})
      return count           

async def get_all_users():
    try:
        users = await collection.find().to_list(length=None)
        return [user['user_id'] for user in users]
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []


async def initialize_db_users():
     users = await get_all_users()
     USER_IDS.extend(users)


async def initialize_db_premium_users():
     users = await get_all_premium_users()
     config.PREMIUM_USERS.extend(users)
     
     
