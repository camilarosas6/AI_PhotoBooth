import threading
import customtkinter as ctk
from tkinter import filedialog
from io import BytesIO
from camera import Camera
from openai_client import OpenAIClient

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
except ImportError:
    Image = None,
    ImageEnhance = None,
    ImageFilter = None,
    ImageOps = None

# Colores
BACKGROUND = "#111111"
CARD = "#1E1E1E"
CARD_HOVER = "#252525"

RED = "#C1121F"
RED_HOVER = "#E63946"

WHITE = "#F5F5F5"
GRAY = "#AFAFAF"

BORDER = "#444444"

GOLD = "#D4AF37"

BUTTON_TEXT = "TOMAR FOTO"


class PhotoBoothApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.camera = Camera("192.168.1.116")
        self.openai_client = None

        self.original_photo = None
        self.generated_photo = None
        self.camera_photo = None
        self.polaroid_img = None

        self.selected_style = None
        self.style_buttons = {}
        self.countdown = 3

        self.title("AI Photo Booth")
        # iniciar en pantalla completa
        self.attributes("-fullscreen", True)
        # Esc para salir de pantalla completa
        self.bind(
            "<Escape>",
            lambda event: self.attributes("-fullscreen", False)
        )
        # F11 alternar pantalla completa
        self.bind(
            "<F11>",
            lambda event: self.attributes(
                "-fullscreen",
                not self.attributes("-fullscreen")
            )
        )
        self.configure(fg_color=BACKGROUND)

        self.create_title()
        self.create_layout()

    # -----------------------------------------
    # SELECCIÓN DE ESTILO
    # -----------------------------------------

    def select_style(self, style):
        self.selected_style = style

        for name, button in self.style_buttons.items():
            if name == style:
                button.configure(
                    fg_color=RED,
                    border_color=WHITE,
                    border_width=3
                )
            else:
                button.configure(
                    fg_color="#2A2A2A",
                    border_color="#555555",
                    border_width=2
                )

        self.style_label.configure(
            text=f"SELECTED STYLE: {style}",
            text_color=WHITE
        )

        print(f"Selected style: {style}")


    # CAPTURAR FOTO CON LA XIAO


    def start_capture(self):

        self.set_controls_state("disabled")

        self.countdown = 3
        self.show_countdown()

    def show_countdown(self):

        if self.countdown > 0:
            self.camera_label.configure(
                image=None,
                text=str(self.countdown),
                font=("Arial", 90, "bold"),
                text_color=WHITE,
                fg_color=CARD
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

        self.after(150, self.capture_camera_photo)

    def capture_camera_photo(self):

        try:
            if Image is None:
                raise ImportError(
                    "Pillow no está instalado."
                )

            print("Capturando foto desde la XIAO...")

            image_data = self.camera.get_snapshot()

            image = Image.open(
                BytesIO(image_data)
            ).convert("RGB")

            self.original_photo = image.copy()
            print("Foto original de la XIAO", image.size)
            print("Tipo de original_photo", type(self.original_photo))

            self.display_preview(image)

            self.style_label.configure(
                text="PHOTO READY - CHOOSE AN ACTION",
                text_color=WHITE
            )

            print("Foto capturada correctamente.")
            print("No se ha llamado a la API.")

        except Exception as error:
            print(f"Camera error: {error}")

            try:
                self.camera_label.configure(
                    image=None,
                    text="CAMERA ERROR",
                    font=("Arial", 30, "bold"),
                    text_color=RED,
                    fg_color=CARD
            )
            except Exception as display_error:
                print(f"Error updating camera label: {display_error}")

        finally:
            self.set_controls_state("normal")

    # CARGAR UNA FOTO DESDE LA COMPUTADORA

    def load_local_photo(self):

        file_path = filedialog.askopenfilename(
            title="Seleccionar una fotografía",
            filetypes=[
                (
                    "Imágenes",
                    "*.png *.jpg *.jpeg *.webp *.bmp"
                ),
                ("Todos los archivos", "*.*")
            ]
        )

        # Si el usuario cancela, no hacemos nada.
        if not file_path:
            return

        try:
            if Image is None:
                raise ImportError(
                    "Pillow no está instalado."
                )

            image = Image.open(
                file_path
            ).convert("RGB")

            self.original_photo = image.copy()

            self.display_preview(image)

            self.style_label.configure(
                text="LOCAL PHOTO LOADED",
                text_color=WHITE
            )

            print(f"Imagen cargada: {file_path}")
            print("La API no ha sido llamada.")
            print("No se han consumido créditos.")

        except Exception as error:
            print(f"Error al cargar la imagen: {error}")

            self.style_label.configure(
                text="ERROR LOADING IMAGE",
                text_color=RED
            )

        finally:
            self.set_controls_state("normal")


    # MOSTRAR LA VISTA PREVIA


    def display_preview(self, image):

        preview = image.copy()
        preview.thumbnail(
            (1000, 650),
            Image.Resampling.LANCZOS
        )
        # crear nueva img sin eliminar la referencia a la imagen anterior
        new_camera_photo = ctk.CTkImage (
            light_image=preview,
            dark_image=preview,
            size=preview.size
        )

        # actualizar etiqueta primero mientras la img anterior tiene una referencia
        self.camera_label.configure (
            image = new_camera_photo,
            text = "",
            fg_color = CARD
        )

        # conservar referencia a la nueva imagen
        self.camera_photo = new_camera_photo

   
    # PROBAR LA POLAROID SIN USAR IA

    def test_without_ai(self):

        if self.original_photo is None:
            self.style_label.configure(
                text="LOAD OR TAKE A PHOTO FIRST",
                text_color=RED
            )
            return

        # Simula el resultado de la generación.
        # No crea ninguna solicitud a OpenAI.
        self.generated_photo = self.original_photo.copy()

        print("Prueba local iniciada.")
        print("Mostrando la imagen original en la Polaroid.")
        print("No se han consumido créditos de la API.")

        self.show_polaroid()

    # -----------------------------------------
    # GENERAR IMAGEN CON OPENAI
    # -----------------------------------------

    def start_ai_generation(self):

        if self.original_photo is None:
            self.style_label.configure(
                text="LOAD OR TAKE A PHOTO FIRST",
                text_color=RED
            )
            return

        if self.selected_style is None:
            self.style_label.configure(
                text="CHOOSE A STYLE FIRST",
                text_color=RED
            )
            return

        # Esta es la única acción que llama a OpenAI.
        self.set_controls_state("disabled")

        self.camera_label.configure(
            image=None,
            text="GENERATING WITH AI...",
            font=("Arial", 28, "bold"),
            text_color=WHITE,
            fg_color=CARD
        )

        self.style_label.configure(
            text=f"GENERATING: {self.selected_style}",
            text_color=GOLD
        )

        thread = threading.Thread(
            target=self.generate_ai_photo,
            daemon=True
        )

        thread.start()

    def generate_ai_photo(self):

        try:
            if self.openai_client is None:
                self.openai_client = OpenAIClient()

            print(
                f"Generating image with style: "
                f"{self.selected_style}"
            )

            # Se conserva el nombre de método de tu código.
            image_data = self.openai_client.generate_img(
                self.original_photo,
                self.selected_style
            )

            self.after(
                0,
                lambda data=image_data:
                    self.show_generated_photo(data)
            )

        except Exception as error:
            print(f"OpenAI error: {error}")

            self.after(
                0,
                self.show_generation_error
            )

    def show_generated_photo(self, image_data):

        try:
            image = Image.open(
                BytesIO(image_data)
            ).convert("RGB")

            print("Tamaño recibido de la IA:", image.size)

            self.generated_photo = image.copy()

            print("Tamaño de generated_photo:", self.generated_photo.size)

            self.set_controls_state("normal")
            self.show_polaroid()

        except Exception as error:
            print(f"Error displaying generated image: {error}")
            self.show_generation_error()

    def show_generation_error(self):

        self.camera_label.configure(
            image=None,
            text="GENERATION ERROR",
            font=("Arial", 30, "bold"),
            text_color=RED,
            fg_color=CARD
        )

        self.style_label.configure(
            text="CHECK THE TERMINAL FOR DETAILS",
            text_color=RED
        )

        self.set_controls_state("normal")

    # -----------------------------------------
    # MOSTRAR LA POLAROID
    # -----------------------------------------

    def show_polaroid(self):

        if self.generated_photo is None:
            return

        # Evita acumular ventanas de resultados.
        if (
            hasattr(self, "polaroid")
            and self.polaroid.winfo_exists()
        ):
            self.polaroid.destroy()

        self.polaroid = ctk.CTkFrame(
            self,
            width=390,
            height=500,
            fg_color="#F5F5F5",
            border_width=1,
            border_color="#D8D8D8",
            corner_radius=6
        )

        self.polaroid.pack_propagate(False)

        self.polaroid.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Marco de la fotografía
        self.polaroid_image_frame = ctk.CTkFrame(
            self.polaroid,
            width=320,
            height=320,
            fg_color="#D0D0D0",
            border_width=2,
            border_color="#D0D0D0",
            corner_radius=2
        )

        self.polaroid_image_frame.pack(
            pady=(20, 10)
        )

        # cuadro inicial: foto sin revelar
        self.polaroid_img_label = ctk.CTkLabel (
            self.polaroid_image_frame,
            text=""
        )
        self.polaroid_img_label.place (
            relx = 0.5,
            rely = 0.5,
            anchor = "center"
        )

        # texto inferior
        self.polaroid_label = ctk.CTkLabel (
            self.polaroid,
            text="DEVELOPING ...",
            font=("Arial", 16, "bold"),
            text_color="#222222"
        )

        self.polaroid_label.pack (
            pady = (5, 12)
        )

        # Boton para cerrar resultado
        self.close_polaroid_button = ctk.CTkButton (
            self.polaroid,
            text = "CLOSE / TRY AGAIN",
            font=("Arial", 14, "bold"),
            fg_color=RED,
            hover_color=RED_HOVER,
            text_color=WHITE,
            width=200,
            height=40,
            command=self.close_polaroid
        )
        self.close_polaroid_button.pack (
            pady=(0, 10)
        )

        # normalizar imagen antes de iniciar la animación
        source_image = self.generated_photo.convert("RGB")

        # Prepara foto en formato cuadrado
        self.reveal_image = ImageOps.fit(
            self.generated_photo.convert("RGB"),
            (316, 316),
            method=Image.Resampling.LANCZOS
            centering=(0.5, 0.5)
        )

        print("Foto para la polaroid: ", self.generated_photo.size)
        
        print("Polaroid creada: ", self.polaroid.winfo_exists())
        print("Tamaño del marco: ", self.polaroid.cget("width"), self.polaroid.cget("height"))
        # Inicia animacion
        self.update_reveal(0)

    def update_reveal (self, step = 0):
        # num total de etapas de la animacion
        total_steps = 12

        # detiene animacion al llegar al final
        if step > total_steps:
            self.polaroid_label.configure(
                text= "AI PHOTO BOOTH"
            )
            return

        #progreso entre 0.0 y 1.0
        progress = step / total_steps

        # img empieza oscura y aumenta luminosidad
        brightness = 0.25 + (0.75 * progress)

        developing_image = ImageEnhance.Brightness (
            self.reveal_image
        ).enhance(brightness)

        # img empieza borrosa y termina nítida
        blur_radius = (1 - progress) * 5

        if blur_radius > 0:
            developing_image = developing_image.filter(
                ImageFilter.GaussianBlur(radius=blur_radius)
            )

        # conserva referencia de img para q tkinter no la elimine de la interfaz
        self.polaroid_img = ctk.CTkImage (
            light_image=developing_image,
            dark_image=developing_image,
            size=(316, 316)
        )

        self.polaroid_img_label.configure(
            image = self.polaroid_img,
            text = ""
        )

        # programa siguiente etapa sin bloquear interfaz
        if step < total_steps:
            self.after (
                150,
                lambda: self.update_reveal(step + 1)
            )
        else:
            self.polaroid_label.configure(
                text = "AI PHOTO BOOTH"
            )

    def close_polaroid(self):

        if (
            hasattr(self, "polaroid")
            and self.polaroid.winfo_exists()
        ):
            self.polaroid.destroy()

    # -----------------------------------------
    # ACTIVAR / DESACTIVAR CONTROLES
    # -----------------------------------------

    def set_controls_state(self, state):

        self.capture_button.configure(state=state)
        self.load_button.configure(state=state)
        self.preview_button.configure(state=state)

        # No se puede generar sin una fotografía cargada.
        if self.original_photo is None:
            self.generate_button.configure(
                state="disabled"
            )
        else:
            self.generate_button.configure(
                state=state
            )

    # -----------------------------------------
    # TÍTULO
    # -----------------------------------------

    def create_title(self):

        self.title_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.title_frame.pack(
            fill="x",
            pady=(10, 10)
        )

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

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="AI PHOTO BOOTH",
            font=("Super Funky", 60),
            text_color=WHITE
        )

        self.title_label.pack(
            pady=10
        )

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

    # INTERFAZ PRINCIPAL

    
    def create_layout(self):

        # Contenedor principal
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(5, 25)
        )

        # Dos columnas: fotografía grande y controles
        self.main_frame.grid_columnconfigure(
            0, weight=3, uniform="content"
        )
        self.main_frame.grid_columnconfigure(
            1, weight=2, uniform="content"
        )
        self.main_frame.grid_rowconfigure(
            0, weight=1
        )

        # PANEL IZQUIERDO: VISTA PREVIA

        self.camera_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD,
            corner_radius=22
        )

        self.camera_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 15),
            pady=5
        )

        self.camera_frame.grid_rowconfigure(
            0, weight=1
        )
        self.camera_frame.grid_columnconfigure(
            0, weight=1
        )

        self.camera_label = ctk.CTkLabel(
            self.camera_frame,
            text="CAMERA PREVIEW",
            font=("Arial", 30, "bold"),
            text_color=GRAY
        )

        self.camera_label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=15,
            pady=15
        )

        # PANEL DERECHO: CONTROLES

        self.controls_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.controls_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(5, 0),
            pady=5
        )

        self.controls_frame.grid_columnconfigure(
            0, weight=1
        )

        self.controls_frame.grid_rowconfigure(
            2, weight=1
        )

        # Indicaciones
        self.style_label = ctk.CTkLabel(
            self.controls_frame,
            text="CHOOSE YOUR STYLE",
            font=("Arial", 22, "bold"),
            text_color=WHITE
        )

        self.style_label.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(5, 15)
        )

        # Estilos
        self.style_frame = ctk.CTkFrame(
            self.controls_frame,
            fg_color=CARD,
            corner_radius=18
        )

        self.style_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        self.style_frame.grid_columnconfigure(
            (0, 1), weight=1
        )

        styles = [
            "PIXAR",
            "ANIME",
            "SCRIBBLE",
            "CYBERPUNK"
        ]

        for index, style in enumerate(styles):

            row = index // 2
            col = index % 2

            button = ctk.CTkButton(
                self.style_frame,
                text=style,
                font=("Arial", 15, "bold"),
                height=55,
                corner_radius=14,
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
                sticky="ew",
                padx=8,
                pady=8
            )

        # Botones de acciones
        self.button_frame = ctk.CTkFrame(
            self.controls_frame,
            fg_color="transparent"
        )

        self.button_frame.grid(
            row=2,
            column=0,
            sticky="nsew"
        )

        self.button_frame.grid_columnconfigure(
            0, weight=1
        )

        self.button_frame.grid_rowconfigure(
            (0, 1, 2), weight=1
        )

        # Tomar foto
        self.capture_button = ctk.CTkButton(
            self.button_frame,
            text="TAKE PIC",
            font=("Anton", 24),
            fg_color=RED,
            hover_color=RED_HOVER,
            text_color=WHITE,
            height=65,
            corner_radius=16,
            border_width=2,
            border_color=WHITE,
            command=self.start_capture
        )

        self.capture_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=5,
            pady=7
        )

        # Cargar foto
        self.load_button = ctk.CTkButton(
            self.button_frame,
            text="LOAD PHOTO",
            font=("Anton", 22),
            fg_color="#292929",
            hover_color="#414141",
            text_color=WHITE,
            height=60,
            corner_radius=16,
            border_width=2,
            border_color="#555555",
            command=self.load_local_photo
        )

        self.load_button.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=5,
            pady=7
        )

        # Prueba sin API
        self.preview_button = ctk.CTkButton(
            self.button_frame,
            text="TEST WITHOUT AI",
            font=("Arial", 15, "bold"),
            fg_color="#292929",
            hover_color="#414141",
            text_color=WHITE,
            height=55,
            corner_radius=16,
            border_width=2,
            border_color="#555555",
            command=self.test_without_ai
        )

        self.preview_button.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=5,
            pady=7
        )

        # Generación con IA: acción independiente
        self.generate_button = ctk.CTkButton(
            self.controls_frame,
            text="GENERATE WITH AI",
            font=("Anton", 24),
            fg_color=RED,
            hover_color=RED_HOVER,
            text_color=WHITE,
            height=70,
            corner_radius=18,
            border_width=2,
            border_color=WHITE,
            command=self.start_ai_generation,
            state="disabled"
        )

        self.generate_button.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(18, 5)
        )
