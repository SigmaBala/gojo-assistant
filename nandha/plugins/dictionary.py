import aiohttp
from nandha import pbot as bot
from pyrogram import filters
from pyrogram.types import Message
import asyncio


__module__ = "Define"

__help__ = """
*Commands*:
/define

```
/define <query>: 
search for word definition and with grammer example.
```
*Example*:
`/define hi`
"""


@bot.on_message(filters.command("define") & ~filters.forwarded)
async def define(bot, message: Message):
    """Dictionary command to look up word definitions"""
    cmd = message.command
    msg = await message.reply("**🔎 Searching for definition ...**")
    # Get input string from command or replied message
    input_string = ""
    if len(cmd) > 1:
        input_string = " ".join(cmd[1:])
    elif message.reply_to_message and len(cmd) == 1:
        input_string = message.reply_to_message.text
    elif not message.reply_to_message and len(cmd) == 1:
        await msg.edit("`Can't pass to the void.`")
        await asyncio.sleep(2)
        await msg.delete()
        return

    def combine(s_word, name):
        """Combine definition and example for a word type"""
        w_word = f"**__{name.title()}__**\n"
        for i in s_word:
            if "definition" in i:
                if "example" in i:
                    w_word += (
                        "\n**Definition**\n<pre>"
                        + i["definition"]
                        + "</pre>\n<b>Example</b>\n<pre>"
                        + i["example"]
                        + "</pre>"
                    )
                else:
                    w_word += (
                        "\n**Definition**\n" + "<pre>" + i["definition"] + "</pre>"
                    )
        w_word += "\n\n"
        return w_word

    def out_print(word1):
        """Format the complete output for all word types"""
        out = ""
        if "meaning" in word1:
            meaning = word1["meaning"]
            word_types = [
                "noun", "verb", "preposition", "adverb", "adjective",
                "abbreviation", "exclamation", "transitive verb",
                "determiner", "crossReference"
            ]
            
            for word_type in word_types:
                if word_type in meaning:
                    out += combine(meaning[word_type], word_type)
                    
        if "title" in word1:
            out += (
                "**__Error Note__**\n\n▪️`"
                + word1["title"]
                + "\n\n▪️"
                + word1["message"]
                + "\n\n▪️<i>"
                + word1["resolution"]
                + "</i>`"
            )
        return out

    if not input_string:
        await msg.edit("`Please enter word to search‼️`")
        return

    # Make API request using aiohttp
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.dictionaryapi.dev/api/v1/entries/en/{input_string}") as response:
                if response.status == 200:
                    r_dec = await response.json()
                    
                    v_word = input_string
                    if isinstance(r_dec, list):
                        r_dec = r_dec[0]
                        v_word = r_dec["word"]
                        
                    last_output = out_print(r_dec)
                    if last_output:
                        await msg.edit(
                            "`Search result for   `" + f" {v_word}\n\n" + last_output
                        )
                    else:
                        await msg.edit("`No result found from the database.`")
                else:
                    await msg.edit("`Error: Could not fetch definition.`")
        except aiohttp.ClientError:
            await msg.edit("`Error: Network request failed.`")
        except Exception as e:
            await msg.edit(f"`Error: {str(e)}`")
