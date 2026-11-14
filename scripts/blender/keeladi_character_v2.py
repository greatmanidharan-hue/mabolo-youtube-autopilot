"""Full-body Keeladi character prototype inspired by the user's Pixar-style head study.
Blender 5.2+; free/local workflow; EEVEE avoids requiring a supported GPU.
Run from repo root:
  blender -b -P scripts/blender/keeladi_character_v2.py
Output: output/keeladi-character-v2.png
This is an artistic reconstruction, not a historically verified individual.
"""
import bpy, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)
OUTPUT = os.path.join(OUT, "keeladi-character-v2.png")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 96
scene.render.resolution_x, scene.render.resolution_y = 900, 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
if scene.world is None:
    scene.world = bpy.data.worlds.new("Keeladi Character World")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.035, 0.055, 0.085, 1)
bg.inputs["Strength"].default_value = 0.45

def mat(name, color, rough=.42, sss=0, metallic=0, coat=0):
    m = bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1); p.inputs["Roughness"].default_value=rough
    if "Subsurface Weight" in p.inputs:
        p.inputs["Subsurface Weight"].default_value=sss
        p.inputs["Subsurface Scale"].default_value=.06
    if "Metallic" in p.inputs: p.inputs["Metallic"].default_value=metallic
    if "Coat Weight" in p.inputs: p.inputs["Coat Weight"].default_value=coat
    return m

skin=mat("warm stylized skin",(0.52,.27,.19),.43,.22)
skin_hi=mat("skin warm highlights",(.68,.39,.29),.46,.12)
hair=mat("dark sculpted hair",(.035,.022,.018),.3,0,0,.18)
hair_hi=mat("hair strand highlights",(.13,.065,.035),.34)
white=mat("warm eye whites",(.96,.87,.75),.2,0,0,.35)
iris=mat("deep brown iris",(.18,.075,.035),.22,0,0,.3)
pupil=mat("black pupils",(.008,.006,.005),.12)
shirt=mat("indigo cotton tunic",(.10,.25,.39),.72)
shirt_light=mat("tunic seam blue",(.25,.43,.55),.66)
cloth=mat("ochre waist cloth",(.66,.31,.10),.78)
gold=mat("aged gold brass",(.62,.36,.09),.28,0,.72)
lip=mat("soft natural lips",(.38,.12,.10),.48)
ground=mat("matte studio floor",(.055,.075,.10),.9)

def smooth(o, material):
    o.data.materials.append(material)
    if o.type=="MESH":
        for p in o.data.polygons: p.use_smooth=True
    return o

def ball(name, loc, scale, material, rot=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=28, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    if rot: o.rotation_euler=rot
    return smooth(o,material)

def link(name, a, b, r1, r2, material):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=r1, radius2=r2, depth=d.length, location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    bevel=o.modifiers.new("soft rounded joints","BEVEL"); bevel.width=.055; bevel.segments=4
    o.modifiers.new("weighted normals","WEIGHTED_NORMAL")
    return smooth(o,material)

def line(name, points, radius, material):
    c=bpy.data.curves.new(name,"CURVE"); c.dimensions="3D"; c.resolution_u=16
    c.bevel_depth=radius; c.bevel_resolution=4
    sp=c.splines.new("BEZIER"); sp.bezier_points.add(len(points)-1)
    for bp,pt in zip(sp.bezier_points,points):
        bp.co=pt; bp.handle_left_type="AUTO"; bp.handle_right_type="AUTO"
    o=bpy.data.objects.new(name,c); scene.collection.objects.link(o); o.data.materials.append(material)
    return o

# Body proportions: stylized, youthful, full-body.
# Feet, ankles and legs
for side in (-1,1):
    x=side*.19
    ball("bare foot",(x,-.17,.16),(.17,.31,.13),skin)
    link("lower leg",(x,0,.25),(x,0,.88),.11,.145,skin)
    ball("knee",(x,0,.88),(.145,.15,.15),skin)
    link("upper leg",(x,0,.91),(side*.16,0,1.48),.15,.19,skin)

# Dhoti/waist garment with surface-following folds
ball("draped waist garment",(0,.02,1.42),(.47,.34,.63),cloth)
for i in range(9):
    x=-.34+i*.085
    pts=[]
    for z,w in ((1.90,.9),(1.55,1.0),(1.18,1.06),(.92,.95)):
        xx=x*w; nx=xx/.47; nz=(z-1.42)/.63
        depth=.02+.34*math.sqrt(max(.06,1-nx*nx-nz*nz))
        pts.append((xx,-depth-.012,z))
    line("fine cloth fold",pts,.009,shirt_light)
# Tunic torso and neck
ball("tunic body",(0,.02,2.10),(.40,.30,.54),shirt)
ball("neck",(0,0,2.62),(.16,.16,.22),skin)
# Shoulder and arms, slightly bent
for side in (-1,1):
    shoulder=(side*.38,0,2.43); elbow=(side*.57,-.02,2.00); wrist=(side*.48,-.10,1.70)
    ball("shoulder joint",shoulder,(.19,.21,.20),shirt)
    link("upper arm",elbow,shoulder,.13,.16,skin)
    ball("elbow joint",elbow,(.14,.14,.14),skin)
    link("forearm",wrist,elbow,.095,.13,skin)
    ball("palm",(side*.48,-.12,1.62),(.12,.09,.15),skin)
    for j in range(4):
        fx=side*.48+(j-1.5)*.045
        link("individual finger",(fx,-.19,1.57),(fx,-.19,1.43+(.02 if j in (1,2) else 0)),.027,.021,skin)
    link("thumb",(side*.38,-.15,1.65),(side*.32,-.20,1.52),.04,.025,skin)
    bpy.ops.mesh.primitive_torus_add(major_radius=.115,minor_radius=.022,major_segments=32,minor_segments=10,location=(side*.49,-.10,1.78))
    smooth(bpy.context.object,gold)
# Tunic collar and stitched hems
line("neckline",[( -.18,-.25,2.52),(0,-.31,2.40),(.18,-.25,2.52)],.025,shirt_light)
line("tunic hem",[(-.34,-.20,1.75),(0,-.31,1.72),(.34,-.20,1.75)],.012,shirt_light)
# Head and ears
ball("head",(0,-.015,3.05),(.39,.34,.47),skin)
for side in (-1,1):
    ball("ear",(side*.385,-.015,3.04),(.095,.10,.145),skin)
    ball("ear inner",(side*.42,-.095,3.04),(.035,.025,.075),skin_hi)
# Hair cap, swept quiff and side locks
ball("hair cap",(0,.035,3.38),(.405,.36,.24),hair)
ball("back hair",(0,.16,3.18),(.39,.28,.32),hair)
for side in (-1,1):
    ball("side lock",(side*.34,.01,3.19),(.10,.27,.27),hair)
for i in range(11):
    x=-.31+i*.062
    line("sculpted hair strand",[(x,-.22,3.42),(x*.92,-.18,3.58),(x*.78,-.02,3.66),(x*.65,.10,3.58)],.022,hair_hi)
# Eyes with catchlights and expressive brows
for side in (-1,1):
    x=side*.145
    ball("eye socket",(x,-.318,3.11),(.12,.045,.105),skin_hi)
    ball("eye white",(x,-.355,3.11),(.087,.036,.074),white)
    ball("iris",(x+.008,-.386,3.11),(.042,.02,.049),iris)
    ball("pupil",(x+.01,-.402,3.11),(.022,.012,.031),pupil)
    ball("eye catchlight",(x-.008,-.414,3.135),(.012,.008,.014),white)
    brow=ball("eyebrow",(x,-.348,3.235),(.12,.035,.032),hair)
    brow.rotation_euler[1]=side*.10
# Nose and smile
ball("nose bridge",(0,-.355,3.02),(.06,.07,.12),skin_hi)
ball("nose tip",(0,-.413,2.98),(.07,.06,.05),skin)
line("upper smile",[(-.08,-.36,2.90),(0,-.385,2.885),(.08,-.36,2.90)],.014,lip)
# Brow/forehead mark and simple ornaments
ball("forehead mark",(0,-.354,3.31),(.026,.016,.055),lip)
line("neck chain",[(-.22,-.24,2.66),(0,-.31,2.53),(.22,-.24,2.66)],.018,gold)
ball("pendant",(0,-.33,2.51),(.055,.035,.075),gold)
for side in (-1,1):
    bpy.ops.mesh.primitive_torus_add(major_radius=.07,minor_radius=.016,major_segments=24,minor_segments=8,location=(side*.40,-.08,2.93),rotation=(math.pi/2,0,0))
    smooth(bpy.context.object,gold)

# Studio ground
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0)); smooth(bpy.context.object,ground)
# Camera full body framing
cam_data=bpy.data.cameras.new("portrait camera"); cam=bpy.data.objects.new("portrait camera",cam_data); scene.collection.objects.link(cam)
cam.location=(3.2,-11,3.45); target=Vector((0,0,1.90)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat("-Z","Y").to_euler()
cam_data.type="ORTHO"; cam_data.ortho_scale=4.35; scene.camera=cam
# Three-point soft cinematic lighting
def area(name,loc,power,size,color,target):
    d=bpy.data.lights.new(name,"AREA"); d.energy=power; d.shape="DISK"; d.size=size; d.color=color
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
area("warm key",(-4,-6,7),1050,5,(1,.78,.62),(0,0,2))
area("cool fill",(4,-4,4),800,4,(.65,.78,1),(0,0,2))
area("hair rim",(1,3,6),1200,3,(1,.64,.38),(0,0,2.7))
scene.camera.data.lens=85
scene.render.filepath=OUTPUT
scene.frame_set(1)
print("Rendering full-body stylized Keeladi character:",OUTPUT)
bpy.ops.render.render(write_still=True)
print("Preview complete:",OUTPUT)
