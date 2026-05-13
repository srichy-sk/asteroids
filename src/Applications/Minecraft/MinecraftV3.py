from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# ---------------------------------
# TEXTURES & AUDIO
# ---------------------------------
grass_texture = load_texture('grass_block.png')
dirt_texture = load_texture('dirt_block.png')
stone_texture = load_texture('stone_block.png')
brick_texture = load_texture('brick_block.png')
wood_texture = load_texture('wood_block.png')
sky_texture = load_texture('skybox.png')
arm_texture = load_texture("arm_texture.png")
punch_sound = Audio('punch_sound', loop=False, autoplay=False)

block_pick = 1

window.fps_counter.enabled = False
window.exit_button.visible = False

# ---------------------------------
# UPDATE
# ---------------------------------
def update():
    global block_pick

    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

    if held_keys['1']: block_pick = 1
    if held_keys['2']: block_pick = 2
    if held_keys['3']: block_pick = 3
    if held_keys['4']: block_pick = 4


# ---------------------------------
# VOXEL
# ---------------------------------
class Voxel(Entity):
    def __init__(self, position=(0,0,0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='block',
            origin_y=.5,
            texture=texture,
            scale=0.5,
            collider='box'
        )

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                punch_sound.play()
                if block_pick == 1:
                    Voxel(self.position + mouse.normal, grass_texture)
                if block_pick == 2:
                    Voxel(self.position + mouse.normal, stone_texture)
                if block_pick == 3:
                    Voxel(self.position + mouse.normal, brick_texture)
                if block_pick == 4:
                    Voxel(self.position + mouse.normal, dirt_texture)

            if key == 'right mouse down':
                punch_sound.play()
                destroy(self)


# ---------------------------------
# BLOCK DECORATIONS (ALL CUBES)
# ---------------------------------
def spawn_tree(pos):
    for y in range(3):
        Voxel(position=pos + Vec3(0, y, 0), texture=wood_texture)

    for x in range(-1, 2):
        for z in range(-1, 2):
            Voxel(position=pos + Vec3(x, 3, z), texture=grass_texture)

def spawn_rock(pos):
    Voxel(position=pos, texture=stone_texture)

def spawn_grass(pos):
    Voxel(position=pos, texture=grass_texture)


# ---------------------------------
# SKY & HAND
# ---------------------------------
class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=sky_texture,
            scale=150,
            double_sided=True
        )

class Hand(Entity):
    def active(self):
        self.position = Vec2(0.3, -0.5)

    def passive(self):
        self.position = Vec2(0.4, -0.6)


hand = Hand(
    parent=camera.ui,
    model='arm',
    texture=arm_texture,
    scale=0.2,
    rotation=Vec3(150, -10, 0),
    position=Vec2(0.4, -0.6)
)

# ---------------------------------
# TERRAIN GENERATION
# ---------------------------------
terrain_size = 12
max_height = 5

for z in range(terrain_size):
    for x in range(terrain_size):

        height = random.randint(2, max_height)

        for y in range(height):
            top = (y == height - 1)

            if top:
                texture = grass_texture
            elif y > height - 3:
                texture = dirt_texture
            else:
                texture = stone_texture

            voxel_pos = Vec3(x, y - height, z)
            Voxel(position=voxel_pos, texture=texture)

            if top:
                r = random.random()
                if r < 0.05:
                    spawn_tree(voxel_pos + Vec3(0, 1, 0))
                elif r < 0.10:
                    spawn_rock(voxel_pos + Vec3(0, 1, 0))
                elif r < 0.20:
                    spawn_grass(voxel_pos + Vec3(0, 1, 0))


# ---------------------------------
# START GAME
# ---------------------------------
Sky()
player = FirstPersonController()
player.y = 2

app.run()
