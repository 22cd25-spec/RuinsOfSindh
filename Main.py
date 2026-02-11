import pygame
import sys
import math
import random
import array
import os
import json

# --- 1. System Setup ---
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ruins of Sindh")
clock = pygame.time.Clock()

# --- 2. Audio Generation ---
def generate_sfx(kind):
    sample_rate = 44100
    if kind == "whoosh": duration, vol = 0.2, 0.05      
    elif kind == "hit": duration, vol = 0.2, 0.4        
    elif kind == "pitfall": duration, vol = 0.4, 0.6    
    elif kind == "pickup": duration, vol = 0.1, 0.2    
    elif kind == "jump": duration, vol = 0.08, 0.15    
    elif kind == "click": duration, vol = 0.05, 0.15
    elif kind == "gameover": duration, vol = 1.5, 0.4  
    elif kind == "highscore": duration, vol = 1.0, 0.5
    elif kind == "heartbeat": duration, vol = 0.3, 0.3
    else: duration, vol = 0.1, 0.2
    
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        env = math.sin(math.pi * (t / duration))
        if kind == "gameover":
            val = (math.sin(2 * math.pi * 100 * t) * (1-t/duration)) + random.uniform(-0.1, 0.1)
        elif kind == "highscore":
            val = math.sin(2 * math.pi * 880 * t) * math.sin(2 * math.pi * 5 * t)
        elif kind == "heartbeat":
            val = math.sin(2 * math.pi * 60 * t) * math.exp(-20 * (t % 0.15))
        else:
            val = (math.sin(2 * math.pi * 440 * t) + random.uniform(-0.3, 0.3)) * env
        buf[i] = int(max(-1.0, min(1.0, val * vol)) * 32767)
    return pygame.mixer.Sound(buffer=buf)

def generate_mohenjo_theme(speed=1.0):
    sample_rate = int(44100 * speed)
    bpm, total_beats = 105, 8
    beat_len = 60 / bpm
    total_samples = int(sample_rate * beat_len * total_beats)
    buf = array.array('h', [0] * total_samples)
    melody = [196, 0, 233, 261, 196, 0, 311, 293]
    for i in range(total_samples):
        t = i / sample_rate
        beat_idx = int(t / beat_len) % total_beats
        t_in_beat = t % beat_len
        drum = (math.sin(2 * math.pi * 60 * t)) * math.exp(-12 * t_in_beat) * (0.5 if beat_idx % 4 == 0 else 0.2)
        freq = melody[beat_idx]
        flute = (math.sin(2 * math.pi * freq * t)) * math.sin(math.pi * (t_in_beat / beat_len)) * 0.25 if freq > 0 else 0
        buf[i] = int(max(-1.0, min(1.0, (drum + flute) * 0.6)) * 32767)
    return pygame.mixer.Sound(buffer=buf)

sfx = {k: generate_sfx(k) for k in ["whoosh", "hit", "pitfall", "pickup", "jump", "click", "gameover", "highscore", "heartbeat"]}
current_theme = generate_mohenjo_theme()

# --- 3. Leaderboard ---
LEADERBOARD_FILE = "leaderboard.json"
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def is_new_best(score):
    lb = load_leaderboard()
    return not lb or score > lb[0]["score"]

def save_to_leaderboard(name, score):
    data = load_leaderboard()
    data.append({"name": name, "score": score})
    data = sorted(data, key=lambda x: x["score"], reverse=True)[:5]
    try:
        with open(LEADERBOARD_FILE, "w") as f: json.dump(data, f)
    except: pass

# --- 4. Asset Helpers ---
def load_properly(path, scale_to_screen=True, force_size=None):
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        if force_size: return pygame.transform.scale(img, force_size)
        if scale_to_screen:
            ratio = SCREEN_HEIGHT / img.get_height()
            return pygame.transform.scale(img, (int(img.get_width() * ratio), SCREEN_HEIGHT))
        return img
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return pygame.Surface((100, 100), pygame.SRCALPHA)

def get_frames(sheet, cols):
    frames = []
    fw, fh = sheet.get_width() // cols, sheet.get_height()
    for i in range(cols):
        f = sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh))
        frames.append(f.subsurface(f.get_bounding_rect()))
    return frames

def create_cinematic_vignette():
    v = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(0, 180, 2):
        alpha = int(max(0, (1 - i/180) * 190))
        rect_color = (110, 0, 0, alpha)
        pygame.draw.rect(v, rect_color, (i, i, SCREEN_WIDTH - 2*i, SCREEN_HEIGHT - 2*i), width=2)
    return v

def draw_text_with_outline(surf, text, font, pos, text_col, shadow_col, thickness=4, center=False, right=False):
    tw, th = font.size(text)
    if center: draw_pos = (pos[0] - tw//2, pos[1])
    elif right: draw_pos = (pos[0] - tw, pos[1])
    else: draw_pos = pos
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-thickness), (0,thickness), (-thickness,0), (thickness,0)]:
        outline_surf = font.render(text, True, shadow_col)
        surf.blit(outline_surf, (draw_pos[0] + dx, draw_pos[1] + dy))
    main_surf = font.render(text, True, text_col)
    surf.blit(main_surf, draw_pos)

# --- 5. Loading Assets ---
background = load_properly("Background.png")
backdrop = load_properly("Backdrop.png")
floating_guides = load_properly("Floating_Objects.png")
front_pillars = load_properly("Front_Objects.png")
arrows_raw = load_properly("Arrows.png")
raw_pickups = load_properly("Pickups.png")
start_bg_img = load_properly("start.png", force_size=(SCREEN_WIDTH, SCREEN_HEIGHT))
game_over_img = load_properly("Game_over.png", force_size=(800, 450))
full_hp_seal = pygame.transform.scale(load_properly("fullhp.png", False), (60, 60))
empty_hp_seal = pygame.transform.scale(load_properly("hpdown.png", False), (60, 60))

idle_frames = get_frames(load_properly("Player_Idle.png", False), 6)
run_frames  = get_frames(load_properly("Player_Run.png", False), 6)
idle_masks = [pygame.mask.from_surface(f) for f in idle_frames]
run_masks = [pygame.mask.from_surface(f) for f in run_frames]

ICON_SIZE = 80
btn_on = pygame.transform.scale(load_properly("music_on.png", False), (ICON_SIZE, ICON_SIZE))
btn_off = pygame.transform.scale(load_properly("music_off.png", False), (ICON_SIZE, ICON_SIZE))
btn_quit_icon = pygame.transform.scale(load_properly("Quit.png", False), (ICON_SIZE, ICON_SIZE))

artifact_info = [
    {"name": "Dancing Girl", "path": "Dancing_Girl.png", "info": "Bronze statuette (2300 BC). It shows high metal-working skill."},
    {"name": "Priest-King", "path": "King_Priest.png", "info": "A soapstone sculpture representing a powerful leader or deity."},
    {"name": "Unicorn Seal", "path": "Seal.png", "info": "Used for trade. Features a mythical creature and ancient Indus script."},
    {"name": "Painted Pottery", "path": "Painted_Pottery.png", "info": "Sturdy red clay pottery with floral and geometric motifs from the Indus Valley."}
]

for item in artifact_info:
    raw = load_properly(item["path"], False)
    item["card_img"] = pygame.transform.scale(raw, (300, 420))
    item["icon_img"] = pygame.transform.scale(raw, (60, 80))

artifact_mapping = ["Painted Pottery", "Dancing Girl", "Unicorn Seal", "Priest-King", "Dancing Girl", "Unicorn Seal", "Painted Pottery"]

def extract_entities(layer):
    if layer.get_width() <= 100: return []
    mask = pygame.mask.from_surface(layer)
    rects = mask.get_bounding_rects()
    rects.sort(key=lambda r: r.x)
    return [{"img": layer.subsurface(r), "rect": r, "mask": pygame.mask.from_surface(layer.subsurface(r)), "active": True, "name": artifact_mapping[i % len(artifact_mapping)]} for i, r in enumerate(rects)]

pickup_objects = extract_entities(raw_pickups)
arrow_templates = extract_entities(arrows_raw)
for a in arrow_templates: a["mask"] = pygame.mask.from_surface(a["img"])

# --- 6. Global State & Reset ---
hp, MAX_HP = 4, 4
game_state = "MENU"
paused, music_enabled, show_guide = False, True, False
camera_x, player_name, name_taken_warning = 0, "", False
collected_inventory, reading_card = {}, None
arrows_in_flight, last_spawn_time, heartbeat_timer = [], 0, 0
loop_count, total_score, is_high_score = 0, 0, False
level_width = background.get_width()
is_moving, is_grounded = False, True
player_x, player_y = 400, 615
vel_y, gravity = 0, 0.8
base_jump, base_speed = -16, 8
player_direction, jumps_left, jump_pressed = 1, 2, False
anim_idx, anim_timer, invuln_timer = 0, 0, 0
vignette_surf = create_cinematic_vignette()

# Touch variables
touch_moving_right = False
touch_moving_left = False

# FIXED HITBOXES
L_HIT = pygame.Rect(50, SCREEN_HEIGHT - 150, 100, 100)
R_HIT = pygame.Rect(180, SCREEN_HEIGHT - 150, 100, 100)
J_HIT = pygame.Rect(SCREEN_WIDTH - 160, SCREEN_HEIGHT - 160, 120, 120)

def update_music(loop):
    global current_theme, music_enabled
    current_theme.stop()
    speed = min(1.0 + (loop * 0.08), 1.8)
    current_theme = generate_mohenjo_theme(speed)
    if music_enabled: current_theme.play(loops=-1)

def reset_game():
    global hp, player_x, player_y, camera_x, collected_inventory, arrows_in_flight, loop_count, total_score, paused, is_moving, anim_idx, anim_timer, invuln_timer, is_high_score
    hp = 4; player_x, player_y = 400, 615; camera_x = 0; collected_inventory = {}
    arrows_in_flight = []; loop_count, total_score = 0, 0; paused, is_moving = False, False
    anim_idx, anim_timer = 0, 0; invuln_timer = 0; is_high_score = False
    for p in pickup_objects: p["active"] = True
    update_music(0)

current_theme.play(-1)

# --- 7. Main Loop ---
while True:
    clock.tick(60)
    curr_ms = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        # TOUCH/MOUSE COORDINATES
        if event.type in [pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION]:
            tx, ty = event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT
        else:
            tx, ty = mouse_pos

        if event.type == pygame.KEYDOWN:
            if game_state == "NAMING":
                name_taken_warning = False
                if event.key == pygame.K_RETURN and player_name.strip():
                    if any(e['name'].lower() == player_name.strip().lower() for e in load_leaderboard()):
                        name_taken_warning = True
                    else: sfx["click"].play(); game_state = "PLAYING"; reset_game()
                elif event.key == pygame.K_BACKSPACE: player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE: game_state = "MENU"
                else:
                    if len(player_name) < 12: player_name += event.unicode
            elif game_state == "PLAYING":
                if event.key in [pygame.K_ESCAPE, pygame.K_p]:
                    if reading_card: reading_card = None
                    else: paused = not paused; sfx["click"].play()

        if event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "MENU":
                if show_guide: show_guide = False
                elif pygame.Rect(SCREEN_WIDTH//2-380, 380, 280, 60).collidepoint((tx, ty)): sfx["click"].play(); game_state = "NAMING"
                elif pygame.Rect(SCREEN_WIDTH//2-380, 460, 280, 60).collidepoint((tx, ty)): sfx["click"].play(); show_guide = True
                elif pygame.Rect(30, SCREEN_HEIGHT - 110, ICON_SIZE, ICON_SIZE).collidepoint((tx, ty)):
                    music_enabled = not music_enabled
                    current_theme.play(-1) if music_enabled else current_theme.stop()
                elif pygame.Rect(130, SCREEN_HEIGHT - 110, ICON_SIZE, ICON_SIZE).collidepoint((tx, ty)): pygame.quit(); sys.exit()
            
            elif game_state == "PLAYING":
                if paused:
                    if pygame.Rect(SCREEN_WIDTH//2 - 140, 450, 280, 60).collidepoint((tx, ty)): sfx["click"].play(); game_state = "MENU"; paused = False
                elif reading_card: reading_card = None
                else:
                    clicked_inv = False
                    for i, (name, data) in enumerate(collected_inventory.items()):
                        if data["rect"].collidepoint((tx, ty)):
                            reading_card = next((it for it in artifact_info if it["name"] == name), None); sfx["click"].play()
                            clicked_inv = True
                    
                    if not clicked_inv:
                        if L_HIT.collidepoint((tx, ty)):
                            touch_moving_left = True
                            touch_moving_right = False
                        elif R_HIT.collidepoint((tx, ty)):
                            touch_moving_right = True
                            touch_moving_left = False
                        elif J_HIT.collidepoint((tx, ty)):
                            if jumps_left > 0:
                                vel_y = base_jump; jumps_left -= 1; sfx["jump"].play(); is_grounded = False
            
            elif game_state == "GAMEOVER":
                save_to_leaderboard(player_name, total_score); reset_game(); game_state = "MENU"

        if event.type == pygame.FINGERUP or event.type == pygame.MOUSEBUTTONUP:
            touch_moving_left = False
            touch_moving_right = False

    # Logic Updates
    if game_state == "PLAYING" and not paused and not reading_card:
        current_speed = base_speed + (loop_count * 0.4)
        if invuln_timer > 0: invuln_timer -= 1
        if hp == 1 and curr_ms - heartbeat_timer > 600:
            sfx["heartbeat"].play(); heartbeat_timer = curr_ms

        is_moving = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] or touch_moving_right: 
            player_x += current_speed; player_direction = 1; is_moving = True
        if (keys[pygame.K_LEFT] or keys[pygame.K_a] or touch_moving_left) and player_x > camera_x: 
            player_x -= current_speed; player_direction = -1; is_moving = True
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and not jump_pressed and jumps_left > 0:
            vel_y = base_jump; jumps_left -= 1; jump_pressed = True; sfx["jump"].play(); is_grounded = False
        if not (keys[pygame.K_SPACE] or keys[pygame.K_w]): jump_pressed = False
        
        vel_y += gravity; player_y += vel_y
        camera_x = max(0, player_x - 400)

        is_grounded = False
        try:
            lx, ly = int(player_x % level_width), int(player_y)
            on_float = floating_guides.get_at((lx, ly))[3] > 0 if 0 <= ly < SCREEN_HEIGHT else False
            if (player_y >= 615) or (vel_y > 0 and on_float):
                player_y = 615 if player_y >= 615 else ly
                vel_y, jumps_left, is_grounded = 0, 2, True
        except: pass

        anim_timer += 0.15
        current_set = run_frames if is_moving else idle_frames
        current_masks = run_masks if is_moving else idle_masks
        if is_moving: anim_timer += 0.08
        if anim_timer >= 1:
            anim_idx = (anim_idx + 1) % len(current_set)
            anim_timer = 0
        active_sprite = current_set[anim_idx]
        active_mask = current_masks[anim_idx]
        p_rect = active_sprite.get_rect(midbottom=(player_x - camera_x, player_y))

        spawn_delay = random.randint(max(150, 700 - (loop_count * 80)), max(350, 1100 - (loop_count * 60)))
        if curr_ms - last_spawn_time > spawn_delay:
            temp = random.choice(arrow_templates)
            tx = random.randint(int(camera_x) + 50, int(camera_x) + SCREEN_WIDTH - 50)
            arrows_in_flight.append({"img": temp["img"], "mask": temp["mask"], "pos": [tx, -100], "vel": 7 + (loop_count * 1.2) + random.uniform(-1.0, 2.5)})
            sfx["whoosh"].play(); last_spawn_time = curr_ms

        for a in arrows_in_flight[:]:
            a["pos"][1] += a["vel"]
            ox, oy = (a["pos"][0] - camera_x) - p_rect.x, a["pos"][1] - p_rect.y
            if active_mask.overlap(a["mask"], (ox, oy)):
                if invuln_timer <= 0:
                    hp -= 1; sfx["hit"].play(); invuln_timer = 60
                arrows_in_flight.remove(a)
            elif a["pos"][1] > SCREEN_HEIGHT: arrows_in_flight.remove(a)

        for p in pickup_objects:
            p_world_x = p["rect"].x + (loop_count * level_width)
            if p["active"]:
                ox, oy = (p_world_x - camera_x) - p_rect.x, p["rect"].y - p_rect.y
                if active_mask.overlap(p["mask"], (ox, oy)):
                    p["active"] = False; sfx["pickup"].play()
                    collected_inventory[p["name"]] = {"rect": pygame.Rect(0,0,0,0)}
                    total_score += 500 * (loop_count + 1)

        if player_x > (loop_count + 1) * level_width:
            loop_count += 1; update_music(loop_count)
            for p in pickup_objects: p["active"] = True

        if hp <= 0 or player_y > SCREEN_HEIGHT + 100:
            game_state = "GAMEOVER"; current_theme.stop()
            if is_new_best(total_score): is_high_score = True; sfx["highscore"].play()
            else: sfx["gameover"].play()
            if player_y > SCREEN_HEIGHT: sfx["pitfall"].play()

    # --- 8. Rendering ---
    def get_font(size):
        try: return pygame.font.Font(resource_path("Jersey10-Regular.ttf"), size)
        except: return pygame.font.SysFont("monospace", size, bold=True)
    pixel_title, pixel_sub, pixel_btn, pixel_desc = get_font(120), get_font(45), get_font(35), get_font(24)

    if game_state in ["PLAYING", "GAMEOVER"]:
        bg_off = camera_x % level_width
        bd_off = (camera_x * 0.4) % backdrop.get_width()
        for i in range(2):
            bx = int(i * level_width - bg_off)
            screen.blit(backdrop, (int(i * backdrop.get_width() - bd_off), 0))
            screen.blit(background, (bx, 0))
            if bx < SCREEN_WIDTH: screen.blit(background, (bx + level_width - 1, 0))
            for p in pickup_objects:
                if p["active"]: screen.blit(p["img"], (p["rect"].x + bx, p["rect"].y + (math.sin(curr_ms * 0.005) * 8)))

        if invuln_timer % 10 < 5:
            flipped = pygame.transform.flip(active_sprite, player_direction == -1, False)
            screen.blit(flipped, p_rect)
        
        for a in arrows_in_flight: screen.blit(a["img"], (a["pos"][0] - camera_x, a["pos"][1]))
        for i in range(2): screen.blit(front_pillars, (int(i * level_width - bg_off), 0))
        
        if game_state == "PLAYING" and hp == 1:
            alpha = int(140 + math.sin(curr_ms * 0.01) * 60)
            vignette_surf.set_alpha(alpha); screen.blit(vignette_surf, (0,0))

        for i in range(MAX_HP): screen.blit(full_hp_seal if i < hp else empty_hp_seal, (30 + i*70, 30))
        for i, (name, data) in enumerate(collected_inventory.items()):
            item = next(it for it in artifact_info if it["name"] == name)
            data["rect"] = pygame.Rect(SCREEN_WIDTH - 80 - (i * 90), 20, 60, 80)
            screen.blit(item["icon_img"], data["rect"])
        
        score_surf = pixel_sub.render(f"SCORE: {total_score}", True, (255,255,255))
        screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 20, 110))

        if paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 150)); screen.blit(overlay, (0, 0))
            draw_text_with_outline(screen, "GAME PAUSED", pixel_title, (SCREEN_WIDTH//2, 250), (255, 255, 255), (0,0,0), center=True)
            r = pygame.Rect(SCREEN_WIDTH//2 - 140, 450, 280, 60); pygame.draw.rect(screen, (180, 140, 40), r, border_radius=5)
            lbl = pixel_btn.render("MAIN MENU", True, (0,0,0)); screen.blit(lbl, (r.centerx - lbl.get_width()//2, r.centery - lbl.get_height()//2))

        if reading_card:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 200)); screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, (40, 30, 20), (SCREEN_WIDTH//2 - 350, 100, 700, 500), border_radius=15)
            pygame.draw.rect(screen, (255, 220, 100), (SCREEN_WIDTH//2 - 350, 100, 700, 500), width=3, border_radius=15)
            screen.blit(reading_card["card_img"], (SCREEN_WIDTH//2 - 320, 140))
            draw_text_with_outline(screen, reading_card["name"], pixel_sub, (SCREEN_WIDTH//2 + 20, 150), (255, 220, 100), (0,0,0))
            words = reading_card["info"].split(' '); line, y_off = "", 220
            for word in words:
                if pixel_desc.size(line + word)[0] < 320: line += word + " "
                else:
                    screen.blit(pixel_desc.render(line, True, (255,255,255)), (SCREEN_WIDTH//2 + 20, y_off)); line = word + " "; y_off += 30
            screen.blit(pixel_desc.render(line, True, (255,255,255)), (SCREEN_WIDTH//2 + 20, y_off))

        if game_state == "GAMEOVER":
            screen.blit(game_over_img, (SCREEN_WIDTH//2-400, 150))
            if is_high_score: draw_text_with_outline(screen, "NEW BEST SCORE!", pixel_sub, (SCREEN_WIDTH//2, 580), (255, 215, 0), (0,0,0), center=True)

        # --- PROFESSIONAL TOUCH OVERLAY ---
        if game_state == "PLAYING" and not paused and not reading_card:
            overlay_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            btns = [(L_HIT, "<", touch_moving_left), (R_HIT, ">", touch_moving_right), (J_HIT, "JUMP", not is_grounded)]
            for rect, label, is_active in btns:
                color = (255, 220, 100, 180) if is_active else (255, 255, 255, 70)
                draw_rect = rect.inflate(10, 10) if is_active else rect
                pygame.draw.ellipse(overlay_surf, color, draw_rect, width=3)
                pygame.draw.ellipse(overlay_surf, (color[0], color[1], color[2], 40), draw_rect)
                f = pixel_btn if label == "JUMP" else pixel_sub
                lbl = f.render(label, True, color)
                overlay_surf.blit(lbl, (draw_rect.centerx - lbl.get_width()//2, draw_rect.centery - lbl.get_height()//2))
            screen.blit(overlay_surf, (0, 0))

    elif game_state in ["MENU", "NAMING"]:
        screen.blit(start_bg_img, (0, 0))
        draw_text_with_outline(screen, "RUINS OF SINDH", pixel_title, (SCREEN_WIDTH//2, 100), (255, 220, 100), (0,0,0), thickness=6, center=True)
        if game_state == "MENU":
            for i, text in enumerate(["PLAY", "HOW TO PLAY"]):
                r = pygame.Rect(SCREEN_WIDTH//2-380, 380 + i*80, 280, 60); pygame.draw.rect(screen, (180, 140, 40), r, border_radius=5)
                lbl = pixel_btn.render(text, True, (0,0,0)); screen.blit(lbl, (r.centerx - lbl.get_width()//2, r.centery - lbl.get_height()//2))
            lb_card = pygame.Rect(SCREEN_WIDTH//2 + 80, 320, 400, 260)
            pygame.draw.rect(screen, (40, 30, 20, 180), lb_card, border_radius=10)
            pygame.draw.rect(screen, (255, 220, 100), lb_card, width=3, border_radius=10)
            draw_text_with_outline(screen, "HALL OF FAME", pixel_sub, (lb_card.centerx, lb_card.y + 30), (255, 220, 100), (0,0,0), center=True)
            for i, entry in enumerate(load_leaderboard()):
                color = (255, 255, 255) if i > 0 else (255, 215, 0)
                screen.blit(pixel_desc.render(f"{i+1}. {entry['name']}: {entry['score']}", True, color), (lb_card.x + 40, lb_card.y + 80 + i*30))
            screen.blit(btn_on if music_enabled else btn_off, (30, SCREEN_HEIGHT - 110))
            screen.blit(btn_quit_icon, (130, SCREEN_HEIGHT - 110))
            if show_guide:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,220)); screen.blit(overlay, (0,0))
                pygame.draw.rect(screen, (40, 30, 20), (290, 120, 700, 480), border_radius=10)
                lines = ["- JOURNEY THROUGH ANCIENT SINDH -", "LEFT/RIGHT: Move | JUMP: Action Button", "Click anywhere to close this guide."]
                for i, l in enumerate(lines): screen.blit(pixel_desc.render(l, True, (255, 220, 100) if i==0 else (255,255,255)), (330, 160 + i*32))
        elif game_state == "NAMING":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,200)); screen.blit(overlay, (0,0))
            ns = pixel_sub.render(f"NAME: {player_name}|", True, (255,255,255))
            screen.blit(ns, (SCREEN_WIDTH//2 - ns.get_width()//2, SCREEN_HEIGHT//2 - 20))
            if name_taken_warning: screen.blit(pixel_desc.render("NAME TAKEN!", True, (255, 80, 80)), (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 40))

    pygame.display.flip()