import os
import importlib
import pkgutil
import logging
import importlib.util
import asyncio

from aiohttp import web
from telegram import Update
from app import keep_alive, web_server
from telegram.ext import Application
from nandha import TOKEN, app, plugins, SUPPORT_CHAT, LOGS_CHANNEL, IS_WEB_SUP, initialize_database, start_pyro_clients, BIND_ADDRESS, PORT

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

def import_plugins(package):
    package_name = package.__name__
    package_file = package.__file__

    logging.debug(f"Importing plugins from package: {package_name}")
    logging.debug(f"Package file attribute: {package_file}")

    if package_file is None:
        raise ValueError(f"Package {package_name} does not have a file attribute. It might be a namespace package.")

    package_dir = os.path.dirname(package_file)
    logging.debug(f"Package directory: {package_dir}")

    imported_modules = []

    for _, name, is_pkg in pkgutil.iter_modules([package_dir]):
        full_name = f"{package_name}.{name}"
        logging.debug(f"Importing module: {full_name}")
        #importlib.import_module(full_name)
        imported_modules.append(full_name)

    logging.info(f"Successfully imported {len(imported_modules)} modules: [{', '.join(module.rsplit('.', 1)[-1] for module in imported_modules)}]")




async def start_services():
        
        server = web.AppRunner(web_server())
        await server.setup()
        await web.TCPSite(server, BIND_ADDRESS, PORT).start()
        logging.info("Web Server Initialized Successfully")
        logging.info("=========== Service Startup Complete ===========")
  
        asyncio.create_task(keep_alive())
        logging.info("Keep Alive Service Started")
        logging.info("=========== Initializing Web Server ===========")
   




     
    
if __name__ == '__main__':
    import_plugins(plugins)
    async_funcs = [
        start_pyro_clients(), 
        initialize_database()
    ]
    if IS_WEB_SUP:
        async_funcs.append(start_services())
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*async_funcs))
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
    
        
  



