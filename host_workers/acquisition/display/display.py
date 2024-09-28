import board
import busio
from digitalio import DigitalInOut
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import time

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
# font_title = ImageFont.truetype("UbuntuMono-R.ttf", 20)
# font_small = ImageFont.truetype("UbuntuMono-R.ttf", 14)
# font_title = ImageFont.truetype("Roboto-Regular.ttf", 26)
# font_small = ImageFont.truetype("Roboto-Regular.ttf", 12)
font_title = ImageFont.truetype("DejaVuSansMono.ttf", 23)
font_small = ImageFont.truetype("DejaVuSansMono.ttf", 12)

# DejaVuSansMono.ttf


# ----------------------------------------------------------------------
def oled(fn):
    """"""

    def inset(*args, **kwargs):
        image = Image.new("1", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
        fn(draw, *args, **kwargs)
        oled_display.image(image)
        oled_display.show()

    return inset


# ----------------------------------------------------------------------
@oled
def title(draw, text):
    """"""
    draw.text((3, 20), text, font=font_title, fill=255)


# ----------------------------------------------------------------------
@oled
def line(draw, text):
    """"""
    draw.text((0, 0), text, font=font_small, fill=255)


# ----------------------------------------------------------------------
def scroll_line(text, speed=0.05):
    """
    Scroll vertical de un texto largo en la pantalla OLED.
    """
    _, _, _, text_height = font_small.getbbox(text)

    # Crear una imagen en blanco para dibujar
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    # Scroll vertical si el texto es más largo que la pantalla
    for y_offset in range(0, text_height + HEIGHT):
        draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
        draw.text((0, HEIGHT - y_offset), text, font=font_small, fill=255)
        oled_display.image(image)
        oled_display.show()
        time.sleep(speed)


title('DunderLab')
