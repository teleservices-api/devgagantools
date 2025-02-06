
import sys
import os
import pathlib
import time
import datetime as dt
import aiofiles

sys.path.insert(0, f"{pathlib.Path(__file__).parent.resolve()}")

from spylib import upload_file, download_file


class Timer:
    def __init__(self, time_between=5):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False

def progress_bar_str(done, total):
    percent = round(done/total*100, 2)
    strin = "░░░░░░░░░░"
    strin = list(strin)
    for i in range(round(percent)//10):
        strin[i] = "█"
    strin = "".join(strin)
    final = f"Percent: {percent}%\n{human_readable_size(done)}/{human_readable_size(total)}\n{strin}"
    return final 

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

async def fast_download(client, msg, reply = None, download_folder = None, progress_bar_function = progress_bar_str, name = None):
    timer = Timer()

    async def progress_bar(downloaded_bytes, total_bytes):
        if timer.can_send():
            data = progress_bar_function(downloaded_bytes, total_bytes)
            await reply.edit(f"{data}")

    file = msg.document
    filename = name if name else msg.file.name
    dir = "downloads/"

    try:
        os.mkdir("downloads/")
    except:
        pass

    if not filename:
        filename = "video.mp4"
                    
    if download_folder == None:
        download_location = dir + filename
    else:
        download_location = download_folder + filename 

    with open(download_location, "wb") as f:
        if reply != None:
            await download_file(
                client=client, 
                location=file, 
                out=f,
                progress_callback=progress_bar
            )
        else:
            await download_file(
                client=client, 
                location=file, 
                out=f,
            )
    return download_location

async def fast_upload(client, file_location, reply=None, name=None, progress_bar_function = progress_bar_str):
    timer = Timer()
    if name == None:
        name = file_location.split("/")[-1]
    async def progress_bar(downloaded_bytes, total_bytes):
        if timer.can_send():
            data = progress_bar_function(downloaded_bytes, total_bytes)
            await reply.edit(f"{data}")
    if reply != None:
        with open(file_location, "rb") as f:
            the_file = await upload_file(
                client=client,
                file=f,
                name=name,
                progress_callback=progress_bar
            )
    else:
        with open(file_location, "rb") as f:
            the_file = await upload_file(
                client=client,
                file=f,
                name=name,
            )
        
    return the_file



async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""

        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1

        unit = ts[index:].lstrip()

        if value:
            value = int(value)

        return value, unit

    value, unit = extract_value_and_unit(time_string)

    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0
PROGRESS_BAR = """\n
│ **__Completed:__** {1}/{2}
│ **__Bytes:__** {0}%
│ **__Speed:__** {3}/s
│ **__ETA:__** {4}
╰─────────────────────╯
"""
async def progress_bar(current, total, ud_type, message, start):

    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:

        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["♦" for i in range(math.floor(percentage / 10))]),
            ''.join(["◇" for i in range(10 - math.floor(percentage / 10))]))

        tmp = progress + PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),

            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text="{}\n│ {}".format(ud_type, tmp),)             
        except:
            pass

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2] 
    
def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def split_and_upload_file(app, sender, target_chat_id, file_path, caption, topic_id, is_pin):
    if not os.path.exists(file_path):
        await app.send_message(sender, "❌ File not found!")
        return

    file_size = os.path.getsize(file_path)
    start = await app.send_message(sender, f"ℹ️ File size: {file_size / (1024 * 1024):.2f} MB")
    PART_SIZE =  1*9 * 1024 * 1024 * 1024

    part_number = 0
    async with aiofiles.open(file_path, mode="rb") as f:
        while True:
            chunk = await f.read(PART_SIZE)
            if not chunk:
                break

            # Create part filename
            base_name, file_ext = os.path.splitext(file_path)
            part_file = f"{base_name}.part{str(part_number).zfill(3)}{file_ext}"

            # Write part to file
            async with aiofiles.open(part_file, mode="wb") as part_f:
                await part_f.write(chunk)

            # Uploading part
            edit = await app.send_message(sender, f"⬆️ Uploading part {part_number + 1}...")
            part_caption = f"{caption} \n\n**Part : {part_number + 1}**"
            await app.send_document(target_chat_id, document=part_file, caption=part_caption, reply_to_message_id=topic_id,
                progress=progress_bar,
                progress_args=("╭─────────────────────╮\n│      **__Pyro Uploader__**\n├─────────────────────", edit, time.time())
            )
            await edit.delete()
            os.remove(part_file)  # Cleanup after upload

            part_number += 1

    await start.delete()
    os.remove(file_path)
