from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
battlefield_size = 2000  
player_pos = [0, 0, 50]  
player_rotation = 90  
player_speed = 10  
player_boost_speed = 15  
enemies = []  
enemy_bullets = []  
player_bullets = []  
player_missiles = []  
score = 0  
game_over = False  
hud_color = (0, 1, 1)  
min_enemy_distance = 300  
max_enemy_distance = 1200  
camera_mode = 0  
camera_distance = 200  
fovY = 45  
enemy_shoot_cooldown = 180  
enemy_shoot_chance = 0.007  
max_shooting_distance = 1500  
cheat_mode_enabled = False
cheat_fire_timer = 0
cheat_fire_interval = 10
player_max_health = 1000  
player_health = player_max_health  
player_lives = 10  
hit_flash_duration = 0  
damage_per_hit = 100  
moving_forward = False  
moving_backward = False  
thruster_glow_intensity = 0.0  
camera_pos = (0, -200, 200)  
grid_offset_x = 0  
grid_offset_y = 0  
grid_line_spacing = 100  
grid_animation_speed = 5  
player_experience = 0  
player_level = 1  
game_won = False
enemies_respawn_timer = 0  
auto_target = None  
auto_move_timer = 0  
auto_target_change = 90  
missile_used_this_level = False  
combo_count = 0  
combo_timer = 0  
combo_multiplier = 1  
max_combo_time = 180  
shield_active = False  
shield_timer = 0  
shield_max_duration = 1200  
shield_color = (0.0, 0.6, 1.0)  
shield_alpha = 0.4  
shield_used_in_game = False  
game_paused = False
button_size = 30
button_padding = 10
play_pause_button_pos = (800, 650)  
restart_button_pos = (900, 650)  
for i in range(10):
    
    preferred_distance = random.uniform(min_enemy_distance, max_enemy_distance)
    angle = random.uniform(0, 2 * math.pi)
    
    
    pos_x = player_pos[0] + math.cos(angle) * preferred_distance
    pos_y = player_pos[1] + math.sin(angle) * preferred_distance
    
    
    pos_x = max(min(pos_x, battlefield_size/2 - 50), -battlefield_size/2 + 50)
    pos_y = max(min(pos_y, battlefield_size/2 - 50), -battlefield_size/2 + 50)
    
    enemies.append([
        pos_x,  
        pos_y,  
        random.uniform(100, 500),  
        random.uniform(0, 360),    
        random.randint(0, enemy_shoot_cooldown),  
        [0, 0, 0],  
        random.uniform(min_enemy_distance, max_enemy_distance)  
    ])
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    
    gluOrtho2D(0, 1000, 0, 800)  
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
def draw_spaceship(is_player=True):
    
    if is_player:
        
        draw_battleship()
    else:
        
        draw_enemy_ship()
def draw_battleship():
    
    
    hull_color = (0.2, 0.25, 0.35)         
    accent_color = (0.0, 0.8, 1.0)         
    deck_color = (0.3, 0.35, 0.45)         
    turret_color = (0.15, 0.18, 0.22)      
    energy_core_color = (0.0, 1.0, 0.7)    
    engine_glow_color = (1.0, 0.5, 0.1)    
    highlight_color = (0.7, 0.9, 1.0)      
    
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(3.2, 1.1, 0.5)
    glutSolidCube(30)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(*accent_color)
    glTranslatef(0, 0, -7)
    glScalef(2.8, 0.7, 0.15)
    glutSolidCube(30)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(*deck_color)
    glTranslatef(0, 0, 10)
    glScalef(2.5, 0.8, 0.18)
    glutSolidCube(30)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(-13, 0, 18)
    glScalef(0.7, 0.5, 0.7)
    glutSolidCube(20)
    
    glColor3f(*energy_core_color)
    glTranslatef(0, 0, 15)
    glutSolidSphere(4, 12, 12)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(*accent_color)
    glTranslatef(55, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(15, 40, 16)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(*hull_color)
    glTranslatef(-55, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glutSolidSphere(15, 25, 12)
    glColor3f(*engine_glow_color)
    glTranslatef(0, 0, -10)
    glutSolidSphere(10, 15, 10)
    glPopMatrix()
    
    draw_turret(35, 0, 13, turret_color, accent_color)
    draw_turret(10, 0, 13, turret_color, accent_color)
    draw_turret(-20, 0, 13, turret_color, accent_color)
    
    draw_secondary_turret(40, 12, 11, accent_color)
    draw_secondary_turret(40, -12, 11, accent_color)
    draw_secondary_turret(20, 15, 11, accent_color)
    draw_secondary_turret(20, -15, 11, accent_color)
    draw_secondary_turret(-35, 12, 11, accent_color)
    draw_secondary_turret(-35, -12, 11, accent_color)
    
    for angle, y_offset in [(-30, 25), (30, -25)]:
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(10, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.2, 0.2, 0.05)
        glutSolidCube(60)
        glPopMatrix()
    
    for y_offset in [-18, 18]:
        glPushMatrix()
        glColor3f(*highlight_color)
        glTranslatef(-10, y_offset, -10)
        glScalef(0.5, 0.1, 0.02)
        glutSolidCube(60)
        glPopMatrix()
    
    draw_engines(engine_glow_color, accent_color)
def draw_turret(x, y, z, color, accent_color):
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    glColor3f(*color)
    glutSolidSphere(7, 12, 12)
    
    glColor3f(*accent_color)
    glScalef(1.2, 1.2, 0.4)
    glutSolidSphere(6, 12, 12)
    
    glColor3f(0.2, 0.8, 1.0)
    for offset in [-2, 0, 2]:
        glPushMatrix()
        glTranslatef(8, offset, 2)
        glRotatef(90, 0, 1, 0)
        glutSolidSphere(2, 18, 8)
        glPopMatrix()
    glPopMatrix()
def draw_secondary_turret(x, y, z, accent_color):
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*accent_color)
    glutSolidSphere(4, 8, 8)
    
    glColor3f(0.2, 0.8, 1.0)
    glPushMatrix()
    glTranslatef(5, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(1, 12, 8)
    glPopMatrix()
    glPopMatrix()
def draw_engines(engine_glow_color, accent_color):
    
    global thruster_glow_intensity, moving_forward, moving_backward
    
    
    if moving_forward:
        
        base_glow = [0.0, 0.8, 1.0]
    else:
        
        base_glow = [1.0, 0.5, 0.1]
    
    
    enhanced_glow = [
        min(1.0, base_glow[0] + thruster_glow_intensity * 0.2),
        min(1.0, base_glow[1] + thruster_glow_intensity * 0.2),
        min(1.0, base_glow[2] + thruster_glow_intensity * 0.2)
    ]
    
    
    size_mult = 1.0 + thruster_glow_intensity * 0.8
    
    
    glPushMatrix()
    glTranslatef(-55, 0, 0)
    glColor3f(*accent_color)
    
    glScalef(0.4, 0.5, 0.5)
    glutSolidCube(40)
    glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-65, 0, 0)
    
    
    glColor3f(*enhanced_glow)
    
    glutSolidSphere(int(10 * size_mult), 16, 16)
    
    glPopMatrix()
    
    
    for y_offset in [-18, 18]:
        glPushMatrix()
        glTranslatef(-50, y_offset, 0)
        glColor3f(*accent_color)
        glScalef(0.2, 0.2, 0.2)
        glutSolidCube(20)
        
        
        glColor3f(*enhanced_glow)
        glTranslatef(-5, 0, 0)
        glutSolidSphere(int(4 * size_mult), 8, 8)
        glPopMatrix()
    
    
    glPushMatrix()
    
    if moving_forward:
        glColor3f(1.0, 0.6, 0.2)  
    else:
         glColor3f(1,1,1) 
    
    glTranslatef(-60, 0, 12)  
    glutSolidSphere(int(6 + thruster_glow_intensity * 2), 12, 12)  
    glPopMatrix()
    
    
    glPushMatrix()
    
    if moving_forward:
        glColor3f(0.0, 0.8, 1.0)  
    else:
        glColor3f(1.0, 0.6, 0.2)  
    
    
    glTranslatef(-58, 0, 6)
    glScalef(0.1, 0.1, 0.6)
    glutSolidCube(30)
    glPopMatrix()
    
def draw_enemy_ship():
    
    
    hull_color = (0.4, 0.1, 0.1)         
    accent_color = (1.0, 0.2, 0.0)       
    highlight_color = (0.8, 0.2, 0.2)    
    energy_core_color = (1.0, 0.7, 0.0)  
    engine_glow_color = (1.0, 0.5, 0.0)  
    
    
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(2.5, 0.9, 0.4)  
    glutSolidCube(25)
    glPopMatrix()
    
    
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(0, 0, 8)
    glScalef(2.0, 0.7, 0.15)
    glutSolidCube(25)
    glPopMatrix()
    
    
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(25, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(10, 25, 12)
    glPopMatrix()
    
    
    for y_offset, angle in [(20, 20), (-20, -20)]:
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(0, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.0, 0.15, 0.1)
        glutSolidCube(50)
        glPopMatrix()
    
    
    for x_offset in [-15, 0, 15]:
        glPushMatrix()
        glTranslatef(x_offset, 0, 10)
        
        glColor3f(*hull_color)
        glutSolidSphere(3, 8, 8)
        
        glColor3f(*accent_color)
        glRotatef(-90, 1, 0, 0)
        glutSolidSphere(1.5, 8, 8)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-40, 0, 0)
    
    
    glColor3f(*hull_color)
    glScalef(0.3, 0.4, 0.4)
    glutSolidCube(35)
    glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-46, 0, 0)
    glColor3f(*engine_glow_color)
    glutSolidSphere(6, 12, 12)
    glPopMatrix()
    
    
    for y_offset in [-15, 15]:
        glPushMatrix()
        glTranslatef(-35, y_offset, 0)
        
        glColor3f(*hull_color)
        glScalef(0.2, 0.2, 0.2)
        glutSolidCube(20)
        
        glTranslatef(-15, 0, 0)
        glColor3f(*engine_glow_color)
        glutSolidSphere(3, 8, 8)
        glPopMatrix()
    
    
    glPushMatrix()
    glColor3f(*energy_core_color)
    glTranslatef(-25, 0, 12)
    glutSolidSphere(4, 10, 10)
    
    glColor3f(*accent_color)
    glTranslatef(-10, 0, -6)
    glScalef(0.8, 0.1, 0.6)
    glutSolidCube(20)
    glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-55, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(1.0, 0.5, 0.0)  
    glutSolidSphere(5, 15, 8)
    glColor3f(1.0, 0.7, 0.0)  
    glutSolidSphere(3, 10, 8)
    glDisable(GL_BLEND)
    glPopMatrix()
def draw_golden_enemy_ship():
    
    
    hull_color = (0.8, 0.7, 0.1)         
    accent_color = (1.0, 0.9, 0.0)       
    highlight_color = (1.0, 1.0, 0.3)    
    energy_core_color = (1.0, 1.0, 0.5)  
    engine_glow_color = (1.0, 0.7, 0.0)  
    dark_accent = (0.5, 0.4, 0.0)        
    
    
    size_scale = 1.4
    
    
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(2.5 * size_scale, 0.9 * size_scale, 0.5 * size_scale)  
    glutSolidCube(25)
    glPopMatrix()
    
    
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(0, 0, 8 * size_scale)
    glScalef(2.0 * size_scale, 0.7 * size_scale, 0.15 * size_scale)
    glutSolidCube(25)
    
    
    glColor3f(*accent_color)
    glTranslatef(0, 0, 4)
    glScalef(0.85, 0.85, 1.0)
    glutSolidCube(25)
    glPopMatrix()
    
    
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(30 * size_scale, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(12 * size_scale), int(30 * size_scale), 16)  
    
    
    glColor3f(*accent_color)
    glTranslatef(0, 0, 10 * size_scale)
    glutSolidSphere(int(2 * size_scale), int(8 * size_scale), 16)
    glPopMatrix()
    
    
    for y_offset, angle in [(20 * size_scale, 20), (-20 * size_scale, -20)]:
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(0, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.2 * size_scale, 0.15 * size_scale, 0.1 * size_scale)
        glutSolidCube(50)
        
        
        glColor3f(*dark_accent)
        glTranslatef(-15, 0, 0)
        glScalef(0.2, 1.0, 1.2)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        glPopMatrix()
    
    
    for x_offset, y_offset in [(-18 * size_scale, 0), (0, 0), (18 * size_scale, 0), 
                          (-12 * size_scale, 10 * size_scale), (12 * size_scale, 10 * size_scale),
                          (-12 * size_scale, -10 * size_scale), (12 * size_scale, -10 * size_scale)]:
        glPushMatrix()
        glTranslatef(x_offset, y_offset, 10 * size_scale)
        
        glColor3f(*dark_accent)
        glutSolidSphere(int(3 * size_scale), 10, 10)
        
        glColor3f(*accent_color)
        glRotatef(-90, 1, 0, 0)
        glutSolidSphere(int(1.8 * size_scale), int(10 * size_scale), 10)
        
        
        glTranslatef(0, 0, 10 * size_scale)
        glColor3f(*highlight_color)
        glutSolidSphere(int(1.2 * size_scale), 8, 8)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-40 * size_scale, 0, 0)
    
    
    glColor3f(*hull_color)
    glScalef(0.4 * size_scale, 0.5 * size_scale, 0.5 * size_scale)
    glutSolidCube(35)
    
    
    glColor3f(*accent_color)
    glTranslatef(-20, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(3, 15, 16)
    glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-48 * size_scale, 0, 0)
    
    
    glColor3f(1.0, 1.0, 0.8)  
    glutSolidSphere(int(5 * size_scale), 16, 16)
    
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(1.0, 0.8, 0.0)  
    glutSolidSphere(int(8 * size_scale), 16, 16)
    glDisable(GL_BLEND)
    glPopMatrix()
    
    
    for y_offset in [-18 * size_scale, 18 * size_scale]:
        glPushMatrix()
        glTranslatef(-40 * size_scale, y_offset, 0)
        
        glColor3f(*dark_accent)
        glScalef(0.25 * size_scale, 0.25 * size_scale, 0.25 * size_scale)
        glutSolidCube(20)
        
        
        glColor3f(*accent_color)
        glTranslatef(-12, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidSphere(2, 8, 12)
        
        
        glColor3f(*engine_glow_color)
        glTranslatef(0, 0, 0)
        glutSolidSphere(int(4 * size_scale), 12, 12)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-25 * size_scale, 0, 15 * size_scale)  
    
    
    glColor3f(*energy_core_color)
    glutSolidSphere(int(5 * size_scale), 16, 16)
    
    
    glColor3f(*dark_accent)
    glRotatef(90, 1, 0, 0)
    glutSolidSphere(int(1.5 * size_scale), int(7 * size_scale), 16)
    
    
    glColor3f(*accent_color)
    glRotatef(90, 0, 1, 0)
    glTranslatef(0, 0, -10 * size_scale)
    glScalef(0.9 * size_scale, 0.1 * size_scale, 0.7 * size_scale)
    glutSolidCube(20)
    glPopMatrix()
    
    
    for z_offset, x_scale in [(8 * size_scale, 0.6), (0, 0.8), (-8 * size_scale, 0.6)]:
        glPushMatrix()
        glColor3f(*dark_accent)
        glTranslatef(-15 * size_scale, 0, 12 * size_scale + z_offset)
        glRotatef(90, 0, 1, 0)
        glScalef(x_scale, 0.1, 0.4)
        glutSolidCube(20 * size_scale)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-55 * size_scale, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    
    glColor3f(1.0, 0.7, 0.2)  
    glutSolidSphere(int(7 * size_scale), int(22 * size_scale), 12)
    
    
    glColor3f(1.0, 0.8, 0.3)  
    glutSolidSphere(int(5 * size_scale), int(16 * size_scale), 12)
    
    
    glColor3f(1.0, 0.9, 0.5)  
    glutSolidSphere(int(3 * size_scale), int(12 * size_scale), 8)
    
    glDisable(GL_BLEND)
    glPopMatrix()
def draw_black_red_enemy_ship():
    
    
    hull_color = (0.08, 0.03, 0.03)       
    accent_color = (0.8, 0.0, 0.0)        
    highlight_color = (0.4, 0.0, 0.0)     
    energy_core_color = (1.0, 0.1, 0.1)   
    dark_detail = (0.15, 0.05, 0.05)      
    
    
    size_scale = 1.45
    
    
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(2.6 * size_scale, 1.1 * size_scale, 0.6 * size_scale)  
    glutSolidCube(25)
    glPopMatrix()
    
    
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(0, 0, 9 * size_scale)
    glScalef(2.1 * size_scale, 0.9 * size_scale, 0.25 * size_scale)
    glutSolidCube(25)
    
    
    glColor3f(*dark_detail)
    glTranslatef(0, 0, 3)
    glScalef(0.9, 0.7, 0.5)
    glutSolidCube(25)
    glPopMatrix()
    
    
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(35 * size_scale, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(14 * size_scale), int(35 * size_scale), 16)  
    
    
    glColor3f(*accent_color)
    glTranslatef(0, 0, 15 * size_scale)
    glRotatef(90, 1, 0, 0)
    glutSolidSphere(int(2 * size_scale), int(8 * size_scale), 16)
    
    
    glColor3f(*dark_detail)
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0, 0, -5 * size_scale)
    glutSolidSphere(int(3 * size_scale), int(15 * size_scale), 8)
    glPopMatrix()
    
    
    for y_offset, angle in [(28 * size_scale, 25), (-28 * size_scale, -25)]:  
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(0, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.4 * size_scale, 0.15 * size_scale, 0.12 * size_scale)  
        glutSolidCube(50)
        
        
        glColor3f(*dark_detail)
        glTranslatef(-15, 0, 0)
        glScalef(0.15, 0.8, 1.0)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        glPopMatrix()
        
        
        glPushMatrix()
        glColor3f(*dark_detail)
        
        wing_tip_x = 0
        wing_tip_y = y_offset + math.sin(math.radians(angle)) * 35 * size_scale
        wing_tip_z = 0
        glTranslatef(wing_tip_x, wing_tip_y, wing_tip_z)
        glRotatef(angle + 90, 0, 0, 1)
        glutSolidSphere(int(2 * size_scale), int(12 * size_scale), 8)
        glPopMatrix()
    
    
    for x_offset, y_offset in [(-22 * size_scale, 0), (-11 * size_scale, 0), (0, 0), (11 * size_scale, 0), (22 * size_scale, 0), 
                          (-16 * size_scale, 14 * size_scale), (16 * size_scale, 14 * size_scale),
                          (-16 * size_scale, -14 * size_scale), (16 * size_scale, -14 * size_scale)]:
        glPushMatrix()
        glTranslatef(x_offset, y_offset, 12 * size_scale)
        
        glColor3f(*dark_detail)
        glutSolidSphere(int(3.5 * size_scale), 10, 10)
        
        glColor3f(*accent_color)
        glRotatef(-90, 1, 0, 0)
        glutSolidSphere(int(2 * size_scale), int(12 * size_scale), 10)
        
        
        glTranslatef(0, 0, 12 * size_scale)
        glColor3f(1.0, 0.3, 0.0)  
        glutSolidSphere(int(1.5 * size_scale), 8, 8)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-45 * size_scale, 0, 0)
    
    
    glColor3f(*hull_color)
    glScalef(0.5 * size_scale, 0.6 * size_scale, 0.6 * size_scale)  
    glutSolidCube(35)
    
    
    glColor3f(*dark_detail)
    glTranslatef(-20, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(4, 18, 16)
    
    
    glColor3f(*accent_color)
    glTranslatef(0, 0, 0)
    glutSolidSphere(2, 12, 12)
    glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-55 * size_scale, 0, 0)
    
    
    glColor3f(1.0, 0.3, 0.0)  
    glutSolidSphere(int(6 * size_scale), 16, 16)
    
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(0.8, 0.1, 0.0)  
    glutSolidSphere(int(10 * size_scale), 16, 16)
    glDisable(GL_BLEND)
    glPopMatrix()
    
    
    for y_offset in [-20 * size_scale, 20 * size_scale]:  
        glPushMatrix()
        glTranslatef(-43 * size_scale, y_offset, 0)
        
        glColor3f(*dark_detail)
        glScalef(0.3 * size_scale, 0.3 * size_scale, 0.3 * size_scale)
        glutSolidCube(20)
        
        
        glColor3f(*accent_color)
        glTranslatef(-12, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidSphere(2.5, 9, 12)
        
        
        glColor3f(1.0, 0.2, 0.0)  
        glTranslatef(0, 0, 0)
        glutSolidSphere(int(5 * size_scale), 12, 12)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-25 * size_scale, 0, 18 * size_scale)  
    
    
    glColor3f(*energy_core_color)
    glutSolidSphere(int(6 * size_scale), 16, 16)
    
    
    glColor3f(*dark_detail)
    glRotatef(45, 1, 0, 0)
    glutSolidSphere(int(1.8 * size_scale), int(8 * size_scale), 16)
    
    
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(1.8 * size_scale), int(8 * size_scale), 16)
    
    
    glColor3f(*accent_color)
    glRotatef(-45, 0, 1, 0)
    glTranslatef(-10 * size_scale, 0, -10 * size_scale)
    glScalef(1.2 * size_scale, 0.15 * size_scale, 0.15 * size_scale)
    glutSolidCube(25)
    glPopMatrix()
    
    
    for z_pos in range(-20, 21, 10):
        glPushMatrix()
        glColor3f(*dark_detail)
        glTranslatef(z_pos * size_scale * 0.7, 0, 15 * size_scale)
        glRotatef(90, 1, 0, 0)
        glutSolidSphere(int(2 * size_scale), int(10 * size_scale), 6)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-65 * size_scale, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    
    glColor3f(0.8, 0.1, 0.0)  
    glutSolidSphere(int(9 * size_scale), int(25 * size_scale), 12)
    
    
    glColor3f(1.0, 0.2, 0.0)  
    glutSolidSphere(int(7 * size_scale), int(20 * size_scale), 12)
    
    
    glColor3f(1.0, 0.5, 0.0)  
    glutSolidSphere(int(4 * size_scale), int(15 * size_scale), 8)
    
    glDisable(GL_BLEND)
    glPopMatrix()
def draw_boss_spaceship():
    
    
    hull_color = (0.06, 0.02, 0.08)       
    accent_color = (0.6, 0.0, 0.8)        
    highlight_color = (0.3, 0.0, 0.4)     
    energy_core_color = (1.0, 0.2, 1.0)   
    dark_detail = (0.12, 0.04, 0.15)      
    
    
    size_scale = 6.0  
    
    
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(2.6 * size_scale, 1.1 * size_scale, 0.6 * size_scale)  
    glutSolidCube(25)
    glPopMatrix()
    
    
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(0, 0, 9 * size_scale)
    glScalef(2.1 * size_scale, 0.9 * size_scale, 0.25 * size_scale)
    glutSolidCube(25)
    
    
    glColor3f(*dark_detail)
    glTranslatef(0, 0, 3)
    glScalef(0.9, 0.7, 0.5)
    glutSolidCube(25)
    glPopMatrix()
    
    
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(35 * size_scale, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(14 * size_scale), int(35 * size_scale), 16)  
    
    
    glColor3f(*accent_color)
    glTranslatef(0, 0, 15 * size_scale)
    glRotatef(90, 1, 0, 0)
    glutSolidSphere(int(2 * size_scale), int(8 * size_scale), 16)
    
    
    glColor3f(*dark_detail)
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0, 0, -5 * size_scale)
    glutSolidSphere(int(3 * size_scale), int(15 * size_scale), 8)
    glPopMatrix()
    
    
    for y_offset, angle in [(28 * size_scale, 25), (-28 * size_scale, -25)]:  
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(0, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.4 * size_scale, 0.15 * size_scale, 0.12 * size_scale)  
        glutSolidCube(50)
        
        
        glColor3f(*dark_detail)
        glTranslatef(-15, 0, 0)
        glScalef(0.15, 0.8, 1.0)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        glPopMatrix()
        
        
        glPushMatrix()
        glColor3f(*dark_detail)
        
        wing_tip_x = 0
        wing_tip_y = y_offset + math.sin(math.radians(angle)) * 35 * size_scale
        wing_tip_z = 0
        glTranslatef(wing_tip_x, wing_tip_y, wing_tip_z)
        glRotatef(angle + 90, 0, 0, 1)
        glutSolidSphere(int(2 * size_scale), int(12 * size_scale), 8)
        glPopMatrix()
    
    
    for y_offset, angle in [(35 * size_scale, 40), (-35 * size_scale, -40)]:
        glPushMatrix()
        glColor3f(*highlight_color)
        glTranslatef(-20 * size_scale, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.0 * size_scale, 0.15 * size_scale, 0.1 * size_scale)
        glutSolidCube(60)
        glPopMatrix()
    
    
    for x_offset, y_offset in [(-25 * size_scale, 0), (-12 * size_scale, 0), (0, 0), (12 * size_scale, 0), (25 * size_scale, 0), 
                          (-20 * size_scale, 18 * size_scale), (20 * size_scale, 18 * size_scale),
                          (-20 * size_scale, -18 * size_scale), (20 * size_scale, -18 * size_scale),
                          (-10 * size_scale, 30 * size_scale), (10 * size_scale, 30 * size_scale),
                          (-10 * size_scale, -30 * size_scale), (10 * size_scale, -30 * size_scale)]:
        glPushMatrix()
        glTranslatef(x_offset, y_offset, 12 * size_scale)
        
        glColor3f(*dark_detail)
        glutSolidSphere(int(3.5 * size_scale), 10, 10)
        
        glColor3f(*accent_color)
        glRotatef(-90, 1, 0, 0)
        glutSolidSphere(int(2 * size_scale), int(12 * size_scale), 10)
        
        
        glTranslatef(0, 0, 12 * size_scale)
        glColor3f(1.0, 0.3, 1.0)  
        glutSolidSphere(int(1.5 * size_scale), 8, 8)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-45 * size_scale, 0, 0)
    
    
    glColor3f(*hull_color)
    glScalef(0.5 * size_scale, 0.6 * size_scale, 0.6 * size_scale)  
    glutSolidCube(35)
    
    
    glColor3f(*dark_detail)
    glTranslatef(-20, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(4, 18, 16)
    
    
    glColor3f(*accent_color)
    glTranslatef(0, 0, 0)
    glutSolidSphere(2, 12, 12)
    glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-55 * size_scale, 0, 0)
    
    
    glColor3f(0.8, 0.3, 1.0)  
    glutSolidSphere(int(6 * size_scale), 16, 16)
    
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(0.6, 0.1, 0.8)  
    glutSolidSphere(int(10 * size_scale), 16, 16)
    glDisable(GL_BLEND)
    glPopMatrix()
    
    
    for y_offset in [-20 * size_scale, 20 * size_scale]:  
        glPushMatrix()
        glTranslatef(-43 * size_scale, y_offset, 0)
        
        glColor3f(*dark_detail)
        glScalef(0.3 * size_scale, 0.3 * size_scale, 0.3 * size_scale)
        glutSolidCube(20)
        
        
        glColor3f(*accent_color)
        glTranslatef(-12, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidSphere(3, 9, 12)
        
        
        glColor3f(0.8, 0.2, 1.0)  
        glTranslatef(0, 0, 0)
        glutSolidSphere(int(5 * size_scale), 12, 12)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-25 * size_scale, 0, 20 * size_scale)  
    
    
    glColor3f(*energy_core_color)
    glutSolidSphere(int(8 * size_scale), 16, 16)
    
    
    glColor3f(*dark_detail)
    glRotatef(45, 1, 0, 0)
    glutSolidSphere(int(1.8 * size_scale), int(10 * size_scale), 16)
    
    
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(1.8 * size_scale), int(10 * size_scale), 16)
    
    
    glColor3f(*accent_color)
    glRotatef(-45, 0, 1, 0)
    glTranslatef(-10 * size_scale, 0, -10 * size_scale)
    glScalef(1.2 * size_scale, 0.15 * size_scale, 0.15 * size_scale)
    glutSolidCube(25)
    glPopMatrix()
    
    
    for z_pos in range(-20, 21, 8):  
        glPushMatrix()
        glColor3f(*dark_detail)
        glTranslatef(z_pos * size_scale * 0.7, 0, 15 * size_scale)
        glRotatef(90, 1, 0, 0)
        glutSolidSphere(int(2 * size_scale), int(10 * size_scale), 6)
        glPopMatrix()
    
    
    for x_offset, y_factor in [(-20, 1), (0, 1.1), (20, 1)]:
        glPushMatrix()
        glColor3f(*hull_color)
        glTranslatef(x_offset * size_scale, 0, 5 * size_scale)
        glScalef(0.5 * size_scale, 1.0 * size_scale * y_factor, 0.3 * size_scale)
        glutSolidCube(30)
        glPopMatrix()
    
    
    glPushMatrix()
    glTranslatef(-65 * size_scale, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    
    glColor3f(0.7, 0.2, 1.0)  
    glutSolidSphere(int(8 * size_scale), int(25 * size_scale), 16)
    
    
    glColor3f(0.9, 0.3, 1.0)  
    glutSolidSphere(int(6 * size_scale), int(20 * size_scale), 12)
    
    
    glColor3f(1.0, 0.5, 1.0)  
    glutSolidSphere(int(4 * size_scale), int(15 * size_scale), 8)
    
    glDisable(GL_BLEND)
    glPopMatrix()
def draw_laser_beam(is_enemy=False):
    if is_enemy:
        if cheat_mode_enabled:
            glColor3f(0.0, 0.3, 1.0)
        else:
            glColor3f(1, 0.3, 0)
    else:
        if cheat_mode_enabled:
            glColor3f(0.8, 0.3, 0.0)
        else:
            glColor3f(0, 0.8, 1)
    glPushMatrix()
    glScalef(30, 0.5, 0.5)
    glutSolidCube(5)
    glPopMatrix()
def draw_explosion(size):
    
    glColor3f(1, 0.5, 0)  
    glutSolidSphere(int(size), 10, 10)
    
    glPushMatrix()
    glColor3f(1, 0, 0)  
    glutSolidSphere(int(size * 0.7), 8, 8)
    glPopMatrix()
def draw_radar():
    
    glPushMatrix()
    
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    
    glColor3f(0, 0.7, 0.7)  
    
    glBegin(GL_LINES)
    for i in range(360):
        angle1 = i * math.pi / 180
        angle2 = (i + 1) * math.pi / 180
        glVertex2f(100 + 80 * math.cos(angle1), 100 + 80 * math.sin(angle1))
        glVertex2f(100 + 80 * math.cos(angle2), 100 + 80 * math.sin(angle2))
    glEnd()
    
    
    glColor3f(0, 0.5, 0.5)  
    glBegin(GL_LINES)
    glVertex2f(20, 100)
    glVertex2f(180, 100)
    glVertex2f(100, 20)
    glVertex2f(100, 180)
    glEnd()
    
    
    glColor3f(0, 1, 0.7)  
    glBegin(GL_LINES)
    glVertex2f(100, 100)
    glVertex2f(100 + 80 * math.cos(player_rotation * math.pi / 180), 
               100 + 80 * math.sin(player_rotation * math.pi / 180))
    glEnd()
    
    
    glPointSize(5)
    glBegin(GL_POINTS)
    glColor3f(1, 0.3, 0.3)  
    for enemy in enemies:
        
        dx = enemy[0] - player_pos[0]
        dy = enemy[1] - player_pos[1]
        
        distance = math.sqrt(dx*dx + dy*dy) / (battlefield_size/2) * 70
        if distance < 80:  
            angle = math.atan2(dy, dx) - player_rotation * math.pi / 180
            radar_x = 100 + distance * math.cos(angle)
            radar_y = 100 + distance * math.sin(angle)
            glVertex2f(radar_x, radar_y)
    glEnd()
    
    
    directions = ['N', 'E', 'S', 'W']
    glColor3f(0, 0.7, 0.7)  
    for i, label in enumerate(directions):
        
        base_angle = i * 90  
        
        angle = (base_angle - player_rotation) * math.pi / 180
        label_x = 100 + 90 * math.cos(angle) - 8  
        label_y = 100 + 90 * math.sin(angle) - 8
        draw_text(label_x, label_y, label)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glPopMatrix()
def draw_hud():
    
    global game_won, missile_used_this_level, combo_count, combo_timer, combo_multiplier
    global shield_active, shield_timer, hit_flash_duration
    
    
    glColor3f(*hud_color)
    
    
    health_percentage = player_health / player_max_health * 100
    
    
    if hit_flash_duration > 0:
        glColor3f(1.0, 0.0, 0.0)  
    else:
        glColor3f(*hud_color)  
    
    
    draw_text(10, 775, f"HEALTH: {int(health_percentage)}%", GLUT_BITMAP_TIMES_ROMAN_24)
    
    
    draw_text(10, 730, f"LIVES: {player_lives}", GLUT_BITMAP_TIMES_ROMAN_24)
    
    
    glColor3f(0.0, 1.0, 0.0)  
    draw_text(800, 750, f"SCORE: {score}")
    
    
    glColor3f(1.0, 1.0, 1.0)  
    draw_text(800, 780, f"EXP: {player_experience}/100", GLUT_BITMAP_TIMES_ROMAN_24)
    
    
    glColor3f(*hud_color)
    
    if cheat_mode_enabled:
        draw_text(750, 720, f"Cheat Mode: ACTIVATED")
    else:
        draw_text(750, 720, f"Cheat Mode: DIACTIVATED")
        
    
    glColor3f(*hud_color)
    
    
    
    if player_level == 4:
        
        pass
    else:
        
        glColor3f(1.0, 0.5, 0.0)  
        draw_text(450, 780, f"LEVEL {player_level}", GLUT_BITMAP_TIMES_ROMAN_24)
    
    
    if player_level == 4:
        
        glColor3f(1.0, 0.5, 0.0)  
        draw_text(450, 780, "FINAL LEVEL", GLUT_BITMAP_TIMES_ROMAN_24)
        
        
        boss_health = 0
        boss_max_health = 10000
        for enemy in enemies:
            if len(enemy) > 7 and enemy[7] == "boss" and len(enemy) > 8:
                boss_health = enemy[8]
                break
        
        if boss_health > 0:
            
            health_percentage = (boss_health / boss_max_health) * 100
            
            
            if health_percentage < 25:
                glColor3f(1.0, 0.0, 0.0)  
            elif health_percentage < 50:
                glColor3f(1.0, 0.8, 0.0)  
            else:
                glColor3f(0.0, 1.0, 0.0)  
                
            draw_text(430, 740, f"BOSS HEALTH: {int(health_percentage)}%", GLUT_BITMAP_TIMES_ROMAN_24)
    
    
    if game_won:
        
        glColor3f(1.0, 0.84, 0.0)  
        draw_text(400, 500, "BOSS DEFEATED - YOU WON!", GLUT_BITMAP_HELVETICA_18)
        
        
        glColor3f(*hud_color)
        draw_text(380, 300, f"Current Score: {score}", GLUT_BITMAP_HELVETICA_18)
        draw_text(390, 350, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
    
    
    if game_over:
        
        glColor3f(1.0, 0.0, 0.0)  
        draw_text(400, 500, "GAME OVER", GLUT_BITMAP_HELVETICA_18)
        glColor3f(1.0, 1.0, 1.0)  
        draw_text(380, 300, f"Final Score: {score}", GLUT_BITMAP_HELVETICA_18)
        draw_text(390, 350, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
        
    
    
    if missile_used_this_level:
        glColor3f(1.0, 0.0, 0.0)  
        draw_text(10, 690, "MISSILE: USED")
    else:
        glColor3f(0.0, 1.0, 0.0)  
        draw_text(10, 690, "MISSILE: READY")
    
    
    if shield_active:
        
        shield_seconds = int(shield_timer / 60)
        
        
        if shield_seconds < 5:
            glColor3f(1.0, 0.0, 0.0)  
        elif shield_seconds < 10:
            glColor3f(1.0, 1.0, 0.0)  
        else:
            glColor3f(0.0, 1.0, 1.0)  
            
        draw_text(10, 660, f"SHIELD: ACTIVE ({shield_seconds}s)")
        
        
        timer_width = (shield_timer / shield_max_duration) * 100
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(10, 660)
        glVertex2f(110, 660)
        glVertex2f(110, 665)
        glVertex2f(10, 665)
        glEnd()
        
        
        if shield_seconds < 5:
            glColor3f(1.0, 0.0, 0.0)  
        elif shield_seconds < 10:
            glColor3f(1.0, 1.0, 0.0)  
        else:
            glColor3f(0.0, 1.0, 1.0)  
            
        glBegin(GL_QUADS)
        glVertex2f(10, 660)
        glVertex2f(10 + timer_width, 660)
        glVertex2f(10 + timer_width, 665)
        glVertex2f(10, 665)
        glEnd()
        
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    elif shield_used_in_game:
        glColor3f(1.0, 0.0, 0.0)  
        draw_text(10, 670, "SHIELD: USED")
    else:
        glColor3f(0.0, 1.0, 0.0)
        draw_text(10, 660, "SHIELD: READY (Press 'P')")
    
    
    if combo_count > 0:
        
        if combo_multiplier == 3:
            combo_color = (1.0, 0.0, 1.0)  
        elif combo_multiplier == 2:
            combo_color = (1.0, 0.5, 0.0)  
        else:
            combo_color = (1.0, 1.0, 0.0)  
        
        
        glColor3f(*combo_color)
        draw_text(10, 630, f"COMBO: {combo_count}x ({combo_multiplier}x SCORE)")
    
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    draw_play_pause_button(play_pause_button_pos[0], play_pause_button_pos[1], button_size, game_paused)
    draw_restart_button(restart_button_pos[0], restart_button_pos[1], button_size)
    
    glColor3f(1.0, 1.0, 1.0)  
    if game_paused:
        draw_text(play_pause_button_pos[0] - 15, play_pause_button_pos[1] - button_size/2 - 15, "Play")
    else:
        draw_text(play_pause_button_pos[0] - 18, play_pause_button_pos[1] - button_size/2 - 15, "Pause")
    draw_text(restart_button_pos[0] - 25, restart_button_pos[1] - button_size/2 - 15, "Restart")
    
    if game_paused and not game_over and not game_won:
        glColor3f(1.0, 1.0, 0.0)  
        draw_text(450, 400, "GAME PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(420, 350, "Click Play button to resume", GLUT_BITMAP_HELVETICA_18)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
def draw_battlefield():
    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(1, 1, 1)
    for i in range(1000):
        x = random.uniform(-battlefield_size*3, battlefield_size*3)
        y = random.uniform(-battlefield_size*3, battlefield_size*3)
        z = random.uniform(-battlefield_size*2, 0)
        glVertex3f(x, y, z)
    glEnd()
    
    draw_animated_floor()
    draw_battlefield_boundaries()
def draw_animated_floor():
    global grid_offset_x, grid_offset_y, game_paused, game_over, game_won
    
    
    if not game_paused and not game_over and not game_won:
        rad = player_rotation * math.pi / 180
        movement_x = math.cos(rad) * grid_animation_speed
        movement_y = math.sin(rad) * grid_animation_speed
        
        grid_offset_x = (grid_offset_x + movement_x) % grid_line_spacing
        grid_offset_y = (grid_offset_y + movement_y) % grid_line_spacing
    
    glBegin(GL_LINES)
    glColor3f(0.2, 0.4, 0.8)
    
    grid_size = battlefield_size * 2
    
    for i in range(-grid_size, grid_size + grid_line_spacing, grid_line_spacing):
        grid_pos = i - grid_offset_x
        glVertex3f(grid_pos, -grid_size, 0)
        glVertex3f(grid_pos, grid_size, 0)
    
    for i in range(-grid_size, grid_size + grid_line_spacing, grid_line_spacing):
        grid_pos = i - grid_offset_y
        glVertex3f(-grid_size, grid_pos, 0)
        glVertex3f(grid_size, grid_pos, 0)
    
    glEnd()
def draw_player():
    if camera_mode == 1:
        return
        
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_rotation, 0, 0, 1)
    draw_spaceship(True)
    
    
    if shield_active:
        draw_shield()
    
    glPopMatrix()
def draw_enemies():
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy[0], enemy[1], enemy[2])
        glRotatef(enemy[3], 0, 0, 1)
        
        if len(enemy) > 7:
            if enemy[7] == "golden":
                draw_golden_enemy_ship()
            elif enemy[7] == "black-red":
                draw_black_red_enemy_ship()
            elif enemy[7] == "boss":
                draw_boss_spaceship()
            else:
                draw_spaceship(False)
        else:
            draw_spaceship(False)
        
        glPopMatrix()
def draw_bullets():
    for bullet in player_bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glRotatef(bullet[3], 0, 0, 1)
        draw_laser_beam(False)
        glPopMatrix()
    
    for bullet in enemy_bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glRotatef(bullet[3], 0, 0, 1)
        draw_laser_beam(True)
        glPopMatrix()
    
    for missile in player_missiles:
        glPushMatrix()
        glTranslatef(missile[0], missile[1], missile[2])
        glRotatef(missile[3], 0, 0, 1)
        
        if missile[6] == 0:
            draw_missile()
        else:
            draw_missile_explosion(missile[7] * 4)  
        
        glPopMatrix()
def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement and actions
    """
    global player_pos, player_rotation, player_speed, player_boost_speed, player_bullets, game_over, camera_mode, grid_animation_speed, camera_distance
    global moving_forward, moving_backward, thruster_glow_intensity, cheat_mode_enabled, player_missiles, missile_used_this_level
    global shield_active, shield_timer, shield_used_in_game
    
    if key == b'c':
        cheat_mode_enabled = not cheat_mode_enabled
        print("Cheat mode:", "ON" if cheat_mode_enabled else "OFF")

    if game_over or game_won:
        if key == b'r':  
            reset_game()
        return
        
    
    if key == b'w':
        rad = player_rotation * math.pi / 180
        
        movement_speed = player_boost_speed
        
        new_x = player_pos[0] + math.cos(rad) * movement_speed
        new_y = player_pos[1] + math.sin(rad) * movement_speed
        
        
        if abs(new_x) < battlefield_size and abs(new_y) < battlefield_size:
            player_pos[0] = new_x
            player_pos[1] = new_y
            moving_forward = True
            moving_backward = False
        else:
            
            if abs(new_x) < battlefield_size:
                player_pos[0] = new_x
            if abs(new_y) < battlefield_size:
                player_pos[1] = new_y
            moving_forward = True
    
    
    if key == b's':
        rad = player_rotation * math.pi / 180
        
        movement_speed = player_speed
        
        new_x = player_pos[0] - math.cos(rad) * movement_speed
        new_y = player_pos[1] - math.sin(rad) * movement_speed
        
        
        if abs(new_x) < battlefield_size and abs(new_y) < battlefield_size:
            player_pos[0] = new_x
            player_pos[1] = new_y
            moving_backward = True
            moving_forward = False
        else:
            
            if abs(new_x) < battlefield_size:
                player_pos[0] = new_x
            if abs(new_y) < battlefield_size:
                player_pos[1] = new_y
            moving_backward = True
    
    
    if key not in (b'w', b's'):
        moving_forward = False
        moving_backward = False
    
    
    if key == b'a':
        rad = (player_rotation + 90) * math.pi / 180  
        
        movement_speed = player_boost_speed
        
        new_x = player_pos[0] + math.cos(rad) * movement_speed
        new_y = player_pos[1] + math.sin(rad) * movement_speed
        
        
        if abs(new_x) < battlefield_size and abs(new_y) < battlefield_size:
            player_pos[0] = new_x
            player_pos[1] = new_y
        else:
            
            if abs(new_x) < battlefield_size:
                player_pos[0] = new_x
            if abs(new_y) < battlefield_size:
                player_pos[1] = new_y
    
    
    if key == b'd':
        rad = (player_rotation - 90) * math.pi / 180  
        
        movement_speed = player_boost_speed
        
        new_x = player_pos[0] + math.cos(rad) * movement_speed
        new_y = player_pos[1] + math.sin(rad) * movement_speed
        
        
        if abs(new_x) < battlefield_size and abs(new_y) < battlefield_size:
            player_pos[0] = new_x
            player_pos[1] = new_y
        else:
            
            if abs(new_x) < battlefield_size:
                player_pos[0] = new_x
            if abs(new_y) < battlefield_size:
                player_pos[1] = new_y
    
    
    if key == b'r':
        new_z = player_pos[2] + player_speed
        
        if new_z < 500:  
            player_pos[2] = new_z
    
    
    if key == b'f':
        new_z = player_pos[2] - player_speed
        
        if new_z > 20:  
            player_pos[2] = new_z
    
    
    if key == b'l':
        camera_mode = 1 - camera_mode  
        
    
    if key in (b'\x10', b' '):  
        
        rad = player_rotation * math.pi / 180
        offsets = [
            (-18, 18),   
            (-9, 9),     
            (0, 0),      
            (9, -9),     
            (18, -18)    
        ]
        for offset_x, offset_y in offsets:
            laser = [
                player_pos[0] + 30 * math.cos(rad) + offset_x * math.sin(rad),
                player_pos[1] + 30 * math.sin(rad) + offset_y * math.cos(rad),
                player_pos[2],
                player_rotation,
                player_boost_speed + 20,  
                200  
            ]
            player_bullets.append(laser)
    
    
    if key == b'm':
        if not missile_used_this_level and len(player_missiles) < 3:  
            rad = player_rotation * math.pi / 180
            missile = [
                player_pos[0] + 40 * math.cos(rad),
                player_pos[1] + 40 * math.sin(rad),
                player_pos[2],
                player_rotation,
                30,  
                150,  
                0,    
                0     
            ]
            player_missiles.append(missile)
            missile_used_this_level = True  
            
    
    if key == b'p':
        if not shield_active and not shield_used_in_game:  
            shield_active = True
            shield_timer = shield_max_duration  
            shield_used_in_game = True  
def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for player rotation and camera distance
    """
    global player_rotation, camera_distance
    
    
    if key == GLUT_KEY_LEFT:
        player_rotation = (player_rotation + 5) % 360
    
    
    if key == GLUT_KEY_RIGHT:
        player_rotation = (player_rotation - 5) % 360
    
    
    if key == GLUT_KEY_UP:
        camera_distance = min(camera_distance + 10, 1000)  
    
    
    if key == GLUT_KEY_DOWN:
        camera_distance = max(camera_distance - 10, 50)  
def mouseListener(button, state, x, y):
    
    global game_paused, game_over
    
    
    y = 800 - y  
    
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        
        if is_point_in_circle(x, y, play_pause_button_pos[0], play_pause_button_pos[1], button_size/2):
            
            game_paused = not game_paused
            if game_paused:
                print("Game paused")
            else:
                print("Game resumed")
        elif is_point_in_circle(x, y, restart_button_pos[0], restart_button_pos[1], button_size/2):
            reset_game()
            print("Game restarted")
def update_game():
    """
    Update game state - move bullets, check collisions, etc.
    """
    global player_bullets, enemy_bullets, enemies, score, game_over, thruster_glow_intensity
    global player_health, player_lives, hit_flash_duration, player_experience, player_level, game_won, enemies_respawn_timer
    global player_missiles, missile_used_this_level, combo_count, combo_timer, combo_multiplier
    global shield_active, shield_timer, auto_target, auto_move_timer, cheat_fire_timer, shield_used_in_game
    
    
    if combo_timer > 0:
        combo_timer -= 1
        
        if combo_timer == 0:
            combo_count = 0
            combo_multiplier = 1
    
    
    
    if game_won:
        
        enemies_respawn_timer += 1
        
        
        if len(enemies) == 0 and enemies_respawn_timer > 180:  
            spawn_enemy("boss")
            for i in range(5):
                spawn_enemy("black-red")
            for i in range(3):
                spawn_enemy("golden")
    
    
    if shield_active:
        shield_timer -= 1
        if shield_timer <= 0:
            shield_active = False
    
    
    if hit_flash_duration > 0:
        hit_flash_duration -= 1
    
    
    thruster_glow_intensity = 0.0
    
    
    for missile in player_missiles[:]:
        
        if missile[6] == 1:
            
            missile[7] += 1
            
            
            if missile[7] < 3:  
                enemies_in_blast = []
                blast_radius = 500  
                
                for enemy in enemies:
                    
                    dx = enemy[0] - missile[0]
                    dy = enemy[1] - missile[1]
                    dz = enemy[2] - missile[2]
                    
                    
                    dist_3d = math.sqrt(dx*dx + dy*dy + dz*dz)
                    
                    
                    if dist_3d < blast_radius:
                        enemies_in_blast.append(enemy)
                
                
                destroy_count = 0
                for enemy in enemies_in_blast[:]:
                    if enemy in enemies:  
                        
                        if len(enemy) > 7 and enemy[7] == "boss":
                            if len(enemy) > 8:
                                enemy[8] -= 4000  
                                if enemy[8] <= 0:
                                    enemies.remove(enemy)
                                    destroy_count += 1
                            else:
                                enemy.append(10000 - 4000)  
                        else:
                            
                            enemies.remove(enemy)
                            destroy_count += 1
                
                
                if destroy_count > 0:
                    
                    combo_count += destroy_count
                    combo_timer = max_combo_time  
                    
                    
                    if combo_count >= 10:
                        combo_multiplier = 3
                    elif combo_count >= 5:
                        combo_multiplier = 2
                    else:
                        combo_multiplier = 1
                
                
                score += 100 * destroy_count * combo_multiplier  
                
                
                if player_experience >= 100:
                    player_level += 1
                    player_experience -= 100
                    missile_used_this_level = False  
                    
                    
                    combo_count = 0
                    combo_timer = 0
                    combo_multiplier = 1
                    
                    enemies.clear()
                    
                    
                    if player_level == 4:
                        spawn_enemy("boss")
                        for i in range(3):
                            spawn_enemy("black-red")
                    elif player_level == 3:
                        for i in range(9):
                            spawn_enemy("black-red")
                        for i in range(5):
                            spawn_enemy("golden")
                    else:
                        for i in range(8):
                            spawn_enemy("golden") 
                        for i in range(5):
                            spawn_enemy("red")
            
            if missile[7] > 20:  
                player_missiles.remove(missile)
            continue
                
        
        rad = missile[3] * math.pi / 180
        missile[0] += math.cos(rad) * missile[4]
        missile[1] += math.sin(rad) * missile[4]
        missile[5] -= 1
        
        
        if missile[5] <= 0:
            
            missile[6] = 1
            continue
            
        
        
        for enemy in enemies:
            
            dx = enemy[0] - missile[0]
            dy = enemy[1] - missile[1]
            dz = enemy[2] - missile[2]
            
            
            dist_3d = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            
            dist_2d = math.sqrt(dx*dx + dy*dy)
            
            
            missile_dir_x = math.cos(rad)
            missile_dir_y = math.sin(rad)
            
            
            dot_product = (dx * missile_dir_x + dy * missile_dir_y) / (dist_2d + 0.0001)
            
            
            
            if (dot_product > 0.5 and dist_2d < 150):
                
                missile[6] = 1
                break
    
    
    for bullet in player_bullets[:]:  
        
        rad = bullet[3] * math.pi / 180
        bullet[0] += math.cos(rad) * bullet[4]
        bullet[1] += math.sin(rad) * bullet[4]
        
        
        bullet[5] -= 1
        
        
        if bullet[5] <= 0:
            player_bullets.remove(bullet)
            continue
        
        
        for enemy in enemies[:]:  
            dx = bullet[0] - enemy[0]
            dy = bullet[1] - enemy[1]
            dz = bullet[2] - enemy[2]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            
            hit_radius = 30
            if len(enemy) > 7:
                if enemy[7] == "boss":
                    hit_radius = 50  
                elif enemy[7] == "black-red" or enemy[7] == "golden":
                    hit_radius = 35  
            
            if distance < hit_radius:  
                if bullet in player_bullets:  
                    player_bullets.remove(bullet)
                
                
                if len(enemy) > 7:
                    if enemy[7] == "boss":
                        
                        if len(enemy) > 8:
                            enemy[8] -= 100  
                            if enemy[8] > 0:
                                continue  
                        else:
                            
                            enemy.append(10000)  
                            continue  
                    elif enemy[7] == "black-red":
                        
                        if len(enemy) > 8:
                            enemy[8] -= 1
                            if enemy[8] > 0:
                                continue  
                        else:
                            
                            enemy.append(3)
                            continue
                    elif enemy[7] == "golden":
                        
                        if len(enemy) > 8:
                            enemy[8] -= 1
                            if enemy[8] > 0:
                                continue  
                        else:
                            
                            enemy.append(2)
                            continue
                
                enemies.remove(enemy)
                score += 100
                
                
                player_experience += 10
                
                
                if player_level == 4 and len(enemy) > 7 and enemy[7] == "boss":
                    game_won = True
                
                
                if player_experience >= 100:
                    player_level += 1
                    player_experience -= 100  
                    missile_used_this_level = False  
                    
                    
                    enemies.clear()
                    
                    
                    if player_level == 4:
                        
                        spawn_enemy("boss")
                        
                        
                        for i in range(3):
                            spawn_enemy("black-red")
                    
                    
                    elif player_level == 3:
                        
                        for i in range(9):
                            spawn_enemy("black-red")
                            
                        
                        for i in range(5):
                            spawn_enemy("golden")
                    
                    else:
                        
                        for i in range(8):
                            spawn_enemy("golden")
                            
                        
                        for i in range(5):
                            spawn_enemy("red")
                else:
                    
                    if player_level < 4 and not game_won:
                        spawn_enemy("red")
                    elif game_won and len(enemies) < 5:
                        
                        enemy_types = ["red", "golden", "black-red"]
                        spawn_enemy(random.choice(enemy_types))
                
                
                combo_count += 1
                combo_timer = max_combo_time  
                
                
                if combo_count >= 10:
                    combo_multiplier = 3  
                elif combo_count >= 5:
                    combo_multiplier = 2  
                else:
                    combo_multiplier = 1  
                
                
                score += 100 * combo_multiplier  
    
    
    if game_over:
        return
    
    
    for bullet in enemy_bullets[:]:
        
        rad = bullet[3] * math.pi / 180
        bullet[0] += math.cos(rad) * bullet[4]
        bullet[1] += math.sin(rad) * bullet[4]
        
        
        bullet[5] -= 1
        
        
        if bullet[5] <= 0:
            enemy_bullets.remove(bullet)
            continue
        
        
        dx = bullet[0] - player_pos[0]
        dy = bullet[1] - player_pos[1]
        dz = bullet[2] - player_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < 40:  
            enemy_bullets.remove(bullet)
            
            
            damage = damage_per_hit
            if len(bullet) > 6 and bullet[6] == "boss":
                damage = damage_per_hit * 2
            
            
            if not shield_active and not cheat_mode_enabled:
                player_health -= damage
                hit_flash_duration = 10
                
                
                if player_health <= 0:
                    player_lives -= 1
                    
                    if player_lives > 0:
                        
                        player_health = player_max_health  
                    else:
                        
                        game_over = True
    
    
    for enemy in enemies:
        
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]
        dz = player_pos[2] - enemy[2]
        distance_to_player = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        
        preferred_distance = enemy[6]
        
        
        if random.random() < 0.02:  
            
            if random.random() < 0.7:  
                enemy[5] = [enemy[0], enemy[1], enemy[2]]
            else:  
                
                angle = random.uniform(0, 2 * math.pi)
                distance = preferred_distance * random.uniform(0.9, 1.1)
                
                target_x = player_pos[0] + math.cos(angle) * distance
                target_y = player_pos[1] + math.sin(angle) * distance
                target_z = random.uniform(player_pos[2] - 100, player_pos[2] + 100)
                
                
                target_x = max(min(target_x, battlefield_size/2 - 50), -battlefield_size/2 + 50)
                target_y = max(min(target_y, battlefield_size/2 - 50), -battlefield_size/2 + 50)
                target_z = max(min(target_z, 500), 50)
                
                enemy[5] = [target_x, target_y, target_z]
        
        
        if enemy[5][0] != 0 or enemy[5][1] != 0 or enemy[5][2] != 0:
            target_x, target_y, target_z = enemy[5]
            dx_target = target_x - enemy[0]
            dy_target = target_y - enemy[1]
            dz_target = target_z - enemy[2]
            distance_to_target = math.sqrt(dx_target*dx_target + dy_target*dy_target + dz_target*dz_target)
            
            if distance_to_target > 10:  
                
                move_speed = 2
                enemy[0] += dx_target / distance_to_target * move_speed
                enemy[1] += dy_target / distance_to_target * move_speed
                enemy[2] += dz_target / distance_to_target * move_speed
        
        
        enemy[0] = max(min(enemy[0], battlefield_size/2 - 50), -battlefield_size/2 + 50)
        enemy[1] = max(min(enemy[1], battlefield_size/2 - 50), -battlefield_size/2 + 50)
        enemy[2] = max(min(enemy[2], 500), 50)
        
        
        enemy[3] = math.degrees(math.atan2(dy, dx)) % 360
        
        
        if distance_to_player < preferred_distance * 0.8:
            
            move_dir_x = enemy[0] - player_pos[0]
            move_dir_y = enemy[1] - player_pos[1]
            move_dir_len = math.sqrt(move_dir_x*move_dir_x + move_dir_y*move_dir_y)
            
            if move_dir_len > 0:  
                
                move_speed = 5  
                enemy[0] += move_dir_x / move_dir_len * move_speed
                enemy[1] += move_dir_y / move_dir_len * move_speed
        
        
        
        enemy[4] -= 1
        
        
        if enemy[4] <= 0 and distance_to_player < max_shooting_distance:
            
            shoot_chance = enemy_shoot_chance
            if len(enemy) > 7 and enemy[7] == "boss":
                shoot_chance = 0.05  
            
            if random.random() < shoot_chance:
                
                if len(enemy) > 7 and enemy[7] == "boss":
                    
                    enemy[4] = random.randint(45, 60)  
                else:
                    enemy[4] = random.randint(int(enemy_shoot_cooldown * 0.7), int(enemy_shoot_cooldown * 1.3))
                
                
                dx = player_pos[0] - enemy[0]
                dy = player_pos[1] - enemy[1]
                shoot_angle = math.degrees(math.atan2(dy, dx))
                
                
                accuracy_factor = min(1.0, 600 / max(distance_to_player, 1))  
                angle_variance = random.uniform(-3, 3) * (1 - accuracy_factor)  
                shoot_angle += angle_variance
                
                
                num_lasers = 1
                if len(enemy) > 7:  
                    if enemy[7] == "golden":
                        num_lasers = 2  
                    elif enemy[7] == "black-red":
                        num_lasers = 3  
                    elif enemy[7] == "boss":
                        num_lasers = 5  
                
                
                for i in range(num_lasers):
                    
                    laser_angle = shoot_angle
                    if num_lasers > 1:
                        
                        if enemy[7] == "golden":
                            
                            spread = 5
                            laser_angle += spread * (i - (num_lasers - 1) / 2)
                        elif enemy[7] == "black-red":
                            
                            spread = 8
                            laser_angle += spread * (i - (num_lasers - 1) / 2)
                        
                        elif enemy[7] == "boss":
                            
                            laser_angle += random.uniform(-1.5, 1.5)
                    
                    
                    if len(enemy) > 7 and enemy[7] == "boss":
                        
                        size_scale = 6.0
                        front_offset = 35 * size_scale
                        
                        
                        grid_size = 3  
                        row = i % grid_size
                        col = i // grid_size
                        
                        
                        y_offset = (row - 1) * 15 * size_scale * 0.5
                        z_offset = (col - 1.5) * 10 * size_scale * 0.5
                        
                        
                        laser_x = enemy[0] + front_offset * math.cos(math.radians(laser_angle))
                        laser_y = enemy[1] + front_offset * math.sin(math.radians(laser_angle)) + y_offset
                        laser_z = enemy[2] + z_offset
                    else:
                        
                        laser_x = enemy[0] + 30 * math.cos(math.radians(laser_angle))
                        laser_y = enemy[1] + 30 * math.sin(math.radians(laser_angle))
                        laser_z = enemy[2]
                    
                    
                    enemy_laser = [
                        laser_x,
                        laser_y,
                        laser_z,
                        laser_angle,
                        20 + random.uniform(-2, 2),  
                        150  
                    ]
                    
                    
                    if len(enemy) > 7 and enemy[7] == "boss":
                        enemy_laser.append("boss")
                    
                    
                    enemy_bullets.append(enemy_laser)
    
    
    if player_experience >= 100:
        
        if player_level == 4 and player_experience >= 100:
            game_won = True
            return  
        
        player_level += 1
        player_experience -= 100  
        
        
        enemies.clear()
        enemy_bullets.clear()  
        
        
        if player_level == 4:
            
            enemies.clear()
            
            
            spawn_enemy("boss")
            
            
            for i in range(3):
                spawn_enemy("black-red")
                
            
            return
        
        
        elif player_level == 3:
            
            for i in range(9):
                spawn_enemy("black-red")
                
            
            for i in range(5):
                spawn_enemy("golden")
        
        
        else:
            
            for i in range(8):
                spawn_enemy("golden")
                
            
            for i in range(5):
                spawn_enemy("red")
    auto_cheat_attack()
def auto_cheat_attack():
    global player_bullets, cheat_fire_timer, enemies, auto_target, auto_move_timer
    global player_pos, player_rotation
    if not cheat_mode_enabled:
        return
    
    
    if enemies and cheat_mode_enabled:
        
        auto_move_timer += 1
        
        
        if auto_target is None or auto_move_timer >= auto_target_change or auto_target not in enemies:
            auto_target = random.choice(enemies) if enemies else None
            auto_move_timer = 0
        
        
        if auto_target:
            
            dx = auto_target[0] - player_pos[0]
            dy = auto_target[1] - player_pos[1]
            dz = auto_target[2] - player_pos[2]
            
            
            target_rotation = math.degrees(math.atan2(dy, dx)) % 360
            
            
            rotation_diff = (target_rotation - player_rotation + 180) % 360 - 180
            if abs(rotation_diff) > 5:  
                player_rotation = (player_rotation + min(5, max(-5, rotation_diff))) % 360
            
            
            distance = math.sqrt(dx*dx + dy*dy)
            
            
            safe_distance = 300  
            if len(auto_target) > 7:
                if auto_target[7] == "boss":
                    safe_distance = 600  
                elif auto_target[7] == "black-red" or auto_target[7] == "golden":
                    safe_distance = 400  
            
            
            if distance > safe_distance:
                
                rad = player_rotation * math.pi / 180
                move_speed = player_speed * 0.7  
                
                
                new_x = player_pos[0] + math.cos(rad) * move_speed
                new_y = player_pos[1] + math.sin(rad) * move_speed
                
                
                if abs(new_x) < battlefield_size and abs(new_y) < battlefield_size:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
            elif distance < safe_distance * 0.8:
                
                rad = player_rotation * math.pi / 180
                move_speed = player_speed * 0.5
                
                
                new_x = player_pos[0] - math.cos(rad) * move_speed
                new_y = player_pos[1] - math.sin(rad) * move_speed
                
                
                if abs(new_x) < battlefield_size and abs(new_y) < battlefield_size:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
            
            
            height_diff = (auto_target[2] - player_pos[2])
            if abs(height_diff) > 20:  
                player_pos[2] += min(5, max(-5, height_diff * 0.1))  
                
                
                player_pos[2] = max(20, min(500, player_pos[2]))
    
    
    cheat_fire_timer += 1
    if cheat_fire_timer < cheat_fire_interval:
        return
    cheat_fire_timer = 0  
    
    for enemy in enemies:
        dx = enemy[0] - player_pos[0]
        dy = enemy[1] - player_pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        
        
        for i in range(3):  
            
            shot_angle = angle + random.uniform(-5, 5)
            
            player_bullets.append([
                player_pos[0],
                player_pos[1],
                player_pos[2],
                shot_angle,
                player_boost_speed + 20,
                200
            ])
def reset_game():
    
    global player_pos, player_rotation, player_speed, player_boost_speed, enemies, player_bullets, enemy_bullets, score, game_over
    global moving_forward, moving_backward, thruster_glow_intensity
    global player_health, player_lives, hit_flash_duration
    global player_experience, player_level, game_won, enemies_respawn_timer
    global camera_mode, camera_distance, player_missiles, missile_used_this_level
    global combo_count, combo_timer, combo_multiplier
    global shield_active, shield_timer, shield_used_in_game
    
    
    player_pos = [0, 0, 50]
    player_rotation = 90  
    player_speed = 10  
    player_boost_speed = 15  
    enemies = []
    player_bullets = []
    player_missiles = []
    enemy_bullets = []
    score = 0
    game_over = False
    moving_forward = False
    moving_backward = False
    thruster_glow_intensity = 0.0
    
    
    player_health = player_max_health
    player_lives = 10  
    hit_flash_duration = 0
    
    
    player_experience = 0
    player_level = 1
    
    
    game_won = False
    enemies_respawn_timer = 0
    
    
    camera_mode = 0
    camera_distance = 200
    
    
    missile_used_this_level = False
    
    
    shield_active = False
    shield_timer = 0
    shield_used_in_game = False  
    
    
    for i in range(10):
        preferred_distance = random.uniform(min_enemy_distance, max_enemy_distance)
        angle = random.uniform(0, 2 * math.pi)
        enemies.append([
            player_pos[0] + math.cos(angle) * preferred_distance,
            player_pos[1] + math.sin(angle) * preferred_distance,
            random.uniform(100, 500),
            random.uniform(0, 360),
            random.randint(0, enemy_shoot_cooldown),
            [0, 0, 0],  
            random.uniform(min_enemy_distance, max_enemy_distance)  
        ])
    
    
    game_over = False
    game_won = False
    
    
    combo_count = 0
    combo_timer = 0
    combo_multiplier = 1
def setupCamera():
    """
    Configures the camera's projection and view settings.
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    if camera_mode == 1:
        gluPerspective(70, 1.25, 0.1, 5000)
    else:
        gluPerspective(fovY, 1.25, 0.1, 5000)
        
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if camera_mode == 0:
        rad = (player_rotation + 180) * math.pi / 180
        camera_x = player_pos[0] + camera_distance * math.cos(rad)
        camera_y = player_pos[1] + camera_distance * math.sin(rad)
        camera_z = player_pos[2] + 100
        
        gluLookAt(camera_x, camera_y, camera_z,
                player_pos[0], player_pos[1], player_pos[2],
                0, 0, 1)
    else:
        rad = player_rotation * math.pi / 180
        
        camera_x = player_pos[0] + 3 * math.cos(rad)
        camera_y = player_pos[1] + 3 * math.sin(rad)
        camera_z = player_pos[2] + 15
        
        look_distance = 200
        look_x = player_pos[0] + look_distance * math.cos(rad)
        look_y = player_pos[1] + look_distance * math.sin(rad)
        look_z = player_pos[2] + 5
        
        gluLookAt(camera_x, camera_y, camera_z,
                look_x, look_y, look_z,
                0, 0, 1)
def idle():
    
    if not game_over and not game_won and not game_paused:
        update_game()
    glutPostRedisplay()
def showScreen():
    """
    Display function to render the game scene
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    
    draw_battlefield()
    draw_player()
    draw_enemies()
    draw_bullets()
    
    
    draw_radar()
    draw_hud()
    
    
    if game_over or game_won:
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(0.0, 0.0, 0.0)
        
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(1000, 0)
        glVertex2f(1000, 800)
        glVertex2f(0, 800)
        glEnd()
        
        glDisable(GL_BLEND)
        
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()
def draw_battlefield_boundaries():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glBegin(GL_QUADS)
    
    boundary_visibility = 200
    
    if battlefield_size - player_pos[1] < boundary_visibility:
        glColor3f(0.4, 0.8, 1.0)
        glVertex3f(-battlefield_size, battlefield_size, 0)
        glVertex3f(battlefield_size, battlefield_size, 0)
        glVertex3f(battlefield_size, battlefield_size, 1000)
        glVertex3f(-battlefield_size, battlefield_size, 1000)
    
    if battlefield_size + player_pos[1] < boundary_visibility:
        glColor3f(0.4, 0.8, 1.0)
        glVertex3f(-battlefield_size, -battlefield_size, 0)
        glVertex3f(battlefield_size, -battlefield_size, 0)
        glVertex3f(battlefield_size, -battlefield_size, 1000)
        glVertex3f(-battlefield_size, -battlefield_size, 1000)
    
    if battlefield_size - player_pos[0] < boundary_visibility:
        glColor3f(0.4, 0.8, 1.0)
        glVertex3f(battlefield_size, -battlefield_size, 0)
        glVertex3f(battlefield_size, battlefield_size, 0)
        glVertex3f(battlefield_size, battlefield_size, 1000)
        glVertex3f(battlefield_size, -battlefield_size, 1000)
    
    if battlefield_size + player_pos[0] < boundary_visibility:
        glColor3f(0.4, 0.8, 1.0)
        glVertex3f(-battlefield_size, -battlefield_size, 0)
        glVertex3f(-battlefield_size, battlefield_size, 0)
        glVertex3f(-battlefield_size, battlefield_size, 1000)
        glVertex3f(-battlefield_size, -battlefield_size, 1000)
        
    glEnd()
    glDisable(GL_BLEND)
def spawn_enemy(enemy_type="red"):
    preferred_distance = random.uniform(min_enemy_distance, max_enemy_distance)
    
    if enemy_type == "boss":
        angle = player_rotation * math.pi / 180
        preferred_distance = max_enemy_distance * 0.8
    else:
        angle = random.uniform(0, 2 * math.pi)
    
    pos_x = player_pos[0] + math.cos(angle) * preferred_distance
    pos_y = player_pos[1] + math.sin(angle) * preferred_distance
    
    pos_x = max(min(pos_x, battlefield_size/2 - 50), -battlefield_size/2 + 50)
    pos_y = max(min(pos_y, battlefield_size/2 - 50), -battlefield_size/2 + 50)
    
    new_enemy = [
        pos_x,
        pos_y,
        random.uniform(100, 500),
        random.uniform(0, 360),
        random.randint(0, enemy_shoot_cooldown),
        [0, 0, 0],
        random.uniform(min_enemy_distance, max_enemy_distance)
    ]
    
    if enemy_type in ["golden", "black-red", "boss"]:
        new_enemy.append(enemy_type)
    
    if enemy_type == "boss":
        new_enemy[4] = 60
        new_enemy[2] = 200
    
    enemies.append(new_enemy)
def draw_missile():
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.8)
    quad = gluNewQuadric()
    gluCylinder(quad, 3.5, 3.5, 40, 16, 8)
    
    glPushMatrix()
    glTranslatef(0, 0, 40)
    glColor3f(0.9, 0.2, 0.0)
    glutSolidSphere(4, 12, 16)
    glPopMatrix()
    
    for angle in [0, 90, 180, 270]:
        glPushMatrix()
        glTranslatef(0, 0, 15)
        glRotatef(angle, 0, 0, 1)
        glTranslatef(3.5, 0, 0)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.3, 0.3, 0.4)
        glutSolidSphere(4, 8, 8)
        glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 0, -1)
    glColor3f(1.0, 0.5, 0.0)
    glutSolidSphere(3.5, 16, 16)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 0, -3)
    glColor3f(1.0, 0.8, 0.0)
    glutSolidSphere(2.5, 12, 12)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 0, -5)
    glColor3f(1.0, 1.0, 0.5)
    glutSolidSphere(1.5, 8, 8)
    glPopMatrix()
    
    glPopMatrix()
def draw_missile_explosion(size):
    
    glColor3f(1.0, 0.4, 0.0)
    glutSolidSphere(size * 1.5, 24, 24)  
    
    glPushMatrix()
    glColor3f(1.0, 0.7, 0.0)
    glutSolidSphere(size * 1.2, 20, 20)  
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(1.0, 0.9, 0.3)
    glutSolidSphere(size * 0.8, 16, 16)  
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(1.0, 1.0, 0.7)
    glutSolidSphere(size * 0.5, 12, 12)  
    glPopMatrix()
    
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 0.3, 0.0, 0.3)  
    glutSolidSphere(size * 2.0, 16, 16)  
    glDisable(GL_BLEND)
def draw_shield():
    
    if not shield_active:
        return
    
    
    pulse = math.sin(shield_timer * 0.05) * 0.1 + 0.9
    scale_factor = 1.5 * pulse  
    
    
    shield_intensity = min(1.0, shield_timer / shield_max_duration * 1.2)
    
    
    glLineWidth(1.0)  
    
    
    
    for angle in range(0, 180, 30):
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glColor3f(0.3, 0.8, 0.9)  
        
        glBegin(GL_LINE_LOOP)
        for i in range(32):
            theta = i * 2.0 * math.pi / 32
            x = 60 * scale_factor * math.cos(theta)
            y = 0
            z = 60 * scale_factor * math.sin(theta)
            glVertex3f(x, y, z)
        glEnd()
        glPopMatrix()
    
    
    for height in range(-90, 91, 30):
        radius = 60 * scale_factor * math.cos(height * math.pi / 180)
        z = 60 * scale_factor * math.sin(height * math.pi / 180)
        
        glPushMatrix()
        glTranslatef(0, 0, z)
        glColor3f(0.3, 0.8, 0.9)  
        
        glBegin(GL_LINE_LOOP)
        for i in range(32):
            theta = i * 2.0 * math.pi / 32
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            glVertex3f(x, y, 0)
        glEnd()
        glPopMatrix()
    
    
    glLineWidth(1.0)
def draw_play_pause_button(x, y, size, is_paused):
    
    glPushMatrix()
    glLoadIdentity()
    
    
    if is_paused:
        glColor3f(0.0, 0.7, 0.0)  
    else:
        glColor3f(0.7, 0.7, 0.0)  
        
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)  
    for angle in range(0, 361, 10):
        glVertex2f(x + size/2 * math.cos(math.radians(angle)), 
                  y + size/2 * math.sin(math.radians(angle)))
    glEnd()
    
    
    glColor3f(1.0, 1.0, 1.0)  
    
    if is_paused:
        
        glBegin(GL_TRIANGLES)
        glVertex2f(x - size/6, y - size/4)  
        glVertex2f(x - size/6, y + size/4)  
        glVertex2f(x + size/4, y)           
        glEnd()
    else:
        
        bar_width = size/8
        bar_height = size/3
        
        
        glBegin(GL_QUADS)
        glVertex2f(x - bar_width*2, y - bar_height/2)
        glVertex2f(x - bar_width, y - bar_height/2)
        glVertex2f(x - bar_width, y + bar_height/2)
        glVertex2f(x - bar_width*2, y + bar_height/2)
        glEnd()
        
        
        glBegin(GL_QUADS)
        glVertex2f(x + bar_width, y - bar_height/2)
        glVertex2f(x + bar_width*2, y - bar_height/2)
        glVertex2f(x + bar_width*2, y + bar_height/2)
        glVertex2f(x + bar_width, y + bar_height/2)
        glEnd()
    
    glPopMatrix()
def draw_restart_button(x, y, size):
    
    glPushMatrix()
    glLoadIdentity()
    
    
    glColor3f(0.7, 0.0, 0.0)  
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)  
    for angle in range(0, 361, 10):
        glVertex2f(x + size/2 * math.cos(math.radians(angle)), 
                  y + size/2 * math.sin(math.radians(angle)))
    glEnd()
    
    
    glColor3f(1.0, 1.0, 1.0)  
    
    
    glBegin(GL_LINE_STRIP)
    for angle in range(45, 315, 10):
        glVertex2f(x + size/3 * math.cos(math.radians(angle)), 
                  y + size/3 * math.sin(math.radians(angle)))
    glEnd()
    
    
    arrow_angle = math.radians(45)  
    tip_x = x + size/3 * math.cos(arrow_angle)
    tip_y = y + size/3 * math.sin(arrow_angle)
    
    glBegin(GL_TRIANGLES)
    glVertex2f(tip_x, tip_y)  
    glVertex2f(tip_x - size/8, tip_y - size/12)  
    glVertex2f(tip_x - size/12, tip_y + size/8)  
    glEnd()
    
    glPopMatrix()
def is_point_in_circle(px, py, cx, cy, radius):
    
    dx = px - cx
    dy = py - cy
    return dx*dx + dy*dy <= radius*radius
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Space Shooter")
    
    glEnable(GL_DEPTH_TEST)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()
if __name__ == "__main__":
    main()