from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import sys

# Game variables
BATTLEFIELD_SIZE = 2000  # Size of the battlefield (increased from 1000)
player_pos = [0, 0, 50]  # Player position (x, y, z)
player_rotation = 90  # Player rotation in degrees (start at 90 degrees)
player_speed = 10  # Player movement speed - increased from 5 to 10
player_boost_speed = 15  # Faster speed for quick maneuvers
enemies = []  # List to store enemy positions
enemy_bullets = []  # List to store enemy laser beam positions
player_bullets = []  # List to store player laser beam positions
score = 0  # Player score
game_over = False  # Game over flag
HUD_color = (0, 1, 1)  # Cyan color for HUD elements
MIN_ENEMY_DISTANCE = 300  # Absolute minimum distance enemies will maintain from player
MAX_ENEMY_DISTANCE = 1200  # Maximum distance enemies will maintain from player (increased from 800)
ENEMY_SHOOT_COOLDOWN = 180  # Frames between enemy shots (3 seconds at 60 FPS, increased from 120)
ENEMY_SHOOT_CHANCE = 0.007  # Probability of an enemy shooting in a given frame
MAX_SHOOTING_DISTANCE = 1500  # Maximum distance from which enemies will shoot (increased from 900)

# Player health and lives system
player_max_health = 1000  # Maximum health per life
player_health = player_max_health  # Current health
player_lives = 15  
hit_flash_duration = 0  # Duration counter for red flash when hit
DAMAGE_PER_HIT = 100  # Damage taken per enemy bullet hit

# Movement effect variables
moving_forward = False  # Flag for forward movement
moving_backward = False  # Flag for backward movement
thruster_glow_intensity = 0.0  # Base thruster glow intensity

# Camera-related variables
camera_mode = 0  # 0 = third-person, 1 = cockpit
camera_pos = (0, -200, 200)  # Behind and above player
camera_distance = 250  # Distance from player in third-person view
fovY = 60  # Field of view

# Grid animation variables
grid_offset_x = 0  # X-offset for grid animation
grid_offset_y = 0  # Y-offset for grid animation
grid_line_spacing = 100  # Spacing between grid lines
grid_animation_speed = 5  # Speed of grid animation

# Player experience and level system
player_experience = 0  # Current experience points
player_level = 1  # Current level

# Add a game won variable to track when the player has won
game_won = False
enemies_respawn_timer = 0  # Timer for post-victory message and enemy respawning

# Initialize some enemies
for i in range(10):
    # Create enemies at random positions far from player
    preferred_distance = random.uniform(MIN_ENEMY_DISTANCE, MAX_ENEMY_DISTANCE)
    angle = random.uniform(0, 2 * math.pi)
    
    # Position based on preferred distance
    pos_x = player_pos[0] + math.cos(angle) * preferred_distance
    pos_y = player_pos[1] + math.sin(angle) * preferred_distance
    
    # Ensure within battlefield bounds
    pos_x = max(min(pos_x, BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
    pos_y = max(min(pos_y, BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
    
    enemies.append([
        pos_x,  # x
        pos_y,  # y
        random.uniform(100, 500),  # z (height)
        random.uniform(0, 360),    # rotation
        random.randint(0, ENEMY_SHOOT_COOLDOWN),  # shooting cooldown
        [0, 0, 0],  # target position (will be set during gameplay)
        random.uniform(MIN_ENEMY_DISTANCE, MAX_ENEMY_DISTANCE)  # preferred distance from player
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
    """Draw a sci-fi battleship-style spaceship for the player"""
    # Colors for sci-fi effect
    hull_color = (0.2, 0.25, 0.35)         # Dark blue-gray
    accent_color = (0.0, 0.8, 1.0)         # Neon blue
    deck_color = (0.3, 0.35, 0.45)         # Slightly lighter
    turret_color = (0.15, 0.18, 0.22)      # Darker for turrets
    energy_core_color = (0.0, 1.0, 0.7)    # Glowing teal
    engine_glow_color = (1.0, 0.5, 0.1)    # Orange
    highlight_color = (0.7, 0.9, 1.0)      # Light blue highlight

    # Main hull - angular, layered
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(3.2, 1.1, 0.5)
    glutSolidCube(30)
    glPopMatrix()

    # Lower hull accent (angular)
    glPushMatrix()
    glColor3f(*accent_color)
    glTranslatef(0, 0, -7)
    glScalef(2.8, 0.7, 0.15)
    glutSolidCube(30)
    glPopMatrix()

    # Upper deck (layered)
    glPushMatrix()
    glColor3f(*deck_color)
    glTranslatef(0, 0, 10)
    glScalef(2.5, 0.8, 0.18)
    glutSolidCube(30)
    glPopMatrix()

    # Command tower (superstructure)
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(-13, 0, 18)
    glScalef(0.7, 0.5, 0.7)
    glutSolidCube(20)
    # Energy core on top
    glColor3f(*energy_core_color)
    glTranslatef(0, 0, 15)
    glutSolidSphere(4, 12, 12)
    glPopMatrix()

    # Front bow - sharp, sci-fi cone
    glPushMatrix()
    glColor3f(*accent_color)
    glTranslatef(55, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(15, 40, 16)
    glPopMatrix()

    # Rear section - layered cones
    glPushMatrix()
    glColor3f(*hull_color)
    glTranslatef(-55, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glutSolidSphere(15, 25, 12)
    glColor3f(*engine_glow_color)
    glTranslatef(0, 0, -10)
    glutSolidSphere(10, 15, 10)
    glPopMatrix()

    # Main gun turrets - angular, sci-fi
    draw_turret(35, 0, 13, turret_color, accent_color)
    draw_turret(10, 0, 13, turret_color, accent_color)
    draw_turret(-20, 0, 13, turret_color, accent_color)

    # Secondary gun turrets (smaller, more)
    draw_secondary_turret(40, 12, 11, accent_color)
    draw_secondary_turret(40, -12, 11, accent_color)
    draw_secondary_turret(20, 15, 11, accent_color)
    draw_secondary_turret(20, -15, 11, accent_color)
    draw_secondary_turret(-35, 12, 11, accent_color)
    draw_secondary_turret(-35, -12, 11, accent_color)

    # Winglets - sci-fi fins
    for angle, y_offset in [(-30, 25), (30, -25)]:
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(10, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.2, 0.2, 0.05)
        glutSolidCube(60)
        glPopMatrix()

    # Lower fins
    for y_offset in [-18, 18]:
        glPushMatrix()
        glColor3f(*highlight_color)
        glTranslatef(-10, y_offset, -10)
        glScalef(0.5, 0.1, 0.02)
        glutSolidCube(60)
        glPopMatrix()

    # Engines (thrusters)
    draw_engines(engine_glow_color, accent_color)

def draw_turret(x, y, z, color, accent_color):
    """Draw a main gun turret at position x,y,z with sci-fi accent"""
    glPushMatrix()
    glTranslatef(x, y, z)
    # Turret base
    glColor3f(*color)
    glutSolidSphere(7, 12, 12)
    # Accent ring
    glColor3f(*accent_color)
    glScalef(1.2, 1.2, 0.4)
    glutSolidSphere(6, 12, 12)
    # Main guns (triple barrels)
    glColor3f(0.2, 0.8, 1.0)
    for offset in [-2, 0, 2]:
        glPushMatrix()
        glTranslatef(8, offset, 2)
        glRotatef(90, 0, 1, 0)
        glutSolidSphere(2, 18, 8)
        glPopMatrix()
    glPopMatrix()

def draw_secondary_turret(x, y, z, accent_color):
    """Draw a smaller secondary turret with accent"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*accent_color)
    glutSolidSphere(4, 8, 8)
    # Single gun
    glColor3f(0.2, 0.8, 1.0)
    glPushMatrix()
    glTranslatef(5, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(1, 12, 8)
    glPopMatrix()
    glPopMatrix()

def draw_engines(engine_glow_color, accent_color):
    """Draw the battleship engines with sci-fi glow and accents"""
    global thruster_glow_intensity, moving_forward, moving_backward
    
    # Set base thruster color based on movement state
    if moving_forward:
        # Cyan color when moving forward (pressing W)
        base_glow = [0.0, 0.8, 1.0]
    else:
        # Default orange color when not moving forward or moving backward
        base_glow = [1.0, 0.5, 0.1]
    
    # Enhance glow based on movement intensity
    enhanced_glow = [
        min(1.0, base_glow[0] + thruster_glow_intensity * 0.2),
        min(1.0, base_glow[1] + thruster_glow_intensity * 0.2),
        min(1.0, base_glow[2] + thruster_glow_intensity * 0.2)
    ]
    
    # Size multiplier based on thruster intensity - bigger when moving
    size_mult = 1.0 + thruster_glow_intensity * 0.8
    
    # Draw large central thruster housing
    glPushMatrix()
    glTranslatef(-55, 0, 0)
    glColor3f(*accent_color)
    # Slightly smaller scale for the main thruster
    glScalef(0.4, 0.5, 0.5)
    glutSolidCube(40)
    glPopMatrix()
    
    # Draw large central thruster glow
    glPushMatrix()
    glTranslatef(-65, 0, 0)
    
    # Engine glow - changes color and size with movement
    glColor3f(*enhanced_glow)
    # Reduced size but still larger than original
    glutSolidSphere(int(10 * size_mult), 16, 16)
    
    glPopMatrix()
    
    # Additional small thrusters on the sides (for maneuvering)
    for y_offset in [-18, 18]:
        glPushMatrix()
        glTranslatef(-50, y_offset, 0)
        glColor3f(*accent_color)
        glScalef(0.2, 0.2, 0.2)
        glutSolidCube(20)
        
        # Small side thruster glow - same color as main thruster
        glColor3f(*enhanced_glow)
        glTranslatef(-5, 0, 0)
        glutSolidSphere(int(4 * size_mult), 8, 8)
        glPopMatrix()
    
    # Extra glowing energy core at the rear
    glPushMatrix()
    # Energy core changes color with movement
    if moving_forward:
        glColor3f(1.0, 0.6, 0.2)  # Orange for forward
    else:
         glColor3f(1,1,1) # Cyan for idle/backward
    
    glTranslatef(-60, 0, 12)  # Positioned above the main thruster
    glutSolidSphere(int(6 + thruster_glow_intensity * 2), 12, 12)  # Adjusted energy core size
    glPopMatrix()
    
    # Add energy conduits connecting to the main thruster
    glPushMatrix()
    # Conduit color matches thruster state
    if moving_forward:
        glColor3f(0.0, 0.8, 1.0)  # Cyan for forward
    else:
        glColor3f(1.0, 0.6, 0.2)  # Orange for idle/backward
    
    # Horizontal conduit
    glTranslatef(-58, 0, 6)
    glScalef(0.1, 0.1, 0.6)
    glutSolidCube(30)
    glPopMatrix()
    


def draw_enemy_ship():
    """Draw enemy spaceship with matching aesthetic to player ship but distinct enemy look"""
    # Colors for enemy ships (red theme)
    hull_color = (0.4, 0.1, 0.1)         # Dark red hull
    accent_color = (1.0, 0.2, 0.0)       # Bright red accent
    highlight_color = (0.8, 0.2, 0.2)    # Lighter red highlight
    energy_core_color = (1.0, 0.7, 0.0)  # Yellow-orange energy
    engine_glow_color = (1.0, 0.5, 0.0)  # Orange engine glow
    
    # Main hull - angular, similar to player but sleeker
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(2.5, 0.9, 0.4)  # Flatter, longer design
    glutSolidCube(25)
    glPopMatrix()
    
    # Upper angular section
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(0, 0, 8)
    glScalef(2.0, 0.7, 0.15)
    glutSolidCube(25)
    glPopMatrix()
    
    # Command module (triangular) at front
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(25, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(10, 25, 12)
    glPopMatrix()
    
    # Side wings/fins - angular with enemy design
    for y_offset, angle in [(20, 20), (-20, -20)]:
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(0, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.0, 0.15, 0.1)
        glutSolidCube(50)
        glPopMatrix()
    
    # Energy weapons on top
    for x_offset in [-15, 0, 15]:
        glPushMatrix()
        glTranslatef(x_offset, 0, 10)
        # Weapon base
        glColor3f(*hull_color)
        glutSolidSphere(3, 8, 8)
        # Weapon barrel
        glColor3f(*accent_color)
        glRotatef(-90, 1, 0, 0)
        glutSolidSphere(1.5, 8, 8)
        glPopMatrix()
    
    # Rear section with central thruster
    glPushMatrix()
    glTranslatef(-40, 0, 0)
    
    # Thruster housing
    glColor3f(*hull_color)
    glScalef(0.3, 0.4, 0.4)
    glutSolidCube(35)
    glPopMatrix()
    
    # Engine glow
    glPushMatrix()
    glTranslatef(-46, 0, 0)
    glColor3f(*engine_glow_color)
    glutSolidSphere(6, 12, 12)
    glPopMatrix()
    
    # Side thrusters
    for y_offset in [-15, 15]:
        glPushMatrix()
        glTranslatef(-35, y_offset, 0)
        # Thruster housing
        glColor3f(*hull_color)
        glScalef(0.2, 0.2, 0.2)
        glutSolidCube(20)
        # Thruster glow
        glTranslatef(-15, 0, 0)
        glColor3f(*engine_glow_color)
        glutSolidSphere(3, 8, 8)
        glPopMatrix()
    
    # Energy core on top (glowing)
    glPushMatrix()
    glColor3f(*energy_core_color)
    glTranslatef(-25, 0, 12)
    glutSolidSphere(4, 10, 10)
    # Energy conduit to engines
    glColor3f(*accent_color)
    glTranslatef(-10, 0, -6)
    glScalef(0.8, 0.1, 0.6)
    glutSolidCube(20)
    glPopMatrix()
    
    # Thruster flame effects (always on for enemies)
    glPushMatrix()
    glTranslatef(-55, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(1.0, 0.5, 0.0)  # Orange flame
    glutSolidSphere(5, 15, 8)
    glColor3f(1.0, 0.7, 0.0)  # Yellow-orange inner flame
    glutSolidSphere(3, 10, 8)
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_golden_enemy_ship():
    """Draw a golden enemy spaceship with enhanced details and more menacing appearance"""
    # Enhanced colors for golden enemy ships - more vibrant and metallic
    hull_color = (0.8, 0.7, 0.1)         # Golden hull
    accent_color = (1.0, 0.9, 0.0)       # Brighter gold accent
    highlight_color = (1.0, 1.0, 0.3)    # Bright gold highlight
    energy_core_color = (1.0, 1.0, 0.5)  # Bright yellow energy
    engine_glow_color = (1.0, 0.7, 0.0)  # Golden-orange engine glow
    dark_accent = (0.5, 0.4, 0.0)        # Darker gold for details
    
    # Overall size increase by 40%
    size_scale = 1.4
    
    # Main hull - enhanced with more details
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(2.5 * size_scale, 0.9 * size_scale, 0.5 * size_scale)  # Larger design
    glutSolidCube(25)
    glPopMatrix()
    
    # Upper angular section - more detailed with layered appearance
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(0, 0, 8 * size_scale)
    glScalef(2.0 * size_scale, 0.7 * size_scale, 0.15 * size_scale)
    glutSolidCube(25)
    
    # Additional upper deck detail
    glColor3f(*accent_color)
    glTranslatef(0, 0, 4)
    glScalef(0.85, 0.85, 1.0)
    glutSolidCube(25)
    glPopMatrix()
    
    # Command module (triangular) at front - sharper and more detailed
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(30 * size_scale, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(12 * size_scale), int(30 * size_scale), 16)  # More detailed cone
    
    # Add ring detail around nose
    glColor3f(*accent_color)
    glTranslatef(0, 0, 10 * size_scale)
    glutSolidSphere(int(2 * size_scale), int(8 * size_scale), 16)
    glPopMatrix()
    
    # Side wings/fins - enhanced design with extra details
    for y_offset, angle in [(20 * size_scale, 20), (-20 * size_scale, -20)]:
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(0, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.2 * size_scale, 0.15 * size_scale, 0.1 * size_scale)
        glutSolidCube(50)
        
        # Add wing details - stripes
        glColor3f(*dark_accent)
        glTranslatef(-15, 0, 0)
        glScalef(0.2, 1.0, 1.2)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        glPopMatrix()
    
    # Energy weapons on top - more and bigger
    for x_offset, y_offset in [(-18 * size_scale, 0), (0, 0), (18 * size_scale, 0), 
                          (-12 * size_scale, 10 * size_scale), (12 * size_scale, 10 * size_scale),
                          (-12 * size_scale, -10 * size_scale), (12 * size_scale, -10 * size_scale)]:
        glPushMatrix()
        glTranslatef(x_offset, y_offset, 10 * size_scale)
        # Weapon base
        glColor3f(*dark_accent)
        glutSolidSphere(int(3 * size_scale), 10, 10)
        # Weapon barrel
        glColor3f(*accent_color)
        glRotatef(-90, 1, 0, 0)
        glutSolidSphere(int(1.8 * size_scale), int(10 * size_scale), 10)
        
        # Add glowing tip
        glTranslatef(0, 0, 10 * size_scale)
        glColor3f(*highlight_color)
        glutSolidSphere(int(1.2 * size_scale), 8, 8)
        glPopMatrix()
    
    # Rear section with central thruster - more detailed
    glPushMatrix()
    glTranslatef(-40 * size_scale, 0, 0)
    
    # Thruster housing
    glColor3f(*hull_color)
    glScalef(0.4 * size_scale, 0.5 * size_scale, 0.5 * size_scale)
    glutSolidCube(35)
    
    # Additional thruster details - rings
    glColor3f(*accent_color)
    glTranslatef(-20, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(3, 15, 16)
    glPopMatrix()
    
    # Engine glow - enhanced with layered effect
    glPushMatrix()
    glTranslatef(-48 * size_scale, 0, 0)
    
    # Inner core
    glColor3f(1.0, 1.0, 0.8)  # Bright white-yellow
    glutSolidSphere(int(5 * size_scale), 16, 16)
    
    # Outer glow
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(1.0, 0.8, 0.0)  # Semi-transparent gold
    glutSolidSphere(int(8 * size_scale), 16, 16)
    glDisable(GL_BLEND)
    glPopMatrix()
    
    # Side thrusters - enhanced
    for y_offset in [-18 * size_scale, 18 * size_scale]:
        glPushMatrix()
        glTranslatef(-40 * size_scale, y_offset, 0)
        # Thruster housing
        glColor3f(*dark_accent)
        glScalef(0.25 * size_scale, 0.25 * size_scale, 0.25 * size_scale)
        glutSolidCube(20)
        
        # Add detail ring
        glColor3f(*accent_color)
        glTranslatef(-12, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidSphere(2, 8, 12)
        
        # Thruster glow
        glColor3f(*engine_glow_color)
        glTranslatef(0, 0, 0)
        glutSolidSphere(int(4 * size_scale), 12, 12)
        glPopMatrix()
    
    # Energy core on top (glowing) - more complex and detailed
    glPushMatrix()
    glTranslatef(-25 * size_scale, 0, 15 * size_scale)  # Higher position
    
    # Main core
    glColor3f(*energy_core_color)
    glutSolidSphere(int(5 * size_scale), 16, 16)
    
    # Surrounding ring
    glColor3f(*dark_accent)
    glRotatef(90, 1, 0, 0)
    glutSolidSphere(int(1.5 * size_scale), int(7 * size_scale), 16)
    
    # Energy conduit to engines
    glColor3f(*accent_color)
    glRotatef(90, 0, 1, 0)
    glTranslatef(0, 0, -10 * size_scale)
    glScalef(0.9 * size_scale, 0.1 * size_scale, 0.7 * size_scale)
    glutSolidCube(20)
    glPopMatrix()
    
    # Decorative fins on top - new feature
    for z_offset, x_scale in [(8 * size_scale, 0.6), (0, 0.8), (-8 * size_scale, 0.6)]:
        glPushMatrix()
        glColor3f(*dark_accent)
        glTranslatef(-15 * size_scale, 0, 12 * size_scale + z_offset)
        glRotatef(90, 0, 1, 0)
        glScalef(x_scale, 0.1, 0.4)
        glutSolidCube(20 * size_scale)
        glPopMatrix()
    
    # Thruster flame effects - enhanced
    glPushMatrix()
    glTranslatef(-55 * size_scale, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Outer flame
    glColor3f(1.0, 0.7, 0.2)  # Golden flame
    glutSolidSphere(int(7 * size_scale), int(22 * size_scale), 12)
    
    # Middle flame
    glColor3f(1.0, 0.8, 0.3)  # Lighter gold
    glutSolidSphere(int(5 * size_scale), int(16 * size_scale), 12)
    
    # Inner flame
    glColor3f(1.0, 0.9, 0.5)  # Bright gold inner flame
    glutSolidSphere(int(3 * size_scale), int(12 * size_scale), 8)
    
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_black_red_enemy_ship():
    """Draw a black-red enemy spaceship with enhanced dark, menacing appearance and more details"""
    # Enhanced colors for black-red enemy ships - more sinister
    hull_color = (0.08, 0.03, 0.03)       # Almost black hull
    accent_color = (0.8, 0.0, 0.0)        # Blood red accent
    highlight_color = (0.4, 0.0, 0.0)     # Dark red highlight
    energy_core_color = (1.0, 0.1, 0.1)   # Bright red energy with slight orange
    dark_detail = (0.15, 0.05, 0.05)      # Very dark red for details
    
    # Overall size increase by 45%
    size_scale = 1.45
    
    # Main hull - larger, more aggressive
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(2.6 * size_scale, 1.1 * size_scale, 0.6 * size_scale)  # Larger, wider design
    glutSolidCube(25)
    glPopMatrix()
    
    # Upper structure - more angular and menacing
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(0, 0, 9 * size_scale)
    glScalef(2.1 * size_scale, 0.9 * size_scale, 0.25 * size_scale)
    glutSolidCube(25)
    
    # Add ridged detail on top
    glColor3f(*dark_detail)
    glTranslatef(0, 0, 3)
    glScalef(0.9, 0.7, 0.5)
    glutSolidCube(25)
    glPopMatrix()
    
    # Command module (triangular) at front - sharper and more aggressive
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(35 * size_scale, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(14 * size_scale), int(35 * size_scale), 16)  # Longer, sharper nose
    
    # Add menacing detail to the front
    glColor3f(*accent_color)
    glTranslatef(0, 0, 15 * size_scale)
    glRotatef(90, 1, 0, 0)
    glutSolidSphere(int(2 * size_scale), int(8 * size_scale), 16)
    
    # Additional nose spike
    glColor3f(*dark_detail)
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0, 0, -5 * size_scale)
    glutSolidSphere(int(3 * size_scale), int(15 * size_scale), 8)
    glPopMatrix()
    
    # Side wings/fins - more aggressive design with spikes
    for y_offset, angle in [(28 * size_scale, 25), (-28 * size_scale, -25)]:  # Wider wingspan
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(0, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.4 * size_scale, 0.15 * size_scale, 0.12 * size_scale)  # Longer wings
        glutSolidCube(50)
        
        # Add wing details - ridges
        glColor3f(*dark_detail)
        glTranslatef(-15, 0, 0)
        glScalef(0.15, 0.8, 1.0)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        glPopMatrix()
        
        # Add spikes to wing tips
        glPushMatrix()
        glColor3f(*dark_detail)
        # Calculate position at wing tip
        wing_tip_x = 0
        wing_tip_y = y_offset + math.sin(math.radians(angle)) * 35 * size_scale
        wing_tip_z = 0
        glTranslatef(wing_tip_x, wing_tip_y, wing_tip_z)
        glRotatef(angle + 90, 0, 0, 1)
        glutSolidSphere(int(2 * size_scale), int(12 * size_scale), 8)
        glPopMatrix()
    
    # Energy weapons on top - more and bigger, arranged in a threatening pattern
    for x_offset, y_offset in [(-22 * size_scale, 0), (-11 * size_scale, 0), (0, 0), (11 * size_scale, 0), (22 * size_scale, 0), 
                          (-16 * size_scale, 14 * size_scale), (16 * size_scale, 14 * size_scale),
                          (-16 * size_scale, -14 * size_scale), (16 * size_scale, -14 * size_scale)]:
        glPushMatrix()
        glTranslatef(x_offset, y_offset, 12 * size_scale)
        # Weapon base
        glColor3f(*dark_detail)
        glutSolidSphere(int(3.5 * size_scale), 10, 10)
        # Weapon barrel
        glColor3f(*accent_color)
        glRotatef(-90, 1, 0, 0)
        glutSolidSphere(int(2 * size_scale), int(12 * size_scale), 10)
        
        # Add glowing tip
        glTranslatef(0, 0, 12 * size_scale)
        glColor3f(1.0, 0.3, 0.0)  # Orange-red glow
        glutSolidSphere(int(1.5 * size_scale), 8, 8)
        glPopMatrix()
    
    # Rear section with larger thruster - more detailed and intimidating
    glPushMatrix()
    glTranslatef(-45 * size_scale, 0, 0)
    
    # Thruster housing
    glColor3f(*hull_color)
    glScalef(0.5 * size_scale, 0.6 * size_scale, 0.6 * size_scale)  # Larger thruster
    glutSolidCube(35)
    
    # Thruster rings/details
    glColor3f(*dark_detail)
    glTranslatef(-20, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(4, 18, 16)
    
    # Additional detail
    glColor3f(*accent_color)
    glTranslatef(0, 0, 0)
    glutSolidSphere(2, 12, 12)
    glPopMatrix()
    
    # Engine glow - enhanced with layered, menacing effect
    glPushMatrix()
    glTranslatef(-55 * size_scale, 0, 0)
    
    # Inner core - bright
    glColor3f(1.0, 0.3, 0.0)  # Orange-red
    glutSolidSphere(int(6 * size_scale), 16, 16)
    
    # Outer glow - with transparency for effect
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(0.8, 0.1, 0.0)  # Semi-transparent red
    glutSolidSphere(int(10 * size_scale), 16, 16)
    glDisable(GL_BLEND)
    glPopMatrix()
    
    # Side thrusters - enhanced and more intimidating
    for y_offset in [-20 * size_scale, 20 * size_scale]:  # Wider spacing
        glPushMatrix()
        glTranslatef(-43 * size_scale, y_offset, 0)
        # Thruster housing
        glColor3f(*dark_detail)
        glScalef(0.3 * size_scale, 0.3 * size_scale, 0.3 * size_scale)
        glutSolidCube(20)
        
        # Add detail ring
        glColor3f(*accent_color)
        glTranslatef(-12, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidSphere(2.5, 9, 12)
        
        # Thruster glow
        glColor3f(1.0, 0.2, 0.0)  # Brighter glow
        glTranslatef(0, 0, 0)
        glutSolidSphere(int(5 * size_scale), 12, 12)
        glPopMatrix()
    
    # Energy core on top - larger, more complex and menacing
    glPushMatrix()
    glTranslatef(-25 * size_scale, 0, 18 * size_scale)  # Higher position
    
    # Pulsing core
    glColor3f(*energy_core_color)
    glutSolidSphere(int(6 * size_scale), 16, 16)
    
    # Surrounding structure - cage-like
    glColor3f(*dark_detail)
    glRotatef(45, 1, 0, 0)
    glutSolidSphere(int(1.8 * size_scale), int(8 * size_scale), 16)
    
    # Second ring at different angle
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(1.8 * size_scale), int(8 * size_scale), 16)
    
    # Energy conduits to weapons and engines
    glColor3f(*accent_color)
    glRotatef(-45, 0, 1, 0)
    glTranslatef(-10 * size_scale, 0, -10 * size_scale)
    glScalef(1.2 * size_scale, 0.15 * size_scale, 0.15 * size_scale)
    glutSolidCube(25)
    glPopMatrix()
    
    # Add spine-like structures along the top - new menacing feature
    for z_pos in range(-20, 21, 10):
        glPushMatrix()
        glColor3f(*dark_detail)
        glTranslatef(z_pos * size_scale * 0.7, 0, 15 * size_scale)
        glRotatef(90, 1, 0, 0)
        glutSolidSphere(int(2 * size_scale), int(10 * size_scale), 6)
        glPopMatrix()
    
    # Thruster flame effects - enhanced for more menacing look
    glPushMatrix()
    glTranslatef(-65 * size_scale, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Outer flame
    glColor3f(0.8, 0.1, 0.0)  # Red flame
    glutSolidSphere(int(9 * size_scale), int(25 * size_scale), 12)
    
    # Middle flame
    glColor3f(1.0, 0.2, 0.0)  # Orange-red
    glutSolidSphere(int(7 * size_scale), int(20 * size_scale), 12)
    
    # Inner flame - brighter core
    glColor3f(1.0, 0.5, 0.0)  # Bright orange inner flame
    glutSolidSphere(int(4 * size_scale), int(15 * size_scale), 8)
    
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_boss_spaceship():
    """Draw the final boss spaceship with enhanced purple-black coloring and massive size"""
    # Colors for the final boss - purple and black theme
    hull_color = (0.06, 0.02, 0.08)       # Almost black with purple tint
    accent_color = (0.6, 0.0, 0.8)        # Bright purple accent
    highlight_color = (0.3, 0.0, 0.4)     # Dark purple highlight
    energy_core_color = (1.0, 0.2, 1.0)   # Bright purple energy
    dark_detail = (0.12, 0.04, 0.15)      # Very dark purple for details
    
    # Boss is much larger - 2.5 times the size of standard enemies
    size_scale = 6.0  # INSANELY HUGE! (was 2.5)
    
    # Main hull - massive and imposing
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(2.6 * size_scale, 1.1 * size_scale, 0.6 * size_scale)  # Larger, wider design
    glutSolidCube(25)
    glPopMatrix()
    
    # Upper structure - more angular and menacing
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(0, 0, 9 * size_scale)
    glScalef(2.1 * size_scale, 0.9 * size_scale, 0.25 * size_scale)
    glutSolidCube(25)
    
    # Add ridged detail on top
    glColor3f(*dark_detail)
    glTranslatef(0, 0, 3)
    glScalef(0.9, 0.7, 0.5)
    glutSolidCube(25)
    glPopMatrix()
    
    # Command module at front - more massive and imposing
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(35 * size_scale, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(14 * size_scale), int(35 * size_scale), 16)  # Longer, sharper nose
    
    # Add menacing detail to the front
    glColor3f(*accent_color)
    glTranslatef(0, 0, 15 * size_scale)
    glRotatef(90, 1, 0, 0)
    glutSolidSphere(int(2 * size_scale), int(8 * size_scale), 16)
    
    # Additional nose spike
    glColor3f(*dark_detail)
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0, 0, -5 * size_scale)
    glutSolidSphere(int(3 * size_scale), int(15 * size_scale), 8)
    glPopMatrix()
    
    # Side wings/fins - more aggressive design with spikes
    for y_offset, angle in [(28 * size_scale, 25), (-28 * size_scale, -25)]:  # Wider wingspan
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(0, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.4 * size_scale, 0.15 * size_scale, 0.12 * size_scale)  # Longer wings
        glutSolidCube(50)
        
        # Add wing details - ridges
        glColor3f(*dark_detail)
        glTranslatef(-15, 0, 0)
        glScalef(0.15, 0.8, 1.0)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        
        glTranslatef(30, 0, 0)
        glutSolidCube(50)
        glPopMatrix()
        
        # Add spikes to wing tips
        glPushMatrix()
        glColor3f(*dark_detail)
        # Calculate position at wing tip
        wing_tip_x = 0
        wing_tip_y = y_offset + math.sin(math.radians(angle)) * 35 * size_scale
        wing_tip_z = 0
        glTranslatef(wing_tip_x, wing_tip_y, wing_tip_z)
        glRotatef(angle + 90, 0, 0, 1)
        glutSolidSphere(int(2 * size_scale), int(12 * size_scale), 8)
        glPopMatrix()
    
    # Additional side wings for more imposing silhouette
    for y_offset, angle in [(35 * size_scale, 40), (-35 * size_scale, -40)]:
        glPushMatrix()
        glColor3f(*highlight_color)
        glTranslatef(-20 * size_scale, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.0 * size_scale, 0.15 * size_scale, 0.1 * size_scale)
        glutSolidCube(60)
        glPopMatrix()
    
    # Energy weapons on top - more and bigger, arranged in a threatening pattern
    for x_offset, y_offset in [(-25 * size_scale, 0), (-12 * size_scale, 0), (0, 0), (12 * size_scale, 0), (25 * size_scale, 0), 
                          (-20 * size_scale, 18 * size_scale), (20 * size_scale, 18 * size_scale),
                          (-20 * size_scale, -18 * size_scale), (20 * size_scale, -18 * size_scale),
                          (-10 * size_scale, 30 * size_scale), (10 * size_scale, 30 * size_scale),
                          (-10 * size_scale, -30 * size_scale), (10 * size_scale, -30 * size_scale)]:
        glPushMatrix()
        glTranslatef(x_offset, y_offset, 12 * size_scale)
        # Weapon base
        glColor3f(*dark_detail)
        glutSolidSphere(int(3.5 * size_scale), 10, 10)
        # Weapon barrel
        glColor3f(*accent_color)
        glRotatef(-90, 1, 0, 0)
        glutSolidSphere(int(2 * size_scale), int(12 * size_scale), 10)
        
        # Add glowing tip
        glTranslatef(0, 0, 12 * size_scale)
        glColor3f(1.0, 0.3, 1.0)  # Purple glow
        glutSolidSphere(int(1.5 * size_scale), 8, 8)
        glPopMatrix()
    
    # Rear section with larger thruster - more detailed and intimidating
    glPushMatrix()
    glTranslatef(-45 * size_scale, 0, 0)
    
    # Thruster housing
    glColor3f(*hull_color)
    glScalef(0.5 * size_scale, 0.6 * size_scale, 0.6 * size_scale)  # Larger thruster
    glutSolidCube(35)
    
    # Thruster rings/details
    glColor3f(*dark_detail)
    glTranslatef(-20, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(4, 18, 16)
    
    # Additional detail
    glColor3f(*accent_color)
    glTranslatef(0, 0, 0)
    glutSolidSphere(2, 12, 12)
    glPopMatrix()
    
    # Engine glow - enhanced with layered, menacing effect
    glPushMatrix()
    glTranslatef(-55 * size_scale, 0, 0)
    
    # Inner core - bright
    glColor3f(0.8, 0.3, 1.0)  # Purple core
    glutSolidSphere(int(6 * size_scale), 16, 16)
    
    # Outer glow - with transparency for effect
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(0.6, 0.1, 0.8)  # Semi-transparent purple
    glutSolidSphere(int(10 * size_scale), 16, 16)
    glDisable(GL_BLEND)
    glPopMatrix()
    
    # Side thrusters - enhanced and more intimidating
    for y_offset in [-20 * size_scale, 20 * size_scale]:  # Wider spacing
        glPushMatrix()
        glTranslatef(-43 * size_scale, y_offset, 0)
        # Thruster housing
        glColor3f(*dark_detail)
        glScalef(0.3 * size_scale, 0.3 * size_scale, 0.3 * size_scale)
        glutSolidCube(20)
        
        # Add detail ring
        glColor3f(*accent_color)
        glTranslatef(-12, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidSphere(3, 9, 12)
        
        # Thruster glow
        glColor3f(0.8, 0.2, 1.0)  # Brighter purple glow
        glTranslatef(0, 0, 0)
        glutSolidSphere(int(5 * size_scale), 12, 12)
        glPopMatrix()
    
    # Energy core on top - larger, more complex and menacing
    glPushMatrix()
    glTranslatef(-25 * size_scale, 0, 20 * size_scale)  # Higher position
    
    # Pulsing core
    glColor3f(*energy_core_color)
    glutSolidSphere(int(8 * size_scale), 16, 16)
    
    # Surrounding structure - cage-like
    glColor3f(*dark_detail)
    glRotatef(45, 1, 0, 0)
    glutSolidSphere(int(1.8 * size_scale), int(10 * size_scale), 16)
    
    # Second ring at different angle
    glRotatef(90, 0, 1, 0)
    glutSolidSphere(int(1.8 * size_scale), int(10 * size_scale), 16)
    
    # Energy conduits to weapons and engines
    glColor3f(*accent_color)
    glRotatef(-45, 0, 1, 0)
    glTranslatef(-10 * size_scale, 0, -10 * size_scale)
    glScalef(1.2 * size_scale, 0.15 * size_scale, 0.15 * size_scale)
    glutSolidCube(25)
    glPopMatrix()
    
    # Add spine-like structures along the top - new menacing feature
    for z_pos in range(-20, 21, 8):  # More spines, closer together
        glPushMatrix()
        glColor3f(*dark_detail)
        glTranslatef(z_pos * size_scale * 0.7, 0, 15 * size_scale)
        glRotatef(90, 1, 0, 0)
        glutSolidSphere(int(2 * size_scale), int(10 * size_scale), 6)
        glPopMatrix()
    
    # Add additional armor plates to make it bulkier
    for x_offset, y_factor in [(-20, 1), (0, 1.1), (20, 1)]:
        glPushMatrix()
        glColor3f(*hull_color)
        glTranslatef(x_offset * size_scale, 0, 5 * size_scale)
        glScalef(0.5 * size_scale, 1.0 * size_scale * y_factor, 0.3 * size_scale)
        glutSolidCube(30)
        glPopMatrix()
    
    # Thruster flame effects - enhanced for more menacing look
    glPushMatrix()
    glTranslatef(-65 * size_scale, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Outer flame
    glColor3f(0.7, 0.2, 1.0)  # Purple flame
    glutSolidSphere(int(8 * size_scale), int(25 * size_scale), 16)
    
    # Middle flame
    glColor3f(0.9, 0.3, 1.0)  # Lighter purple
    glutSolidSphere(int(6 * size_scale), int(20 * size_scale), 12)
    
    # Inner flame
    glColor3f(1.0, 0.5, 1.0)  # Bright purple inner flame
    glutSolidSphere(int(4 * size_scale), int(15 * size_scale), 8)
    
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_laser_beam(is_enemy=False):
    """Draw a laser beam"""
    if is_enemy:
        glColor3f(1, 0.3, 0)  # Orange-red for enemy lasers
    else:
        glColor3f(0, 0.8, 1)  # Cyan-blue for player lasers
    
    # Draw a long, thin beam using a scaled cube
    glPushMatrix()
    glScalef(30, 0.5, 0.5)  # Long in the x direction, thin in y and z
    glutSolidCube(5)
    glPopMatrix()

def draw_explosion(size):
    """Draw an explosion"""
    glColor3f(1, 0.5, 0)  # Orange
    glutSolidSphere(int(size), 10, 10)
    
    glPushMatrix()
    glColor3f(1, 0, 0)  # Red
    glutSolidSphere(int(size * 0.7), 8, 8)
    glPopMatrix()

def draw_radar():
    """Draw a radar in the corner of the screen"""
    glPushMatrix()
    
    # Set up orthographic projection for 2D overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Draw radar circle outline (no background fill)
    glColor3f(0, 0.7, 0.7)  # Cyan outline
    
    glBegin(GL_LINES)
    for i in range(360):
        angle1 = i * math.pi / 180
        angle2 = (i + 1) * math.pi / 180
        glVertex2f(100 + 80 * math.cos(angle1), 100 + 80 * math.sin(angle1))
        glVertex2f(100 + 80 * math.cos(angle2), 100 + 80 * math.sin(angle2))
    glEnd()
    
    # Draw radar grid
    glColor3f(0, 0.5, 0.5)  # Darker cyan
    glBegin(GL_LINES)
    glVertex2f(20, 100)
    glVertex2f(180, 100)
    glVertex2f(100, 20)
    glVertex2f(100, 180)
    glEnd()
    
    # Draw radar sweep line (direction facing)
    glColor3f(0, 1, 0.7)  # Bright cyan
    glBegin(GL_LINES)
    glVertex2f(100, 100)
    glVertex2f(100 + 80 * math.cos(player_rotation * math.pi / 180), 
               100 + 80 * math.sin(player_rotation * math.pi / 180))
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

    # Draw cardinal direction labels (N, S, E, W) around the radar
    # These should rotate with the player's rotation
    directions = ['N', 'E', 'S', 'W']
    for i, label in enumerate(directions):
        # 0 = N, 1 = E, 2 = S, 3 = W
        base_angle = i * 90  # 0, 90, 180, 270
        # Adjust for player rotation (so N always points to world north)
        angle = (base_angle - player_rotation) * math.pi / 180
        label_x = 100 + 90 * math.cos(angle) - 8  # -8 to center text
        label_y = 100 + 90 * math.sin(angle) - 8
        draw_text(label_x, label_y, label)

    # Reset matrix state
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glPopMatrix()

def draw_hud():
    """Draw the heads-up display (HUD)"""
    global game_won
    
    # Player health and lives display (top left)
    health_percentage = player_health / player_max_health * 100
    draw_text(10, 770, f"HEALTH: {int(health_percentage)}%")
    draw_text(10, 740, f"LIVES: {player_lives}")
    
    # Health bar (graphical)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw health bar background (dark gray)
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(10, 710)
    glVertex2f(210, 710)
    glVertex2f(210, 730)
    glVertex2f(10, 730)
    glEnd()
    
    # Draw health bar (color based on health percentage)
    if health_percentage > 60:
        glColor3f(0, 1, 0.3)  # Green for high health
    elif health_percentage > 30:
        glColor3f(1, 1, 0)  # Yellow for medium health
    else:
        glColor3f(1, 0.3, 0)  # Red for low health
    
    bar_width = 200 * (player_health / player_max_health)
    glBegin(GL_QUADS)
    glVertex2f(10, 710)
    glVertex2f(10 + bar_width, 710)
    glVertex2f(10 + bar_width, 730)
    glVertex2f(10, 730)
    glEnd()
    
    # Draw Boss health bar when in level 4
    if player_level == 4:
        # Find the boss if it exists
        boss_health = 0
        for enemy in enemies:
            if len(enemy) > 7 and enemy[7] == "boss" and len(enemy) > 8:
                boss_health = enemy[8]
                break
        
        if boss_health > 0:
            # Draw boss health text
            glColor3f(1, 0, 0)  # Red text for boss health
            draw_text(400, 750, f"BOSS: {boss_health}/10000", GLUT_BITMAP_HELVETICA_18)
            
            # Draw boss health bar (background)
            glColor3f(0.3, 0.0, 0.0)  # Dark red background
            glBegin(GL_QUADS)
            glVertex2f(300, 730)
            glVertex2f(700, 730)
            glVertex2f(700, 745)
            glVertex2f(300, 745)
            glEnd()
            
            # Draw boss health bar (foreground)
            health_ratio = boss_health / 10000.0
            glColor3f(1.0, 0.0, 0.0)  # Bright red for boss health
            glBegin(GL_QUADS)
            glVertex2f(300, 730)
            glVertex2f(300 + 400 * health_ratio, 730)
            glVertex2f(300 + 400 * health_ratio, 745)
            glVertex2f(300, 745)
            glEnd()
    
    # Restore matrix state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # Speed indicator
    draw_text(10, 680, f"SPEED: {int(player_speed * 200)} KPH")
    
    # Score
    draw_text(10, 650, f"SCORE: {score}")
    
    # Ammo
    draw_text(800, 750, f"LASERS: {len(player_bullets)}/50")
    
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
    
    # Player experience and level display
    draw_text(800, 780, f"EXP: {player_experience}")  # Top right
    
    # Make level display more prominent, especially for level 4
    if player_level == 4:
        # Draw a more noticeable level indicator for the final level
        draw_text(450, 780, "FINAL LEVEL", GLUT_BITMAP_TIMES_ROMAN_24)
    else:
        draw_text(500, 780, f"LEVEL: {player_level}")  # Top center
    
    # If the player has won, display the victory message
    if game_won:
        # Static victory indicator for defeating the boss
        draw_text(400, 500, "BOSS DEFEATED - YOU WON!", GLUT_BITMAP_HELVETICA_18)
        draw_text(380, 300, f"Current Score: {score}", GLUT_BITMAP_HELVETICA_18)
        draw_text(390, 350, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Semi-transparent dark overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(0.0, 0.0, 0.0)
        
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(1000, 0)
        glVertex2f(1000, 800)
        glVertex2f(0, 800)
        glEnd()
        # Restore matrix state
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        

def draw_battlefield():
    """Draw the space battlefield with animated floor grid"""
    # Draw a starfield background
    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(1, 1, 1)  # White stars
    for i in range(1000):  # Doubled the number of stars
        x = random.uniform(-BATTLEFIELD_SIZE*3, BATTLEFIELD_SIZE*3)  # Extended star field
        y = random.uniform(-BATTLEFIELD_SIZE*3, BATTLEFIELD_SIZE*3)  # Extended star field
        z = random.uniform(-BATTLEFIELD_SIZE*2, 0)  # Stars below the battlefield
        glVertex3f(x, y, z)
    glEnd()
    
    # Draw the animated grid floor
    draw_animated_floor()
    
    # Draw invisible boundary indicators
    draw_battlefield_boundaries()

def draw_animated_floor():
    """Draw an animated grid floor that gives a sense of movement"""
    global grid_offset_x, grid_offset_y
    
    # Calculate grid offsets based on player orientation and speed
    rad = player_rotation * math.pi / 180
    movement_x = math.cos(rad) * grid_animation_speed
    movement_y = math.sin(rad) * grid_animation_speed
    
    # Update grid offsets
    grid_offset_x = (grid_offset_x + movement_x) % grid_line_spacing
    grid_offset_y = (grid_offset_y + movement_y) % grid_line_spacing
    
    glBegin(GL_LINES)
    glColor3f(0.2, 0.4, 0.8)  # Light blue grid
    
    # Draw an extended grid to create motion effect
    # The grid should extend beyond player's view for smooth animation
    grid_size = BATTLEFIELD_SIZE * 2  # Extended grid size
    
    # Draw X-axis lines
    for i in range(-grid_size, grid_size + grid_line_spacing, grid_line_spacing):
        grid_pos = i - grid_offset_x
        glVertex3f(grid_pos, -grid_size, 0)
        glVertex3f(grid_pos, grid_size, 0)
    
    # Draw Y-axis lines
    for i in range(-grid_size, grid_size + grid_line_spacing, grid_line_spacing):
        grid_pos = i - grid_offset_y
        glVertex3f(-grid_size, grid_pos, 0)
        glVertex3f(grid_size, grid_pos, 0)
    
    glEnd()

def draw_player():
    """Draw the player's spaceship"""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_rotation, 0, 0, 1)  # Rotate around z-axis
    draw_spaceship(True)
    glPopMatrix()

def draw_enemies():
    """Draw enemy spaceships"""
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy[0], enemy[1], enemy[2])
        glRotatef(enemy[3], 0, 0, 1)  # Rotate around z-axis
        
        # Check enemy type (stored in enemy[7])
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
    """Draw laser beams"""
    for bullet in player_bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glRotatef(bullet[3], 0, 0, 1)  # Rotate to match firing direction
        draw_laser_beam(False)  # Player lasers
        glPopMatrix()
    
    for bullet in enemy_bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glRotatef(bullet[3], 0, 0, 1)  # Rotate to match firing direction
        draw_laser_beam(True)  # Enemy lasers
        glPopMatrix()

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement and actions
    """
    global player_pos, player_rotation, player_speed, player_boost_speed, player_bullets, game_over, camera_mode, grid_animation_speed, camera_distance
    global moving_forward, moving_backward, thruster_glow_intensity
    
    if key == b'\x1b':  # ESC key
        sys.exit(0)
        
    if game_over or game_won:
        if key == b'r':  # Reset game
            reset_game()
        return
        
    # Move forward (W key) with increased speed
    if key == b'w':
        rad = player_rotation * math.pi / 180
        # Using enhanced speed for forward movement
        movement_speed = player_boost_speed
        # Calculate new position
        new_x = player_pos[0] + math.cos(rad) * movement_speed
        new_y = player_pos[1] + math.sin(rad) * movement_speed
        
        # Check battlefield boundaries before moving
        if abs(new_x) < BATTLEFIELD_SIZE and abs(new_y) < BATTLEFIELD_SIZE:
            player_pos[0] = new_x
            player_pos[1] = new_y
            moving_forward = True
            moving_backward = False
        else:
            # If would hit boundary, still allow partial movement (slide along boundary)
            if abs(new_x) < BATTLEFIELD_SIZE:
                player_pos[0] = new_x
            if abs(new_y) < BATTLEFIELD_SIZE:
                player_pos[1] = new_y
            moving_forward = True
    
    # Move backward (S key) with increased speed
    if key == b's':
        rad = player_rotation * math.pi / 180
        # Same speed for backward movement
        movement_speed = player_speed
        # Calculate new position
        new_x = player_pos[0] - math.cos(rad) * movement_speed
        new_y = player_pos[1] - math.sin(rad) * movement_speed
        
        # Check battlefield boundaries before moving
        if abs(new_x) < BATTLEFIELD_SIZE and abs(new_y) < BATTLEFIELD_SIZE:
            player_pos[0] = new_x
            player_pos[1] = new_y
            moving_backward = True
            moving_forward = False
        else:
            # If would hit boundary, still allow partial movement (slide along boundary)
            if abs(new_x) < BATTLEFIELD_SIZE:
                player_pos[0] = new_x
            if abs(new_y) < BATTLEFIELD_SIZE:
                player_pos[1] = new_y
            moving_backward = True
    
    # Reset movement flags when releasing W or S
    if key not in (b'w', b's'):
        moving_forward = False
        moving_backward = False
    
    # Strafe left (A key) with increased speed
    if key == b'a':
        rad = (player_rotation + 90) * math.pi / 180  # 90 degrees to the left of player orientation
        # Enhanced speed for strafing
        movement_speed = player_boost_speed
        # Calculate new position
        new_x = player_pos[0] + math.cos(rad) * movement_speed
        new_y = player_pos[1] + math.sin(rad) * movement_speed
        
        # Check battlefield boundaries before moving
        if abs(new_x) < BATTLEFIELD_SIZE and abs(new_y) < BATTLEFIELD_SIZE:
            player_pos[0] = new_x
            player_pos[1] = new_y
        else:
            # If would hit boundary, still allow partial movement (slide along boundary)
            if abs(new_x) < BATTLEFIELD_SIZE:
                player_pos[0] = new_x
            if abs(new_y) < BATTLEFIELD_SIZE:
                player_pos[1] = new_y
    
    # Strafe right (D key) with increased speed
    if key == b'd':
        rad = (player_rotation - 90) * math.pi / 180  # 90 degrees to the right of player orientation
        # Enhanced speed for strafing
        movement_speed = player_boost_speed
        # Calculate new position
        new_x = player_pos[0] + math.cos(rad) * movement_speed
        new_y = player_pos[1] + math.sin(rad) * movement_speed
        
        # Check battlefield boundaries before moving
        if abs(new_x) < BATTLEFIELD_SIZE and abs(new_y) < BATTLEFIELD_SIZE:
            player_pos[0] = new_x
            player_pos[1] = new_y
        else:
            # If would hit boundary, still allow partial movement (slide along boundary)
            if abs(new_x) < BATTLEFIELD_SIZE:
                player_pos[0] = new_x
            if abs(new_y) < BATTLEFIELD_SIZE:
                player_pos[1] = new_y
    
    # Rise (R key) with increased speed - add height limit
    if key == b'r':
        new_z = player_pos[2] + player_speed
        # Limit maximum height to prevent leaving the battlefield vertically
        if new_z < 500:  # Maximum height
            player_pos[2] = new_z
    
    # Descend (F key) with increased speed - add minimum height
    if key == b'f':
        new_z = player_pos[2] - player_speed
        # Prevent going below a minimum height
        if new_z > 20:  # Minimum height above battlefield floor
            player_pos[2] = new_z
    
    # Toggle camera mode (C key)
    if key == b'c':
        camera_mode = 1 - camera_mode  # Toggle between 0 and 1
        
    # Fire lasers (Shift key)
    if key in (b'\x10', b' '):  # Left shift (0x10) or spacebar as alternative
        if len(player_bullets) < 50:  # Limit number of laser beams
            rad = player_rotation * math.pi / 180
            offsets = [
                (-18, 18),   # Far left
                (-9, 9),     # Left-center
                (0, 0),      # Center
                (9, -9),     # Right-center
                (18, -18)    # Far right
            ]
            for offset_x, offset_y in offsets:
                laser = [
                    player_pos[0] + 30 * math.cos(rad) + offset_x * math.sin(rad),
                    player_pos[1] + 30 * math.sin(rad) + offset_y * math.cos(rad),
                    player_pos[2],
                    player_rotation,
                    player_boost_speed + 20,  # Faster bullet speed based on boosted speed
                    200  # Increased lifetime for longer range
                ]
                player_bullets.append(laser)

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for player rotation and camera distance
    """
    global player_rotation, camera_distance
    
    # Rotate left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        player_rotation = (player_rotation + 5) % 360
    
    # Rotate right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        player_rotation = (player_rotation - 5) % 360
    
    # Move camera farther (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_distance = min(camera_distance + 10, 1000)  # Set a reasonable max distance
    
    # Move camera closer (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_distance = max(camera_distance - 10, 50)  # Set a reasonable min distance

def mouseListener(button, state, x, y):
    """
    Handles mouse inputs (no longer used for firing)
    """
    # Mouse click functionality moved to keyboard handler
    pass

def update_game():
    """
    Update game state - move bullets, check collisions, etc.
    """
    global player_bullets, enemy_bullets, enemies, score, game_over, thruster_glow_intensity
    global player_health, player_lives, hit_flash_duration, player_experience, player_level, game_won, enemies_respawn_timer
    
    # If the game has won, continue the game but keep the victory message
    # Allow player to continue fighting enemies
    if game_won:
        # Increment the respawn timer
        enemies_respawn_timer += 1
        
        # If there are no enemies, spawn new ones after a delay
        if len(enemies) == 0 and enemies_respawn_timer > 180:  # Wait 3 seconds after victory
            spawn_enemy("boss")
            for i in range(5):
                spawn_enemy("black-red")
            for i in range(3):
                spawn_enemy("golden")
    
    # Update hit flash effect (decreases over time)
    if hit_flash_duration > 0:
        hit_flash_duration -= 1
    
    # Set thruster glow intensity to 0 (no thruster effects)
    thruster_glow_intensity = 0.0
    
    # Update player bullets
    for bullet in player_bullets[:]:  # Use a copy for safe removal
        # Move bullet forward based on its direction
        rad = bullet[3] * math.pi / 180
        bullet[0] += math.cos(rad) * bullet[4]
        bullet[1] += math.sin(rad) * bullet[4]
        
        # Decrease lifetime
        bullet[5] -= 1
        
        # Remove bullet if lifetime expired
        if bullet[5] <= 0:
            player_bullets.remove(bullet)
            continue
        
        # Check for collisions with enemies
        for enemy in enemies[:]:  # Use a copy for safe removal
            dx = bullet[0] - enemy[0]
            dy = bullet[1] - enemy[1]
            dz = bullet[2] - enemy[2]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Adjust hit detection radius based on enemy type
            hit_radius = 30
            if len(enemy) > 7:
                if enemy[7] == "boss":
                    hit_radius = 50  # Boss has a larger hit radius
                elif enemy[7] == "black-red" or enemy[7] == "golden":
                    hit_radius = 35  # Special enemies have slightly larger hit radius
            
            if distance < hit_radius:  # Hit!
                if bullet in player_bullets:  # Ensure bullet still exists
                    player_bullets.remove(bullet)
                
                # Boss and special enemies take multiple hits to destroy
                if len(enemy) > 7:
                    if enemy[7] == "boss":
                        # Boss has a "health" parameter at index 8 if it exists
                        if len(enemy) > 8:
                            enemy[8] -= 100  # Each hit reduces boss health by 100
                            if enemy[8] > 0:
                                continue  # Boss isn't destroyed yet
                        else:
                            # Initialize boss health if not set
                            enemy.append(10000)  # Boss has 10000 health
                            continue  # Boss isn't destroyed yet
                    elif enemy[7] == "black-red":
                        # Black-red enemies take 3 hits
                        if len(enemy) > 8:
                            enemy[8] -= 1
                            if enemy[8] > 0:
                                continue  # Not destroyed yet
                        else:
                            # Initialize health
                            enemy.append(3)
                            continue
                    elif enemy[7] == "golden":
                        # Golden enemies take 2 hits
                        if len(enemy) > 8:
                            enemy[8] -= 1
                            if enemy[8] > 0:
                                continue  # Not destroyed yet
                        else:
                            # Initialize health
                            enemy.append(2)
                            continue
                
                enemies.remove(enemy)
                score += 100
                
                # Increase player experience
                player_experience += 10
                
                # Check if we're in level 4 and just defeated a boss
                if player_level == 4 and len(enemy) > 7 and enemy[7] == "boss":
                    game_won = True
                
                # Normal level up check
                if player_experience >= 100:
                    player_level += 1
                    player_experience -= 100  # Reset experience for next level
                    
                    # Clear all existing enemies regardless of level
                    enemies.clear()
                    
                    # Special event for level 4 (final boss level)
                    if player_level == 4:
                        # Spawn 1 boss spaceship
                        spawn_enemy("boss")
                        
                        # Spawn 3 black-red enemies as the boss's guards
                        for i in range(3):
                            spawn_enemy("black-red")
                    
                    # Special event for level 3
                    elif player_level == 3:
                        # Spawn 9 black-red enemies
                        for i in range(9):
                            spawn_enemy("black-red")
                            
                        # Spawn 5 golden enemies
                        for i in range(5):
                            spawn_enemy("golden")
                    # Original special event for other level-ups
                    else:
                        # Spawn 8 golden enemies
                        for i in range(8):
                            spawn_enemy("golden")
                            
                        # Spawn 5 red enemies
                        for i in range(5):
                            spawn_enemy("red")
                else:
                    # Only spawn a new enemy if it wasn't a level up event and we're not in level 4
                    if player_level < 4 and not game_won:
                        spawn_enemy("red")
                    elif game_won and len(enemies) < 5:
                        # If game is won (beat level 4 boss), spawn random enemies occasionally
                        enemy_types = ["red", "golden", "black-red"]
                        spawn_enemy(random.choice(enemy_types))
                
                break
    
    # Skip updates if game is over
    if game_over:
        return
    
    # Update enemy bullets
    for bullet in enemy_bullets[:]:
        # Move bullet forward based on its direction
        rad = bullet[3] * math.pi / 180
        bullet[0] += math.cos(rad) * bullet[4]
        bullet[1] += math.sin(rad) * bullet[4]
        
        # Decrease lifetime
        bullet[5] -= 1
        
        # Remove bullet if lifetime expired
        if bullet[5] <= 0:
            enemy_bullets.remove(bullet)
            continue
        
        # Check for collision with player
        dx = bullet[0] - player_pos[0]
        dy = bullet[1] - player_pos[1]
        dz = bullet[2] - player_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < 30:  # Hit player!
            enemy_bullets.remove(bullet)
            
            # Determine damage based on bullet source
            damage = DAMAGE_PER_HIT
            
            # Boss bullets do double damage
            if len(bullet) > 6 and bullet[6] == "boss":  
                damage = DAMAGE_PER_HIT * 2
            
            # Apply damage and show hit effect
            player_health -= damage
            hit_flash_duration = 10  # Set flash duration (frames)
            
            # Check if player lost a life
            if player_health <= 0:
                player_lives -= 1
                
                if player_lives > 0:
                    # Player still has lives left
                    player_health = player_max_health  # Reset health for next life
                else:
                    # Player is out of lives - game over
                    game_over = True
    
    # Update enemies
    for enemy in enemies:
        # Calculate distance to player
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]
        dz = player_pos[2] - enemy[2]
        distance_to_player = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Get this enemy's preferred distance
        preferred_distance = enemy[6]
        
        # Update target position occasionally to maintain fixed position in space
        if random.random() < 0.02:  # Reduced update frequency to keep positions more stable
            # Either stay at current position or choose a new random position
            if random.random() < 0.7:  # 70% chance to just maintain current position
                enemy[5] = [enemy[0], enemy[1], enemy[2]]
            else:  # 30% chance to pick a new random position
                # Calculate a random position at preferred distance from player
                angle = random.uniform(0, 2 * math.pi)
                distance = preferred_distance * random.uniform(0.9, 1.1)
                
                target_x = player_pos[0] + math.cos(angle) * distance
                target_y = player_pos[1] + math.sin(angle) * distance
                target_z = random.uniform(player_pos[2] - 100, player_pos[2] + 100)
                
                # Clamp to battlefield bounds
                target_x = max(min(target_x, BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
                target_y = max(min(target_y, BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
                target_z = max(min(target_z, 500), 50)
                
                enemy[5] = [target_x, target_y, target_z]
        
        # Move toward target position if not close enough and only if we have a target
        if enemy[5][0] != 0 or enemy[5][1] != 0 or enemy[5][2] != 0:
            target_x, target_y, target_z = enemy[5]
            dx_target = target_x - enemy[0]
            dy_target = target_y - enemy[1]
            dz_target = target_z - enemy[2]
            distance_to_target = math.sqrt(dx_target*dx_target + dy_target*dy_target + dz_target*dz_target)
            
            if distance_to_target > 10:  # Only move if not at target position
                # Calculate direction to target
                move_speed = 2
                enemy[0] += dx_target / distance_to_target * move_speed
                enemy[1] += dy_target / distance_to_target * move_speed
                enemy[2] += dz_target / distance_to_target * move_speed
        
        # Keep enemies within battlefield bounds
        enemy[0] = max(min(enemy[0], BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
        enemy[1] = max(min(enemy[1], BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
        enemy[2] = max(min(enemy[2], 500), 50)
        
        # Update enemy rotation to face player
        enemy[3] = math.degrees(math.atan2(dy, dx)) % 360
        
        # If too close to player, move away rapidly
        if distance_to_player < preferred_distance * 0.8:
            # Calculate direction away from player
            move_dir_x = enemy[0] - player_pos[0]
            move_dir_y = enemy[1] - player_pos[1]
            move_dir_len = math.sqrt(move_dir_x*move_dir_x + move_dir_y*move_dir_y)
            
            if move_dir_len > 0:  # Avoid division by zero
                # Move away from player
                move_speed = 5  # Faster escape speed
                enemy[0] += move_dir_x / move_dir_len * move_speed
                enemy[1] += move_dir_y / move_dir_len * move_speed
        
        # Random shooting behavior
        # Decrement shooting cooldown
        enemy[4] -= 1
        
        # Check if enemy can shoot - now based on random chance and distance
        if enemy[4] <= 0 and distance_to_player < MAX_SHOOTING_DISTANCE:
            # Determine shooting chance - much higher for boss
            shoot_chance = ENEMY_SHOOT_CHANCE
            if len(enemy) > 7 and enemy[7] == "boss":
                shoot_chance = 0.05  # Moderate chance for boss to shoot (adjusted from 0.08)
            
            if random.random() < shoot_chance:
                # Reset cooldown with some randomization
                if len(enemy) > 7 and enemy[7] == "boss":
                    # Boss has a longer cooldown - shoots at reasonable intervals
                    enemy[4] = random.randint(45, 60)  # Slower shooting (0.75-1.0 seconds at 60 FPS)
                else:
                    enemy[4] = random.randint(int(ENEMY_SHOOT_COOLDOWN * 0.7), int(ENEMY_SHOOT_COOLDOWN * 1.3))
                
                # Calculate shooting angle to hit player
                dx = player_pos[0] - enemy[0]
                dy = player_pos[1] - enemy[1]
                shoot_angle = math.degrees(math.atan2(dy, dx))
                
                # Add a small amount of inaccuracy based on distance - more accurate now
                accuracy_factor = min(1.0, 600 / max(distance_to_player, 1))  # Normalize based on distance
                angle_variance = random.uniform(-3, 3) * (1 - accuracy_factor)  # Significantly reduced variance
                shoot_angle += angle_variance
                
                # Determine number of lasers to shoot based on enemy type
                num_lasers = 1
                if len(enemy) > 7:  # Check if enemy has a type specified
                    if enemy[7] == "golden":
                        num_lasers = 2  # Golden enemies shoot 2 lasers
                    elif enemy[7] == "black-red":
                        num_lasers = 3  # Black-red enemies shoot 3 lasers
                    elif enemy[7] == "boss":
                        num_lasers = 5  # Boss shoots 5 lasers (reduced from 10)
                
                # Create enemy lasers
                for i in range(num_lasers):
                    # Add slight angle variation for multiple lasers
                    laser_angle = shoot_angle
                    if num_lasers > 1:
                        # Only spread for non-boss enemies
                        if enemy[7] == "golden":
                            # Spread the lasers by 5 degrees
                            spread = 5
                            laser_angle += spread * (i - (num_lasers - 1) / 2)
                        elif enemy[7] == "black-red":
                            # Spread the lasers by 8 degrees
                            spread = 8
                            laser_angle += spread * (i - (num_lasers - 1) / 2)
                        # Boss shoots all lasers directly at player with minimal spread
                        elif enemy[7] == "boss":
                            # Just add a tiny variation for visual effect
                            laser_angle += random.uniform(-1.5, 1.5)
                    
                    # Calculate laser origin point
                    if len(enemy) > 7 and enemy[7] == "boss":
                        # Calculate front position of boss
                        size_scale = 6.0
                        front_offset = 35 * size_scale
                        
                        # Calculate positions in a grid pattern at the boss front
                        grid_size = 3  # 3x3 grid + 1 center = 10 lasers
                        row = i % grid_size
                        col = i // grid_size
                        
                        # Generate coordinates in a grid at the front of the boss
                        y_offset = (row - 1) * 15 * size_scale * 0.5
                        z_offset = (col - 1.5) * 10 * size_scale * 0.5
                        
                        # Adjust position to boss front
                        laser_x = enemy[0] + front_offset * math.cos(math.radians(laser_angle))
                        laser_y = enemy[1] + front_offset * math.sin(math.radians(laser_angle)) + y_offset
                        laser_z = enemy[2] + z_offset
                    else:
                        # Regular enemies - shoot from center with default offset
                        laser_x = enemy[0] + 30 * math.cos(math.radians(laser_angle))
                        laser_y = enemy[1] + 30 * math.sin(math.radians(laser_angle))
                        laser_z = enemy[2]
                    
                    # Create the laser beam
                    enemy_laser = [
                        laser_x,
                        laser_y,
                        laser_z,
                        laser_angle,
                        20 + random.uniform(-2, 2),  # Faster, more consistent speed
                        150  # Lifetime
                    ]
                    
                    # Tag boss lasers so they can do more damage
                    if len(enemy) > 7 and enemy[7] == "boss":
                        enemy_laser.append("boss")
                    
                    # Add to enemy bullets list
                    enemy_bullets.append(enemy_laser)
    
    # Check for level up with special events or victory
    if player_experience >= 100:
        # Check for victory condition - already at level 4 and reached 100 XP
        if player_level == 4 and player_experience >= 100:
            game_won = True
            return  # Stop updating the game
        
        player_level += 1
        player_experience -= 100  # Reset experience for next level
        
        # Clear all existing enemies regardless of level
        enemies.clear()
        enemy_bullets.clear()  # Also clear enemy bullets when level changes
        
        # Special event for level 4 (final boss level)
        if player_level == 4:
            # Clear enemies again to be absolutely sure
            enemies.clear()
            
            # Spawn 1 boss spaceship
            spawn_enemy("boss")
            
            # Spawn 3 black-red enemies as the boss's guards
            for i in range(3):
                spawn_enemy("black-red")
                
            # Return early to prevent other enemy spawns
            return
        
        # Special event for level 3
        elif player_level == 3:
            # Spawn 9 black-red enemies
            for i in range(9):
                spawn_enemy("black-red")
                
            # Spawn 5 golden enemies
            for i in range(5):
                spawn_enemy("golden")
        
        # Original special event for other level-ups
        else:
            # Spawn 8 golden enemies
            for i in range(8):
                spawn_enemy("golden")
                
            # Spawn 5 red enemies
            for i in range(5):
                spawn_enemy("red")


def reset_game():
    """Reset game state for a new game"""
    global player_pos, player_rotation, player_speed, player_boost_speed, enemies, player_bullets, enemy_bullets, score, game_over
    global moving_forward, moving_backward, thruster_glow_intensity
    global player_health, player_lives, hit_flash_duration
    global player_experience, player_level, game_won, enemies_respawn_timer
    
    player_pos = [0, 0, 50]
    player_rotation = 90  # Start at 90 degrees
    player_speed = 10  # Reset to increased speed
    player_boost_speed = 15  # Reset boost speed
    enemies = []
    player_bullets = []
    enemy_bullets = []
    score = 0
    game_over = False
    moving_forward = False
    moving_backward = False
    thruster_glow_intensity = 0.0
    
    # Reset health and lives
    player_health = player_max_health
    player_lives = 10  # Increased from 3 to 10
    hit_flash_duration = 0
    
    # Reset experience and level
    player_experience = 0
    player_level = 1
    
    # Reset victory status
    game_won = False
    enemies_respawn_timer = 0
    
    # Initialize enemies at random positions far from player
    for i in range(10):
        preferred_distance = random.uniform(MIN_ENEMY_DISTANCE, MAX_ENEMY_DISTANCE)
        angle = random.uniform(0, 2 * math.pi)
        
        # Position based on preferred distance
        pos_x = player_pos[0] + math.cos(angle) * preferred_distance
        pos_y = player_pos[1] + math.sin(angle) * preferred_distance
        
        # Ensure within battlefield bounds
        pos_x = max(min(pos_x, BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
        pos_y = max(min(pos_y, BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
        
        enemies.append([
            pos_x,  # x
            pos_y,  # y
            random.uniform(100, 500),  # z (height)
            random.uniform(0, 360),    # rotation
            random.randint(0, ENEMY_SHOOT_COOLDOWN),  # shooting cooldown
            [0, 0, 0],  # target position (will be set during gameplay)
            random.uniform(MIN_ENEMY_DISTANCE, MAX_ENEMY_DISTANCE)  # preferred distance from player
        ])
    
    # Reset game state
    game_over = False
    game_won = False

def setupCamera():
    """
    Configures the camera's projection and view settings.
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 5000)  # Extended view distance from 3000 to 5000
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if camera_mode == 0:  # Third-person view
        # Position camera behind and above player
        rad = (player_rotation + 180) * math.pi / 180  # Behind player
        camera_x = player_pos[0] + camera_distance * math.cos(rad)
        camera_y = player_pos[1] + camera_distance * math.sin(rad)
        camera_z = player_pos[2] + 100  # Above player
        
        # Look at player
        gluLookAt(camera_x, camera_y, camera_z,  # Camera position
                player_pos[0], player_pos[1], player_pos[2],  # Look at player
                0, 0, 1)  # Up vector (z-axis)
    else:  # First-person/cockpit view
        # Position camera at player position
        rad = player_rotation * math.pi / 180
        look_x = player_pos[0] + 100 * math.cos(rad)
        look_y = player_pos[1] + 100 * math.sin(rad)
        
        gluLookAt(player_pos[0], player_pos[1], player_pos[2] + 10,  # Camera at player
                look_x, look_y, player_pos[2],  # Look forward
                0, 0, 1)  # Up vector

def idle():
    """
    Idle function for continuous updates
    """
    if not game_over and not game_won:
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
    
    # Draw damage flash overlay when hit (red screen effect)
    if hit_flash_duration > 0:
        # Set up orthographic projection for 2D overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Draw red overlay with alpha based on hit_flash_duration
        alpha = hit_flash_duration / 10.0 * 0.5  # Maximum 50% opacity
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(1.0, 0.0, 0.0)
        
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(1000, 0)
        glVertex2f(1000, 800)
        glVertex2f(0, 800)
        glEnd()
        
        glDisable(GL_BLEND)
        
        # Restore matrix state
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    # Draw HUD elements (always on top)
    draw_radar()
    draw_hud()
    
    # Show game over message if needed
    if game_over:
        # Set up orthographic projection for 2D overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Semi-transparent dark overlay
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
        
        # Game over text
        glColor3f(1.0, 0.0, 0.0)
        glRasterPos2f(400, 450)
        for ch in "GAME OVER":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(350, 400)
        for ch in "Press 'R' to restart":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        glRasterPos2f(350, 350)
        for ch in f"Final Score: {score}":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        # Restore matrix state
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()

def draw_battlefield_boundaries():
    """Draw subtle indicators for battlefield boundaries"""
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw subtle boundary walls
    glBegin(GL_QUADS)
    
    # Get player's distance from boundaries
    dist_to_boundary_x = BATTLEFIELD_SIZE - abs(player_pos[0])
    dist_to_boundary_y = BATTLEFIELD_SIZE - abs(player_pos[1])
    
    # Only show boundaries when player is close to them (within 200 units)
    boundary_visibility = 200
    
    # North boundary (positive Y)
    if BATTLEFIELD_SIZE - player_pos[1] < boundary_visibility:
        # Calculate alpha based on proximity to boundary
        alpha = 0.2 * (1.0 - (BATTLEFIELD_SIZE - player_pos[1]) / boundary_visibility)
        glColor3f(0.4, 0.8, 1.0)  # Cyan-blue, semi-transparent
        glVertex3f(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 1000)  # Increased wall height from 500 to 1000
        glVertex3f(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 1000)  # Increased wall height from 500 to 1000
    
    # South boundary (negative Y)
    if BATTLEFIELD_SIZE + player_pos[1] < boundary_visibility:
        # Calculate alpha based on proximity to boundary
        alpha = 0.2 * (1.0 - (BATTLEFIELD_SIZE + player_pos[1]) / boundary_visibility)
        glColor3f(0.4, 0.8, 1.0)  # Cyan-blue, semi-transparent
        glVertex3f(-BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 1000)  # Increased wall height from 500 to 1000
        glVertex3f(-BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 1000)  # Increased wall height from 500 to 1000
    
    # East boundary (positive X)
    if BATTLEFIELD_SIZE - player_pos[0] < boundary_visibility:
        # Calculate alpha based on proximity to boundary
        alpha = 0.2 * (1.0 - (BATTLEFIELD_SIZE - player_pos[0]) / boundary_visibility)
        glColor3f(0.4, 0.8, 1.0)  # Cyan-blue, semi-transparent
        glVertex3f(BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 1000)  # Increased wall height from 500 to 1000
        glVertex3f(BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 1000)  # Increased wall height from 500 to 1000
    
    # West boundary (negative X)
    if BATTLEFIELD_SIZE + player_pos[0] < boundary_visibility:
        # Calculate alpha based on proximity to boundary
        alpha = 0.2 * (1.0 - (BATTLEFIELD_SIZE + player_pos[0]) / boundary_visibility)
        glColor3f(0.4, 0.8, 1.0)  # Cyan-blue, semi-transparent
        glVertex3f(-BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 0)
        glVertex3f(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 0)
        glVertex3f(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 1000)  # Increased wall height from 500 to 1000
        glVertex3f(-BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 1000)  # Increased wall height from 500 to 1000
        
    glEnd()
    
    glDisable(GL_BLEND)

def spawn_enemy(enemy_type="red"):
    """Spawn a new enemy of specific type"""
    preferred_distance = random.uniform(MIN_ENEMY_DISTANCE, MAX_ENEMY_DISTANCE)
    
    # For boss, use fixed position directly ahead of player
    if enemy_type == "boss":
        angle = player_rotation * math.pi / 180
        preferred_distance = MAX_ENEMY_DISTANCE * 0.8  # Place boss at 80% of max distance
    else:
        angle = random.uniform(0, 2 * math.pi)
    
    # Position based on preferred distance
    pos_x = player_pos[0] + math.cos(angle) * preferred_distance
    pos_y = player_pos[1] + math.sin(angle) * preferred_distance
    
    # Ensure within battlefield bounds
    pos_x = max(min(pos_x, BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
    pos_y = max(min(pos_y, BATTLEFIELD_SIZE/2 - 50), -BATTLEFIELD_SIZE/2 + 50)
    
    # Create base enemy with standard attributes
    new_enemy = [
        pos_x,  # x
        pos_y,  # y
        random.uniform(100, 500),  # z (height)
        random.uniform(0, 360),    # rotation
        random.randint(0, ENEMY_SHOOT_COOLDOWN),  # shooting cooldown
        [0, 0, 0],  # target position (will be set during gameplay)
        random.uniform(MIN_ENEMY_DISTANCE, MAX_ENEMY_DISTANCE)  # preferred distance from player
    ]
    
    # Add enemy type
    if enemy_type in ["golden", "black-red", "boss"]:
        new_enemy.append(enemy_type)
    
    # For boss, give it a longer shooting cooldown, but make it more aggressive
    if enemy_type == "boss":
        new_enemy[4] = 60  # Boss starts shooting after longer delay (adjusted from 30)
        # Use a fixed height for the boss
        new_enemy[2] = 200
    
    enemies.append(new_enemy)

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

if __name__ == "__main__":
    main()