"""Small procedural-modelling helpers on top of trimesh. Units: metres, Y-up (glTF)."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals
from trimesh.transformations import rotation_matrix, translation_matrix

_SPH = {s: trimesh.creation.icosphere(subdivisions=s).vertices for s in (1, 2, 3)}
Z2Y = rotation_matrix(-np.pi / 2, [1, 0, 0])   # revolve axis Z -> Y
Z2X = rotation_matrix(np.pi / 2, [0, 1, 0])    # revolve axis Z -> X
I4 = np.eye(4)


def T(x=0, y=0, z=0):
    return translation_matrix([x, y, z])


def R(angle_deg, axis):
    return rotation_matrix(np.radians(angle_deg), axis)


def hull_spheres(points, r, sub=2):
    """Convex hull of spheres -> soft, rounded convex shapes."""
    pts = np.asarray(points, float)
    rr = np.broadcast_to(np.asarray(r, float).reshape(-1, 1, 1), (len(pts), 1, 1))
    allp = (pts[:, None, :] + _SPH[sub][None] * rr).reshape(-1, 3)
    return trimesh.convex.convex_hull(allp)


def rbox(sx, sy, sz, r=0.02, c=(0, 0, 0), sub=2):
    """Rounded box of full size sx,sy,sz centred at c."""
    r = max(1e-4, min(r, min(sx, sy, sz) / 2 - 1e-5))
    hx, hy, hz = sx / 2 - r, sy / 2 - r, sz / 2 - r
    corners = [(i * hx, j * hy, k * hz) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)]
    m = hull_spheres(corners, r, sub)
    m.apply_translation(c)
    return m


def box(sx, sy, sz, c=(0, 0, 0)):
    m = trimesh.creation.box([sx, sy, sz])
    m.apply_translation(c)
    return m


def box_mm(x0, x1, y0, y1, z0, z1):
    return box(x1 - x0, y1 - y0, z1 - z0, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def rbox_mm(x0, x1, y0, y1, z0, z1, r=0.02):
    return rbox(x1 - x0, y1 - y0, z1 - z0, r, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def fillet(pts, r, n=5, keep_ends=True):
    """Round every interior corner of a 2D polyline with radius-ish r."""
    pts = [np.asarray(p, float) for p in pts]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p, p1 = pts[i - 1], pts[i], pts[i + 1]
        rr = r[i] if isinstance(r, (list, tuple)) else r
        if rr <= 0:
            out.append(p)
            continue
        d0 = p0 - p; l0 = np.linalg.norm(d0)
        d1 = p1 - p; l1 = np.linalg.norm(d1)
        a = p + d0 / l0 * min(rr, l0 * 0.49)
        b = p + d1 / l1 * min(rr, l1 * 0.49)
        for t in np.linspace(0, 1, n):
            out.append((1 - t) ** 2 * a + 2 * (1 - t) * t * p + t ** 2 * b)
    out.append(pts[-1])
    return np.array(out)


def revolve(profile, sections=48, axis='y'):
    """profile: list of (radius, height). Start/end on axis for closed solids."""
    m = trimesh.creation.revolve(np.asarray(profile, float), sections=sections)
    m.apply_transform(Z2Y if axis == 'y' else (Z2X if axis == 'x' else I4))
    if m.volume < 0:
        m.invert()
    return m


def _frames(path):
    path = np.asarray(path, float)
    tang = np.gradient(path, axis=0)
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    ref = np.array([0, 1, 0.0]) if abs(tang[0][1]) < 0.9 else np.array([1, 0, 0.0])
    n = np.cross(tang[0], ref); n /= np.linalg.norm(n)
    normals = [n]
    for i in range(1, len(path)):
        t = tang[i]
        n = normals[-1] - np.dot(normals[-1], t) * t
        n /= np.linalg.norm(n)
        normals.append(n)
    normals = np.array(normals)
    binorm = np.cross(tang, normals)
    return tang, normals, binorm


def tube(path, radius, seg=16, cap=True, closed=False):
    """Swept circular tube along a polyline. radius may be scalar or per-point."""
    path = np.asarray(path, float)
    n = len(path)
    rad = np.broadcast_to(np.asarray(radius, float), (n,))
    tang, nor, bi = _frames(path)
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    ring = np.cos(ang)[None, :, None] * nor[:, None, :] + np.sin(ang)[None, :, None] * bi[:, None, :]
    verts = (path[:, None, :] + ring * rad[:, None, None]).reshape(-1, 3)
    faces = []
    rows = n if closed else n - 1
    for i in range(rows):
        i2 = (i + 1) % n
        for j in range(seg):
            j2 = (j + 1) % seg
            a, b, c, d = i * seg + j, i * seg + j2, i2 * seg + j2, i2 * seg + j
            faces += [[a, b, c], [a, c, d]]
    verts = list(verts)
    if cap and not closed:
        for end, flip in ((0, True), (n - 1, False)):
            ci = len(verts); verts.append(path[end])
            for j in range(seg):
                j2 = (j + 1) % seg
                f = [ci, end * seg + j, end * seg + j2]
                faces.append(f[::-1] if not flip else f)
    m = trimesh.Trimesh(np.array(verts), np.array(faces), process=True)
    trimesh.repair.fix_normals(m)
    return m


def round_tube(path, radius, seg=16):
    """Tube with spherical end caps."""
    path = np.asarray(path, float)
    parts = [tube(path, radius, seg)]
    rad = np.broadcast_to(np.asarray(radius, float), (len(path),))
    for i in (0, -1):
        s = trimesh.creation.icosphere(subdivisions=2, radius=rad[i] * 0.999)
        s.apply_translation(path[i]); parts.append(s)
    return trimesh.util.concatenate(parts)


def spline(ctrl, n=60):
    """Catmull-Rom through control points."""
    P = np.asarray(ctrl, float)
    P = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    out = []
    segs = len(P) - 3
    per = max(2, n // segs)
    for i in range(segs):
        p0, p1, p2, p3 = P[i:i + 4]
        for t in np.linspace(0, 1, per, endpoint=(i == segs - 1)):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


def arc(center, r, a0, a1, plane='xy', n=24):
    a = np.radians(np.linspace(a0, a1, n))
    c = np.asarray(center, float)
    if plane == 'xy':
        return c + np.stack([r * np.cos(a), r * np.sin(a), 0 * a], 1)
    if plane == 'zy':
        return c + np.stack([0 * a, r * np.sin(a), r * np.cos(a)], 1)
    if plane == 'xz':
        return c + np.stack([r * np.cos(a), 0 * a, r * np.sin(a)], 1)


def sphere(r, c=(0, 0, 0), sub=3):
    s = trimesh.creation.icosphere(subdivisions=sub, radius=r)
    s.apply_translation(c)
    return s


def merge(*ms):
    flat = []
    for m in ms:
        flat += list(m) if isinstance(m, (list, tuple)) else [m]
    return trimesh.util.concatenate(flat)


# ---------------------------------------------------------------- materials
_mat_cache = {}


def mat(name, rgb, rough=0.75, metal=0.0, alpha=1.0, emissive=None, double=False):
    key = name
    if key in _mat_cache:
        return _mat_cache[key]
    col = [rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha]
    m = PBRMaterial(name=name, baseColorFactor=col, roughnessFactor=rough, metallicFactor=metal,
                    doubleSided=double, alphaMode='BLEND' if alpha < 1 else 'OPAQUE',
                    emissiveFactor=emissive)
    _mat_cache[key] = m
    return m


# ---------------------------------------------------------------- scene builder
class Builder:
    def __init__(self, root_name):
        self.scene = trimesh.Scene()
        self.root = root_name
        self.scene.graph.update(frame_from=self.scene.graph.base_frame, frame_to=root_name, matrix=I4)
        self.names = set([root_name])

    def group(self, name, parent=None, M=I4):
        assert name not in self.names, name
        self.names.add(name)
        self.scene.graph.update(frame_from=parent or self.root, frame_to=name, matrix=M)
        return name

    def add(self, mesh, name, material, parent=None, M=I4, smooth_angle=35):
        assert name not in self.names, name
        self.names.add(name)
        mesh = mesh.copy()
        mesh.merge_vertices()
        mesh = trimesh.graph.smooth_shade(mesh, angle=np.radians(smooth_angle), facet_minarea=1e9)
        mesh.visual = TextureVisuals(material=material)
        self.scene.add_geometry(mesh, node_name=name, geom_name=name + "_mesh",
                                parent_node_name=parent or self.root, transform=M)
        return name

    def export(self, path):
        data = trimesh.exchange.gltf.export_glb(self.scene, include_normals=True)
        with open(path, 'wb') as f:
            f.write(data)
        return path
