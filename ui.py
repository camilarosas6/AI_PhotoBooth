import customtkinter as ctk
# ===== Colores =====
BACKGROUND = "#111111"
CARD = "#1E1E1E"
CARD_HOVER = "#252525"

RED = "#C1121F"
RED_HOVER = "#E63946"

WHITE = "#F5F5F5"
GRAY = "#AFAFAF"

BORDER = "#444444"

BUTTON_TEXT = "TOMAR FOTO"

class PhotoBoothApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AI Photo Booth")
        self.geometry("900x700")

        self.create_title()

        self.selected_style = None
        self.style_buttons = {}

        self.create_layout()

    def select_style(self, style):
        self.selected_style = style

        for name, button in self.style_buttons.items():
            if name == style:
                button.configure(
                    fg_color="#C1121F",
                    border_color="#FFFFFF"
                )
            else:
                button.configure(
                    fg_color="#2A2A2A",
                    border_color="#555555"
                )
        print(f"Selected. style: {style}")

    def create_title(self):

        self.titleLabel = ctk.CTkLabel(
            self, 
            text="AI PHOTO BOOTH",
            font=("Arial", 60, "bold"),
            text_color=WHITE
        )

        self.titleLabel.pack(pady=(20,25))

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

        self.top_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="transparent"
        )

        self.top_frame.pack(fill="x")

        # ------ Cámara ------

        self.camera_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD,
            corner_radius=20,
            height=300
        )

        self.camera_frame.pack_propagate(False)

        self.camera_frame.pack(
            fill="x", 
            pady=20,
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

        self.button_frame.pack(fill="x", pady=25)

        self.capture_button = ctk.CTkButton(
            self.button_frame,
            text="TAKE PIC",
            font=("Arial", 24, "bold"),
            fg_color=RED,
            hover_color=RED_HOVER,
            text_color=WHITE,
            width=300,
            height=70,
            corner_radius=20
        )

        self.capture_button.pack()

        self.result_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color=CARD,
            corner_radius=20,
            height=250
        )

        self.result_frame.pack(
            fill="both",
            expand=True,
            pady=(10,0)
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
            pady=10
        )

        styles = [
            "PIXAR",
            "ANIME",
            "SCRIBBLE",
            "CYBERPUNK"
        ]

        for style in styles:
            button = ctk.CTkButton(
                self.style_frame,
                text=style,
                width=130,
                height=45,
                corner_radius=15,
                fg_color="#2A2A2A",
                hover_color="#C1121F",
                border_width=2,
                border_color="#555555",
                text_color=WHITE,
                command=lambda s=style: self.select_style(s)
            )

            self.style_buttons[style] = button

            button.pack(
                side="left",
                padx=10
            )