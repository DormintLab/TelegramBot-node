import argparse
import asyncio
from pathlib import Path
from dormai.async_api import AsyncDormAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser("sender")
    subparsers.add_parser("receiver")
    return parser.parse_args()


async def start_sender():
    async with AsyncDormAI(Path("./dormai.yml")) as dormai:
        while True:
            inputs, context = await dormai.receive_event()
            if inputs is None:
                continue
            text: str = inputs.message_text
            tg_id: int = context.tg_id
            payload = {
                'chat_id': tg_id,
                'text': text,
                'parse_mode': "Markdown",
            }
            await dormai.client.post("https://api.telegram.org/bot{token}/sendMessage".format(token=dormai.settings["BOT_TOKEN"]),
                                     data=payload)


async def start_receiver():
    async with AsyncDormAI(Path("./dormai.yml")) as dormai:

        async def on_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            message_text = str(update.message.text)
            tg_id: int = int(update.message.from_user.id)
            await dormai.send_event(dormai.OutputData(message_text=message_text),
                                    dormai.ContextData(tg_id=tg_id))

        app = (ApplicationBuilder()
               .token(dormai.settings["BOT_TOKEN"])
               .build())

        app.add_handler(MessageHandler(filters.TEXT,
                                       on_text_handler,
                                       block=False))
        app.run_polling()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "sender":
        asyncio.run(start_sender())
    elif args.command == "receiver":
        asyncio.run(start_receiver())
    else:
        raise ValueError("Invalid command")
