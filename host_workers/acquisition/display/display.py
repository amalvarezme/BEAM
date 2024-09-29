import asyncio
import board
import busio
from digitalio import DigitalInOut
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import textwrap


# Configuración de I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Configuración del OLED SSD1306
WIDTH = 128
HEIGHT = 64
oled_display = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Limpiar el display
oled_display.fill(0)
oled_display.show()

# Cargar la fuente Roboto
font_title = ImageFont.truetype("DejaVuSansMono.ttf", 23)
font_small = ImageFont.truetype("DejaVuSansMono.ttf", 12)


# Decorador para dibujar en la pantalla OLED
def oled(fn):
    def inset(*args, **kwargs):
        image = Image.new("1", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
        fn(draw, *args, **kwargs)
        oled_display.image(image)
        oled_display.show()

    return inset


@oled
def title(draw, text):
    draw.text((3, 20), text, font=font_title, fill=255)


@oled
def line(draw, text):
    draw.text((0, 0), text, font=font_small, fill=255)


def get_text_height(text, font, max_width):
    # Dividir el texto en múltiples líneas según el ancho máximo permitido
    lines = textwrap.wrap(text, width=(max_width // font.getbbox('A')[-2]))
    # Altura de cada línea
    line_height = font.getbbox('A')[-1]
    # Altura total = número de líneas * altura de cada línea
    return len(lines) * line_height, lines


# Función asíncrona para hacer scroll vertical de un texto largo
async def scroll_vertical(text, speed=1, keep=2):
    text_height, lines = get_text_height(text, font_small, WIDTH)

    # Crear una imagen en blanco para dibujar
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    # Scroll vertical si el texto es más largo que la pantalla
    for y_offset in range(0, text_height + HEIGHT, speed):
        draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
        y = -y_offset

        # Dibujar cada línea
        for line in lines:
            draw.text((0, y), line, font=font_small, fill=255)
            y += font_small.getbbox('A')[-1] + 3

        oled_display.image(image)
        oled_display.show()
        await asyncio.sleep(0)
        if y_offset == 0:
            await asyncio.sleep(keep)


async def scroll_horizontal(text, speed=1, keep=2, vertical_center=False):
    _, _, text_width, _ = font_small.getbbox(text)

    # Crear una imagen en blanco para dibujar
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    if vertical_center:
        vertical_center = (HEIGHT - font_small.getbbox(text)[3]) // 2
    else:
        vertical_center = 0

    # Scroll horizontal si el texto es más ancho que la pantalla
    for x_offset in range(0, text_width + WIDTH, speed):
        draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

        draw.text(
            (-x_offset, vertical_center),
            text,
            font=font_small,
            fill=255,
        )

        oled_display.image(image)
        oled_display.show()
        await asyncio.sleep(0)
        if x_offset == 0:
            await asyncio.sleep(keep)


title('DunderLab')
