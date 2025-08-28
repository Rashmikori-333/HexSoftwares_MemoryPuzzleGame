import pygame
import os
import json

# Score file at project root
SCORE_FILE = "scores.json"

def load_images():
    images = []
    image_folder = os.path.join("Assets", "images")

    # Loop through all PNG files in Assets/images/
    if not os.path.exists(image_folder):
        raise FileNotFoundError(f"Images folder not found: {image_folder}")

    for img_file in os.listdir(image_folder):
        # skip back.png for now
        if img_file.endswith(".png") and img_file != "back.png":
            img = pygame.image.load(os.path.join(image_folder, img_file)).convert_alpha()
            images.append(img)

    # Load back.png separately; if missing, create a simple surface
    back_path = os.path.join(image_folder, "back.png")
    if os.path.exists(back_path):
        back_image = pygame.image.load(back_path).convert_alpha()
    else:
        # fallback simple rectangle surface
        back_image = pygame.Surface((100, 150))
        back_image.fill((150, 150, 150))

    return images, back_image

def load_sounds():
    sounds = {}
    sound_folder = os.path.join("Assets", "sounds")

    if os.path.exists(sound_folder):
        for snd_file in os.listdir(sound_folder):
            if snd_file.endswith(".wav"):
                try:
                    sounds[snd_file] = pygame.mixer.Sound(os.path.join(sound_folder, snd_file))
                except Exception:
                    # skip if loading fails
                    pass
    return sounds

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        print(f"⚠️ Could not load sound: {path}")
        return None

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

# ---------------- Score helpers ----------------
def load_scores():
    try:
        with open(SCORE_FILE, "r") as f:
            data = json.load(f)
            # ensure keys present
            return {"best_moves": data.get("best_moves"), "best_time": data.get("best_time")}
    except Exception:
        # default
        return {"best_moves": None, "best_time": None}

def save_scores(scores_dict):
    try:
        with open(SCORE_FILE, "w") as f:
            json.dump({
                "best_moves": scores_dict.get("best_moves"),
                "best_time": scores_dict.get("best_time")
            }, f)
    except Exception as e:
        print("Could not save scores:", e)
