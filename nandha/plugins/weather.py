
import aiohttp
import config

from nandha import pbot
from bs4 import BeautifulSoup
from pyrogram import filters, types


__help__ = """
*Commands*:
/weather

```
/wether <city name>: weather information article for your city.
```

*Example*:
`/weather Shibuya`
"""

__module__ = "Weather"

@pbot.on_message(filters.command('weather') & ~filters.forwarded)
async def weatherInfo(_, message):
      m = message
      city_name = m.text.split(maxsplit=1)[1] if len(m.text.split()) > 1 else None
      if not city_name:
           return await m.reply_text('**Provide me city name.**')
      async with aiohttp.ClientSession() as session:
           try:
                url = "https://www.timeanddate.com/scripts/completion.php"
                params = {"xd": 21, "query": city_name, "mode": "ci"}
                async with session.get(url, params=params) as response:
                       response_text = await response.text()
                       if response_text == "":
                             return await m.reply_text('❌ **No results found**')
                       else:
                           url = "https://www.timeanddate.com" + response_text.split("/ext")[0]
                           async with session.get(url) as response:
                                 soup = BeautifulSoup(await response.text(), "html.parser")
                                 weather = soup.find("div", {"id": "qlook"})
                                 data = weather.find_all("p")
                                 stat = data[0].text
                                 info = str(data[1]).split("<br/>")
                                 details = [x.text for x in soup.find(class_="bk-focus__info").find_all("td")]
                                 result = (
        "<b>⛈️ Weather in <code>{}</code></b>\n\n".format(city_name)
        + "<b>🌞 Temperature:</b> <code>{}</code>\n".format(
            weather.find("div", {"class": "h2"}).text
        )
        + "<b>📊 Status:</b> {}\n".format(stat)
        + "<b>👃 Feels like:</b> <code>{}</code>\n".format(info[0].split(": ")[1])
        + "<b>🌳 Forecast:</b> <code>{}</code>\n".format(
            info[1].split(": ")[1].split("<")[0]
        )
        + "<b>💨 Wind:</b> <code>{}</code>\n".format(info[2].split(": ")[1].split("<")[0])
        + "<b>🏙️ Location:</b> {}\n".format(details[0])
        + "<b>⏳ Current Time:</b> <code>{}</code>\n".format(details[1])
        + "<b>⚙️ Latest Update:</b> <code>{}</code>\n".format(details[2])
        + "<b>👁️‍🗨️ Visibility:</b> {}\n".format(details[3])
        + "<b>⚖️ Pressure:</b> <code>{}</code>\n".format(details[4])
        + "<b>🚶‍♂️ Humidity:</b> <code>{}</code>\n".format(details[5])
        + "<b>✴️ Dew Point:</b> <code>{}</code>\n".format(details[6])
        + f"\n<b>By {config.BOT_USERNAME}</b>"
                                 )
                             
                                 return await m.reply_text(result)
                       
           except Exception as e:
                await m.reply_text(f'❌ **ERROR**: `{str(e)}`')
 
