
from pyrogram import filters, types
from nandha import pbot as bot


__help__ = """
*Commands*:
/flames

```
/flames person & person: 
this module will predict your future with
your given person names ( just a joyful childhood game )

PREDICTION:
Friends,
Love,
Affection, 
Marriage, 
Enemy, 
Siblings
```

*Example*:
`/flames gojo & makima`
"""


__module__ = 'Flames'

def remove_match_char(list1: list, list2: list) -> list:
    for i in range(len(list1)):
        for j in range(len(list2)):
            if list1[i] == list2[j]:
                c = list1[i]
                list1.remove(c)
                list2.remove(c)
                list3 = list1 + ["*"] + list2
                return [list3, True]
    list3 = list1 + ["*"] + list2
    return [list3, False]


def flames(p1: str, p2: str) -> str:
    p1 = p1.lower()
    p1.replace(" ", "")
    p1_list = list(p1)
    p2 = p2.lower()
    p2.replace(" ", "")
    p2_list = list(p2)
    proceed = True

    while proceed:
        ret_list = remove_match_char(p1_list, p2_list)

        con_list = ret_list[0]

        proceed = ret_list[1]

        star_index = con_list.index("*")

        p1_list = con_list[:star_index]

        p2_list = con_list[star_index + 1 :]

    count = len(p1_list) + len(p2_list)

    result = ["Friends", "Love", "Affection", "Marriage", "Enemy", "Siblings"]

    while len(result) > 1:

        split_index = count % len(result) - 1

        if split_index >= 0:

            right = result[split_index + 1 :]
            left = result[:split_index]

            result = right + left

        else:
            result = result[: len(result) - 1]

    return p1, p2, result[0]



@bot.on_message(filters.command('flames') & ~filters.forwarded)
async def check_flames(_, message):
       m = message
       format = "/flames gojo & makima"
       couple = m.text.split(maxsplit=1)[1] if len(m.text.split()) > 1 else None
       
       if not couple:
           return await m.reply_text(format)
         
       try:
           person1, person2 = couple.split('&')
       except Exception:
           return await m.reply_text(format)
         
       p1, p2, text = flames(person1.strip(), person2.strip())

       info = "<blockquote>FLAMES is a game where you determine the relationship between two people based on their names.</blockquote>"
       await m.reply_text(
              f"**💜 {p1.capitalize()} and ❤️ {p2.capitalize()} flames is {text} ✨**\n\n{info}"
       )
