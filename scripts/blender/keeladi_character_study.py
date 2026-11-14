"""Keeladi high-end stylized character study.
Blender 5.2+; run: blender -b -P scripts/blender/keeladi_character_study.py
Renders one full-body character preview to output/keeladi-character-study.png.
Artistic character concept; not a historically verified portrait.
"""
import bpy, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)
PREVIEW = os.path.join(OUT, "keeladi-character-study.png")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.resolution_percentage = 75
scene.view_settings.view_transform = "AgX"
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.16,0.20,0.28,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45

def material(name, color, rough=0.55, metallic=0.0, subsurface=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metallic
    if "Subsurface Weight" in p.inputs: p.inputs["Subsurface Weight"].default_value=subsurface
    return m

skin=material("warm terracotta skin",(0.48,0.235,0.145),0.48,0,0.08)
skin_light=material("warm skin highlights",(0.62,0.34,0.23),0.5,0,0.05)
hair=material("deep dark hair",(0.025,0.018,0.016),0.34)
hair_hi=material("hair warm strands",(0.09,0.045,0.028),0.42)
ivory=material("eye ivory",(0.94,0.82,0.68),0.28)
iris=material("deep brown iris",(0.12,0.055,0.028),0.25)
black=material("pupil",(0.012,0.009,0.008),0.18)
lip=material("soft warm lips",(0.36,0.095,0.075),0.48)
sari=material("deep indigo cotton",(0.035,0.13,0.22),0.82)
sari_hi=material("indigo fabric folds",(0.10,0.23,0.33),0.82)
ochre=material("ochre blouse",(0.68,0.31,0.09),0.68)
gold=material("aged brass",(0.62,0.36,0.09),0.28,0.72)
ground=material("studio warm slate",(0.12,0.15,0.19),0.88)

def smooth(obj, mat):
    obj.data.materials.append(mat)
    if obj.type=="MESH":
        for p in obj.data.polygons: p.use_smooth=True
    return obj

def ellipsoid(name, loc, scale, mat, rot=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=28, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    if rot: o.rotation_euler=rot
    return smooth(o,mat)

def tapered(name, a, b, r1, r2, mat, vertices=32):
    mid=(Vector(a)+Vector(b))*0.5
    d=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r1, radius2=r2, depth=d.length, location=mid)
    o=bpy.context.object; o.name=name
    o.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    bevel=o.modifiers.new("soft tailored edges","BEVEL"); bevel.width=0.08; bevel.segments=4
    o.modifiers.new("weighted corner normals","WEIGHTED_NORMAL")
    return smooth(o,mat)

def curve_tube(name, pts, radius, mat, bevel_res=4):
    c=bpy.data.curves.new(name,"CURVE"); c.dimensions="3D"; c.resolution_u=16
    c.bevel_depth=radius; c.bevel_resolution=bevel_res
    sp=c.splines.new("BEZIER"); sp.bezier_points.add(len(pts)-1)
    for bp,co in zip(sp.bezier_points,pts):
        bp.co=co; bp.handle_left_type="AUTO"; bp.handle_right_type="AUTO"
    o=bpy.data.objects.new(name,c); scene.collection.objects.link(o); o.data.materials.append(mat)
    return o

# Full-body adult woman, front faces toward negative Y.
# Feet and legs
for side in (-1,1):
    x=side*0.19
    ellipsoid("bare foot",(x,-0.18,0.16),(0.16,0.30,0.12),skin)
    tapered("lower leg",(x,0,0.27),(x*0.95,0,0.92),0.105,0.15,skin)
    ellipsoid("knee",(x*0.95,-0.005,0.90),(0.145,0.14,0.16),skin)
    tapered("upper leg",(x*0.95,0,0.92),(x*0.82,0,1.55),0.15,0.21,skin)
# Wrapped skirt silhouette and visible pleat lines
ellipsoid("long wrapped skirt",(0,0.02,1.38),(0.49,0.34,0.75),sari)
for i in range(9):
    # Keep each fold seated on the skirt surface; avoid the previous dangling
    # lines that extended below the hem.
    x=-0.34+i*0.085
    pts=[]
    for z, widen in ((1.88,0.90),(1.52,1.00),(1.12,1.08),(0.78,1.02)):
        xx=x*widen
        nz=(z-1.38)/0.75
        nx=xx/0.49
        depth=0.02+0.34*math.sqrt(max(0.05,1-nx*nx-nz*nz))
        pts.append((xx,-depth-0.012,z))
    curve_tube("subtle stitched sari fold",pts,0.008,sari_hi,3)
# Blouse torso and neck
ellipsoid("blouse torso",(0,0,2.16),(0.42,0.29,0.58),ochre)
ellipsoid("neck",(0,-0.01,2.72),(0.16,0.16,0.25),skin)
# Shoulder and arms
for side in (-1,1):
    sh=(side*0.37,0,2.48); elbow=(side*0.60,-0.015,2.05); wrist=(side*0.48,-0.10,1.78)
    ellipsoid("shoulder",sh,(0.20,0.22,0.22),skin)
    tapered("upper arm",elbow,sh,0.13,0.17,skin)
    ellipsoid("elbow",elbow,(0.14,0.14,0.14),skin)
    tapered("forearm",wrist,elbow,0.095,0.13,skin)
    ellipsoid("hand",(side*0.47,-0.12,1.70),(0.12,0.10,0.17),skin)
    # Individual finger forms
    for j in range(4):
        fx=side*0.47+(j-1.5)*0.045
        ellipsoid("finger",(fx,-0.19,1.60+0.012*(j%2)),(0.027,0.035,0.09),skin)
    # Brass bangles
    bpy.ops.mesh.primitive_torus_add(major_radius=0.115,minor_radius=0.025,major_segments=32,minor_segments=10,location=(side*0.49,-0.10,1.82))
    smooth(bpy.context.object,gold)
# Sash draped diagonally across torso
curve_tube("sari shoulder border",[(-0.32,-0.26,2.62),(-0.18,-0.32,2.40),(0.05,-0.33,2.12),(0.25,-0.31,1.88)],0.055,gold,5)
# Head, jaw and ears
ellipsoid("head",(0,-0.015,3.15),(0.39,0.34,0.48),skin)
for side in (-1,1):
    ellipsoid("ear",(side*0.385,-0.015,3.13),(0.095,0.10,0.15),skin)
    ellipsoid("ear inner",(side*0.425,-0.095,3.13),(0.035,0.025,0.075),skin_light)
# Hair cap and bun
ellipsoid("hair cap",(0,0.045,3.48),(0.405,0.36,0.25),hair)
ellipsoid("hair bun",(0,0.22,3.57),(0.24,0.23,0.25),hair)
for side in (-1,1):
    ellipsoid("side hair",(side*0.33,0.04,3.28),(0.11,0.30,0.30),hair)
# Hair locks as curved strands swept backward
for i in range(9):
    x=-0.30+i*0.075
    curve_tube("sculpted hair strand",[(x,-0.20,3.55),(x*0.9,-0.16,3.70),(x*0.72,0.00,3.76),(x*0.6,0.16,3.68)],0.025,hair_hi,3)
# Eyes and brows
for side in (-1,1):
    x=side*0.145
    ellipsoid("eye socket shadow",(x,-0.322,3.22),(0.12,0.045,0.105),skin_light)
    ellipsoid("eye white",(x,-0.354,3.22),(0.088,0.035,0.072),ivory)
    ellipsoid("iris",(x+0.008,-0.384,3.22),(0.040,0.018,0.048),iris)
    ellipsoid("pupil",(x+0.01,-0.399,3.22),(0.021,0.012,0.030),black)
    ellipsoid("eye sparkle",(x-0.006,-0.411,3.244),(0.010,0.008,0.012),ivory)
    brow=ellipsoid("eyebrow",(x,-0.345,3.345),(0.12,0.035,0.035),hair)
    brow.rotation_euler[1]=side*0.10
# Nose bridge, tip, nostrils and smile
ellipsoid("nose bridge",(0,-0.355,3.12),(0.065,0.075,0.13),skin_light)
ellipsoid("nose tip",(0,-0.414,3.075),(0.075,0.065,0.055),skin)
curve_tube("smiling upper lip",[(-0.085,-0.355,2.99),(0,-0.385,2.975),(0.085,-0.355,2.99)],0.018,lip,3)
curve_tube("smile lower lip",[(-0.065,-0.36,2.97),(0,-0.38,2.955),(0.065,-0.36,2.97)],0.012,skin_light,3)
# Traditional jewelry: forehead mark, earrings, necklace and waist chain
ellipsoid("forehead tilak",(0,-0.355,3.43),(0.035,0.018,0.07),lip)
for side in (-1,1):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.075,minor_radius=0.018,major_segments=24,minor_segments=8,location=(side*0.40,-0.10,3.00),rotation=(math.pi/2,0,0))
    smooth(bpy.context.object,gold)
curve_tube("necklace",[(-0.25,-0.25,2.72),(0,-0.34,2.55),(0.25,-0.25,2.72)],0.025,gold,4)
ellipsoid("necklace pendant",(0,-0.36,2.52),(0.07,0.04,0.10),gold)
curve_tube("waist chain",[(-0.38,-0.28,1.76),(0,-0.36,1.68),(0.38,-0.28,1.76)],0.018,gold,3)

# Studio ground and backdrop
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,0))
smooth(bpy.context.object,ground)
# Camera
cam_data=bpy.data.cameras.new("portrait camera"); cam=bpy.data.objects.new("portrait camera",cam_data); scene.collection.objects.link(cam)
cam.location=(3.6,-12,4.15); target=Vector((0,0,1.92)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat("-Z","Y").to_euler()
cam_data.type="ORTHO"; cam_data.ortho_scale=4.55; scene.camera=cam
# Soft studio lights
def area(name,loc,power,size,color,target):
    data=bpy.data.lights.new(name,"AREA"); data.energy=power; data.shape="DISK"; data.size=size; data.color=color
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=loc
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
area("large warm key",(-4,-6,7),1100,5,(1.0,0.78,0.60),(0,0,2))
area("soft cool fill",(4,-4,4),850,4,(0.62,0.76,1.0),(0,0,2))
area("hair rim",(1,3,6),1250,3,(1.0,0.62,0.34),(0,0,2.5))
scene.render.filepath=PREVIEW
scene.camera.data.lens=50
scene.render.image_settings.file_format="PNG"
scene.render.resolution_percentage=100
scene.render.engine="BLENDER_EEVEE"
scene.eevee.taa_render_samples=96
scene.frame_set(1)
print("Rendering high-end stylized Keeladi character study:",PREVIEW)
bpy.ops.render.render(write_still=True)
print("Finished character study:",PREVIEW)
