"""
> Copyright (C) 2025 devgagan - https://github.com/devgagan/devgagantools
"""

import sys
import os
import pathlib
import time
import logging
import mimetypes
from telethon.tl.types import DocumentAttributeFilename
from pyrogram.enums import ParseMode

sys.path.insert(0, f"{pathlib.Path(__file__).parent.resolve()}")

from spylib import upload_file, download_file

class Timer:
    def __init__(self, time_between=1):  # 1 second for frequent updates
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False

def progress_bar_str(done, total, user_id):
    percent = round(done/total*100, 2)
    strin = "♦" * (int(percent // 10)) + "◇" * (10 - int(percent // 10))
    final = (
        f"╭──────────────────╮\n"
        f"│     **__Progress__**       \n"
        f"├──────────\n"
        f"│ {strin}\n\n"
        f"│ **__Progress:__** {percent:.2f}%\n"
        f"│ **__Done:__** {done / (1024 * 1024):.2f} MB / {total / (1024 * 1024):.2f} MB\n"
        f"╰──────────────────╯\n"
        f"**__Powered by Team SPY__**"
    )
    return final 

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

async def fast_download(client, msg, reply=None, download_folder=None, progress_bar_function=None, name=None, user_id=None, fallback_client=None, chat_id=None):
    """
    Download a file from a message with progress tracking and user-specific isolation.
    
    Args:
        client: Telegram client (Telethon)
        msg: Message containing the file
        reply: Reply message for progress updates (Pyrogram Message)
        download_folder: Base folder for downloads
        progress_bar_function: Function to format progress
        name: Custom filename (optional)
        user_id: User identifier for isolation (optional)
        fallback_client: Telethon client for fallback messaging (optional)
        chat_id: Chat ID for fallback messaging (optional)
        
    Returns:
        Tuple of (path to the downloaded file, document attributes)
    """
    # Create a unique download ID
    timestamp = int(time.time())
    message_id = getattr(msg, 'id', 0)
    
    # Use provided user_id or extract from message if possible
    if user_id is None:
        try:
            user_id = getattr(msg.from_user, 'id', None) or \
                    getattr(msg, 'from_id', None) or \
                    f"unknown_{message_id}_{timestamp}"
        except AttributeError:
            user_id = f"unknown_{message_id}_{timestamp}"
    
    # Set up progress tracking
    timer = Timer()
    
    # Create progress callback
    async def progress_callback(downloaded_bytes, total_bytes):
        if reply and timer.can_send() and progress_bar_function:
            data = progress_bar_function(downloaded_bytes, total_bytes, user_id)
            try:
                logging.info(f"Updating progress for user {user_id}: {data}")
                await reply.edit_text(data, parse_mode=ParseMode.MARKDOWN)
            except pyrogram.errors.MessageNotModified:
                pass  # Ignore if the message content hasn't changed
            except Exception as e:
                logging.error(f"Pyrogram edit failed: {e}. Falling back to Telethon.")
                if fallback_client and chat_id:
                    try:
                        await fallback_client.send_message(chat_id, data, parse_mode='md')
                    except Exception as te:
                        logging.error(f"Telethon fallback failed: {te}")

    # Get file info
    file = msg.document
    
    # Set filename priority: custom name > document attribute > generated name
    if name:
        filename = name
    else:
        # Check document attributes for filename
        attributes = getattr(file, 'attributes', [])
        filename = None
        for attr in attributes:
            if isinstance(attr, DocumentAttributeFilename):
                filename = attr.file_name
                break
        
        if not filename:
            # Generate a default filename with extension based on mime type
            try:
                mime = getattr(file, 'mime_type', 'application/octet-stream')
                ext = mimetypes.guess_extension(mime) or '.bin'

                if ext == '.bin' and mime.startswith('video/'):
                    ext = '.mp4'  # Default to .mp4 for videos
            except AttributeError:
                ext = '.bin'
                
            filename = f"file_{user_id}_{timestamp}{ext}"
    
    # Create user-specific directory for isolation
    base_dir = download_folder or "downloads/"
    user_dir = os.path.join(base_dir, f"user_{user_id}")
    
    try:
        os.makedirs(user_dir, exist_ok=True)
    except Exception as e:
        logging.error(f"Error creating directory {user_dir}: {e}")
        # Fallback to base directory if user_dir creation fails
        user_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    # Full path for the downloaded file
    download_location = os.path.join(user_dir, filename)
    
    # Get document attributes
    attributes = getattr(file, 'attributes', [])
    
    # Log the download start
    logging.info(f"Downloading file to {download_location} (User: {user_id})")
    
    try:
        # Create the file and download
        with open(download_location, "wb") as f:
            await download_file(
                client=client, 
                location=file, 
                out=f,
                progress_callback=progress_callback if reply else None
            )
        
        logging.info(f"Download completed: {download_location}")
        return download_location
    
    except Exception as e:
        logging.error(f"Download failed: {e}")
        # Clean up partial file if it exists
        if os.path.exists(download_location):
            try:
                os.remove(download_location)
            except:
                pass
        raise

async def fast_upload(client, file_location, reply=None, name=None, progress_bar_function=None, user_id=None):
    """
    Upload a file with progress tracking and user-specific naming.
    
    Args:
        client: Telegram client
        file_location: Path to the file to upload
        reply: Reply message for progress updates
        name: Custom filename (optional)
        progress_bar_function: Function to format progress
        user_id: User identifier for filename prefix (optional)
        
    Returns:
        Uploaded file object
    """
    # Validate file exists
    if not os.path.exists(file_location):
        raise FileNotFoundError(f"File not found: {file_location}")
    
    # Create a unique identifier for this upload
    timestamp = int(time.time())
    
    # Set up progress tracking
    timer = Timer()
    
    # Determine filename with proper isolation
    if name is None:
        # Extract base filename
        base_name = os.path.basename(file_location)
        
        # Add user prefix if provided
        if user_id:
            # Check if the filename already has a user prefix to avoid duplication
            if not base_name.startswith(f"{user_id}_"):
                name = f"{user_id}_{base_name}"
            else:
                name = base_name
        else:
            # Add timestamp to ensure uniqueness if no user_id
            base, ext = os.path.splitext(base_name)
            name = f"{base}_{timestamp}{ext}"
    
    # Log upload start
    logging.info(f"Uploading file {file_location} as {name} (User: {user_id})")
    
    # Create progress callback
    async def progress_callback(uploaded_bytes, total_bytes):
        if timer.can_send() and progress_bar_function:
            data = progress_bar_function(uploaded_bytes, total_bytes)
            try:
                await reply.edit(f"{data}")
            except Exception as e:
                logging.error(f"Error updating progress: {e}")
    
    try:
        # Upload the file
        if reply:
            with open(file_location, "rb") as f:
                the_file = await upload_file(
                    client=client,
                    file=f,
                    name=name,
                    progress_callback=progress_callback
                )
        else:
            with open(file_location, "rb") as f:
                the_file = await upload_file(
                    client=client,
                    file=f,
                    name=name
                )
                
        logging.info(f"Upload completed: {name}")
        return the_file
        
    except Exception as e:
        logging.error(f"Upload failed: {e}")
        raise
