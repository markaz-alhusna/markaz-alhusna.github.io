"""Tiny software rasteriser for preview PNGs (z-buffer, Lambert + ambient, SSAA)."""
import sys
import numpy as np
import trimesh
from PIL import Image


def scene_tris(scene):
    tris, cols = [], []
    for node in scene.graph.nodes_geometry:
        M, gname = scene.graph[node]
        g = scene.geometry[gname]
        v = trimesh.transform_points(g.vertices, M)
        mt = getattr(g.visual, 'material', None)
        c = np.array(mt.baseColorFactor if mt is not None and mt.baseColorFactor is not None else [200, 200, 200, 255], float)
        if c.max() > 1.0:
            c = c / 255.0
        e = np.zeros(3)
        if mt is not None and getattr(mt, 'emissiveFactor', None) is not None:
            e = np.asarray(mt.emissiveFactor, float)
        tris.append(v[g.faces])
        cols.append(np.repeat(np.concatenate([c[:4], e])[None], len(g.faces), 0))
    return np.concatenate(tris), np.concatenate(cols)


def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(lambda a: np.asarray(a, float), (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return eye, np.stack([r, u, -f])


def render(scene, eye, target, size=(900, 700), fov=45, ss=2, light=(0.4, 1.0, 0.6), bg=(238, 234, 228), path=None):
    W, H = size[0] * ss, size[1] * ss
    tris, cols = scene_tris(scene)
    eye, Rm = look_at(eye, target)
    cam = (tris - eye) @ Rm.T            # x right, y up, z towards viewer (negative in front)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nl = np.linalg.norm(n, axis=1); ok = nl > 1e-14
    tris, cols, cam, n = tris[ok], cols[ok], cam[ok], n[ok] / nl[ok][:, None]
    L = np.asarray(light, float); L /= np.linalg.norm(L)
    view = (eye - tris.mean(1)); view /= np.linalg.norm(view, axis=1)[:, None]
    n = np.where((np.sum(n * view, 1) < 0)[:, None], -n, n)   # two-sided lighting
    diff = np.clip(n @ L, 0, 1)
    fill = np.clip(n @ np.array([-0.5, 0.3, -0.4]) / np.linalg.norm([-0.5, 0.3, -0.4]), 0, 1)
    shade = 0.45 + 0.5 * diff + 0.12 * fill
    rgb = np.clip(cols[:, :3] * shade[:, None] + cols[:, 4:7], 0, 1)
    alpha = cols[:, 3]
    f = 0.5 * H / np.tan(np.radians(fov) / 2)
    z = -cam[..., 2]
    keep = (z > 0.02).all(1)
    cam, z, rgb, alpha = cam[keep], z[keep], rgb[keep], alpha[keep]
    sx = W / 2 + f * cam[..., 0] / z
    sy = H / 2 - f * cam[..., 1] / z
    zb = np.full((H, W), np.inf); img = np.zeros((H, W, 3)); img[:] = np.array(bg) / 255
    order = np.argsort(alpha < 1)        # opaque first, then transparent
    trans = []
    for i in order:
        x0, x1 = int(max(0, np.floor(sx[i].min()))), int(min(W - 1, np.ceil(sx[i].max())))
        y0, y1 = int(max(0, np.floor(sy[i].min()))), int(min(H - 1, np.ceil(sy[i].max())))
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, bx, cx), (ay, by, cy) = sx[i], sy[i]
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        w0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        w1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not inside.any():
            continue
        iz = w0 / z[i, 0] + w1 / z[i, 1] + w2 / z[i, 2]
        depth = 1 / iz
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        m = inside & (depth < sub)
        if alpha[i] >= 1:
            sub[m] = depth[m]
            img[y0:y1 + 1, x0:x1 + 1][m] = rgb[i]
        else:
            a = alpha[i]
            region = img[y0:y1 + 1, x0:x1 + 1]
            region[m] = region[m] * (1 - a) + rgb[i] * a
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    if path:
        out.save(path)
    return out


if __name__ == '__main__':
    sc = trimesh.load(sys.argv[1])
    bmin, bmax = sc.bounds
    c = (bmin + bmax) / 2; d = np.linalg.norm(bmax - bmin)
    render(sc, c + np.array([0.9, 0.75, 1.2]) * d * 0.95, c, (700, 560), path=sys.argv[2])
