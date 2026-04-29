import pygame
import random
import time
import os
import zipfile

pygame.init()

#Screen & Scaling
BASE_WIDTH, BASE_HEIGHT = 180, 140
SCALE = 3

WIDTH, HEIGHT = BASE_WIDTH * SCALE, BASE_HEIGHT * SCALE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NPC")

game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

#Folder Paths
BASE_PATH = r"C:\Users\ACER\Documents\Doro"
SCAN_PATH = r"C:\Users\ACER\Documents\ScanFolder"

#Sprites 
def load_frames(folder):
    path = os.path.join(BASE_PATH, folder)
    frames = []

    if not os.path.exists(path):
        return frames

    for file in sorted(os.listdir(path)):
        if file.endswith(".png"):
            img = pygame.image.load(os.path.join(path, file)).convert_alpha()
            frames.append(img)

    return frames

happy = load_frames("happy")
neutral = load_frames("neutral")
derp = load_frames("derp")
think = load_frames("think")
danger = load_frames("danger")

if not danger:
    danger = derp

#Dialogues
idle_dialogue = [
    ("Hey...", happy),
    ("Nice to see you.", happy),
    ("Doro...", neutral),
    ("Just resting.", neutral),
    ("Hmmm...", think),
    ("Uh huh...", think)
]

suspicious_keywords = [
    "virus", "malware", "trojan",
    "hack", "steal", "password", "keylogger"
]

current_text = ""
current_frames = neutral
frame_index = 0

files = []
selected_index = 0

font = pygame.font.SysFont(None, 12)

clock = pygame.time.Clock()

last_talk = time.time()
talk_delay = 5

#Files
def load_files():
    global files

    if not os.path.exists(SCAN_PATH):
        files = []
        return

    files = [
        f for f in os.listdir(SCAN_PATH)
        if f.endswith((".txt", ".zip", ".docx", ".rar"))
    ]

def scan_single_file(filename):
    full_path = os.path.join(SCAN_PATH, filename)

    try:
        if filename.endswith(".txt"):
            with open(full_path, "r", errors="ignore") as f:
                content = f.read().lower()
                if any(word in content for word in suspicious_keywords):
                    return "sus"
                return "clean"

        elif filename.endswith(".zip"):
            with zipfile.ZipFile(full_path, 'r') as z:
                if any(".exe" in name for name in z.namelist()):
                    return "sus"
                return "zip"

        elif filename.endswith(".docx"):
            return "doc"

        elif filename.endswith(".rar"):
            return "rar"

    except:
        return "unknown"

    return "unknown"

def generate_ai_dialogue(result, filename):
    global current_text, current_frames

    if result == "sus":
        current_text = random.choice([
            f"{filename}? That’s sketchy.",
            "I don’t trust this file.",
            "Yeah… that’s bad news.",
            "Nope. Not safe."
        ])
        current_frames = danger

    elif result == "clean":
        current_text = random.choice([
            f"{filename} looks fine.",
            "Nothing weird here.",
            "Safe file. Boring."
        ])
        current_frames = happy

    elif result == "zip":
        current_text = "Compressed file... suspicious."
        current_frames = think

    elif result == "doc":
        current_text = "Just a document."
        current_frames = neutral

    elif result == "rar":
        current_text = random.choice([
            "A RAR file? That’s suspiciously sealed.",
            "Compressed mystery detected.",
            "I can’t see inside that easily...",
            "Old-school hiding technique..."
        ])
        current_frames = think

    else:
        current_text = "Unreadable file..."
        current_frames = derp

#Idle 
def idle_talk():
    global current_text, current_frames
    text, anim = random.choice(idle_dialogue)
    current_text = text
    current_frames = anim
load_files()

running = True

while running:

    if current_frames == danger:
        game_surface.fill((40, 0, 0))
    else:
        game_surface.fill((15, 15, 25))

    if current_frames:
        frame = current_frames[frame_index]
        frame_index = (frame_index + 1) % len(current_frames)

        x = (BASE_WIDTH - frame.get_width()) // 2
        y = 15
        game_surface.blit(frame, (x, y))

    if time.time() - last_talk > talk_delay:
        idle_talk()
        last_talk = time.time()
        talk_delay = random.randint(4, 7)

    if current_text:
        box_rect = pygame.Rect(4, 100, 172, 35)
        pygame.draw.rect(game_surface, (0, 0, 0), box_rect)
        pygame.draw.rect(game_surface, (255, 255, 255), box_rect, 1)

        text_surface = font.render(current_text, True, (255, 255, 255))
        game_surface.blit(text_surface, (8, 108))

    if files:
        file_text = font.render(f"> {files[selected_index]}", True, (200, 200, 100))
        game_surface.blit(file_text, (5, 5))
    else:
        file_text = font.render("No files found.", True, (200, 100, 100))
        game_surface.blit(file_text, (5, 5))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_RIGHT and files:
                selected_index = (selected_index + 1) % len(files)

            if event.key == pygame.K_LEFT and files:
                selected_index = (selected_index - 1) % len(files)

            if event.key == pygame.K_RETURN and files:
                filename = files[selected_index]
                result = scan_single_file(filename)
                generate_ai_dialogue(result, filename)

    scaled = pygame.transform.scale(game_surface, (WIDTH, HEIGHT))
    screen.blit(scaled, (0, 0))

    pygame.display.flip()
    clock.tick(10 if current_frames == danger else 6)

pygame.quit()