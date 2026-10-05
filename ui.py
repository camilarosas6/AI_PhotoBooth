import threading
import customtkinter as ctk
from pathlib import Path
from io import BytesIO
from camera import Camera
from openai_client import OpenAIClient

try:
    from PIL import Image, ImageEnhance
except ImportError:
    Image = None
    ImageEnhance = None
# Colores
BACKGROUND = "#111111"
CARD = "#1E1E1E"
CARD_HOVER = "#252525"

RED = "#C1121F"
RED_HOVER = "#E63946"

WHITE = "#F5F5F5"
GRAY = "#AFAFAF"

BORDER = "#444444"

CURTAIN_DARK = "#8B0D16"
CURTAIN_LIGHT = "#D51A28"
CURTAIN_SHADOW = "#5E080F"

GOLD="#D4AF37"

BUTTON_TEXT = "TOMAR FOTO"

class PhotoBoothApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.camera = Camera("192.168.1.116") # Replace with your camera's IP address
        self.openai_client = OpenAIClient()

        self.title("AI Photo Booth")
        self.geometry("1000x850")
        self.minsize(900, 760)

        self.create_title()

        self.selected_style = None
        self.style_buttons = {}

        self.create_layout()

        self.configure(fg_color=BACKGROUND)

    def select_style(self, style):
        self.selected_style = style

        for name, button in self.style_buttons.items():
            if name == style:
                button.configure(
                    fg_color="#C1121F",
                    border_color="#FFFFFF",
                    border_width=3
                )
            else:
                button.configure(
                    fg_color="#2A2A2A",
                    border_color="#555555"
                )
        print(f"Selected. style: {style}")

    def start_capture(self):

        if self.selected_style is None:
            self.style_label.configure (
                text = "CHOOSE A STYLE FIRST",
                text_color = RED
            )

            self.after (
                1500,
                lambda: self.style_label.configure (
                    text = "CHOOSE STYLE",
                    text_color = WHITE
                )
            )

            return

        # Evitar presionar varias veces
        self.capture_button.configure(state="disabled")

        self.countdown = 3
        self.show_countdown()

    def show_countdown(self):
        if self.countdown > 0:
            self.camera_label.configure(
                text=str(self.countdown),
                font=("Arial", 90, "bold"),
                text_color=WHITE
            )

            self.countdown -= 1
            self.after(800, self.show_countdown)

        else:
            self.take_photo()

    def take_photo(self):
        self.camera_label.configure(
            text="",
            fg_color=WHITE
        )

        self.after(
            150, self.capture_camera_photo
        )

    def capture_camera_photo(self):
        try:
            image_data = self.camera.get_snapshot()

            image = Image.open(BytesIO(image_data))
            self.original_photo = image.copy()
            

            image.thumbnail((800, 250), Image.Resampling.LANCZOS)

            self.camera_photo = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=image.size,
            )

            self.camera_label.configure(
                image=self.camera_photo,
                text=""
            )

            self.after (
                500,
                self.start_ai_generation
            )

        except Exception as error:
            print(f"Failed to capture photo: {error}")

            self.camera_label.configure(
                text = "CAMERA ERROR",
                image = None,
                font = ("Arial", 30, "bold"),
                text_color = RED
            )

            self.capture_button.configure(state="normal")

    def show_photo(self):
        self.camera_label.configure(
            fg_color= CARD
        )

        self.camera_label.configure(
            text="PHOTO TAKEN!",
            font=("Arial", 30, "bold"),
            text_color=WHITE
        )

        self.after(
            150, self.show_polarid
        )

    def show_polarid(self):

        self.polaroid = ctk.CTkFrame(
            self,
            width = 360,
            height = 430,
            fg_color = "#F5F5F5",
            border_width = 1,
            border_color = "#D8D8D8",
            corner_radius = 6
        )

        self.polaroid.place(
            relx = 0.5,
            rely = 1.2,
            anchor = "center"
        )

        self.polaroid_img_frame = ctk.CTkFrame(
            self.polaroid,
            width = 320,
            height = 320,
            fg_color = "#222222",
            border_width = 2,
            border_color = "#D8D8D8",
            corner_radius = 2
        )

        self.polaroid_img_frame.place(
            relx=0.5,
            rely=0.43,
            anchor="center"
        )

        self.polaroid_img = ctk.CTkLabel(
            self.polaroid_img_frame,
            text="",
        )

        self.polaroid_img.pack(
            fill="both",
            expand=True
        )

        self.polaroid_text = ctk.CTkLabel(
            self.polaroid,
            text="AI PHOTO BOOTH",
            font=("Arial", 18, "bold"),
            text_color="#222222",
        )
        self.polaroid_text.place(
            relx = 0.5,
            rely = 0.88,
            anchor = "center"
        )

        self.load_test_image()
        self.animate_polaroid()

    def load_test_image(self):
        if Image is None or ImageEnhance is None:
            self.polaroid_img.configure(text="PHOTO TAKEN", text_color=WHITE)
            self.polaroid_text.configure(text="PILLOW IS REQUIRED FOR PHOTO PREVIEW")
            self.after(2000, lambda: self.capture_button.configure(state="normal"))
            return

        image_path = Path(__file__).parent / "assets" / "test_photo.jpeg"
        image = Image.open(image_path)

        image.thumbnail((300, 300), Image.Resampling.LANCZOS)

        self.original_image = image
        self.update_reveal(0)

    def update_reveal(self, step):
        if step > 10:
            self.polaroid_text.configure(text="AI PHOTO BOOTH")
            self.capture_button.configure(state="normal")
            return

        brightness = 0.15 + (step / 10) * 0.85

        revealed = ImageEnhance.Brightness(self.original_image).enhance(brightness)

        self.polaroid_photo = ctk.CTkImage(
            light_image=revealed,
            dark_image=revealed,
            size=revealed.size,
        )

        self.polaroid_img.configure(image=self.polaroid_photo)

        self.polaroid_text.configure(text="DEVELOPING ...")

        self.after(180, lambda: self.update_reveal(step + 1))

    def animate_polaroid(self):
        self.polaroid_y = 1.2
        self.move_polaroid()

    def move_polaroid(self):
        self.polaroid_y -= 0.04

        if self.polaroid_y > 0.5:
            self.polaroid.place(
                relx=0.5,
                rely=self.polaroid_y,
                anchor="center"
            )

            self.after(
                20,
                self.move_polaroid
            )

        else:
            self.polaroid.place(
                relx=0.5,
                rely=0.5,
                anchor="center"
            )

    def generate_ai_photo(self):
        try:
            print(
                f"Generating image with style: "
                f"{self.select_style}"
            )

            image_data = self.openai_client.generate_img(
                self.original_photo,
                self.select_style
            )

            self.after (
                0, lambda: self.show_generated_photo(image_data)
            )

        except Exception as error:
            print(f"OpenAI error: {error}")

            self.after(
                0, self.show_generation_error
            )

    def start_ai_generation(self):
        thread = threading.Thread(
            target=self.generate_ai_photo,
            daemon=True
        )

        thread.start()

    def show_generating(self):
        self.camera_label.configure(
            text = "GENERATING IMAGE ...",
            image = None,
            text_color = WHITE
        )

    def show_generated_photo(self, image_data):
        image = Image.open(
            BytesIO(image_data)
        )

        self.generated_photo = image.copy()
        self.show_polarid()

    def show_generation_error(self):
        self.camera_label.configure(
            text = "GENERATION ERROR",
            image = None,
            text_color = RED
        )

        self.capture_button.configure(state = "normal")


    def create_title(self):

        self.title_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.title_frame.pack(
            fill="x",
            pady=(10, 10)
        )

        # linea superior
        self.top_line = ctk.CTkFrame(
            self.title_frame,
            fg_color=RED,
            height=4,
            corner_radius=2
        )

        self.top_line.pack(
            fill="x",
            padx=40
        )

        # Titulo
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="AI PHOTO BOOTH",
            font=("Super Funky", 60),
            text_color=WHITE
        )

        self.title_label.pack(
            pady=10
        )

        # Linea inferior
        self.bottom_line = ctk.CTkFrame(
            self.title_frame,
            fg_color=RED,
            height=4,
            corner_radius=2
        )

        self.bottom_line.pack(
            fill="x",
            padx=40
        )

    def create_layout(self):

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=(10,30)
        )

        # ------ Cámara ------

        self.camera_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD,
            corner_radius=20,
            height=280
        )

        self.camera_frame.pack_propagate(False)

        self.camera_frame.pack(
            fill="x",
            pady=5,
            padx=20
        )

        self.camera_label = ctk.CTkLabel(
            self.camera_frame,
            text="CAMERA PREVIEW",
            font=("Arial", 30, "bold"),
            text_color=GRAY
        )

        self.camera_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        self.button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.button_frame.pack(fill="x", pady=10)

        self.capture_button = ctk.CTkButton(
            self.button_frame,
            text="TAKE PIC",
            font=("Anton", 24),
            fg_color=RED,
            hover_color=RED_HOVER,
            text_color=WHITE,
            width=320,
            height=75,
            corner_radius=18,
            border_width=2,
            border_color=WHITE,
            command = self.start_capture
        )

        self.capture_button.pack()

        self.result_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD,
            corner_radius=20,
            height=160
        )

        self.result_frame.pack(
            fill="x",
            pady=(5,0)
            )

        self.style_label = ctk.CTkLabel(
            self.result_frame,
            text="CHOOSE STYLE",
            font=("Arial", 20, "bold"),
            text_color=WHITE
        )

        self.style_label.pack(pady=20)

        self.style_frame = ctk.CTkFrame(
            self.result_frame,
            fg_color="transparent"
        )

        self.style_frame.pack(
            pady=5
        )

        styles = [
            "PIXAR",
            "ANIME",
            "SCRIBBLE",
            "CYBERPUNK"
        ]

        row = 0
        col = 0

        for style in styles:
            button = ctk.CTkButton(
                self.style_frame,
                text=style,
                width=160,
                height=55,
                corner_radius=15,
                fg_color="#2A2A2A",
                hover_color=RED,
                border_width=2,
                border_color="#555555",
                text_color=WHITE,
                command=lambda s=style: self.select_style(s)
            )

            self.style_buttons[style] = button

            button.grid(
                row=row,
                column=col,
                padx=10,
                pady=8
            )

            col += 1

            if col == 2:
                col = 0
                row += 1
