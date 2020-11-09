import asyncio
import html
import os
import re
import traceback

from config import sudoers
from pyrogram import Client, filters
from meval import meval

@Client.on_message(filters.su_cmd(r"(?P<cmd>ev(al)?)\s+(?P<code>.+)", flags=re.S))
async def evals(client, message):
    cmd = message.matches[0]['cmd']
    eval_code = message.matches[0]['code']
    
    # Shortcuts that will be available for the user code
    reply = message.reply_to_message
    user = (reply or message).from_user
    chat = message.chat
    
    try:
        output = await meval(eval_code, globals(), **locals())
    except:
        traceback_string = traceback.format_exc()
        text = f"Exception while running the code:\n{traceback_string}"
        if cmd == 'ev':
            return await message.edit(text)
        return await message.reply(text)
    else:
        try:
            output = html.escape(str(output)) # escape html special chars
            text = ''
            for line in output.splitlines():
                text += f"<code>{line}</code>\n"
            if cmd == 'ev':
                return await message.edit(text)
            await message.reply(text)
        except:
            traceback_string = traceback.format_exc()
            text = f"Exception while sending output:\n{traceback_string}"
            if cmd == 'ev':
                return await message.edit(text)
            await message.reply(text)