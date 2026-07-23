import customtkinter as ctk # pyright: ignore[reportMissingImports]

from ui import PhotoBoothApp 

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = PhotoBoothApp()
app.mainloop()