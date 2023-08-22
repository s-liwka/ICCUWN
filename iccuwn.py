import customtkinter as ctk
from CTkMessagebox import CTkMessagebox as msgbox
import subprocess as sb
from PIL import Image
import os
import platform
import json
import re
import yt_dlp
import asyncio
import threading
import requests
import sys

path_to_iccuwn = os.path.join(os.path.dirname(sys.argv[0]), os.path.basename(sys.argv[0]))

home_dir = os.path.expanduser('~')

if platform.system() == 'Linux':
    config_dir = os.path.join(home_dir, '.config', 'ICCUWN')
else:
    config_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'ICCUWN')
    home_dir = home_dir.replace('\\', '\\\\')

themes_dir = os.path.join(config_dir, 'themes')
config_file = os.path.join(config_dir, 'config.json')

if not os.path.exists(config_file):
    if not os.path.exists(config_dir):    
        os.makedirs(config_dir)
        os.makedirs(themes_dir)
    with open(config_file, 'w') as f:
        f.write('{')
        f.write('\n\t"iccuwn_version": "a1.1",')
        f.write('\n\t"update_notif": "True",')
        f.write(f'\n\t"default_output": "{home_dir}",')
        f.write('\n\t"default_format": "mp3",')
        f.write('\n\t"appearance": "system",')
        f.write('\n\t"ctk_theme": "blue",')
        f.write('\n\t"custom_ctk_theme": ""')
        f.write('\n}')


def load_config(file_path):
    with open(file_path, 'r') as cfg:
        cfg = json.load(cfg)
    return cfg


cfg = load_config(config_file)

iccuwn_version = cfg['iccuwn_version']
update_notif = cfg['update_notif']
default_output_dir = cfg['default_output']
default_format = cfg['default_format']
appearance = cfg['appearance']
ctk_theme = cfg['ctk_theme']
custom_ctk_theme = cfg['custom_ctk_theme']

print(custom_ctk_theme)

github_version = None
outdated = False


def check_for_updates():
    global outdated
    global github_version
    check_version =  requests.get(r'https://raw.githubusercontent.com/s-liwka/ICCUWN/main/version')
    if check_version.status_code == 200:
        github_version = check_version.content.decode('utf-8')
        if github_version == iccuwn_version:
            return
        else:
            outdated = True


def update_iccuwn():
    latest_script = requests.get(r'https://raw.githubusercontent.com/s-liwka/ICCUWN/main/iccuwn.py')
    if latest_script.status_code == 200:
        with open(path_to_iccuwn, 'wb') as f:
            f.write(latest_script.content)
        exit()


def update_msgbox():
    global github_version
    update_prompt = msgbox(title='Update', message=f'You are running an outdated version! ({iccuwn_version}) The latest version is {github_version}You may disable this prompt in settings.', option_1='Ignore', option_2='Update')

    response = update_prompt.get()

    if response == 'Update':
        update_iccuwn()
    else:
        pass

# download icons
if not os.path.exists(os.path.join(config_dir, 'folder.png')):
    download_folder_icon = requests.get(r'https://github.com/Donnnno/Arcticons/blob/main/app/src/dark/res/drawable-nodpi/folder_alt_4.png?raw=true')
    download_settings_icon = requests.get(r'https://github.com/Donnnno/Arcticons/blob/main/app/src/dark/res/drawable-nodpi/settings.png?raw=true')\

    if download_folder_icon.status_code == 200:
        with open(os.path.join(config_dir, 'folder.png'), 'wb') as f:
            f.write(download_folder_icon.content)
    else:
        pass

    if download_settings_icon.status_code == 200:
        with open(os.path.join(config_dir, 'settings.png'), 'wb') as f:
            f.write(download_settings_icon.content)

def download_themes():
    global themes_dir
    pink_theme = requests.get(r'https://raw.githubusercontent.com/a13xe/CTkThemesPack/main/themes/pink.json')
    yellow_theme = requests.get(r'https://raw.githubusercontent.com/a13xe/CTkThemesPack/main/themes/yellow.json')
    red_theme = requests.get(r'https://raw.githubusercontent.com/a13xe/CTkThemesPack/main/themes/red.json')
    marsh_theme = requests.get(r'https://raw.githubusercontent.com/a13xe/CTkThemesPack/main/themes/marsh.json')

    if pink_theme.status_code == 200:
        with open(os.path.join(themes_dir, 'pink.json'), 'w') as f:
            f.write(pink_theme.content.decode('utf-8'))
    if red_theme.status_code == 200:
        with open(os.path.join(themes_dir, 'red.json'), 'w') as f:
            f.write(red_theme.content.decode('utf-8'))
    if yellow_theme.status_code == 200:
        with open(os.path.join(themes_dir, 'yellow.json'), 'w') as f:
            f.write(yellow_theme.content.decode('utf-8'))
    if marsh_theme.status_code == 200:
        with open(os.path.join(themes_dir, 'marsh.json'), 'w') as f:
            f.write(marsh_theme.content.decode('utf-8'))


if not os.path.exists(os.path.join(themes_dir, 'pink.json')):
    download_themes = threading.Thread(target=download_themes)
    download_themes.start()

check_for_updates()
#check_for_updates_thread = threading.Thread(target=check_for_updates)
#check_for_updates_thread.start()
    

settings_img = ctk.CTkImage(dark_image=Image.open(os.path.join(config_dir, 'settings.png')))
folder_img = ctk.CTkImage(dark_image=Image.open(os.path.join(config_dir, 'folder.png')))


def extract_percentage(percent_str):
    percent_match = re.search(r'(\d+\.\d+)\s?%', percent_str)
    if percent_match:
        return float(percent_match.group(1)) / 100.0
    return 0.0


def yt_dlp_error(e):
    msgbox(title="Error", message=f"YT-DLP Error: {e}", icon="cancel")


# get video title
async def get_video_title(url):
    ydl_opts = {
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = await asyncio.to_thread(ydl.extract_info, url)
        video_title = info_dict.get('title', 'Untitled')
        return video_title

# download function
async def download(url, output, resolution, Format):
    try:
        video_title = await get_video_title(url)
        output_mp4 = os.path.join(output, f"{video_title}.mp4")
        if Format == 'mp4':
            ydl_opts = {
                'format': f"bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]/best[height<={resolution}][ext=mp4]/best",
                'outtmpl': output_mp4,
                'progress_hooks': [progress_hook],
            }

        if Format == 'mp3':
            ydl_opts = {
                'format': 'worstvideo+bestaudio',
                'merge_output_format': 'mp4',
                'outtmpl': output_mp4,
                'progress_hooks': [progress_hook],
            }


        ydl = yt_dlp.YoutubeDL(ydl_opts)
        await asyncio.to_thread(ydl.download, [url])
        print('finished')
            

        if Format == 'mp3':
            precentage_label.configure(text="Converting to mp3...")
            to_mp3 = sb.Popen(['ffmpeg', '-i', output_mp4, '-c:a', 'libmp3lame', '-q:a', '0', '-y', f"{os.path.join(output, video_title)}.mp3"])
            to_mp3.wait()
            precentage_label.configure(text="Finished")
            os.remove(output_mp4)
        
    except Exception as e:
        yt_dlp_error(e)


mem_precent_value = 0.0

def progress_hook(d):
    global mem_precent_value
    if d['status'] == 'downloading':
        percent_str = d['_percent_str']
        percent_value = extract_percentage(percent_str)

        if percent_value > 1.0:
            percent_value = 1.0

        if mem_precent_value < percent_value:
            progressbar.set(round(percent_value, 2))
            formatted_precent_value = str("{:.2f}".format(percent_value*100))
            precentage_label.configure(text=f"{formatted_precent_value}%")
        else:
            pass

        mem_precent_value = round(percent_value, 2)


# actually download the video lol
def download_in_thread(url, output, resolution, Format):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(download(url, output, resolution, Format))
    if Format == 'mp4':
        precentage_label.configure(text="Finished")
    loop.close()



def download_button_command():
    precentage_label.configure(text="Preparing...")
    audioq = audio_quality_menu.get()
    resolution = resolution_menu.get()
    Format = format_menu.get()
    url = url_entry.get()
    output = output_folder_entry.get()
    aspect_ratio = '16:9'
    print(url)

    if aspect_ratio == '16:9':
        if resolution == 'Best Resolution':
            h = 9999
        elif resolution == '8K':
            h = 4608
        elif resolution == '4K':
            h = 2160
        elif resolution == '1440p':
            h = 1440
        elif resolution == '1080p':
            h = 1080
        elif resolution == '720p':
            h = 720
        elif resolution == '480p':
            h = 480
        elif resolution == '360p':
            h = 360
        elif resolution == '240p':
            h = 240
        elif resolution == '144p':
            h = 144

    print(url)
    thread = threading.Thread(target=download_in_thread, args=(url, output, h, Format))
    thread.start()


# ctrl+a handling
def select_all(event):
    event.widget.select_range(0, 'end')
    event.widget.icursor('end')
    return 'break'


ctk.set_appearance_mode(f"{appearance}")


if not custom_ctk_theme:
    ctk.set_default_color_theme(ctk_theme)
else:
    ctk.set_default_color_theme(custom_ctk_theme)


app = ctk.CTk()  # create CTk window like you do with the Tk window
app.geometry("640x360")
app.title('ICCUWN')
app.resizable(False, False)

first_loop = True
settings_window = None


def open_settings():
    global settings_window
    if settings_window is None or not settings_window.winfo_exists():

        def save_settings():
            global config_file
            print('wiowiow')
            cfg["default_output"] = default_output_folder_entry.get()
            cfg["default_format"] = default_format_menu.get()
            cfg["appearance"] = appearance_menu.get().lower()
            cfg["ctk_theme"] = ctk_theme_menu.get().lower()
            cfg["custom_ctk_theme"] = ctk_theme_entry.get()
            cfg["update_notif"] = update_prompt_checkbox.get()

            if cfg["ctk_theme"] == 'dark blue':
                cfg["ctk_theme"] = 'dark-blue'
            elif cfg["ctk_theme"] == 'red':
                cfg["custom_ctk_theme"] = os.path.join(themes_dir, 'red.json')
            elif cfg["ctk_theme"] == 'yellow':
                cfg["custom_ctk_theme"] = os.path.join(themes_dir, 'yellow.json')
            elif cfg["ctk_theme"] == 'pink':
                cfg["custom_ctk_theme"] = os.path.join(themes_dir, 'pink.json')
            elif cfg["ctk_theme"] == 'marsh':
                cfg["custom_ctk_theme"] = os.path.join(themes_dir, 'marsh.json')
            
            if cfg['update_notif'] == 1:
                cfg['update_notif'] = 'True'
            elif cfg['update_notif'] == 0:
                cfg['update_notif'] = 'False'

            
            with open(config_file, 'w') as f:
                json.dump(cfg, f, indent=4)
                pass

        def file_dialog_default_output():
            file_path = ctk.filedialog.askdirectory()
            if file_path:
                default_output_folder_entry.delete(0, ctk.END)
                default_output_folder_entry.insert(0, file_path)

        def file_dialog_ctk():
            file_path = ctk.filedialog.askdirectory()
            if file_path:
                ctk_theme_entry.delete(0, ctk.END)
                ctk_theme_entry.insert(0, file_path)


        settings_window = ctk.CTkToplevel(app)
        settings_window.title('ICCUWN Settings')
        settings_window.resizable(False, False)
        settings_window.geometry("320x480")

        # define widgets
        default_output_text = ctk.CTkLabel(settings_window, text='Default Output Folder')
        default_output_folder_entry = ctk.CTkEntry(settings_window, placeholder_text='Output Folder', width=200)
        default_output_folder_picker_button = ctk.CTkButton(settings_window, text="", image=folder_img, width=32, height=32, command=file_dialog_default_output)

        default_format_text = ctk.CTkLabel(settings_window, text='Default Format')
        default_format_menu = ctk.CTkOptionMenu(settings_window, values=['mp3', 'mp4'])

        appearance_text = ctk.CTkLabel(settings_window, text='Appearance')

        ctk_theme_text = ctk.CTkLabel(settings_window, text='Accent Color')
        ctk_theme_menu = ctk.CTkOptionMenu(settings_window, values=['Blue', 'Dark Blue', 'Green', 'Custom'])
        ctk_theme_entry = ctk.CTkEntry(settings_window, placeholder_text='Path to custom CTk Theme', width=200)
        ctk_theme_picker = ctk.CTkButton(settings_window, text="", image=folder_img, width=32, height=32, command=file_dialog_ctk)

        update_prompt_label = ctk.CTkLabel(settings_window, text="Update Prompt On Start")
        update_prompt_checkbox = ctk.CTkCheckBox(settings_window, text="Enable")

        save_settings_button = ctk.CTkButton(settings_window, text="Save", command=save_settings)

        default_output_folder_entry.insert(0, default_output_dir)

        if custom_ctk_theme:
            ctk_theme_entry.insert(0, custom_ctk_theme)

        if default_format == 'mp3':
           default_format_menu = ctk.CTkOptionMenu(settings_window, values=['mp3', 'mp4'])
        elif default_format == 'mp4':
            default_format_menu = ctk.CTkOptionMenu(settings_window, values=['mp4', 'mp3']) 
        
        if appearance == 'system':
            appearance_menu = ctk.CTkOptionMenu(settings_window, values=['System', 'Light', 'Dark'])
        elif appearance == 'dark':
            appearance_menu = ctk.CTkOptionMenu(settings_window, values=['Dark', 'System', 'Light'])
        elif appearance == 'light':
            appearance_menu = ctk.CTkOptionMenu(settings_window, values=['Light', 'System', 'Dark'])

        if ctk_theme == 'blue':
            ctk_theme_menu = ctk.CTkOptionMenu(settings_window, values=['Blue', 'Dark Blue', 'Green', 'Red', 'Yellow', 'Pink', 'Marsh', 'Custom'])
        elif ctk_theme == 'dark-blue':
            ctk_theme_menu = ctk.CTkOptionMenu(settings_window, values=['Dark Blue', 'Blue', 'Green', 'Red', 'Yellow', 'Pink', 'Marsh',  'Custom'])
        elif ctk_theme == 'green':
            ctk_theme_menu = ctk.CTkOptionMenu(settings_window, values=['Green', 'Blue', 'Dark Blue', 'Red', 'Yellow', 'Pink', 'Marsh',  'Custom'])
        elif ctk_theme == 'custom':
            ctk_theme_menu = ctk.CTkOptionMenu(settings_window, values=['Custom', 'Blue', 'Dark Blue', 'Green', 'Red', 'Yellow', 'Pink', 'Marsh'])
        elif ctk_theme == 'red':
            ctk_theme_menu = ctk.CTkOptionMenu(settings_window, values=['Red', 'Blue', 'Dark Blue', 'Green', 'Yellow', 'Pink', 'Marsh', 'Custom'])
        elif ctk_theme == 'yellow':
            ctk_theme_menu = ctk.CTkOptionMenu(settings_window, values=['Yellow',' Blue', 'Dark Blue', 'Green', 'Red', 'Pink', 'Marsh', 'Custom'])
        elif ctk_theme == 'pink':
            ctk_theme_menu = ctk.CTkOptionMenu(settings_window, values=['Pink', 'Blue', 'Dark Blue', 'Green', 'Red', 'Yellow', 'Marsh', 'Custom'])
        elif ctk_theme == 'marsh':
            ctk_theme_menu = ctk.CTkOptionMenu(settings_window, values=['Marsh', 'Blue', 'Dark Blue', 'Green', 'Red', 'Yellow', 'Pink', 'Custom'])
        
        if update_notif == 'True':
            update_prompt_checkbox.select()
        elif update_notif == 'False':
            update_prompt_checkbox.deselect()               


        #place widgets
        default_output_text.place(relx=0.5, rely=0.04, anchor=ctk.CENTER)
        default_output_folder_entry.place(relx=0.5, rely=0.1, anchor=ctk.CENTER)
        default_output_folder_picker_button.place(relx=0.9, rely=0.1, anchor=ctk.CENTER)

        default_format_text.place(relx=0.5, rely=0.18, anchor=ctk.CENTER)
        default_format_menu.place(relx=0.5, rely=0.24, anchor=ctk.CENTER)

        appearance_text.place(relx=0.5, rely=0.32, anchor=ctk.CENTER)
        appearance_menu.place(relx=0.5, rely=0.38, anchor=ctk.CENTER)

        ctk_theme_text.place(relx=0.5, rely=0.46, anchor=ctk.CENTER)
        ctk_theme_menu.place(relx=0.5, rely=0.52, anchor=ctk.CENTER)
        ctk_theme_entry.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)
        ctk_theme_picker.place(relx=0.9, rely=0.6, anchor=ctk.CENTER)

        update_prompt_label.place(relx=0.5, rely=0.68, anchor=ctk.CENTER)
        update_prompt_checkbox.place(relx=0.535, rely=0.74, anchor=ctk.CENTER)

        save_settings_button.place(relx=0.5, rely=0.92, anchor=ctk.CENTER)
        
    else:
        settings_window.lift()
        settings_window.focus_force()




frame=ctk.CTkFrame(app, width=600, height=320)
frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

url_entry = ctk.CTkEntry(app, placeholder_text='URL', width=520)
download_button = ctk.CTkButton(app, text="Download", command=download_button_command)

settings_button = ctk.CTkButton(app, text="", image=settings_img, width=32, height=32, command=open_settings)
#info_button = ctk.CTkButton(app, text="", image=settings_img, width=32, height=32)


def use_default_output():
    if default_output_button.get() == 0:
        output_folder_entry.configure(state='normal')
    else:
        output_folder_entry.delete(0, ctk.END)
        output_folder_entry.insert(0, default_output_dir)
        output_folder_entry.configure(state='disabled')
        
def file_dialog_current_output():
    file_path = ctk.filedialog.askdirectory()
    if file_path:
        output_folder_entry.delete(0, ctk.END)
        output_folder_entry.insert(0, file_path)


default_output_button = ctk.CTkCheckBox(app, text='Use Default', command=use_default_output)
output_folder_entry = ctk.CTkEntry(app, placeholder_text='Output Folder', width=200)
output_folder_picker_button = ctk.CTkButton(app, text="", image=folder_img, width=32, height=32, command=file_dialog_current_output)

if default_format == 'mp3':
    format_menu = ctk.CTkOptionMenu(app, values=['mp3', 'mp4'])
elif default_format == 'mp4':
    format_menu = ctk.CTkOptionMenu(app, values=['mp4', 'mp3'])

resolution_menu = ctk.CTkOptionMenu(app, values=['Best Resolution', '8K', '4K', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'])
audio_quality_menu = ctk.CTkOptionMenu(app, values=['Best Audio'])

url_entry.bind("<Control-a>", select_all)
output_folder_entry.bind("<Control-a>", select_all)

progressbar = ctk.CTkProgressBar(app, orientation="horizontal", mode='determinate', width=520, indeterminate_speed=1)
precentage_label = ctk.CTkLabel(app, text='Not Downloading')

url_entry.place(relx=0.5, rely=0.13, anchor=ctk.CENTER)
format_menu.place(relx=0.25, rely=0.25, anchor=ctk.CENTER)
resolution_menu.place(relx=0.5, rely=0.25, anchor=ctk.CENTER)
audio_quality_menu.place(relx=0.75, rely=0.25, anchor=ctk.CENTER)
precentage_label.place(relx=0.5, rely=0.35, anchor=ctk.CENTER)
progressbar.place(relx=0.5, rely=0.42, anchor=ctk.CENTER)
download_button.place(relx=0.75, rely=0.87, anchor=ctk.CENTER)
#info_button.place(relx=0.92, rely=0.73, anchor=ctk.CENTER)
settings_button.place(relx=0.92, rely=0.87, anchor=ctk.CENTER)
output_folder_entry.place(relx=0.22, rely=0.87, anchor=ctk.CENTER)
output_folder_picker_button.place(relx=0.42, rely=0.87, anchor=ctk.CENTER)
default_output_button.place(relx=0.145, rely=0.77, anchor=ctk.CENTER)

if outdated and update_notif == 'True':
    update_msgbox()

app.mainloop()