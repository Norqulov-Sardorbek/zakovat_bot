import logging
import sys
import asyncio
from django.core.management.base import BaseCommand
from zakovat_bot.handlers import *
from zakovat_bot.dispatcher import bot,  dp
from zakovat_bot.utils import set_bot_commands

# Set the default settings module for your Django project
async def main() -> None:
    await set_bot_commands(bot)
    await dp.start_polling(bot)



class Command(BaseCommand):

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())