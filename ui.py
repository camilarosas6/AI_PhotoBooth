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

CURTAIN_DARK = "#8B0D16"
CURTAIN_LIGHT = "#D51A28"
CURTAIN_SHADOW = "#5E080F"

GOLD="#D4AF37"

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

        self.create_curtains()

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
            border_color=WHITE
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

    def create_curtains(self):

        # ===== Cortina izquierda =====

        self.left_curtain = ctk.CTkFrame(
            self,
            fg_color=RED,
            corner_radius=0
        )

        self.left_curtain.place(
            relx=0,
            rely=0,
            relwidth=0.5,
            relheight=1
        )

        # ===== Cortina derecha =====

        self.right_curtain = ctk.CTkFrame(
            self,
            fg_color=RED,
            corner_radius=0
        )

        self.right_curtain.place(
            relx=0.5,
            rely=0,
            relwidth=0.5,
            relheight=1
        )

        # ===== Pliegues =====

        self.left_folds = []
        self.right_folds = []

        for i in range(10):

            if i % 2 == 0:
                fold_color = CURTAIN_DARK
            else:
                fold_color = CURTAIN_SHADOW

            left_fold = ctk.CTkFrame(
                self.left_curtain,
                fg_color=fold_color,
                corner_radius=0,
                width=8
            )

            right_fold = ctk.CTkFrame(
                self.right_curtain,
                fg_color=fold_color,
                corner_radius=0,
                width=8
            )

            self.left_folds.append(left_fold)
            self.right_folds.append(right_fold)

        # ===== Parte superior =====

        self.curtain_top = ctk.CTkFrame(
            self,
            fg_color=CURTAIN_DARK,
            corner_radius=0,
            height=35
        )

        self.curtain_top.place(
            relx=0,
            rely=0,
            relwidth=1
        )

        # ===== Amarres =====

        self.left_tie = ctk.CTkFrame(
            self,
            fg_color=GOLD,
            corner_radius=10,
            width=12,
            height=90
        )

        self.right_tie = ctk.CTkFrame(
            self,
            fg_color=GOLD,
            corner_radius=10,
            width=12,
            height=90
        )

        self.left_tie.place(
            relx=0.02,
            rely=0.55,
            anchor="w"
        )

        self.right_tie.place(
            relx=0.98,
            rely=0.55,
            anchor="e"
        )

        # ===== Posición inicial =====

        self.curtain_progress = 0

        self.after(500, self.animate_curtains)

    def animate_curtains(self):

        self.curtain_progress += 0.025

        if self.curtain_progress <= 1:

            # ===== Movimiento suave =====

            ease = 1 - (1 - self.curtain_progress) ** 3

            # Ancho de las cortinas
            curtain_width = 0.5 * (1 - ease)

            # ===== CORTINA IZQUIERDA =====

            self.left_curtain.place(
                relx=0,
                rely=0,
                relwidth=curtain_width,
                relheight=1
            )

            # ===== CORTINA DERECHA =====

            self.right_curtain.place(
                relx=1 - curtain_width,
                rely=0,
                relwidth=curtain_width,
                relheight=1
            )

            # ===== PLIEGUES IZQUIERDOS =====

            for i, fold in enumerate(self.left_folds):

                # Posición normal del pliegue
                normal_position = (i + 1) / 11

                # Conforme la cortina se abre,
                # los pliegues se concentran en el extremo
                compressed_position = normal_position * (1 - ease)

                fold.place(
                    relx=compressed_position,
                    rely=0,
                    relheight=1,
                    anchor="n"
                )

            # ===== PLIEGUES DERECHOS =====

            for i, fold in enumerate(self.right_folds):

                normal_position = (i + 1) / 11

                compressed_position = normal_position * (1 - ease)

                fold.place(
                    relx=1 - compressed_position,
                    rely=0,
                    relheight=1,
                    anchor="n"
                )

            self.after(20, self.animate_curtains)

        else:

            # ===== POSICIÓN FINAL =====

            self.left_curtain.place(
                relx=0,
                rely=0,
                relwidth=0.045,
                relheight=1
            )

            self.right_curtain.place(
                relx=0.955,
                rely=0,
                relwidth=0.045,
                relheight=1
            )

            # Ocultar barra superior
            self.curtain_top.place_forget()