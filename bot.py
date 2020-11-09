from config import load_env, sudoers, langs, client, bot
from database import connect_database, Config
from datetime import datetime
from pyrogram import idle
from rich import print, box
from rich.panel import Panel
from tortoise import run_async
from utils import info
import asyncio
import os
import rich

async def alert_startup():
    plugins = [(handler.user_callback if hasattr(handler, 'user_callback') else handler.callback) for group in client.dispatcher.groups.values() for handler in group]
    
    plugins_count = len(plugins)
    
    started_alert = f"""🚀 UserLixo launched. <code>{plugins_count}</code> plugins loaded.
- <b>app_version</b>: <code>{client.app_version}</code>
- <b>device_model</b>: <code>{client.device_model}</code>
- <b>system_version</b>: <code>{client.system_version}</code>
"""
    try:
        await bot.send_message(info['user']['username'], started_alert)
    except:
        await client.send_message(os.getenv('LOGS_CHAT'), started_alert)

async def main():
    await connect_database()
    await load_env()
    
    await client.start()
    info['user'] = await client.get_me()
    sudoers.append(info['user'].id)
    
    await bot.start()
    info['bot'] = await bot.get_me()
    
    # Editing restaring alert
    restarting_alert = await Config.get_or_none(key="restarting_alert")
    if restarting_alert:
        message_id, chat_id, cmd_timestamp = restarting_alert.value.split('|')
        cmd_timestamp = float(cmd_timestamp)
        now_timestamp = datetime.now().timestamp()
        diff = round(now_timestamp-cmd_timestamp, 2)
        
        try:
            await client.edit_message_text(int(chat_id), int(message_id), langs.restarted_alert(seconds=diff))
        except Exception as e:
            print(f'[yellow]Failed to edit the restarting alert. Maybe the message has been deleted or somehow it became inacessible.\n{e}[/yellow]')
        await Config.get(id=restarting_alert.id).delete()
    
    # Showing alert in cli
    process = await asyncio.create_subprocess_shell("git log -1 --format=%cd --date=local",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.STDOUT)
    commit_date = (await process.communicate())[0].decode().strip()
    
    account = '@'+info['user']['username'] if info['user']['username'] else info['user']['id']
    text = f":ok: [bold green]UserLixo is running[/bold green] :ok:"
    
    userlixo_info = dict(
        Account=account,
        Bot=info['bot']['username'],
        Prefixes=os.getenv('PREFIXES'),
        Logs_chat=os.getenv('LOGS_CHAT'),
        Sudoers=', '.join([*set(map(str, sudoers))]), # using set() to make the values unique
        Commit_date=commit_date
    )
    for k,v in userlixo_info.items():
        text += f"\n[dim cyan]{k}:[/dim cyan] [dim]{v}[/dim]"

    print(Panel.fit(text, border_style='green', box=box.ASCII))
    
    # Sending alert via Telegram
    await alert_startup()
    
    await idle()
    
run_async(main())