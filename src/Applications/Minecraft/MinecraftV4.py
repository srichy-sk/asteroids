from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math, random

app = Ursina()

# ---------------- SETTINGS ----------------
BLOCK = 0.5
CHUNK_SIZE = 8
RENDER_DISTANCE = 2
ACTIVE_RADIUS = 5  # how far real blocks spawn around player
MAX_HEIGHT = 6
SEED = random.randint(0, 9999)

# ---------------- TEXTURES ----------------
grass = load_texture('grass_block.png')
dirt  = load_texture('dirt_block.png')
stone = load_texture('stone_block.png')
sky_tex = load_texture('skybox.png')

window.fps_counter.enabled = False
window.exit_button.visible = False

# ---------------- HEIGHT FUNCTION ----------------
def get_height(x, z):
    return int(
        math.sin((x + SEED) * 0.3) * 2 +
        math.cos((z + SEED) * 0.3) * 2 +
        MAX_HEIGHT
    )

# ---------------- BLOCK ----------------
class Voxel(Entity):
    def __init__(self, pos, tex):
        super().__init__(
            model='block',
            texture=tex,
            position=pos,
            scale=BLOCK,
            collider='box'
        )

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                destroy(self)
            if key == 'left mouse down':
                Voxel(self.position + mouse.normal * BLOCK, grass)

# ---------------- CHUNK SYSTEM ----------------
chunk_data = {}   # (cx, cz) -> list of positions
active_blocks = []
current_chunk = None

def generate_chunk(cx, cz):
    blocks = []
    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            wx = cx*CHUNK_SIZE + x
            wz = cz*CHUNK_SIZE + z
            h = max(1, get_height(wx, wz))
            y = h - 1
            pos = Vec3(wx*BLOCK, y*BLOCK, wz*BLOCK)
            blocks.append(pos)
    chunk_data[(cx, cz)] = blocks

def load_active_blocks():
    global active_blocks
    # destroy old blocks
    for b in active_blocks:
        destroy(b)
    active_blocks.clear()

    px = player.x
    pz = player.z

    for blocks in chunk_data.values():
        for pos in blocks:
            if distance(Vec3(px,0,pz), Vec3(pos.x,0,pos.z)) < ACTIVE_RADIUS:
                active_blocks.append(Voxel(pos, grass))

def update_chunks():
    global current_chunk
    cx = int(player.x // CHUNK_SIZE)
    cz = int(player.z // CHUNK_SIZE)

    if current_chunk == (cx, cz):
        return

    current_chunk = (cx, cz)

    # generate chunks around player
    for x in range(cx-RENDER_DISTANCE, cx+RENDER_DISTANCE+1):
        for z in range(cz-RENDER_DISTANCE, cz+RENDER_DISTANCE+1):
            if (x,z) not in chunk_data:
                generate_chunk(x,z)

    load_active_blocks()

# ---------------- SKY ----------------
Sky(model='sphere', texture=sky_tex, scale=250, double_sided=True)

# ---------------- PLAYER ----------------
player = FirstPersonController()
player.y = 3

# ---------------- GAME LOOP ----------------
def update():
    update_chunks()

app.run()
