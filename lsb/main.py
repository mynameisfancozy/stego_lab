import os
from PIL import Image

STOP_SEQ = '1111111111111110'
RAW_DIR = 'raw'
ENCODED_DIR = 'encoded'

def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join([chr(int(b, 2)) for b in chars])

def embed_lsb(filename, message):
    input_path = os.path.join(RAW_DIR, filename)
    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_lsb{ext}"
    output_path = os.path.join(ENCODED_DIR, output_filename)

    if not os.path.exists(input_path):
        print(f"File {input_path} not found.")
        return

    os.makedirs(ENCODED_DIR, exist_ok=True)

    img = Image.open(input_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = list(img.getdata())

    binary_message = text_to_bits(message) + STOP_SEQ
    binary_index = 0
    new_pixels = []

    for pixel in pixels:
        r, g, b = pixel
        if binary_index < len(binary_message):
            r = (r & ~1) | int(binary_message[binary_index])
            binary_index += 1
        if binary_index < len(binary_message):
            g = (g & ~1) | int(binary_message[binary_index])
            binary_index += 1
        if binary_index < len(binary_message):
            b = (b & ~1) | int(binary_message[binary_index])
            binary_index += 1
        new_pixels.append((r, g, b))

    img.putdata(new_pixels)
    img.save(output_path)
    print(f"Message embedded into {output_path}")

def extract_lsb(filename):
    input_path = os.path.join(ENCODED_DIR, filename)
    if not os.path.exists(input_path):
        print(f"File {input_path} not found.")
        return

    img = Image.open(input_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = list(img.getdata())

    bits = ''
    for pixel in pixels:
        for color in pixel:
            bits += str(color & 1)
            if bits[-16:] == STOP_SEQ:
                return bits_to_text(bits[:-16])
    return bits_to_text(bits)

if __name__ == "__main__":
    mode = input("Mode (0 - embed, 1 - extract): ").strip().lower()

    if mode == '0':
        filename = input("Enter BMP file name: ").strip()
        message = input("Enter the message to embed: ")
        embed_lsb(filename, message)

    elif mode == '1':
        filename = input("Enter BMP file name: ").strip()
        message = extract_lsb(filename)
        if message:
            print(f"Extracted message: {message}")
        else:
            print("No message found.")

    else:
        print("Invalid mode. Use 0 to embed or 1 to extract.")