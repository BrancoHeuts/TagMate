from os import path
import json
import tkinter
import tkinter.messagebox
import customtkinter
from tkhtmlview import HTMLLabel

# GUI based on: https://github.com/TomSchimansky/CustomTkinter

abs_path = path.abspath(path.dirname(__file__))
with open(path.join(abs_path, f'../data/custom_genres.json')) as json_file:
    CUSTOM_GENRES = json.load(json_file)

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class GenreSelectionGUI(customtkinter.CTk):
    WIDTH = 1000
    HEIGHT = 500

    def on_closing(self, event=0):
        self.destroy()

    def __init__(self, track, preview_url, library):
        super().__init__()

        self.title("")
        self.geometry(f"{GenreSelectionGUI.WIDTH}x{GenreSelectionGUI.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed
        self.wm_attributes("-topmost", "True")
        self.wm_attributes("-toolwindow", "True")
        self.track = track
        self.library = library
        self.picked_genre = ""
        self.preview_url = ""

        if preview_url:
            self.preview_url = preview_url
            preview = "Preview"
        else:
            preview = "No preview"

        def button_clicked(i):
            self.picked_genre = i
            self.on_closing()

        def button_clicked_entry():
            self.picked_genre = self.entry.get()
            self.on_closing()

        # ------ create two frames ------

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ------ frame left ------

        # ------ Custom genre list ------
        self.frame_left.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Custom genre list",
                                              font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=1, pady=10, padx=10)

        for lib in CUSTOM_GENRES:
            if lib == self.library:
                column_grid_n = 0
                for i in CUSTOM_GENRES[lib]:
                    custom_genre_list = CUSTOM_GENRES[lib][i]
                    column_grid_n += 1

                    row_grid_n = 2
                    button_list = []
                    for genre in custom_genre_list:
                        button = customtkinter.CTkButton(master=self.frame_left,
                                                         text=f"{genre}", width=15,
                                                         command=lambda x=genre: button_clicked(x))
                        button.grid(row=row_grid_n, column=column_grid_n, pady=10, padx=20)
                        row_grid_n += 1
                        button_list.append(button)

        # ------ frame right ------

        # configure grid layout (3x7)
        self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=0)

        self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_info.grid(row=0, column=0, columnspan=2, rowspan=4, pady=20, padx=20, sticky="nsew")

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            width=120,
                                            placeholder_text="Pick a genre")
        self.entry.grid(row=8, column=0, columnspan=1, pady=20, padx=20, sticky="we")

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Add genre",
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=button_clicked_entry)
        self.button_5.grid(row=8, column=1, columnspan=1, pady=20, padx=20, sticky="we")

        # ------ frame info ------

        # configure grid layout (1x1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)

        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text=f"{self.track}",
                                                   height=100,
                                                   corner_radius=6,  # <- custom corner radius
                                                   fg_color=("white", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.LEFT)
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)

        self.label_info_2 = HTMLLabel(master=self.frame_info,
                                      html=f'<a style="color:white; font-family: courier ; font-size: 80%" href="{self.preview_url}"> {preview} </a>',
                                      height=5, background="gray38")
        self.label_info_2.grid(column=0, row=1, sticky="nwe", padx=15, pady=15)

        self.mainloop()
