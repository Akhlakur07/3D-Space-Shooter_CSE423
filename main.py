from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Game variables
BATTLEFIELD_SIZE = 1000  # Size of the battlefield
player_pos = [0, 0, 50]  # Player position (x, y, z)
player_rotation = 0  # Player rotation in degrees
player_speed = 5  # Player movement speed
enemies = []  # List to store enemy positions
bullets = []  # List to store bullet positions
score = 0  # Player score
game_over = False  # Game over flag
HUD_color = (0, 1, 1)  # Cyan color for HUD elements

# Camera-related variables
camera_mode = 0  # 0 = third-person, 1 = cockpit, 2 = side view
camera_pos = (0, -200, 200)  # Behind and above player
camera_distance = 250  # Distance from player in third-person view
fovY = 60  # Field of view

# New features variables
obstacles = []  # List to store obstacles (asteroids)
shield = 3  # Player shield (number of hits)
missiles = []  # List to store missile positions
missile_ammo = 5  # Number of missiles available
level = 1  # Current level
boss = None  # Boss data (None if not present)
cheat_mode = False  # Cheat mode flag
combo_count = 0  # Combo counter
combo_timer = 0  # Combo timer
max_combo_time = 60  # Frames to keep combo alive
enemy_types = [  # Enemy types for levels
    {'hp': 1, 'speed': 2, 'color': (1, 0.3, 0), 'damage': 1, 'size': 1.0},     # Scout - Basic
    {'hp': 2, 'speed': 2.5, 'color': (1, 0.6, 0), 'damage': 2, 'size': 1.2},   # Fighter - Medium
    {'hp': 3, 'speed': 3, 'color': (1, 1, 0), 'damage': 3, 'size': 1.5},       # Elite - Advanced
    {'hp': 4, 'speed': 2, 'color': (0.7, 0, 0.7), 'damage': 4, 'size': 1.8},   # Destroyer - Heavy
    {'hp': 5, 'speed': 1.5, 'color': (0.1, 0.5, 0.9), 'damage': 5, 'size': 2}, # Battleship - Massive
]

# Add new global variable for enemy bullets
enemy_bullets = []  # List to store enemy bullet positions

# Add new player life and HP variables
player_lives = 5  # Starting lives
player_hp = 10000  # HP per life
max_hp = 10000  # Maximum HP

# Add a timer for cheat mode firing
cheat_fire_timer = 0
cheat_fire_interval = 15  # Fire every 15 frames

# Add variables for target tracking in cheat mode
cheat_target_enemy = None  # Current enemy being targeted
cheat_target_angle = 0     # Angle to rotate towards
cheat_aim_complete = False # Whether aiming is complete
cheat_rotation_speed = 5   # Degrees per frame for rotation

# Initialize some enemies
for i in range(10):
    enemies.append([
        random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),  # x
        random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),  # y
        random.uniform(100, 500),  # z (height)
        random.uniform(0, 360),  # rotation
        random.randint(0, len(enemy_types) - 1),  # enemy type index
        enemy_types[random.randint(0, len(enemy_types) - 1)]['hp']
    ])

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(*HUD_color)  # Use HUD color
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_spaceship(is_player=True):
    """Draw a spaceship (player battleship or enemy)"""
    if is_player:
        # Battleship style for player
        draw_battleship()
    else:
        # Simpler design for enemies
        draw_enemy_ship()

def draw_battleship():
    """Draw a battleship-style spaceship for the player"""
    # Base hull color - military gray/blue
    hull_color = (0.4, 0.45, 0.5)
    deck_color = (0.5, 0.55, 0.6)
    turret_color = (0.3, 0.35, 0.4)
    detail_color = (0.2, 0.25, 0.3)
    highlight_color = (0.6, 0.7, 0.8)
    
    # Main hull - elongated and larger
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(3.0, 1.0, 0.5)  # Increased length and width
    glutSolidCube(30)
    glPopMatrix()
    
    # Upper deck
    glPushMatrix()
    glColor3f(*deck_color)
    glTranslatef(0, 0, 8)
    glScalef(2.7, 0.9, 0.2)  # Wider deck
    glutSolidCube(30)
    glPopMatrix()
    
    # Command tower (superstructure)
    glPushMatrix()
    glColor3f(*detail_color)
    glTranslatef(-15, 0, 16)  # Positioned towards the back
    glScalef(0.6, 0.5, 0.6)  # Larger tower
    glutSolidCube(30)
    
    # Bridge (top of command tower)
    glColor3f(*highlight_color)
    glTranslatef(0, 0, 20)
    glScalef(0.8, 1.2, 0.4)
    glutSolidCube(15)
    glPopMatrix()
    
    # Front bow section - tapered
    glPushMatrix()
    glColor3f(*hull_color)
    glTranslatef(55, 0, 0)  # Moved further out for longer ship
    glRotatef(90, 0, 1, 0)
    glutSolidCone(15, 35, 12, 12)  # Larger cone
    glPopMatrix()
    
    # Rear section
    glPushMatrix()
    glColor3f(*hull_color)
    glTranslatef(-55, 0, 0)  # Moved further back
    glRotatef(-90, 0, 1, 0)
    glutSolidCone(15, 25, 12, 12)  # Larger cone
    glPopMatrix()
    
    # Main gun turrets - front, middle, rear
    draw_turret(35, 0, 11, turret_color)  # Adjusted positions for larger ship
    draw_turret(10, 0, 11, turret_color)
    draw_turret(-20, 0, 11, turret_color)
    
    # Secondary gun turrets
    draw_secondary_turret(40, 12, 9)
    draw_secondary_turret(40, -12, 9)
    draw_secondary_turret(20, 15, 9)
    draw_secondary_turret(20, -15, 9)
    draw_secondary_turret(-35, 12, 9)
    draw_secondary_turret(-35, -12, 9)
    
    # Wings (significantly larger)
    glPushMatrix()
    glColor3f(*hull_color)
    glTranslatef(0, 0, 0)
    glScalef(2.0, 3.0, 0.1)  # Much wider wings
    glutSolidCube(30)
    glPopMatrix()
    
    # Engines (thrusters)
    draw_engines()

def draw_turret(x, y, z, color):
    """Draw a main gun turret at position x,y,z"""
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Turret base
    glColor3f(*color)
    glutSolidSphere(7, 12, 12)  # Larger turret
    
    # Turret rotation platform
    glPushMatrix()
    glScalef(1, 1, 0.5)
    glutSolidSphere(6, 12, 12)
    glPopMatrix()
    
    # Main guns (triple barrels)
    glColor3f(0.2, 0.2, 0.25)
    glPushMatrix()
    glTranslatef(8, -2, 1)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 1.2, 1.2, 18, 8, 1)  # Longer barrels
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(8, 0, 1)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 1.2, 1.2, 18, 8, 1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(8, 2, 1)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 1.2, 1.2, 18, 8, 1)
    glPopMatrix()
    
    glPopMatrix()

def draw_secondary_turret(x, y, z):
    """Draw a smaller secondary turret"""
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Turret base
    glColor3f(0.35, 0.4, 0.45)
    glutSolidSphere(4, 8, 8)  # Slightly larger
    
    # Single gun
    glColor3f(0.2, 0.2, 0.25)
    glPushMatrix()
    glTranslatef(5, 0, 0)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.8, 0.8, 12, 8, 1)  # Longer barrel
    glPopMatrix()
    
    glPopMatrix()

def draw_engines():
    """Draw the battleship engines"""
    # Main engines
    glPushMatrix()
    glTranslatef(-50, 0, 0)  # Moved back for larger ship
    
    # Engine housing
    glColor3f(0.3, 0.3, 0.35)
    glPushMatrix()
    glScalef(0.4, 0.8, 0.4)  # Larger housing
    glutSolidCube(30)
    glPopMatrix()
    
    # Engine exhaust - left and right
    glPushMatrix()
    glTranslatef(-5, 10, 0)
    glRotatef(-90, 0, 1, 0)
    glColor3f(0.8, 0.4, 0.1)  # Orange glow
    glutSolidCone(4, 12, 8, 8)  # Larger exhaust
    
    # Inner bright glow
    glColor3f(1.0, 0.7, 0.2)  # Brighter orange-yellow
    glutSolidCone(3, 18, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-5, -10, 0)
    glRotatef(-90, 0, 1, 0)
    glColor3f(0.8, 0.4, 0.1)  # Orange glow
    glutSolidCone(4, 12, 8, 8)
    
    # Inner bright glow
    glColor3f(1.0, 0.7, 0.2)  # Brighter orange-yellow
    glutSolidCone(3, 18, 8, 8)
    glPopMatrix()
    
    # Center main engine
    glPushMatrix()
    glTranslatef(-5, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glColor3f(0.8, 0.4, 0.1)  # Orange glow
    glutSolidCone(6, 18, 10, 10)  # Larger main engine
    
    # Inner bright glow
    glColor3f(1.0, 0.7, 0.2)  # Brighter orange-yellow
    glutSolidCone(4.5, 25, 10, 10)
    glPopMatrix()
    
    glPopMatrix()

def draw_enemy_ship():
    """Draw enemy spaceship (simpler design)"""
    glColor3f(1, 0.3, 0)  # Red-orange for enemies
    
    # Main body
    glPushMatrix()
    glScalef(1, 0.8, 0.2)
    glutSolidCube(30)
    glPopMatrix()
    
    # Wings
    glPushMatrix()
    glTranslatef(0, 0, -5)
    glScalef(2, 0.1, 0.7)
    glutSolidCube(30)
    glPopMatrix()
    
    # Front nose cone
    glPushMatrix()
    glTranslatef(20, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCone(10, 20, 10, 10)
    glPopMatrix()
    
    # Engines (thrusters)
    glPushMatrix()
    glTranslatef(-20, 5, 0)
    glRotatef(-90, 0, 1, 0)
    glColor3f(1, 0.5, 0)  # Orange for engines
    glutSolidCylinder(5, 10, 10, 5)
    
    glTranslatef(0, -10, 0)
    glutSolidCylinder(5, 10, 10, 5)
    glPopMatrix()
    
    # Engine glow
    glPushMatrix()
    glTranslatef(-30, 5, 0)
    glRotatef(-90, 0, 1, 0)
    glColor3f(1, 0.7, 0)  # Bright orange-yellow
    glutSolidCylinder(3, 20, 8, 1)
    
    glTranslatef(0, -10, 0)
    glutSolidCylinder(3, 20, 8, 1)
    glPopMatrix()

def draw_bullet():
    """Draw a bullet"""
    glColor3f(1, 1, 0)  # Yellow
    glPushMatrix()
    glScalef(1, 0.3, 0.3)
    glutSolidSphere(5, 8, 8)
    glPopMatrix()

def draw_explosion(size):
    """Draw an explosion"""
    glColor3f(1, 0.5, 0)  # Orange
    glutSolidSphere(size, 10, 10)
    
    glPushMatrix()
    glColor3f(1, 0, 0)  # Red
    glutSolidSphere(size * 0.7, 8, 8)
    glPopMatrix()

def draw_radar():
    """Draw a radar in the corner of the screen"""
    glPushMatrix()
    
    # Draw radar background
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Draw circular radar background
    glColor3f(0, 0, 0)  # Black background
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(100, 100)  # Center
    for i in range(361):
        angle = i * math.pi / 180
        glVertex2f(100 + 80 * math.cos(angle), 100 + 80 * math.sin(angle))
    glEnd()
    
    # Draw radar circle outline
    glColor3f(0, 0.7, 0.7)  # Cyan outline
    glBegin(GL_LINE_LOOP)
    for i in range(361):
        angle = i * math.pi / 180
        glVertex2f(100 + 80 * math.cos(angle), 100 + 80 * math.sin(angle))
    glEnd()
    
    # Draw radar sweep lines
    glColor3f(0, 1, 0.7)  # Bright cyan
    glBegin(GL_LINES)
    glVertex2f(100, 100)
    glVertex2f(100 + 80 * math.cos(player_rotation * math.pi / 180), 
               100 + 80 * math.sin(player_rotation * math.pi / 180))
    glEnd()
    
    # Draw radar grid
    glColor3f(0, 0.5, 0.5)  # Darker cyan
    glBegin(GL_LINES)
    glVertex2f(20, 100)
    glVertex2f(180, 100)
    glVertex2f(100, 20)
    glVertex2f(100, 180)
    glEnd()
    
    # Draw enemy blips on radar
    glPointSize(5)
    glBegin(GL_POINTS)
    glColor3f(1, 0.3, 0.3)  # Red for enemies
    for enemy in enemies:
        # Convert enemy position to radar coordinates
        dx = enemy[0] - player_pos[0]
        dy = enemy[1] - player_pos[1]
        # Scale down and rotate to match player's orientation
        distance = math.sqrt(dx*dx + dy*dy) / (BATTLEFIELD_SIZE/2) * 70
        if distance < 80:  # Only show enemies within radar range
            angle = math.atan2(dy, dx) - player_rotation * math.pi / 180
            radar_x = 100 + distance * math.cos(angle)
            radar_y = 100 + distance * math.sin(angle)
            glVertex2f(radar_x, radar_y)
    glEnd()
    
    # Reset matrix state
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glPopMatrix()

def draw_hud():
    """Draw the heads-up display (HUD)"""
    # Speed indicator
    draw_text(10, 750, f"SPEED: {int(player_speed * 200)} KPH")
    
    # Score
    draw_text(10, 720, f"SCORE: {score}")
    
    # Level display
    draw_text(10, 690, f"LEVEL: {level}")
    
    # Lives and HP display
    if cheat_mode:
        draw_text(10, 660, f"LIVES: ∞   HP: ∞/∞")
    else:
        draw_text(10, 660, f"LIVES: {player_lives}   HP: {player_hp}/{max_hp}")
    
    # Shield
    draw_text(400, 750, f"SHIELD: {'∞' if cheat_mode else shield}")
    
    # Missiles
    draw_text(650, 750, f"MISSILES: {'∞' if cheat_mode else missile_ammo}")
    
    # Ammo
    draw_text(800, 750, f"AMMO: {len(bullets)}/50")
    
    # Combo
    if combo_count > 1:
        draw_text(500, 720, f"COMBO x{combo_count}")
    
    # Distance indicator
    if enemies:
        # Find closest enemy
        closest_dist = float('inf')
        for enemy in enemies:
            dx = enemy[0] - player_pos[0]
            dy = enemy[1] - player_pos[1]
            dz = enemy[2] - player_pos[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < closest_dist:
                closest_dist = dist
        draw_text(800, 720, f"TARGET: {int(closest_dist)} M")
    
    # Boss health (if boss exists)
    if boss:
        draw_text(400, 690, f"BOSS HP: {boss[7]}")
    
    # Draw crosshair in center of screen
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glColor3f(*HUD_color)
    glBegin(GL_LINES)
    # Horizontal line
    glVertex2f(480, 400)
    glVertex2f(520, 400)
    # Vertical line
    glVertex2f(500, 380)
    glVertex2f(500, 420)
    # Circle
    for i in range(0, 361, 30):
        angle1 = i * math.pi / 180
        angle2 = (i + 30) * math.pi / 180
        glVertex2f(500 + 30 * math.cos(angle1), 400 + 30 * math.sin(angle1))
        glVertex2f(500 + 30 * math.cos(angle2), 400 + 30 * math.sin(angle2))
    glEnd()
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_battlefield():
    """Draw the space battlefield"""
    # Draw a starfield background
    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(1, 1, 1)  # White stars
    for i in range(500):
        x = random.uniform(-BATTLEFIELD_SIZE*2, BATTLEFIELD_SIZE*2)
        y = random.uniform(-BATTLEFIELD_SIZE*2, BATTLEFIELD_SIZE*2)
        z = random.uniform(-BATTLEFIELD_SIZE, 0)  # Stars below the battlefield
        glVertex3f(x, y, z)
    glEnd()
    
    # Draw a nebula effect using transparent quads
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glBegin(GL_QUADS)
    for i in range(20):
        x = random.uniform(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE)
        y = random.uniform(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE)
        z = random.uniform(-500, -100)
        size = random.uniform(100, 300)
        
        r = random.uniform(0, 0.5)
        g = random.uniform(0, 0.5)
        b = random.uniform(0.5, 1.0)
        a = 0.2  # Alpha (transparency)
        
        glColor4f(r, g, b, a)
        glVertex3f(x - size, y - size, z)
        glVertex3f(x + size, y - size, z)
        glVertex3f(x + size, y + size, z)
        glVertex3f(x - size, y + size, z)
    glEnd()
    
    glDisable(GL_BLEND)
    
    # Draw a grid to represent the battlefield
    glBegin(GL_LINES)
    glColor3f(0.2, 0.4, 0.8)  # Light blue grid
    
    # Draw grid lines
    line_spacing = 100
    grid_size = BATTLEFIELD_SIZE
    for i in range(-grid_size, grid_size + 1, line_spacing):
        # X-axis lines
        glVertex3f(i, -grid_size, 0)
        glVertex3f(i, grid_size, 0)
        
        # Y-axis lines
        glVertex3f(-grid_size, i, 0)
        glVertex3f(grid_size, i, 0)
    glEnd()

    # Draw obstacles
    draw_obstacles()

def draw_player():
    """Draw the player's spaceship"""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_rotation, 0, 0, 1)  # Rotate around z-axis
    draw_spaceship(True)
    glPopMatrix()

def draw_enemy_ships(enemy, etype):
    """Draw different types of enemy spaceships using only basic shapes"""
    scale_factor = enemy_types[etype]['size']
    base_color = enemy_types[etype]['color']
    
    if etype == 0:  # Scout - Small fast ship
        # Main body (small cube)
        glColor3f(*base_color)
        glPushMatrix()
        glScalef(1.0 * scale_factor, 0.7 * scale_factor, 0.3 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Wings (thin cubes)
        glPushMatrix()
        glTranslatef(0, 0, -3)
        glScalef(0.5 * scale_factor, 1.5 * scale_factor, 0.1 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
    elif etype == 1:  # Fighter - Medium ship
        # Main body
        glColor3f(*base_color)
        glPushMatrix()
        glScalef(1.2 * scale_factor, 0.8 * scale_factor, 0.4 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Wings
        glPushMatrix()
        glTranslatef(-10, 0, 0)
        glRotatef(45, 0, 0, 1)
        glScalef(0.7 * scale_factor, 1.0 * scale_factor, 0.1 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Cockpit
        glColor3f(0.7, 0.7, 0.9)
        glPushMatrix()
        glTranslatef(5, 0, 5)
        glutSolidSphere(5 * scale_factor, 8, 8)
        glPopMatrix()
        
    elif etype == 2:  # Elite - Advanced fighter
        # Main body
        glColor3f(*base_color)
        glPushMatrix()
        glScalef(1.5 * scale_factor, 0.6 * scale_factor, 0.4 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Wings - X shape
        glPushMatrix()
        glRotatef(45, 0, 0, 1)
        glScalef(0.8 * scale_factor, 1.5 * scale_factor, 0.1 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        glPushMatrix()
        glRotatef(-45, 0, 0, 1)
        glScalef(0.8 * scale_factor, 1.5 * scale_factor, 0.1 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Engines (cylinders)
        glColor3f(0.9, 0.3, 0.1)
        glPushMatrix()
        glTranslatef(-15, 10, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidCylinder(3 * scale_factor, 8 * scale_factor, 8, 2)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-15, -10, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidCylinder(3 * scale_factor, 8 * scale_factor, 8, 2)
        glPopMatrix()
        
    elif etype == 3:  # Destroyer - Heavy ship
        # Main body - longer ship
        glColor3f(*base_color)
        glPushMatrix()
        glScalef(2.0 * scale_factor, 0.8 * scale_factor, 0.5 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Upper structure
        glPushMatrix()
        glTranslatef(0, 0, 7)
        glScalef(1.0 * scale_factor, 0.6 * scale_factor, 0.3 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Weapon turrets (spheres)
        glColor3f(0.3, 0.3, 0.5)
        for x in [-15, 0, 15]:
            glPushMatrix()
            glTranslatef(x, 0, 10)
            glutSolidSphere(4 * scale_factor, 8, 8)
            glPopMatrix()
        
        # Side pods
        glColor3f(*[c*0.8 for c in base_color])
        glPushMatrix()
        glTranslatef(0, 15, 0)
        glScalef(1.0 * scale_factor, 0.4 * scale_factor, 0.4 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -15, 0)
        glScalef(1.0 * scale_factor, 0.4 * scale_factor, 0.4 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
    else:  # Battleship - Massive ship (etype == 4)
        # Main hull
        glColor3f(*base_color)
        glPushMatrix()
        glScalef(2.5 * scale_factor, 1.2 * scale_factor, 0.6 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Bridge superstructure
        glColor3f(*[c*0.7 for c in base_color])
        glPushMatrix()
        glTranslatef(-5, 0, 12)
        glScalef(0.8 * scale_factor, 0.6 * scale_factor, 0.6 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Main gun (cylinder)
        glColor3f(0.2, 0.2, 0.3)
        glPushMatrix()
        glTranslatef(30, 0, 5)
        glRotatef(90, 0, 1, 0)
        glutSolidCylinder(5 * scale_factor, 25 * scale_factor, 10, 2)
        glPopMatrix()
        
        # Turrets
        for x, y in [(-20, 10), (-20, -10), (0, 15), (0, -15), (20, 0)]:
            glPushMatrix()
            glTranslatef(x, y, 12)
            glutSolidSphere(4 * scale_factor, 8, 8)
            glPopMatrix()
        
        # Engine section
        glColor3f(0.3, 0.5, 0.8)
        glPushMatrix()
        glTranslatef(-25, 0, 0)
        glScalef(0.5 * scale_factor, 1.0 * scale_factor, 0.4 * scale_factor)
        glutSolidCube(20)
        glPopMatrix()
        
        # Engine glow (cylinders)
        glColor3f(0.9, 0.4, 0.1)
        for y in [-10, 0, 10]:
            glPushMatrix()
            glTranslatef(-35, y, 0)
            glRotatef(90, 0, 1, 0)
            glutSolidCylinder(3 * scale_factor, 10 * scale_factor, 8, 2)
            glPopMatrix()
    
    # All ships have front shield emitter
    glColor3f(0.7, 0.9, 1.0)
    glPushMatrix() 
    glTranslatef(10 * scale_factor, 0, 0)
    glutSolidSphere(2 * scale_factor, 8, 8)
    glPopMatrix()

def draw_enemies():
    """Draw enemy spaceships"""
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy[0], enemy[1], enemy[2])
        glRotatef(enemy[3], 0, 0, 1)
        etype = enemy[4] if len(enemy) > 4 else 0
        draw_enemy_ships(enemy, etype)
        glPopMatrix()

def draw_bullets():
    """Draw bullets"""
    for bullet in bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glRotatef(bullet[3], 0, 0, 1)  # Rotate to match firing direction
        draw_bullet()
        glPopMatrix()

def draw_missile(missile):
    glColor3f(0.8, 0.8, 0.2)
    glPushMatrix()
    glTranslatef(missile[0], missile[1], missile[2])
    glRotatef(missile[3], 0, 0, 1)
    glRotatef(90, 1, 0, 0)
    glutSolidCylinder(3, 18, 8, 1)
    glPopMatrix()

def draw_missiles():
    for m in missiles:
        draw_missile(m)

def draw_enemy_bullet():
    """Draw an enemy bullet"""
    glColor3f(1, 0, 0)  # Red color for enemy bullets
    glPushMatrix()
    glScalef(1, 0.3, 0.3)
    glutSolidSphere(5, 8, 8)
    glPopMatrix()

def draw_enemy_bullets():
    """Draw all enemy bullets"""
    for bullet in enemy_bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glRotatef(bullet[3], 0, 0, 1)
        draw_enemy_bullet()
        glPopMatrix()

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement and actions
    """
    global player_pos, player_rotation, player_speed, bullets, game_over, camera_mode, cheat_mode
    
    if key == b'\x1b':  # ESC key
        sys.exit(0)
        
    if game_over:
        if key == b'r':  # Reset game
            reset_game()
        return
        
    # Move forward (W key)
    if key == b'w':
        rad = player_rotation * math.pi / 180
        player_pos[0] += math.cos(rad) * player_speed
        player_pos[1] += math.sin(rad) * player_speed
    
    # Move backward (S key)
    if key == b's':
        rad = player_rotation * math.pi / 180
        player_pos[0] -= math.cos(rad) * player_speed
        player_pos[1] -= math.sin(rad) * player_speed
    
    # Strafe left (A key)
    if key == b'd':
        rad = (player_rotation - 90) * math.pi / 180
        player_pos[0] += math.cos(rad) * player_speed
        player_pos[1] += math.sin(rad) * player_speed
    
    # Strafe right (D key)
    if key == b'a':
        rad = (player_rotation + 90) * math.pi / 180
        player_pos[0] += math.cos(rad) * player_speed
        player_pos[1] += math.sin(rad) * player_speed
    
    # Rise (R key)
    if key == b'r':
        player_pos[2] += player_speed
    
    # Descend (F key)
    if key == b'f':
        player_pos[2] -= player_speed
    
    # Increase speed (Q key)
    if key == b'q':
        player_speed = min(player_speed + 0.5, 10)
    
    # Decrease speed (E key)
    if key == b'e':
        player_speed = max(player_speed - 0.5, 1)
    
    # Toggle camera mode (C key)
    if key == b'c':
        camera_mode = (camera_mode + 1) % 3  # 0, 1, 2
    
    # Toggle side view (V key)
    if key == b'v':
        camera_mode = 2 if camera_mode != 2 else 0
    
    # Toggle cheat mode (M key)
    if key == b'm':
        cheat_mode = not cheat_mode

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for player rotation
    """
    global player_rotation, camera_pos
    
    # Rotate left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        player_rotation = (player_rotation - 5) % 360
    
    # Rotate right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        player_rotation = (player_rotation + 5) % 360
    
    # Look up (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] + 5)
    
    # Look down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] - 5)

def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets
    """
    global bullets, missiles, missile_ammo, cheat_mode
    
    # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if len(bullets) < 50:
            rad = player_rotation * math.pi / 180
            new_bullet = [
                player_pos[0] + 30 * math.cos(rad),
                player_pos[1] + 30 * math.sin(rad),
                player_pos[2],
                player_rotation,
                player_speed + 10,
                100
            ]
            bullets.append(new_bullet)
    # Right mouse button fires a missile
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if missile_ammo > 0 or cheat_mode:
            rad = player_rotation * math.pi / 180
            new_missile = [
                player_pos[0] + 30 * math.cos(rad),
                player_pos[1] + 30 * math.sin(rad),
                player_pos[2],
                player_rotation,
                15,  # missile speed
                120   # missile lifetime
            ]
            missiles.append(new_missile)
            if not cheat_mode:
                missile_ammo -= 1

def auto_fire():
    """Auto-fire function for cheat mode - rotates to face enemies before firing"""
    global cheat_fire_timer, enemies, cheat_target_enemy, cheat_target_angle, player_rotation, cheat_aim_complete
    
    if not enemies:  # If no enemies, don't fire
        cheat_target_enemy = None
        return
    
    # Select a target if we don't have one
    if cheat_target_enemy is None or cheat_target_enemy not in enemies:
        cheat_target_enemy = enemies[0]  # Target first enemy in the list
        cheat_aim_complete = False
        
        # Calculate angle to target
        dx = cheat_target_enemy[0] - player_pos[0]
        dy = cheat_target_enemy[1] - player_pos[1]
        cheat_target_angle = math.atan2(dy, dx) * 180 / math.pi
    
    # Rotate player to face the target
    angle_diff = (cheat_target_angle - player_rotation) % 360
    if angle_diff > 180:
        angle_diff -= 360
    
    # Smoothly rotate towards target
    if abs(angle_diff) > cheat_rotation_speed:
        if angle_diff > 0:
            player_rotation = (player_rotation + cheat_rotation_speed) % 360
        else:
            player_rotation = (player_rotation - cheat_rotation_speed) % 360
        cheat_aim_complete = False
    else:
        # We're facing the target now
        player_rotation = cheat_target_angle % 360
        cheat_aim_complete = True
    
    # Only fire when timer is ready and we're facing the target
    cheat_fire_timer += 1
    if cheat_fire_timer >= cheat_fire_interval and cheat_aim_complete:
        # Reset timer
        cheat_fire_timer = 0
        
        # Fire a bullet at the target
        rad = player_rotation * math.pi / 180
        new_bullet = [
            player_pos[0] + 30 * math.cos(rad),
            player_pos[1] + 30 * math.sin(rad),
            player_pos[2],
            player_rotation,
            player_speed + 20,  # Moderate speed so it's visible
            200,  # Longer lifetime
            cheat_target_enemy,  # Store reference to target enemy
            True  # Special flag for homing bullets in cheat mode
        ]
        bullets.append(new_bullet)
        
        # Reset target after firing (will pick next enemy on next frame)
        cheat_target_enemy = None

def update_game():
    """
    Update game state - move bullets, check collisions, etc.
    """
    global bullets, enemies, score, game_over, obstacles, shield, missiles, missile_ammo, combo_count, combo_timer, level, boss, enemy_bullets, player_hp, player_lives
    
    # Cheat mode effects
    if cheat_mode:
        shield = 999
        missile_ammo = 999
        player_lives = 999
        player_hp = 999999
        # Auto-fire in cheat mode - rotates to face enemies
        auto_fire()
    
    # Update bullets
    for bullet in bullets[:]:
        # Special handling for cheat mode homing bullets
        if len(bullet) > 7 and bullet[7] == True and bullet[6] in enemies:
            target = bullet[6]
            
            # Update direction to follow the target (homing behavior)
            dx = target[0] - bullet[0]
            dy = target[1] - bullet[1]
            dz = target[2] - bullet[2]
            
            # Calculate new angle to target
            new_angle = math.atan2(dy, dx) * 180 / math.pi
            
            # Gradually adjust bullet direction toward target
            angle_diff = (new_angle - bullet[3]) % 360
            if angle_diff > 180:
                angle_diff -= 360
                
            # Update bullet direction (homing effect)
            bullet[3] += angle_diff * 0.2  # Smooth turning
            
            # Move bullet forward in its current direction
            rad = bullet[3] * math.pi / 180
            bullet[0] += math.cos(rad) * bullet[4]
            bullet[1] += math.sin(rad) * bullet[4]
            
            # Calculate distance to target
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Check for hit
            if distance < 30:
                bullets.remove(bullet)
                
                # Kill the enemy
                enemies.remove(target)
                score += 100
                combo_count += 1
                combo_timer = max_combo_time
                
                # Spawn a new enemy
                enemies.append([
                    random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                    random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                    random.uniform(100, 500),
                    random.uniform(0, 360),
                    random.randint(0, len(enemy_types) - 1),
                    enemy_types[random.randint(0, len(enemy_types) - 1)]['hp']
                ])
                continue
            
            # Decrease lifetime
            bullet[5] -= 1
            if bullet[5] <= 0:
                bullets.remove(bullet)
            
            continue  # Skip regular bullet update for homing bullets
        
        # Regular bullet update (for non-cheat bullets)
        rad = bullet[3] * math.pi / 180
        bullet[0] += math.cos(rad) * bullet[4]
        bullet[1] += math.sin(rad) * bullet[4]
        
        # Decrease lifetime
        bullet[5] -= 1
        
        # Remove bullet if lifetime expired
        if bullet[5] <= 0:
            bullets.remove(bullet)
            continue
            
        # Regular collision checks for normal bullets
        for enemy in enemies[:]:
            dx = bullet[0] - enemy[0]
            dy = bullet[1] - enemy[1]
            dz = bullet[2] - enemy[2]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if distance < 30:  # Hit!
                if bullet in bullets:
                    bullets.remove(bullet)
                
                # Handle enemy damage
                if cheat_mode:
                    enemy[5] = 0  # Instant kill in cheat mode
                else:
                    enemy[5] -= 1
                    
                if enemy[5] <= 0:
                    enemies.remove(enemy)
                    score += 100
                    combo_count += 1
                    combo_timer = max_combo_time
                    
                    # Spawn a new enemy
                    enemies.append([
                        random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                        random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                        random.uniform(100, 500),
                        random.uniform(0, 360),
                        random.randint(0, len(enemy_types) - 1),
                        enemy_types[random.randint(0, len(enemy_types) - 1)]['hp']
                    ])
                break
    
    # Move enemies
    for enemy in enemies[:]:
        # Random movement
        if random.random() < 0.02:  # 2% chance to change direction
            enemy[3] = (enemy[3] + random.uniform(-30, 30)) % 360
        
        # Move forward in current direction
        rad = enemy[3] * math.pi / 180
        enemy[0] += math.cos(rad) * 2  # Enemy speed
        enemy[1] += math.sin(rad) * 2
        
        # Keep enemies within battlefield bounds
        enemy[0] = max(min(enemy[0], BATTLEFIELD_SIZE), -BATTLEFIELD_SIZE)
        enemy[1] = max(min(enemy[1], BATTLEFIELD_SIZE), -BATTLEFIELD_SIZE)
        enemy[2] = max(min(enemy[2], BATTLEFIELD_SIZE), 20)
        
        # Enemy shooting logic
        if random.random() < 0.01:  # 1% chance to shoot each frame
            # Calculate direction to player
            dx = player_pos[0] - enemy[0]
            dy = player_pos[1] - enemy[1]
            dz = player_pos[2] - enemy[2]
            
            # Calculate angle to player
            angle = math.atan2(dy, dx) * 180 / math.pi
            
            # Create enemy bullet aimed at player
            etype = enemy[4] if len(enemy) > 4 else 0
            enemy_bullets.append([
                enemy[0],  # x
                enemy[1],  # y
                enemy[2],  # z
                angle,    # direction
                15,      # speed
                150,     # lifetime
                enemy_types[etype]['damage']  # damage based on enemy type
            ])
    
    # Update enemy bullets
    for bullet in enemy_bullets[:]:
        # Move bullet forward
        rad = bullet[3] * math.pi / 180
        bullet[0] += math.cos(rad) * bullet[4]
        bullet[1] += math.sin(rad) * bullet[4]
        
        # Decrease lifetime
        bullet[5] -= 1
        
        # Remove if lifetime expired
        if bullet[5] <= 0:
            enemy_bullets.remove(bullet)
            continue
        
        # Check collision with player
        dx = player_pos[0] - bullet[0]
        dy = player_pos[1] - bullet[1]
        dz = player_pos[2] - bullet[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < 20:  # Hit player!
            enemy_bullets.remove(bullet)
            if not cheat_mode:
                damage = bullet[6] if len(bullet) > 6 else 1  # Get bullet damage
                damage_hp = damage * 100  # Convert damage to HP loss (100 HP per hit)
                player_hp -= damage_hp
                if player_hp <= 0:
                    player_lives -= 1
                    if player_lives <= 0:
                        game_over = True
                    else:
                        player_hp = max_hp  # Reset HP for next life
    
    # Update obstacles
    for obs in obstacles[:]:
        # Move obstacle forward (toward -z, or random drift)
        obs[2] -= 2 + level * 0.5  # Speed increases with level
        obs[4] = (obs[4] + 2) % 360  # Spin
        # Remove if out of bounds
        if obs[2] < 0:
            obstacles.remove(obs)
            continue
        # Check collision with player
        dx = player_pos[0] - obs[0]
        dy = player_pos[1] - obs[1]
        dz = player_pos[2] - obs[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < obs[3] + 20:
            obstacles.remove(obs)
            if not cheat_mode:
                damage_hp = 300  # Obstacle collision does 300 HP damage
                player_hp -= damage_hp
                if player_hp <= 0:
                    player_lives -= 1
                    if player_lives <= 0:
                        game_over = True
                    else:
                        player_hp = max_hp  # Reset HP for next life
            continue
        # Check collision with bullets
        for bullet in bullets[:]:
            dx = bullet[0] - obs[0]
            dy = bullet[1] - obs[1]
            dz = bullet[2] - obs[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < obs[3] + 5:
                if bullet in bullets:
                    bullets.remove(bullet)
                if obs in obstacles:
                    obstacles.remove(obs)
                score += 50
                combo_count += 1
                combo_timer = max_combo_time
                break
        # Check collision with missiles
        for missile in missiles[:]:
            dx = missile[0] - obs[0]
            dy = missile[1] - obs[1]
            dz = missile[2] - obs[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < obs[3] + 10:
                if missile in missiles:
                    missiles.remove(missile)
                if obs in obstacles:
                    obstacles.remove(obs)
                score += 100
                combo_count += 1
                combo_timer = max_combo_time
                break
    # Combo timer logic
    if combo_timer > 0:
        combo_timer -= 1
    else:
        combo_count = 0

    # Update missiles
    for missile in missiles[:]:
        rad = missile[3] * math.pi / 180
        missile[0] += math.cos(rad) * missile[4]
        missile[1] += math.sin(rad) * missile[4]
        missile[5] -= 1
        if missile[5] <= 0:
            missiles.remove(missile)

    # Level progression
    if not enemies and not boss:
        # global level
        level += 1
        # Spawn more enemies
        for i in range(10 + level * 2):
            etype = random.choice(range(min(level, len(enemy_types))))
            enemies.append([
                random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                random.uniform(100, 500),
                random.uniform(0, 360),
                etype,  # enemy type index
                enemy_types[etype]['hp']
            ])
        # Spawn more obstacles
        for i in range(3 + level):
            obstacles.append([
                random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                random.uniform(20, 400),
                random.uniform(15, 40),
                random.uniform(0, 360),
                random.randint(0, 1)
            ])
        # Boss appears at level 5+
        if level % 5 == 0:
            # global boss
            boss = [0, 0, 400, 0, 20 + level * 5, 20 + level * 5, 20 + level * 5, 20 + level * 2, 50 + level * 10]  # x, y, z, rot, sizeX, sizeY, sizeZ, hp, cooldown

    # Boss logic
    if boss:
        boss[3] = (boss[3] + 1) % 360  # Spin
        # Move boss slowly toward player
        dx = player_pos[0] - boss[0]
        dy = player_pos[1] - boss[1]
        dz = player_pos[2] - boss[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist > 100:
            boss[0] += dx / dist * 1.5
            boss[1] += dy / dist * 1.5
            boss[2] += dz / dist * 1.5
        # Boss collision with player
        if dist < boss[4]:
            if not cheat_mode:
                damage_hp = 500  # Boss collision does 500 HP damage
                player_hp -= damage_hp
                if player_hp <= 0:
                    player_lives -= 1
                    if player_lives <= 0:
                        game_over = True
                    else:
                        player_hp = max_hp  # Reset HP for next life
        # Boss hit by bullets
        for bullet in bullets[:]:
            dx = bullet[0] - boss[0]
            dy = bullet[1] - boss[1]
            dz = bullet[2] - boss[2]
            if math.sqrt(dx*dx + dy*dy + dz*dz) < boss[4]:
                if bullet in bullets:
                    bullets.remove(bullet)
                if cheat_mode:
                    boss[7] = 0
                else:
                    boss[7] -= 1
                if boss[7] <= 0:
                    # global score
                    score += 1000
                    # global combo_count, combo_timer
                    combo_count += 1
                    combo_timer = max_combo_time
                    boss.clear()
        # Boss hit by missiles
        for missile in missiles[:]:
            dx = missile[0] - boss[0]
            dy = missile[1] - boss[1]
            dz = missile[2] - boss[2]
            if math.sqrt(dx*dx + dy*dy + dz*dz) < boss[4] + 10:
                if missile in missiles:
                    missiles.remove(missile)
                if cheat_mode:
                    boss[7] = 0
                else:
                    boss[7] -= 5
                if boss[7] <= 0:
                    score += 1000
                    combo_count += 1
                    combo_timer = max_combo_time
                    boss.clear()

def reset_game():
    """Reset game state for a new game"""
    global player_pos, player_rotation, player_speed, enemies, bullets, score, game_over, obstacles, shield, missiles, missile_ammo, level, boss, combo_count, combo_timer, enemy_bullets, player_lives, player_hp
    
    player_pos = [0, 0, 50]
    player_rotation = 0
    player_speed = 5
    enemies = []
    bullets = []
    score = 0
    game_over = False
    player_lives = 5
    player_hp = max_hp
    
    # Initialize enemies
    for i in range(10):
        enemies.append([
            random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
            random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
            random.uniform(100, 500),
            random.uniform(0, 360),
            random.randint(0, len(enemy_types) - 1),  # enemy type index
            enemy_types[random.randint(0, len(enemy_types) - 1)]['hp']
        ])
    
    # Initialize obstacles
    obstacles = []
    for i in range(5 + level * 2):
        obstacles.append([
            random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
            random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
            random.uniform(20, 400),
            random.uniform(15, 40),  # size
            random.uniform(0, 360),  # rotation
            random.randint(0, 1)  # 0=sphere, 1=cube
        ])
    shield = 3
    missiles = []
    missile_ammo = 5
    level = 1
    boss = None
    combo_count = 0
    combo_timer = 0
    enemy_bullets = []  # Clear enemy bullets

def setupCamera():
    """
    Configures the camera's projection and view settings.
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_mode == 0:  # Third-person view
        rad = (player_rotation + 180) * math.pi / 180
        camera_x = player_pos[0] + camera_distance * math.cos(rad)
        camera_y = player_pos[1] + camera_distance * math.sin(rad)
        camera_z = player_pos[2] + 100
        gluLookAt(camera_x, camera_y, camera_z,
                  player_pos[0], player_pos[1], player_pos[2],
                  0, 0, 1)
    elif camera_mode == 1:  # First-person/cockpit view
        rad = player_rotation * math.pi / 180
        look_x = player_pos[0] + 100 * math.cos(rad)
        look_y = player_pos[1] + 100 * math.sin(rad)
        gluLookAt(player_pos[0], player_pos[1], player_pos[2] + 10,
                  look_x, look_y, player_pos[2],
                  0, 0, 1)
    elif camera_mode == 2:  # Side view
        gluLookAt(player_pos[0] - 400, player_pos[1], player_pos[2] + 50,
                  player_pos[0], player_pos[1], player_pos[2],
                  0, 0, 1)

def idle():
    """
    Idle function for continuous updates
    """
    if not game_over:
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
    
    # Draw game elements
    draw_battlefield()
    draw_player()
    draw_enemies()
    draw_bullets()
    draw_missiles()
    draw_enemy_bullets()  # Add enemy bullets rendering
    draw_boss()
    
    # Draw HUD elements (always on top)
    draw_radar()
    draw_hud()
    
    # Show game over message if needed
    if game_over:
        draw_text(400, 400, "GAME OVER - Press 'R' to restart")
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Space Shooter")
    
    # Enable depth testing for 3D rendering
    glEnable(GL_DEPTH_TEST)
    
    # Register callback functions
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

def draw_obstacle(obstacle):
    """Draw an obstacle (asteroid) using only spheres and cubes"""
    glPushMatrix()
    glTranslatef(obstacle[0], obstacle[1], obstacle[2])
    glRotatef(obstacle[4], 1, 1, 0)  # Spin for effect
    glColor3f(0.5, 0.4, 0.3)
    if obstacle[5] == 0:
        glutSolidSphere(obstacle[3], 12, 12)
    else:
        glScalef(1, 1, 0.7)
        glutSolidCube(obstacle[3]*2)
    glPopMatrix()

def draw_obstacles():
    for obs in obstacles:
        draw_obstacle(obs)

def draw_boss():
    if boss:
        glPushMatrix()
        glTranslatef(boss[0], boss[1], boss[2])
        glRotatef(boss[3], 0, 0, 1)
        # Main body (cube)
        glColor3f(0.7, 0, 0.7)
        glPushMatrix()
        glScalef(boss[4]/10, boss[5]/10, boss[6]/10)
        glutSolidCube(40)
        glPopMatrix()
        # Spheres as turrets
        glColor3f(1, 0.5, 0)
        for dx in [-boss[4]/2, boss[4]/2]:
            glPushMatrix()
            glTranslatef(dx, boss[5]/2, 0)
            glutSolidSphere(8, 10, 10)
            glPopMatrix()
        # Cylinders as cannons
        glColor3f(0.8, 0.8, 0.2)
        for dz in [-boss[6]/2, boss[6]/2]:
            glPushMatrix()
            glTranslatef(0, boss[5]/2, dz)
            glRotatef(-90, 1, 0, 0)
            glutSolidCylinder(3, 30, 8, 1)
            glPopMatrix()
        glPopMatrix()

if __name__ == "__main__":
    main()