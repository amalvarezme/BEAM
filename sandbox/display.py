import board
import busio
from digitalio import DigitalInOut
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# Configuración de I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Configuración del OLED SSD1306
WIDTH = 128
HEIGHT = 64

oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Limpiar el display
oled.fill(0)
oled.show()

# Crear una imagen en blanco para dibujar
image = Image.new("1", (WIDTH, HEIGHT))

# Obtener el objeto de dibujo para la imagen
draw = ImageDraw.Draw(image)

# Limpiar la imagen con un rectángulo negro
draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

# Cargar la fuente Roboto
roboto_font_small = ImageFont.truetype("Roboto-Regular.ttf", 12)
roboto_font_large = ImageFont.truetype("Roboto-Regular.ttf", 26)

# Dibujar texto en la imagen con diferentes tamaños
draw.text((3, 20), "DunderLab", font=roboto_font_large, fill=255)
# draw.text((0, 20), "Roboto 16pt!", font=roboto_font_large, fill=255)

# Mostrar la imagen en la pantalla OLED
oled.image(image)
oled.show()
