from telegram import LabeledPrice
from nandha.helpers.decorator import Command


__module__ = 'Pay'


__help__ = '''
*✨ Support Our Bot's Development!*

Support our bot's continuous improvement and maintenance by becoming a star supporter.

*Commands:*
```
/pay [amount] - Make a contribution to support the bot
```

*How to Use:*
Simply send `/pay` followed by your desired amount
• Default contribution: 5 Stars
• Custom amount: `/pay 10` (for 10 stars)

*Benefits of Supporting:*
• Help maintain bot uptime and performance
• Enable new feature development
• Support ongoing maintenance
• Join our premium supporter community

*Every star makes a difference!* 🌟
'''


@Command('pay')
async def StarPayment(update, context):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    bot = context.bot

    amount = 5  # default contribution amount

    if args:
        amount = args[0]
        if not amount.isdigit() or int(amount) == 0:
            amount = 5

    try:
        await bot.send_invoice(
            chat_id=chat.id,
            title=f"Support {bot.first_name}",
            description="Thank you for supporting our bot! Your contribution helps keep our services running and enables new features.",
            currency='XTR',
            payload='star_support',
            provider_token='',
            prices=[
                LabeledPrice(label='Star Support', amount=amount)
            ],
            reply_to_message_id=message.reply_to_message.id if message.reply_to_message else message.id
        )
    except Exception as e:
        return await message.reply_text(
            text=f"❌ Sorry, we encountered an error: {str(e)}\nPlease try again or contact support if the issue persists.",
        )




