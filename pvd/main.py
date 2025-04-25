import os
from PIL import Image

STOP_SEQ = '1111111111111110'
RAW_DIR = 'raw'
ENCODED_DIR = 'encoded'

def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(b, 2)) for b in chars)

def range_capacity(diff):
    if 0 <= diff <= 7:
        return (0, 7, 3)
    elif 8 <= diff <= 15:
        return (8, 15, 4)
    elif 16 <= diff <= 31:
        return (16, 31, 5)
    elif 32 <= diff <= 63:
        return (32, 63, 6)
    elif 64 <= diff <= 127:
        return (64, 127, 7)
    elif 128 <= diff <= 255:
        return (128, 255, 8)
    return (0, 0, 0)

def embed_pvd(filename, message):
    input_path = os.path.join(RAW_DIR, filename)
    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_pvd{ext}"
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

    i = 0
    while binary_index < len(binary_message) and i < len(pixels) // 2:
        r1 = pixels[2 * i][0]
        r2 = pixels[2 * i + 1][0]
        d = r1 - r2
        l, u, n = range_capacity(abs(d))
        secret = int(binary_message[binary_index:binary_index + n].ljust(n, '0'), 2)
        m = l + secret

        new_diff = m if d >= 0 else -m

        sum_pixels = r1 + r2
        new_r1 = (sum_pixels + new_diff) // 2
        new_r2 = (sum_pixels - new_diff) // 2

        new_r1 = max(0, min(255, new_r1))
        new_r2 = max(0, min(255, new_r2))

        new_pixels.append((new_r1, pixels[2 * i][1], pixels[2 * i][2]))
        new_pixels.append((new_r2, pixels[2 * i + 1][1], pixels[2 * i + 1][2]))

        binary_index += n
        i += 1

    new_pixels.extend(pixels[2 * i:])

    img.putdata(new_pixels)
    img.save(output_path)
    print(f"Message embedded into {output_path}")

def extract_pvd(filename):
    input_path = os.path.join(ENCODED_DIR, filename)
    if not os.path.exists(input_path):
        print(f"File {input_path} not found.")
        return

    img = Image.open(input_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = list(img.getdata())

    bits = ''
    i = 0
    while i < len(pixels) // 2:
        r1 = pixels[2 * i][0]
        r2 = pixels[2 * i + 1][0]
        d = abs(r1 - r2)
        l, u, n = range_capacity(d)
        secret = d - l
        extracted_bits_str = bin(secret)[2:].zfill(n)

        for j in range(n):
            bits += extracted_bits_str[j]
            if bits[-16:] == STOP_SEQ:
                return bits_to_text(bits[:-16])

        i += 1
    return bits_to_text(bits)

if __name__ == "__main__":
    mode = input("Mode (0 - embed, 1 - extract): ").strip()

    if mode == '0':
        filename = input("Enter BMP file name: ").strip()
        message = input("Enter the message to embed: ")
        embed_pvd(filename, message)

    elif mode == '1':
        filename = input("Enter BMP file name: ").strip()
        message = extract_pvd(filename)
        if message:
            print(f"Extracted message: {message}")
        else:
            print("No message found.")

    else:
        print("Invalid mode. Use 0 to embed or 1 to extract.")