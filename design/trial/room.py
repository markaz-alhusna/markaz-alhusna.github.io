"""The room: 6 x 6 m interior (x,z in [-3,3]), 2.8 m high, floor at y=0, Y-up, metres."""
import numpy as np
from lib3d import *
from items import CREAM, CORAL, MINT, MUSTARD, SKY, LAV, WOOD, DARK, STEEL, WHITE

WALL_A = (246, 214, 186)    # warm peach
WALL_B = (243, 230, 205)    # cream
CEIL = (250, 246, 238)
FLOOR = [(214, 162, 108), (201, 149, 97), (222, 172, 118)]
TRIM = (252, 248, 240)
HONEY = (222, 168, 98)

H = 2.8
WIN = dict(x0=-1.1, x1=0.3, y0=0.95, y1=2.15)
DOOR = dict(z0=0.9, z1=1.8, y1=2.05)


def build():
    b = Builder("Room")

    # ---------------------------------------------------------------- floor
    fg = b.group("Floor")
    planks = [[], [], []]
    w = 0.2
    for i, x in enumerate(np.arange(-3.1, 3.1 - 1e-6, w)):
        # stagger plank joints for a parquet look
        off = (i * 1.37) % 1.6
        zs = [-3.1] + list(np.arange(-3.1 + off + 0.4, 3.1, 1.6)) + [3.1]
        for k in range(len(zs) - 1):
            if zs[k + 1] - zs[k] < 0.05:
                continue
            planks[(i + k) % 3].append(rbox_mm(x + 0.002, x + w - 0.002, -0.06, 0.0, zs[k] + 0.002, zs[k + 1] - 0.002, 0.004))
    for k in range(3):
        b.add(merge(planks[k]), f"Floor_Planks_{k + 1}", mat(f"floor_wood_{k + 1}", FLOOR[k], 0.7), fg)
    b.add(box_mm(-3.1, 3.1, -0.12, -0.059, -3.1, 3.1), "Floor_Base", mat("floor_base", (150, 105, 70), 0.9), fg)

    # ---------------------------------------------------------------- walls
    wg = b.group("Walls")
    t0, t1 = 3.0, 3.1
    wp, wc, bb = mat("wall_peach", WALL_A, 0.9), mat("wall_cream", WALL_B, 0.9), mat("trim", TRIM, 0.6)
    walls = {
        "Back": ([box_mm(-t1, WIN['x0'], 0, H, -t1, -t0), box_mm(WIN['x1'], t1, 0, H, -t1, -t0),
                  box_mm(WIN['x0'], WIN['x1'], 0, WIN['y0'], -t1, -t0), box_mm(WIN['x0'], WIN['x1'], WIN['y1'], H, -t1, -t0)], wp,
                 [rbox_mm(-3.0, 3.0, 0, 0.09, -3.0, -2.985, 0.005)],
                 [rbox_mm(-3.0, 3.0, H - 0.06, H, -3.0, -2.975, 0.01)]),
        "Front": ([box_mm(-t1, t1, 0, H, t0, t1)], wp,
                  [rbox_mm(-3.0, 3.0, 0, 0.09, 2.985, 3.0, 0.005)],
                  [rbox_mm(-3.0, 3.0, H - 0.06, H, 2.975, 3.0, 0.01)]),
        "Left": ([box_mm(-t1, -t0, 0, H, -t0, DOOR['z0']), box_mm(-t1, -t0, 0, H, DOOR['z1'], t0),
                  box_mm(-t1, -t0, DOOR['y1'], H, DOOR['z0'], DOOR['z1'])], wc,
                 [rbox_mm(-3.0, -2.985, 0, 0.09, -2.985, DOOR['z0'] - 0.08, 0.005),
                  rbox_mm(-3.0, -2.985, 0, 0.09, DOOR['z1'] + 0.08, 2.985, 0.005)],
                 [rbox_mm(-3.0, -2.975, H - 0.06, H, -2.975, 2.975, 0.01)]),
        "Right": ([box_mm(t0, t1, 0, H, -t0, t0)], wc,
                  [rbox_mm(2.985, 3.0, 0, 0.09, -2.985, 2.985, 0.005)],
                  [rbox_mm(2.975, 3.0, H - 0.06, H, -2.975, 2.975, 0.01)]),
    }
    for name, (surf, m_, base, corn) in walls.items():
        g = b.group(f"Wall_{name}", wg)
        b.add(merge(surf), f"Wall_{name}_Surface", m_, g)
        b.add(merge(base), f"Wall_{name}_Baseboard", bb, g)
        b.add(merge(corn), f"Wall_{name}_Cornice", bb, g)
    b.add(box_mm(-t1, t1, H, H + 0.1, -t1, t1), "Ceiling", mat("ceiling", CEIL, 0.95))

    # ---------------------------------------------------------------- window + curtain
    wn = b.group("Window")
    x0, x1, y0, y1 = WIN['x0'], WIN['x1'], WIN['y0'], WIN['y1']
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    fm = mat("window_frame", WHITE, 0.5)
    fr = 0.06
    frame = [rbox_mm(x0, x1, y0, y0 + fr, -3.09, -2.99, 0.012), rbox_mm(x0, x1, y1 - fr, y1, -3.09, -2.99, 0.012),
             rbox_mm(x0, x0 + fr, y0, y1, -3.09, -2.99, 0.012), rbox_mm(x1 - fr, x1, y0, y1, -3.09, -2.99, 0.012),
             rbox_mm(xm - 0.025, xm + 0.025, y0, y1, -3.07, -3.01, 0.01),
             rbox_mm(x0, x1, ym + 0.15 - 0.025, ym + 0.15 + 0.025, -3.07, -3.01, 0.01)]
    trimw = [rbox_mm(x0 - 0.07, x1 + 0.07, y1, y1 + 0.07, -3.0, -2.98, 0.01),
             rbox_mm(x0 - 0.07, x0, y0, y1, -3.0, -2.98, 0.01), rbox_mm(x1, x1 + 0.07, y0, y1, -3.0, -2.98, 0.01)]
    b.add(merge(frame + trimw), "Window_Frame", fm, wn)
    b.add(box_mm(x0 + 0.01, x1 - 0.01, y0 + 0.01, y1 - 0.01, -3.042, -3.038), "Window_Glass",
          mat("glass", (200, 228, 245), 0.05, alpha=0.25, double=True), wn)
    b.add(rbox_mm(x0 - 0.1, x1 + 0.1, y0 - 0.05, y0 + 0.0, -3.08, -2.84, 0.015), "Window_Sill", fm, wn)
    b.add(box_mm(x0 - 0.6, x1 + 0.6, y0 - 0.6, y1 + 0.6, -3.62, -3.6), "Window_SkyBackdrop",
          mat("sky_backdrop", (168, 210, 240), 1.0, emissive=[0.55, 0.7, 0.82]), wn)
    rod_y, rod_z = y1 + 0.16, -2.9
    rod = round_tube([(x0 - 0.3, rod_y, rod_z), (x1 + 0.3, rod_y, rod_z)], 0.013, 16)
    fin = [sphere(0.03, (x0 - 0.32, rod_y, rod_z)), sphere(0.03, (x1 + 0.32, rod_y, rod_z))]
    brk = [round_tube([(x, rod_y, -2.995), (x, rod_y, rod_z)], 0.009, 10) for x in (x0 - 0.2, x1 + 0.2)]
    b.add(merge([rod] + fin + brk), "Curtain_Rod", mat("rod_wood", HONEY, 0.5), wn)

    def curtain(xa, xb, folds, gather_bottom=0.0):
        nu, nv = 70, 30
        u = np.linspace(0, 1, nu); v = np.linspace(0, 1, nv)
        top, bot = rod_y - 0.02, y0 + 0.05
        V = []
        for vv in v:
            # pinch the panel towards its outer edge near the bottom (tie-back look)
            for uu in u:
                width = (xb - xa) * (1 - gather_bottom * np.sin(np.pi * min(1, vv * 1.15)) ** 2 * 0.0)
                x = xa + uu * (xb - xa)
                amp = 0.028 + 0.012 * vv
                z = rod_z + 0.05 + amp * np.sin(uu * folds * 2 * np.pi)
                y = top - vv * (top - bot)
                V.append((x, y, z))
        V = np.array(V)
        F = []
        for j in range(nv - 1):
            for i in range(nu - 1):
                a, bq, c, d = j * nu + i, j * nu + i + 1, (j + 1) * nu + i + 1, (j + 1) * nu + i
                F += [[a, c, bq], [a, d, c]]
        m = trimesh.Trimesh(V, np.array(F))
        # hem: a soft rolled edge along the bottom
        hem = tube(V[-nu:] + [0, 0.004, 0], 0.008, 8)
        return m, hem

    cm = mat("curtain", CORAL, 0.95, double=True)
    for side, (xa, xb) in (("L", (x0 - 0.28, x0 + 0.32)), ("R", (x1 - 0.32, x1 + 0.28))):
        m, hem = curtain(xa, xb, 5)
        b.add(m, f"Curtain_{side}", cm, wn, smooth_angle=80)
        b.add(hem, f"Curtain_{side}_Hem", mat("curtain_hem", (245, 205, 170), 0.9), wn)
        rings = [tube(arc((x, rod_y, rod_z), 0.022, 0, 360, 'zy', 20)[:-1], 0.004, 8, closed=True)
                 for x in np.linspace(xa + 0.02, xb - 0.02, 6)]
        b.add(merge(rings), f"Curtain_{side}_Rings", mat("rod_wood", HONEY), wn)

    # ---------------------------------------------------------------- door (pivot on hinge)
    dg = b.group("DoorFrame")
    z0, z1, dy = DOOR['z0'], DOOR['z1'], DOOR['y1']
    jamb = [box_mm(-3.1, -3.0, 0, dy, z0, z0 + 0.02), box_mm(-3.1, -3.0, 0, dy, z1 - 0.02, z1),
            box_mm(-3.1, -3.0, dy - 0.02, dy, z0, z1)]
    arch = [rbox_mm(-3.0, -2.975, 0, dy + 0.08, z0 - 0.08, z0, 0.01), rbox_mm(-3.0, -2.975, 0, dy + 0.08, z1, z1 + 0.08, 0.01),
            rbox_mm(-3.0, -2.975, dy, dy + 0.08, z0 - 0.08, z1 + 0.08, 0.01)]
    b.add(merge(jamb + arch), "DoorFrame_Trim", mat("trim", TRIM), dg)
    door = b.group("Door", M=T(-3.05, 0, z0 + 0.02))
    dw = (z1 - z0) - 0.04
    b.add(rbox_mm(-0.022, 0.022, 0.005, dy - 0.025, 0.004, dw - 0.004, 0.012), "Door_Slab",
          mat("door_wood", HONEY, 0.6), door)
    panels = [rbox_mm(0.018, 0.03, py0, py1, 0.12, dw - 0.12, 0.02) for (py0, py1) in ((0.22, 0.95), (1.1, 1.85))]
    panels += [rbox_mm(-0.03, -0.018, py0, py1, 0.12, dw - 0.12, 0.02) for (py0, py1) in ((0.22, 0.95), (1.1, 1.85))]
    b.add(merge(panels), "Door_Panels", mat("door_panel", (232, 185, 120), 0.6), door)
    kn = []
    for s in (1, -1):
        kn.append(revolve(fillet([(0, 0), (0.03, 0), (0.03, 0.01), (0.008, 0.02), (0.008, 0.05), (0.028, 0.06),
                                  (0.026, 0.08), (0, 0.085)], 0.006), 32, axis='z'))
        kn[-1].apply_transform(T(s * 0.022, 1.0, dw - 0.08) @ R(90 * s, [0, 1, 0]))
    b.add(merge(kn), "Door_Knob", mat("brass", (215, 175, 90), 0.3, 0.9), door)

    # light switch near the door
    sw = b.group("Light_Switch", M=T(-3.0, 1.05, z0 - 0.2) @ R(90, [0, 1, 0]))
    b.add(rbox(0.08, 0.08, 0.012, 0.012, (0, 0, 0.006)), "Light_Switch_Plate", mat("outlet_plastic", WHITE, 0.45), sw)
    b.add(rbox(0.026, 0.04, 0.012, 0.006, (0, 0, 0.014)), "Light_Switch_Key", mat("outlet_inner", (232, 228, 220), 0.5), sw)

    # ---------------------------------------------------------------- ceiling lamp
    lg = b.group("Ceiling_Lamp", M=T(0.2, H, 0.2))
    b.add(revolve(fillet([(0, 0), (0.07, 0), (0.06, -0.025), (0, -0.03)], 0.01)), "Lamp_Canopy",
          mat("lamp_white", WHITE, 0.5), lg)
    b.add(tube([(0, -0.02, 0), (0, -0.42, 0)], 0.005, 10), "Lamp_Cord", mat("cord_dark", DARK, 0.6), lg)
    outer = fillet([(0.03, -0.40), (0.06, -0.42), (0.16, -0.52), (0.24, -0.64), (0.25, -0.66)], 0.03, 8)
    inner = outer[::-1] + np.array([-0.012, 0.0])
    inner[0][0] -= 0.0
    shade_prof = np.vstack([outer, [(0.252, -0.665), (0.238, -0.664)], inner])
    shade = trimesh.creation.revolve(np.asarray(shade_prof), sections=64)
    shade.apply_transform(Z2Y)
    b.add(shade, "Lamp_Shade", mat("lamp_shade", MUSTARD, 0.55, double=True, emissive=[0.12, 0.08, 0.02]), lg)
    b.add(revolve([(0, -0.40), (0.035, -0.40), (0.035, -0.47), (0, -0.47)], 24), "Lamp_Socket",
          mat("lamp_white", WHITE, 0.5), lg)
    b.add(sphere(0.055, (0, -0.52, 0)), "Lamp_Bulb", mat("bulb", (255, 238, 200), 0.2, emissive=[1.0, 0.85, 0.6]), lg)
    b.group("Lamp_LightPoint", lg, T(0, -0.55, 0))

    # ---------------------------------------------------------------- bed (back-right corner)
    bed = b.group("Bed", M=T(2.2, 0, -1.9))
    bw, bl = 1.5, 2.1
    b.add(rbox(bw, 0.2, bl, 0.04, (0, 0.24, 0)), "Bed_Frame", mat("bed_wood", WOOD, 0.6), bed)
    legs = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            l = revolve(fillet([(0, 0), (0.035, 0), (0.045, 0.14), (0, 0.14)], 0.01), 24)
            l.apply_translation((sx * (bw / 2 - 0.08), 0, sz * (bl / 2 - 0.08)))
            legs.append(l)
    b.add(merge(legs), "Bed_Legs", mat("bed_wood", WOOD), bed)
    hx = np.linspace(-bw / 2 + 0.04, bw / 2 - 0.04, 13)
    hb_pts = [(x, 0.95 + 0.18 * np.sqrt(max(0, 1 - (x / (bw / 2)) ** 2)), z) for x in hx for z in (-0.012, 0.012)]
    hb_pts += [(sx * (bw / 2 - 0.04), 0.2, z) for sx in (-1, 1) for z in (-0.012, 0.012)]
    hb = hull_spheres(hb_pts, 0.035); hb.apply_translation((0, 0, -bl / 2 + 0.04))
    b.add(hb, "Bed_Headboard", mat("bed_head", MINT, 0.6), bed)
    fb_pts = [(x, 0.55 + 0.08 * np.sqrt(max(0, 1 - (x / (bw / 2)) ** 2)), z) for x in hx for z in (-0.01, 0.01)]
    fb_pts += [(sx * (bw / 2 - 0.04), 0.2, z) for sx in (-1, 1) for z in (-0.01, 0.01)]
    fb = hull_spheres(fb_pts, 0.032); fb.apply_translation((0, 0, bl / 2 - 0.035))
    b.add(fb, "Bed_Footboard", mat("bed_head", MINT, 0.6), bed)
    b.add(rbox(bw - 0.1, 0.2, bl - 0.16, 0.07, (0, 0.43, -0.01)), "Bed_Mattress", mat("mattress", (250, 248, 242), 0.9), bed)
    b.add(rbox(bw - 0.02, 0.26, 1.42, 0.08, (0, 0.425, 0.28)), "Bed_Blanket", mat("blanket", MUSTARD, 0.95), bed)
    b.add(round_tube([(-bw / 2 + 0.03, 0.56, -0.42), (bw / 2 - 0.03, 0.56, -0.42)], 0.04, 20), "Bed_Blanket_Fold",
          mat("blanket_fold", (252, 240, 215), 0.95), bed)
    for side, x in (("L", -0.34), ("R", 0.34)):
        pts = [(x + sx * 0.22, 0.6, -0.78 + sz * 0.14) for sx in (-1, 1) for sz in (-1, 1)]
        pts += [(x, 0.64, -0.78)]
        b.add(hull_spheres(pts, [0.045] * 4 + [0.075]), f"Bed_Pillow_{side}", mat("pillow", (255, 252, 246), 0.95), bed)

    # ---------------------------------------------------------------- wardrobe (right wall, faces -X)
    wr = b.group("Wardrobe", M=T(2.68, 0, 1.4))
    wd, ww, wh = 0.6, 1.4, 2.1
    wbody = mat("wardrobe_body", CREAM, 0.6)
    b.add(rbox(wd - 0.04, wh - 0.12, ww, 0.03, (0.02, 0.12 + (wh - 0.12) / 2, 0)), "Wardrobe_Body", wbody, wr)
    b.add(rbox(wd + 0.02, 0.06, ww + 0.06, 0.025, (0.0, wh + 0.02, 0)), "Wardrobe_Top", mat("bed_wood", WOOD), wr)
    wl = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            l = revolve(fillet([(0, 0), (0.03, 0), (0.04, 0.13), (0, 0.13)], 0.008), 20)
            l.apply_translation((0.02 + sx * (wd / 2 - 0.08), 0, sz * (ww / 2 - 0.08)))
            wl.append(l)
    b.add(merge(wl), "Wardrobe_Legs", mat("bed_wood", WOOD), wr)
    for side, s in (("L", -1), ("R", 1)):
        dgp = b.group(f"Wardrobe_Door_{side}", wr, T(-wd / 2 + 0.03, 0, s * ww / 2))
        z_in, z_out = -s * 0.004, -s * (ww / 2 - 0.004)
        b.add(rbox_mm(-0.03, 0.0, 0.16, wh - 0.04, min(z_in, z_out), max(z_in, z_out), 0.015),
              f"Wardrobe_Door_{side}_Slab", mat("wardrobe_door", MINT, 0.55), dgp)
        zc = (z_in + z_out) / 2
        pan = rbox_mm(-0.04, -0.028, 0.32, wh - 0.22, zc - 0.22, zc + 0.22, 0.03)
        b.add(pan, f"Wardrobe_Door_{side}_Panel", mat("wardrobe_panel", (160, 215, 192), 0.55), dgp)
        k = sphere(0.025, (-0.06, 1.15, z_out + s * (ww / 2 - 0.07)))
        st = round_tube([(-0.03, 1.15, z_out + s * (ww / 2 - 0.07)), (-0.05, 1.15, z_out + s * (ww / 2 - 0.07))], 0.008)
        b.add(merge(k, st), f"Wardrobe_Door_{side}_Knob", mat("brass", (215, 175, 90), 0.3, 0.9), dgp)

    # ---------------------------------------------------------------- desk + stool (under window)
    dk = b.group("Desk", M=T(-0.4, 0, -2.66))
    dwid, ddep, dh = 1.3, 0.6, 0.75
    b.add(rbox(dwid, 0.04, ddep, 0.015, (0, dh - 0.02, 0)), "Desk_Top", mat("bed_wood", WOOD), dk)
    dl = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            l = revolve(fillet([(0, 0), (0.022, 0), (0.03, dh - 0.04), (0, dh - 0.04)], 0.006), 20)
            l.apply_translation((sx * (dwid / 2 - 0.06), 0, sz * (ddep / 2 - 0.06)))
            dl.append(l)
    b.add(merge(dl), "Desk_Legs", mat("desk_legs", HONEY, 0.6), dk)
    drw = b.group("Desk_Drawer", dk, T(0.3, dh - 0.11, 0))
    b.add(rbox(0.46, 0.12, ddep - 0.06, 0.015, (0, 0, 0)), "Desk_Drawer_Box", mat("wardrobe_door", MINT), drw)
    b.add(sphere(0.02, (0, 0, ddep / 2 - 0.02)), "Desk_Drawer_Knob", mat("brass", (215, 175, 90), 0.3, 0.9), drw)
    st = b.group("Stool", M=T(-0.4, 0, -1.95))
    b.add(revolve(fillet([(0, 0.42), (0.19, 0.42), (0.2, 0.46), (0.18, 0.48), (0, 0.485)], [0, 0.015, 0.02, 0.02, 0], 6), 48),
          "Stool_Seat", mat("stool_seat", CORAL, 0.7), st)
    sl = []
    for a in range(3):
        an = np.radians(90 + a * 120)
        sl.append(round_tube([(np.cos(an) * 0.12, 0.42, np.sin(an) * 0.12), (np.cos(an) * 0.17, 0.015, np.sin(an) * 0.17)], 0.018))
    ring = tube(arc((0, 0.16, 0), 0.155, 0, 360, 'xz', 40)[:-1], 0.008, 8, closed=True)
    b.add(merge(sl + [ring]), "Stool_Legs", mat("bed_wood", WOOD), st)

    # ---------------------------------------------------------------- kitchen counter (left wall, back)
    kc = b.group("Kitchen_Counter", M=T(-2.7, 0, -1.94))
    kd, kl, kh = 0.6, 2.08, 0.9
    b.add(rbox_mm(-0.3, 0.26, 0.0, 0.08, -kl / 2 + 0.02, kl / 2 - 0.02, 0.01), "Counter_Plinth", mat("plinth", (110, 95, 90), 0.8), kc)
    b.add(rbox_mm(-0.3, 0.28, 0.08, kh - 0.04, -kl / 2, kl / 2, 0.02), "Counter_Cabinet", mat("wardrobe_body", CREAM), kc)
    b.add(rbox_mm(-0.3, 0.33, kh - 0.045, kh, -kl / 2 - 0.02, kl / 2 + 0.02, 0.012), "Counter_Top",
          mat("countertop", (238, 232, 222), 0.4), kc)
    fronts, knobs = [], []
    n = 3
    dwk = kl / n
    for i in range(n):
        za, zb = -kl / 2 + i * dwk + 0.008, -kl / 2 + (i + 1) * dwk - 0.008
        fronts.append(rbox_mm(0.27, 0.3, 0.1, kh - 0.07, za, zb, 0.015))
        knobs.append(sphere(0.02, (0.32, kh - 0.18, zb - 0.07 if i % 2 == 0 else za + 0.07)))
    b.add(merge(fronts), "Counter_Doors", mat("counter_door", SKY, 0.55), kc)
    b.add(merge(knobs), "Counter_Knobs", mat("brass", (215, 175, 90), 0.3, 0.9), kc)
    # sink + tap
    sz_ = 0.52
    b.add(rbox_mm(-0.2, 0.2, kh - 0.002, kh + 0.006, sz_ - 0.24, sz_ + 0.24, 0.03), "Sink_Rim", mat("steel", STEEL, 0.25, 0.9), kc)
    b.add(rbox_mm(-0.17, 0.17, kh + 0.004, kh + 0.0075, sz_ - 0.21, sz_ + 0.21, 0.03), "Sink_Basin",
          mat("sink_inner", (150, 155, 162), 0.3, 0.8), kc)
    tap = spline([(-0.25, kh, sz_), (-0.25, kh + 0.2, sz_), (-0.2, kh + 0.27, sz_), (-0.12, kh + 0.24, sz_), (-0.1, kh + 0.17, sz_)], 40)
    b.add(round_tube(tap, 0.014, 16), "Sink_Tap", mat("steel", STEEL, 0.25, 0.9), kc)
    # backsplash tiles on the wall
    tiles = [[], []]
    tz = np.arange(-kl / 2 - 0.02, kl / 2 + 0.02 - 1e-6, 0.15)
    for r_, ty in enumerate(np.arange(kh, kh + 0.6 - 1e-6, 0.15)):
        for c_, z in enumerate(tz):
            tiles[(r_ + c_) % 2].append(rbox_mm(-0.3, -0.288, ty + 0.004, ty + 0.146, z + 0.004, z + 0.146, 0.006))
    b.add(merge(tiles[0]), "Backsplash_Tiles_A", mat("tile_a", (250, 247, 240), 0.35), kc)
    b.add(merge(tiles[1]), "Backsplash_Tiles_B", mat("tile_b", (150, 205, 200), 0.35), kc)

    # ---------------------------------------------------------------- hanging shelf (above the counter)
    sh = b.group("Hanging_Shelf", M=T(-2.88, 1.66, -1.95))
    b.add(rbox_mm(-0.12, 0.13, -0.035, 0.0, -0.65, 0.65, 0.012), "Shelf_Board", mat("bed_wood", WOOD), sh)
    br = []
    for z in (-0.45, 0.45):
        br.append(hull_spheres([(-0.115, -0.03, z), (-0.115, -0.2, z), (0.07, -0.03, z)], 0.012))
    b.add(merge(br), "Shelf_Brackets", mat("desk_legs", HONEY), sh)
    # a couple of harmless jars for decoration
    jars = []
    for z, h_, r_ in ((0.45, 0.14, 0.045), (0.3, 0.1, 0.04)):
        j = revolve(fillet([(0, 0), (r_, 0), (r_, h_), (r_ * 0.7, h_ + 0.012), (0, h_ + 0.012)], 0.008), 32)
        j.apply_translation((0, 0, z)); jars.append(j)
    b.add(merge(jars), "Shelf_Jars", mat("jar_glass", (190, 225, 215), 0.15, alpha=0.7), sh)
    lids = []
    for z, h_, r_ in ((0.45, 0.14, 0.045), (0.3, 0.1, 0.04)):
        l = revolve(fillet([(0, h_ + 0.008), (r_ * 0.78, h_ + 0.008), (r_ * 0.78, h_ + 0.03), (0, h_ + 0.032)], 0.004), 32)
        l.apply_translation((0, 0, z)); lids.append(l)
    b.add(merge(lids), "Shelf_Jar_Lids", mat("stool_seat", CORAL), sh)

    # ---------------------------------------------------------------- rug
    rug = b.group("Rug", M=T(0.3, 0, 0.5))
    def disc(r0, r1, h, rad):
        p = fillet([(r0, 0), (r1, 0), (r1, h), (r0, h)], 0.004) if r0 > 0 else fillet([(0, 0), (r1, 0), (r1, h), (0, h)], [0, 0.004, 0.004, 0])
        m = revolve(p, 96)
        m.apply_scale([1.3, 1, 1])
        return m
    b.add(disc(0, 1.15, 0.012, 0), "Rug_Base", mat("rug_coral", CORAL, 1.0), rug)
    b.add(disc(0, 0.95, 0.014, 0), "Rug_Ring", mat("rug_cream", (250, 236, 210), 1.0), rug)
    b.add(disc(0, 0.75, 0.016, 0), "Rug_Middle", mat("rug_mustard", MUSTARD, 1.0), rug)
    b.add(disc(0, 0.45, 0.018, 0), "Rug_Center", mat("rug_cream", (250, 236, 210), 1.0), rug)

    # ---------------------------------------------------------------- anchors (empty nodes) for the props
    # each prop file has its origin at its own bottom centre; place it at the anchor with the anchor's rotation
    A = {
        "stove":      T(-2.68, 0.9, -2.35) @ R(90, [0, 1, 0]),
        "kettle":     T(-2.70, 1.064, -2.49),
        "pot":        T(-2.70, 1.064, -2.21),
        "knife":      T(-2.62, 0.9, -1.85) @ R(70, [0, 1, 0]),
        "matches":    T(-2.86, 1.66, -2.25) @ R(80, [0, 1, 0]),
        "pills":      T(-2.88, 1.66, -1.65) @ R(90, [0, 1, 0]),
        "iron":       T(-0.8, 0.75, -2.62) @ R(-35, [0, 1, 0]),
        "flashlight": T(0.0, 0.75, -2.55) @ R(-25, [0, 1, 0]),
        "outlet":     T(0.75, 0.32, -3.0),
        "wire":       T(1.05, 0.0, -2.62) @ R(10, [0, 1, 0]),
        "tower":      T(0.7, 0.018, 0.75),
        "box":        T(1.4, 0.0, 2.0) @ R(15, [0, 1, 0]),
    }
    ag = b.group("Anchors")
    for k, M in A.items():
        b.group(f"Spot_{k}", ag, M)
    return b, A


if __name__ == '__main__':
    b, A = build()
    b.export('out/room.glb')
    print(len(b.scene.geometry), sum(len(g.faces) for g in b.scene.geometry.values()))
