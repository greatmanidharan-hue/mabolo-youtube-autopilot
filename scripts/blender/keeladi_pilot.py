"""
MABOLO Keeladi animated pilot — free Blender procedural 3D proof of concept.
Run from repository root:
  blender -b -P scripts/blender/keeladi_pilot.py
Output: output/keeladi-pilot-visual.mp4
This is an artistic reconstruction, not a documentary reconstruction.
"""
import bpy, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)
OUTPUT = os.path.join(OUT, "keeladi-pilot-visual.mp4")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x, scene.render.resolution_y = 720, 1280
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 864
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.ffmpeg.video_bitrate = 5000
scene.render.filepath = OUTPUT
scene.world.color = (0.22, 0.22, 0.22)
scene.view_settings.view_transform = "AgX"

def mat(name, color, rough=0.78, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metallic
    return m

EARTH=mat("warm red earth",(0.34,0.19,0.12)); WALL=mat("sun baked clay",(0.55,0.31,0.19))
ROOF=mat("thatch",(0.29,0.18,0.10)); SKIN=mat("warm brown skin",(0.48,0.25,0.15))
HAIR=mat("dark hair",(0.035,0.025,0.02)); BLUE=mat("indigo cotton",(0.12,0.20,0.30))
OCHRE=mat("turmeric cotton",(0.72,0.42,0.12)); ROSE=mat("muted rose cotton",(0.48,0.20,0.19))
CLAY=mat("terracotta",(0.55,0.22,0.10)); WATER=mat("water",(0.08,0.28,0.34),0.22)
WOOD=mat("timber",(0.20,0.11,0.06)); LEAF=mat("palm leaves",(0.16,0.25,0.12))
BRASS=mat("warm brass",(0.68,0.42,0.12),0.3,0.45)

def finish(o, material):
    o.data.materials.append(material)
    if o.type == "MESH":
        for p in o.data.polygons: p.use_smooth=True
    return o

def uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    return finish(o,material)

def cube(name, loc, scale, material, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod=o.modifiers.new("soft edges","BEVEL"); mod.width=bevel; mod.segments=3
    return finish(o,material)

def cyl(name, loc, radius, depth, material, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name
    return finish(o,material)

def cone(name, loc, r1, r2, depth, material):
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=r1, radius2=r2, depth=depth, location=loc)
    o=bpy.context.object; o.name=name
    return finish(o,material)

def look_at(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()

def light(name,loc,energy,size,color,target):
    data=bpy.data.lights.new(name,"AREA"); data.energy=energy; data.shape="DISK"; data.size=size; data.color=color
    o=bpy.data.objects.new(name,data); scene.collection.objects.link(o); o.location=loc; look_at(o,target)

light("warm key",(8,-12,16),1800,10,(1.0,0.72,0.48),(25,0,2))
light("sky fill",(-8,-2,10),950,12,(0.55,0.68,1.0),(25,0,2))
light("golden rim",(30,8,12),1300,8,(1.0,0.55,0.26),(25,0,2))
cube("earth stage",(30,0,-0.35),(90,28,0.7),EARTH,0.15)

def hut(x,y=3):
    cube("clay house",(x,y,2),(6,4,4),WALL,0.16)
    cube("door shadow",(x,y-2.03,1.15),(1.25,0.12,2.3),WOOD,0.12)
    roof=cone("thatched roof",(x,y,4.7),4.2,0.25,2.2,ROOF); roof.scale.y=0.72

def palm(x,y,height=7):
    cyl("palm trunk",(x,y,height/2),0.22,height,WOOD,16)
    for a in range(0,360,60):
        leaf=uv("palm frond",(x+math.cos(math.radians(a))*1.2,y+math.sin(math.radians(a))*0.9,height+0.1),(1.5,0.22,0.10),LEAF)
        leaf.rotation_euler[2]=math.radians(a)

def pot(x,y,z=0.7,size=1.0):
    uv("rounded clay pot",(x,y,z),(0.48*size,0.48*size,0.62*size),CLAY)
    cyl("pot neck",(x,y,z+0.55*size),0.24*size,0.22*size,CLAY)
    cyl("pot rim",(x,y,z+0.68*size),0.29*size,0.08*size,BRASS)

def person(name,x,y,clothing,s=1.0):
    uv(name+" torso",(x,y,1.55*s),(0.48*s,0.32*s,0.68*s),clothing)
    uv(name+" head",(x,y-0.02,2.48*s),(0.43*s,0.40*s,0.48*s),SKIN)
    uv(name+" hair",(x,y+0.02,2.77*s),(0.45*s,0.42*s,0.27*s),HAIR)
    for dx in (-0.15,0.15):
        uv(name+" eye",(x+dx*s,y-0.385*s,2.52*s),(0.055*s,0.035*s,0.075*s),HAIR)
    uv(name+" nose",(x,y-0.43*s,2.39*s),(0.07*s,0.07*s,0.09*s),SKIN)
    for side in (-1,1):
        arm=uv(name+" arm",(x+side*0.56*s,y-0.02,1.75*s),(0.18*s,0.20*s,0.52*s),clothing)
        arm.rotation_euler[1]=side*math.radians(18)
        uv(name+" hand",(x+side*0.62*s,y-0.08,1.25*s),(0.16*s,0.15*s,0.16*s),SKIN)
        uv(name+" leg",(x+side*0.20*s,y,0.55*s),(0.19*s,0.22*s,0.52*s),WOOD)

# Shot 1 — dawn settlement
hut(0,4); hut(-6,5); palm(-8,-1); palm(8,4)
person("mother dawn",-1.2,-1.0,OCHRE); person("child dawn",1.0,-1.2,ROSE,0.72)
for px in (-3.5,3.6,5.2): pot(px,-1.0,0.55,0.8)
uv("morning sun",(5,7,8),(1.3,1.3,1.3),BRASS)

# Shot 2 — pottery
hut(20,4)
cyl("potter wheel base",(20,-0.8,0.28),1.0,0.35,WOOD)
wheel=cyl("spinning wheel top",(20,-0.8,0.55),1.15,0.18,BRASS)
person("potter",18.1,-1.2,BLUE)
pot(20,-0.8,1.2,0.8)
for px in (22.5,24,17): pot(px,-1.0,0.55,0.85)
wheel.keyframe_insert(data_path="rotation_euler",frame=181)
wheel.rotation_euler.z=math.tau*12
wheel.keyframe_insert(data_path="rotation_euler",frame=360)

# Shot 3 — household craft and weaving
hut(40,4)
cube("loom frame",(40,-0.7,1.7),(3.2,0.35,3.0),WOOD,0.08)
for i in range(11): cube("loom thread",(38.65+i*0.27,-0.91,1.7),(0.025,0.025,2.7),OCHRE,0.005)
person("weaver",38.0,-1.4,ROSE); person("young helper",42.5,-1.2,OCHRE,0.72)
for px in (44,45.2,36): pot(px,-1.1,0.55,0.75)

# Shot 4 — shared water point
cyl("water pool",(60,0.8,0.5),2.4,1.0,WATER,48)
cyl("stone rim",(60,0.8,1.05),2.55,0.25,WALL,48)
person("water carrier",57.0,-2.0,OCHRE); person("child helper",62.7,-1.8,ROSE,0.72)
person("neighbour",64.0,1.0,BLUE,0.95)
for px in (56.2,58.2,63.4,65.5): pot(px,-2.4,0.55,0.82)

# Stylized arm gestures, repeated across the timeline.
for obj in [o for o in bpy.data.objects if o.name.endswith(" arm")]:
    base=obj.rotation_euler.copy()
    obj.keyframe_insert(data_path="rotation_euler",frame=1)
    obj.rotation_euler.x += math.radians(12); obj.keyframe_insert(data_path="rotation_euler",frame=90)
    obj.rotation_euler.x -= math.radians(24); obj.keyframe_insert(data_path="rotation_euler",frame=180)
    obj.rotation_euler=base; obj.keyframe_insert(data_path="rotation_euler",frame=864)

def camera(name,loc,target,lens=48):
    data=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,data); scene.collection.objects.link(o)
    o.location=loc; data.lens=lens; look_at(o,target); return o

cams=[
 camera("shot 1 dawn wide",(0,-16,6.2),(0,1,2.3),42),
 camera("shot 2 pottery medium",(18,-9,4),(20,-0.3,1.5),52),
 camera("shot 3 craft close",(38,-9,4.1),(40,-0.5,1.8),55),
 camera("shot 4 water wide",(60,-13,7),(60,0.2,1.5),43)
]
for idx,cam in enumerate(cams):
    f=1+idx*216
    marker=scene.timeline_markers.new("SHOT_%d"%(idx+1),frame=f); marker.camera=cam
    cam.keyframe_insert(data_path="location",frame=f)
    cam.location += Vector((0,0,-0.35)); cam.keyframe_insert(data_path="location",frame=f+215)
scene.camera=cams[0]
scene.render.image_settings.color_mode="RGB"
scene.render.film_transparent=False
scene.eevee.taa_render_samples=32
for action in bpy.data.actions:
    for fc in action.fcurves:
        for key in fc.keyframe_points: key.interpolation="BEZIER"
scene.frame_set(1)
print("Rendering Keeladi pilot:",OUTPUT)
bpy.ops.render.render(animation=True)
print("Finished:",OUTPUT)
