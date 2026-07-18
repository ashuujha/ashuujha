import os
import requests
from PIL import Image, ImageDraw, ImageOps

def download_avatar(username, output_path):
    """Downloads the GitHub avatar for a user."""
    url = f"https://github.com/{username}.png"
    print(f"Downloading avatar from {url}...")
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Avatar saved to {output_path}")
            return True
        else:
            print(f"Failed to download avatar. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading avatar: {e}")
        return False

def make_circular(img):
    """Crops an image into a circle with a transparent background."""
    img = img.convert("RGBA")
    size = min(img.size)
    
    # Center crop to square
    left = (img.width - size) // 2
    top = (img.height - size) // 2
    img = img.crop((left, top, left + size, top + size))
    
    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    
    # Apply mask
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask=mask)
    return output

def image_to_ascii(image_path, width=40, color_threshold=None):
    """Converts an image file to grayscale ASCII art."""
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return ""

    # Crop to circle first
    img = make_circular(img)

    # Convert to grayscale
    img_gray = img.convert("L")
    
    # Calculate height based on width and character aspect ratio (usually ~0.5 to 0.55)
    aspect_ratio = img.height / img.width
    # A standard terminal char is roughly 1.8 to 2.0 times taller than wide
    char_aspect = 0.48
    height = int(width * aspect_ratio * char_aspect)
    
    # Resize image
    img_resized = img_gray.resize((width, height), Image.Resampling.LANCZOS)
    
    # ASCII character palette (dark to light for dark terminal theme)
    # Background outside the circle (transparent in RGBA) will be black (0) in grayscale.
    # So 0 needs to be empty/space, and bright highlights (255) should be dense characters.
    chars = [" ", ".", ",", "-", "~", ":", ";", "=", "!", "*", "#", "$", "@"]
    num_chars = len(chars)
    
    # Get alpha channel from resized RGBA image to handle transparency properly
    img_rgba_resized = img.resize((width, height), Image.Resampling.LANCZOS)
    rgba_bytes = img_rgba_resized.tobytes()
    gray_bytes = img_resized.tobytes()
    
    ascii_str = []
    for i in range(len(gray_bytes)):
        alpha = rgba_bytes[i * 4 + 3]
        gray_val = gray_bytes[i]
        # If the pixel is fully transparent, render as space
        if alpha < 50:
            ascii_str.append(" ")
        else:
            # Map grayscale value (0-255) to character index
            idx = int((gray_val / 255.0) * (num_chars - 1))
            ascii_str.append(chars[idx])
            
    # Chunk string into lines of specified width
    lines = [ "".join(ascii_str[index : index + width]) for index in range(0, len(ascii_str), width) ]
    return "\n".join(lines)

if __name__ == "__main__":
    import json
    # Load config to get username
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {"github_username": "ashuu1408"}
        
    username = config.get("github_username", "ashuu1408")
    avatar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "avatar.png")
    
    # Make sure download is successful or fallback to existing
    download_avatar(username, avatar_path)
    
    if os.path.exists(avatar_path):
        ascii_art = image_to_ascii(avatar_path, width=44)
        print("Generated ASCII Preview:")
        print(ascii_art)
        
        # Save to assets/ascii_art.txt
        ascii_txt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "ascii_art.txt")
        with open(ascii_txt_path, "w") as f:
            f.write(ascii_art)
        print(f"ASCII art saved to {ascii_txt_path}")
    else:
        print("Could not generate ASCII: avatar file not found.")
