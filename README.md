<div align="center">
  <h1>devgagantools</h1>
  
  <p>
    <img src="https://img.shields.io/pypi/v/devgagantools?color=blue&style=flat-square" alt="PyPI Version">
    <img src="https://img.shields.io/pypi/pyversions/devgagantools?style=flat-square" alt="Python Versions">
    <img src="https://img.shields.io/github/license/devgaganin/devgagantools?style=flat-square" alt="License">
    <img src="https://img.shields.io/pypi/dm/devgagantools?style=flat-square&color=brightgreen" alt="Downloads">
  </p>

</div>

`devgagantools` is a Python library designed for fast and efficient file upload and download operations. It includes features like progress tracking, customizable file names, and human-readable file size formatting. The library is asynchronous and integrates seamlessly with Telegram bots or other projects requiring file management.

---

## Features

- **Fast File Downloads**: Asynchronous file downloading with real-time progress updates.
- **Fast File Uploads**: Asynchronous file uploading with customizable filenames and progress tracking.
- **Progress Bar**: Dynamic progress bar for file operations.
- **Human-Readable Sizes**: Easily convert file sizes to human-readable formats.
- **Custom Timing**: Control update intervals for progress tracking.

---

## Installation

To install the library once it's published to PyPI, use:

```bash
pip install devgagantools
```

---

## Usage

### 1. Fast Download

You can use the `devgagantools` download functionality by providing the required parameters:

- **`client`**: The Telegram client instance (e.g., Pyrogram Client).  
- **`msg`**: The Telegram message containing the file to download.  
- **`reply`** *(Optional)*: The reply message to update with progress.  
- **`download_folder`** *(Optional)*: Folder where the file will be saved (default: `downloads/`).  
- **`name`** *(Optional)*: A custom filename for the downloaded file (default: original file name).  
- **`progress_bar_function`** *(Optional)*: A function to customize the progress bar display.

#### Example

```python
download_location = await devgagantools.fast_download(
    client=client,
    msg=message,
    reply=reply_message,  # Optional
    download_folder="my_files/",  # Optional
    name="custom_filename.mp4",  # Optional
    user_id=1234 # must pass int
)
print(f"File downloaded to: {download_location}")
```

---

### 2. Fast Upload

You can upload files using the following arguments:

- **`client`**: The Telegram client instance (e.g., Pyrogram Client).  
- **`file_location`**: The local file path to upload.  
- **`reply`** *(Optional)*: The reply message to update with progress.  
- **`name`** *(Optional)*: A custom name for the uploaded file (default: original file name).  
- **`progress_bar_function`** *(Optional)*: A function to customize the progress bar display.

#### Example

```python
uploaded_file = await devgagantools.fast_upload(
    client=client,
    file_location="my_files/custom_filename.mp4",
    reply=reply_message,  # Optional
    name="uploaded_file.mp4",  # Optional
    user_id=12344 # must pass
)
print(f"File uploaded successfully: {uploaded_file}")
```

---

## Parameters for Progress Bar Customization

You can use a custom progress bar function for more control over how the progress is displayed. The function must accept two arguments:

- **`done`**: Bytes downloaded or uploaded so far.  
- **`total`**: Total size of the file in bytes.  

Example of a custom progress bar function:

```python
def custom_progress_bar(done, total):
    percent = round(done / total * 100, 2)
    return f"Progress: {percent}% ({done}/{total} bytes)"
```

Pass this function as the `progress_bar_function` argument in the download or upload methods.

---

## Human-Readable File Sizes

The library also provides a utility to convert file sizes into human-readable formats:

```python
from devgagantools import human_readable_size

size = human_readable_size(1048576)  # Output: '1.00 MB'
```

---

## Dependencies

- **telethon**: For Telegram client and file management.  
- **pathlib, os, time, datetime**: Standard Python libraries for file and time management.

---

## License

This project is licensed under the MIT License.

---

## Contributions

Contributions are welcome! Feel free to fork the repository, make your changes, and submit a pull request.

## Special Thanks
- Mautrix Telegram Bridge


## Contacts
- Contact us on telegram for any query [Team Spy](https://team_spy_pro)
