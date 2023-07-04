import json
import os
import threading
from tkinter import END, Listbox, StringVar, Tk
from tkinter.filedialog import askdirectory
from tkinter.ttk import Button, Entry, Frame, Label, OptionMenu
from typing import Callable

from services.videomodel import YtVideo
from services.yt import YoutubeDownloader


class MainApp(Tk):
    def __init__(self, icon=None, ffmpeg_path = None, *args, **kwargs):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("500x500")
        self.resizable(False, False)

        if icon:
            self.iconbitmap(icon)

        self.downloader = YoutubeDownloader(ffmpeg_path=ffmpeg_path)

        self.search_term = ""
        self.download_location = ""

        self.is_searching = False

        self.config_widget = ConfigWidget(self)
        self.config_widget.pack(fill="x", padx=10, pady=2)

        self.url_download = UrlDownloadWidget(self, self.download_url)
        self.url_download.pack(fill="x", padx=10, pady=2)

        self.download_location = self.config_widget.get_download_location()

        self.search_frame = SearchWidget(self, self.search, self.download)
        self.search_frame.pack(fill="x", padx=10, pady=2)

        self.result_box = ResultsWidget(self)
        self.result_box.pack(fill="both", expand=True, padx=10, pady=2)

        self.bottom_info_frame = BottomInfoWidget(self)
        self.bottom_info_frame.pack(fill="x", padx=10, pady=10)

    def search(self, query):
        if self.is_searching:
            return
        self.is_searching = True
        self.search_frame.desable_search()
        if len(query) == 0:
            return
        self.search_term = query
        thread = threading.Thread(target=self.search_yt_thread, args=(query,))
        thread.start()

    def search_yt_thread(self, query):
        try:
            videos = self.downloader.search(query)
        except Exception as e:
            self.bottom_info_frame.show_error(str(e))
            self.is_searching = False
            self.search_frame.enable_search()
            return
        self.result_box.update_results(videos)
        self.is_searching = False
        self.search_frame.enable_search()

    def download(self):
        location = self.config_widget.get_download_location()
        format = self.config_widget.get_format()
        path = os.path.join(location, self.search_term)

        videos = self.result_box.get_selected()
        self.result_box.deselect_all()

        if len(videos) == 0:
            return

        urls = [video.url for video in videos]

        thread = threading.Thread(
            target=self.download_thread,
            args=(urls, path, format, self.bottom_info_frame.show_progress),
        )

        thread.start()

    def download_url(self, url):
        download_folder = "URL Downloads"
        location = self.config_widget.get_download_location()
        format = self.config_widget.get_format()
        path = os.path.join(location, download_folder)

        thread = threading.Thread(
            target=self.download_thread,
            args=([url], path, format, self.bottom_info_frame.show_progress),
        )

        thread.start()

    def download_thread(self, urls: list[str], location, format, hook):
        try:
            if format == "mp3":
                self.downloader.download_audio_url(urls, location, hook)
            else:
                self.downloader.download_video_url(urls, location, hook)
            self.bottom_info_frame.show_finished()
        except Exception as e:
            self.bottom_info_frame.show_error(str(e))

    def run(self):
        self.mainloop()


class DownloadLocationWidget(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.download_location = os.path.expanduser("~/Downloads")
        self.label = Label(self, text="Folder: ")
        self.label.pack(side="left")
        self.location_label = Label(self, text=os.path.basename(self.download_location))
        self.location_label.pack(side="left")
        self.change_button = Button(
            self, text="Change", command=self.change_download_location
        )
        self.change_button.pack(side="right")

    def change_download_location(self):
        self.download_location = askdirectory() or self.download_location
        self.location_label.config(text=os.path.basename(self.download_location))


    def get_download_location(self):
        return os.path.join(self.download_location, "YTDownloader")




class FormatWidget(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        options = ["mp3", "mp4"]
        self.format = StringVar(self)
        self.format.set(options[0])
        self.label = Label(self, text="Format: ")
        self.label.pack(side="left")
        self.format_menu = OptionMenu(self, self.format,"mp3", *options)
        self.format_menu.pack(side="left")

    def get_format(self):
        return self.format.get()

class ConfigWidget(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.set_download_location = DownloadLocationWidget(self, width = 30) #width = 3
        self.set_download_location.pack(side="left",fill="x")
        self.set_format = FormatWidget(self)
        self.set_format.pack(side="right", fill="x")

    def get_download_location(self):
        return self.set_download_location.get_download_location()
    def get_format(self):
        return self.set_format.get_format()


class UrlDownloadWidget(Frame):
    def __init__(self, parent, on_download: Callable[[str], None], *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.url_label = Label(self, text="URL: ")
        self.url_label.pack(side="left")

        self.url_entry = Entry(self)
        self.url_entry.pack(side="left", fill="x", expand=True)

        self.on_download = on_download
        self.download_button = Button(self, text="Download", command=self.download)
        self.download_button.pack(side="right")

    def download(self):
        url = self.url_entry.get()
        self.url_entry.delete(0, END)
        if len(url) == 0:
            return
        self.on_download(url)

class SearchWidget(Frame):
    def __init__(self, parent, on_search, on_download, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.search_label = Label(self, text="Search: ")
        self.search_label.pack(side="left")
        self.search_entry = Entry(self)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.download_button = Button(self, text="Download", command=on_download)
        self.download_button.pack(side="right")

        self.search_button = Button(
            self, text="Search", command=lambda: on_search(self.search_entry.get())
        )
        self.search_button.pack(side="right")
        self.search_entry.bind(
            "<Return>", lambda event: on_search(self.search_entry.get())
        )

    def desable_search(self):
        self.search_button["state"] = "disabled"

    def enable_search(self):
        self.search_button["state"] = "normal"


class ResultsWidget(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.current_videos = {}

        self.control_frame = Frame(self)
        self.control_frame.pack(fill="x")

        self.select_all_button = Button(
            self.control_frame,
            text="Select All",
            command=self.select_all,
        )
        self.select_all_button.pack(side="left")

        self.deselect_all_button = Button(
            self.control_frame,
            text="Deselect All",
            command=self.deselect_all,
        )
        self.deselect_all_button.pack(side="left")
        self.results_listbox = Listbox(self, selectmode="multiple", font=("Arial", 12))
        self.results_listbox.pack(fill="both", expand=True, padx=10, pady=5)

    def select_all(self):
        self.results_listbox.select_set(0, "end")

    def deselect_all(self):
        self.results_listbox.selection_clear(0, "end")

    def get_selected(self) -> list[YtVideo]:
        selections = self.results_listbox.curselection()
        return [self.current_videos[self.results_listbox.get(i)] for i in selections]

    def update_results(self, videos: list[YtVideo]):
        self.results_listbox.delete(0, "end")
        self.current_videos = {}
        for video in videos:
            self.results_listbox.insert("end", video.title)
            self.current_videos[video.title] = video


class BottomInfoWidget(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.download_label = Label(self, text="Downloading: None")
        self.download_label.pack(fill="x", expand=True)
        self.download_info = Label(self, text="")
        self.download_info.pack(fill="x", expand=True)

    def show_progress(self, progress):
        filename = progress["filename"]
        title = os.path.basename(filename)
        self.download_label["text"] = f"Downloading: {title}"
        if progress["status"] == "finished":
            self.download_label["text"] = f"Processing: {title}"
            return
        speed = progress.get("speed") or 0
        downloaded = progress.get("downloaded_bytes") or 0
        total = progress.get("total_bytes") or  progress.get("total_bytes_estimate") or 0
        frag_idx = progress.get("fragment_index") or 0
        frag_count = progress.get("fragment_count") or 0
        percent = downloaded / total * 100 if total > 0 else 0
        eta = progress.get("eta") or 0
        # self.download_info["text"] = f"{percent:.2f}% at {speed:.2f} kb/s {eta}s"
        if frag_count > 1:
            text = f"{percent:.2f} at {speed:.2f} kb/s {eta}s frag: {frag_idx}/{frag_count}"
        else:
            text = f"{percent:.2f}% at {speed:.2f} kb/s {eta}s"
        self.download_info["text"] = text

    def show_finished(self):
        self.download_label["text"] = f"Download Finished"
        self.download_info["text"] = ""

    def show_error(self, error):
        self.download_label["text"] = f"Error: {error}"
        self.download_info["text"] = ""


def test():
    app = MainApp()
    app.run()
    os._exit(0)


if __name__ == "__main__":
    test()
