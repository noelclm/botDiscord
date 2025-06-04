import json
import os
import signal

import discord
import pytz

from discord.ext import commands
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from db_connections import SQLiteDB
from functions import Log, split_message, text_state

TOKEN_BOT_DISCORD = os.getenv('TOKEN_BOT_DISCORD')
DISCORD_CHANNEL = json.loads(os.getenv('DISCORD_CHANNEL'))
CALENDAR_SCOPES = os.getenv('CALENDAR_SCOPES').split(',')
CALENDAR_CREDENTIALS = json.loads(os.getenv('CALENDAR_CREDENTIALS'))
CALENDAR_ID = os.getenv('CALENDAR_ID')
TIMEZONE = os.getenv('TIMEZONE')

log = Log('./', 'discord_logs')
db = SQLiteDB('bot.sqlite')

intents = discord.Intents(guilds=True, members=True, presences=True, message_content=True)
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=False)
scheduler = AsyncIOScheduler()


@bot.event
async def on_ready():
    log.info('on_ready', f'Iniciando bot {bot.user.name}')
    scheduler.start()
    channel = bot.get_channel(1379121716336529461)
    await channel.send(f"Hola!!")


@bot.event
async def on_member_join(member):
    message = f"Hola {member.mention}!! Bienvenid@ a {member.guild.name}!! ya somos {member.guild.member_count}!!"
    channel = bot.get_channel(DISCORD_CHANNEL['GENERAL'])
    if channel:
        await channel.send(message)
    else:
        log.error('on_member_join', f'channel general not found')


@bot.event
async def on_presence_update(before, after):
    try:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        formatted_now = now.strftime("%d-%m-%Y %H:%M:%S")

        member_id = before.id
        member_name = before.name
        member_display_name = before.display_name
        old_status = before.status
        new_status = after.status
        old_mobile_status = before.mobile_status
        new_mobile_status = after.mobile_status

        if old_status != new_status and old_mobile_status == new_mobile_status:
            old_status_name = text_state(old_status)
            new_status_name = text_state(new_status)
            log.data('on_presence_update', f'PC | {member_display_name} ({member_name}) ha cambiado de {old_status_name} '
                     f'a {new_status_name} a las {formatted_now}')
            sql = (f"INSERT INTO discord_log (user_id, member_name, member_display_name, old_status, new_status) "
                   f"VALUES ({member_id}, '{member_name}', '{member_display_name}', '{old_status}', '{new_status}');")
            db.insert(sql)

        if old_mobile_status != new_mobile_status:
            old_status_name = text_state(old_mobile_status)
            new_status_name = text_state(new_mobile_status)
            log.data('on_presence_update', f'Móvil | {member_display_name} ({member_name}) ha cambiado de {old_status_name} '
                     f'a {new_status_name} a las {formatted_now}')
            sql = (f"INSERT INTO discord_log "
                   f"(user_id, member_name, member_display_name, old_status, new_status, mobile) "
                   f"VALUES ({member_id}, '{member_name}', '{member_display_name}', '{old_mobile_status}', "
                   f"'{new_mobile_status}', 1);")
            db.insert(sql)

    except Exception as e:
        log.error('on_presence_update', f'{e}')


async def check_calendar():
    try:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz).replace(microsecond=0)
        time_str = now.strftime('%H:%M')
        log.debug('check_calendar', f'Search events')

        events = db.select("SELECT * FROM calendar_event;")

        for event in events:
            d_time = event['time']
            channel_id = int(event['chanel'])  # Convert to int as channel IDs are integers

            if d_time == time_str:
                time_text = '***ahora***'
            else:
                time_text = f'a las **{d_time}**'

            msg = event['msg'].replace('%time%', time_text)
            log.debug('check_calendar', f'send {d_time} {msg}')

            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(msg)
            else:
                log.error('check_calendar', f'channel {channel_id} not found')
    except Exception as e:
        log.error('check_calendar', f'{e}')


async def cron_calendar():
    get_calendar()


def get_calendar():
    try:
        db.delete("DELETE FROM calendar_event;")

        credentials = service_account.Credentials.from_service_account_info(CALENDAR_CREDENTIALS, scopes=CALENDAR_SCOPES)
        service = build('calendar', 'v3', credentials=credentials)

        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz).replace(tzinfo=None)
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(hours=24)).isoformat() + 'Z'

        now_check = datetime.strptime(datetime.now(tz).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S'),
                                      '%Y-%m-%d %H:%M:%S')
        time_check = now_check.isoformat() + 'Z'

        events = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        # Procesar los eventos encontrados
        if len(events['items']):
            for event in events['items']:
                start = event['start'].get('dateTime', event['start'].get('date'))
                if time_check < start:
                    channel_id = None
                    meet = 'Entra en el canal de Discord para acceder a la reunión '
                    name = str(event['summary']).strip()
                    if 'hangoutLink' in event:
                        meet = 'Entra en [Google Meet]({}) para acceder a la reunión'.format(event['hangoutLink'])
                    inicio = event['start'].get('dateTime', event['start'].get('date'))
                    d_time = datetime.fromisoformat(inicio).strftime('%H:%M')
                    msg = f'@everyone Os recuerdo que %time% tenéis ***{name}*** \n{meet}'
                    if name.startswith('Discord event -'):
                        channel_id = DISCORD_CHANNEL['GENERAL']
                    if channel_id:
                        # Insert event into the calendar_event table
                        sql = f"INSERT INTO calendar_event (chanel, msg, time) VALUES ('{channel_id}', '{msg}', '{d_time}')"
                        db.insert(sql)
                    else:
                        raise Exception(f'channel id {channel_id} not found')
    except Exception as e:
        log.error('get_calendar', f'{e}')


async def send_registre():
    try:
        data = get_times()
        if data != "":
            channel = bot.get_channel(DISCORD_CHANNEL['CONTROL'])
            if channel:
                date_today = datetime.now()
                date_yesterday = date_today - timedelta(days=1)
                yesterday = date_yesterday.strftime('%d-%m-%Y')
                data = f"Ayer día {yesterday} se obtuvo el siguiente registro de horas en Discord:\n" + data
                messages = split_message(data)
                for message in messages:
                    await channel.send(message)
            else:
                raise Exception(f'channel CONTROL not found')
    except Exception as e:
        log.error('send_registre', f'{e}')


def get_time_db(mobile=0):
    try:
        sql = f"""
WITH status_changes AS (
    SELECT user_id, member_name, member_display_name, old_status, new_status, mobile, created_at,
           LEAD(created_at) OVER (PARTITION BY user_id ORDER BY created_at) AS next_created_at
    FROM discord_log
    WHERE mobile = {mobile}
),
status_durations AS (
    SELECT user_id, member_name, member_display_name, new_status AS status, mobile,
           DATE(created_at) AS date,
           CASE 
               WHEN next_created_at IS NOT NULL THEN strftime('%s', next_created_at) - strftime('%s', created_at)
               ELSE strftime('%s', CURRENT_TIMESTAMP) - strftime('%s', created_at)
           END AS duration_seconds
    FROM status_changes
)
SELECT user_id, member_name, member_display_name, status, mobile, date, SUM(duration_seconds) / 3600 AS hours_in_status
FROM status_durations 
WHERE status != 'offline' AND date = DATE('now', '-1 day')
GROUP BY user_id, member_name, member_display_name, status, mobile, date
ORDER BY member_display_name, status, hours_in_status DESC;"""
        return db.select(sql)
    except Exception as e:
        raise Exception(f'get_time_db - {str(e)}')


def get_formated_data(data_object, registre, pc_mobile):
    try:
        for row in registre:
            user_id = row['user_id']
            name = row['member_display_name']
            status = row['status']
            hours = int(row['hours_in_status']) if row['hours_in_status'] >= 1 else 0
            minutes_decimal = (row['hours_in_status'] - hours) * 60
            minutes = int(minutes_decimal)
            seconds = round((minutes_decimal - minutes) * 60)
            if seconds > 30:
                minutes += 1
            if hours != 0 or minutes != 0:
                if user_id not in data_object:
                    data_object[user_id] = {'name': name, 'time_pc': {}, 'time_mobile': {}}
                data_object[user_id][pc_mobile][status] = f'{hours}h {minutes}m'
        return data_object
    except Exception as e:
        raise Exception(f'get_formated_data - {str(e)}')


def get_times():
    try:
        registre_pc = get_time_db(0)
        registre_mobile = get_time_db(1)

        data_object = {}
        data_object = get_formated_data(data_object, registre_pc, 'time_pc')
        data_object = get_formated_data(data_object, registre_mobile, 'time_mobile')

        data_array = []
        for user_id in data_object:
            name = data_object[user_id]['name']

            time_pc = data_object[user_id]['time_pc']
            time_array_pc = []
            for t in time_pc:
                time_array_pc.append(time_pc[t] + " " + text_state(t))

            time_mobile = data_object[user_id]['time_mobile']
            time_array_mobile = []
            for t in time_mobile:
                time_array_mobile.append(time_mobile[t] + " " + text_state(t))

            time_text = " y ".join(time_array_pc)
            if len(time_array_mobile) > 0:
                time_text = time_text + ", desde el móvil " + " y ".join(time_array_mobile)
            data_array.append(f"**{name}** estuvo {time_text}")

        data = '\n'.join(data_array)
        return data
    except Exception as e:
        raise Exception(f'get_times - {str(e)}')


def signal_handler(sig, frame):
    log.info('signal_handler','Exiting...')
    db.close()


def main():
    events = db.select("SELECT COUNT(*) as count FROM calendar_event;")
    if events[0]['count'] == 0:
        get_calendar()

    scheduler.add_job(cron_calendar, CronTrigger(minute=0, hour='00,12', timezone=pytz.timezone(TIMEZONE)))
    scheduler.add_job(check_calendar, CronTrigger(minute='0,15,30,45', timezone=pytz.timezone(TIMEZONE)))
    scheduler.add_job(send_registre, CronTrigger(minute=0, hour=6, timezone=pytz.timezone(TIMEZONE)))

    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        bot.run(TOKEN_BOT_DISCORD)
    finally:
        db.close()

if __name__ == "__main__":
    main()
