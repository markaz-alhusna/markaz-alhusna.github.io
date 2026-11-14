"""Interactive props. Each builder returns a Builder; origin at the bottom centre of the prop
(outlet: centre of its back plate, which sits on the wall, facing +Z)."""
import numpy as np
from lib3d import *

# shared palette
CREAM = (250, 238, 215); CORAL = (238, 112, 90); MINT = (130, 200, 175); MUSTARD = (238, 186, 78)
SKY = (120, 175, 225); LAV = (165, 145, 215); WOOD = (210, 155, 100); DARK = (58, 54, 60)
STEEL = (205, 208, 212); WHITE = (246, 244, 238); RED = (220, 70, 60); KRAFT = (200, 155, 100)


def stove():
    b = Builder("stove")
    W, D, H = 0.58, 0.42, 0.10
    b.add(rbox(W, H, D, 0.03, (0, 0.012 + H / 2, 0)), "Stove_Body", mat("stove_enamel", CREAM, 0.45))
    b.add(rbox(W - 0.03, 0.012, D - 0.03, 0.005, (0, 0.012 + H, 0)), "Stove_Top", mat("stove_top", (215, 210, 205), 0.35, 0.3))
    feet = [rbox(0.04, 0.014, 0.04, 0.007, (sx * (W / 2 - 0.05), 0.007, sz * (D / 2 - 0.05)))
            for sx in (-1, 1) for sz in (-1, 1)]
    b.add(merge(feet), "Stove_Feet", mat("rubber_dark", DARK, 0.9))
    top = 0.012 + H + 0.006
    for side, x in (("L", -0.14), ("R", 0.14)):
        g = b.group(f"Burner_{side}", M=T(x, top, -0.02))
        b.add(revolve(fillet([(0, 0), (0.075, 0), (0.075, 0.014), (0.055, 0.022), (0, 0.022)], 0.006)),
              f"Burner_{side}_Base", mat("burner_metal", (90, 88, 92), 0.5, 0.6), g)
        b.add(revolve(fillet([(0, 0.02), (0.045, 0.02), (0.047, 0.03), (0, 0.034)], 0.004)),
              f"Burner_{side}_Cap", mat("burner_cap", (35, 33, 38), 0.4, 0.5), g)
        # grate: ring + 4 arms
        ring = tube(arc((0, 0.04, 0), 0.10, 0, 360, 'xz', 48)[:-1], 0.006, 10, closed=True)
        arms = []
        for a in range(4):
            ang = np.radians(45 + 90 * a)
            p0 = np.array([np.cos(ang) * 0.06, 0.04, np.sin(ang) * 0.06])
            p1 = np.array([np.cos(ang) * 0.115, 0.04, np.sin(ang) * 0.115])
            arms.append(round_tube([p0, (p0 + p1) / 2, p1], 0.006, 10))
            foot = p1.copy(); foot[1] = 0.0
            arms.append(round_tube([p1, foot], 0.006, 10))
        b.add(merge([ring] + arms), f"Burner_{side}_Grate", mat("grate", (45, 42, 48), 0.6, 0.4), g)
        # knob on the front face: own node so it can be rotated around Z
        kg = b.group(f"Knob_{side}", M=T(x, 0.012 + H / 2, D / 2))
        knob = revolve(fillet([(0, 0), (0.024, 0), (0.024, 0.016), (0.018, 0.026), (0, 0.026)], 0.005), axis='z')
        b.add(knob, f"Knob_{side}_Body", mat("knob", (60, 60, 66), 0.5), kg)
        b.add(rbox(0.008, 0.032, 0.012, 0.003, (0, 0.0, 0.026)), f"Knob_{side}_Grip", mat("knob_mark", CORAL, 0.5), kg)
    return b


def kettle():
    b = Builder("kettle")
    prof = fillet([(0, 0), (0.085, 0), (0.108, 0.07), (0.098, 0.14), (0.062, 0.185), (0.062, 0.19), (0, 0.19)],
                  [0, 0.02, 0.05, 0.04, 0.012, 0.002, 0], 8)
    b.add(revolve(prof, 64), "Kettle_Body", mat("kettle_enamel", CORAL, 0.35))
    b.add(revolve(fillet([(0, 0.006), (0.087, 0.006), (0.087, 0.0), (0, 0)], 0.002)), "Kettle_Base",
          mat("kettle_trim", WHITE, 0.4))
    lid = revolve(fillet([(0, 0.186), (0.068, 0.186), (0.066, 0.196), (0.04, 0.214), (0, 0.218)], [0, 0.004, 0.01, 0.01, 0], 6))
    b.add(merge(lid, sphere(0.016, (0, 0.226, 0))), "Kettle_Lid", mat("kettle_trim", WHITE, 0.4))
    sp = spline([(0.07, 0.05, 0), (0.12, 0.08, 0), (0.155, 0.13, 0), (0.18, 0.17, 0)], 30)
    b.add(round_tube(sp, np.linspace(0.022, 0.013, len(sp)), 20), "Kettle_Spout", mat("kettle_enamel", CORAL))
    b.add(sphere(0.016, (0.183, 0.175, 0)), "Kettle_Whistle", mat("kettle_black", DARK, 0.5))
    hp = spline([(-0.06, 0.17, 0), (-0.06, 0.255, 0), (0, 0.29, 0), (0.06, 0.255, 0), (0.06, 0.17, 0)], 40)
    b.add(round_tube(hp, 0.012, 16), "Kettle_Handle", mat("kettle_black", DARK, 0.5))
    return b


def pot():
    b = Builder("pot")
    R0, H = 0.125, 0.14
    prof = fillet([(0, 0), (R0 - 0.005, 0), (R0, 0.012), (R0, H), (R0 + 0.006, H + 0.004), (R0 - 0.006, H + 0.006),
                   (R0 - 0.008, 0.014), (R0 - 0.02, 0.008), (0, 0.008)], [0, 0.01, 0.01, 0.004, 0.003, 0.003, 0.01, 0.008, 0], 6)
    b.add(revolve(prof, 64), "Pot_Body", mat("pot_enamel", MINT, 0.4))
    for side, s in (("L", -1), ("R", 1)):
        hp = spline([(s * (R0 - 0.002), 0.115, -0.035), (s * (R0 + 0.035), 0.12, -0.03),
                     (s * (R0 + 0.045), 0.122, 0), (s * (R0 + 0.035), 0.12, 0.03), (s * (R0 - 0.002), 0.115, 0.035)], 30)
        b.add(round_tube(hp, 0.009, 14), f"Pot_Handle_{side}", mat("pot_handle", CREAM, 0.5))
    lg = b.group("Pot_Lid", M=T(0, H + 0.004, 0))
    b.add(revolve(fillet([(0, 0.0), (R0 + 0.004, 0.0), (R0 + 0.004, 0.006), (0.06, 0.03), (0, 0.035)], [0, 0.002, 0.004, 0.03, 0], 8), 64),
          "Pot_Lid_Shell", mat("pot_enamel", MINT, 0.4), lg)
    b.add(revolve(fillet([(0, 0.03), (0.015, 0.03), (0.022, 0.05), (0, 0.055)], 0.006)), "Pot_Lid_Knob",
          mat("pot_handle", CREAM, 0.5), lg)
    return b


def knife():
    b = Builder("knife")
    th = 0.0016
    out = [(0.0, 0.019), (0.10, 0.02), (0.15, 0.012), (0.175, 0.0), (0.15, -0.006), (0.09, -0.014), (0.0, -0.016)]
    pts = [(x, y, z) for (x, z) in out for y in (0.008 - th, 0.008 + th)]
    b.add(hull_spheres(pts, 0.0018, 1), "Knife_Blade", mat("steel", STEEL, 0.25, 0.9))
    b.add(rbox(0.016, 0.017, 0.04, 0.006, (-0.004, 0.0085, 0.0015)), "Knife_Bolster", mat("steel_dark", (160, 163, 170), 0.3, 0.9))
    hpts = [(-0.012, 0.008, 0), (-0.115, 0.009, 0)]
    handle = hull_spheres([(-0.014, 0.008, 0.008), (-0.014, 0.008, -0.006), (-0.11, 0.009, 0.011), (-0.11, 0.009, -0.009),
                           (-0.125, 0.009, 0.0)], 0.0085, 2)
    b.add(handle, "Knife_Handle", mat("knife_handle", RED, 0.5))
    rivets = [sphere(0.0028, (x, 0.0172, 0.001), 2) for x in (-0.035, -0.065, -0.095)]
    b.add(merge(rivets), "Knife_Rivets", mat("steel", STEEL, 0.25, 0.9))
    return b


def iron():
    b = Builder("iron")
    sole = [(-0.06, -0.12), (0.06, -0.12), (0.066, -0.04), (0.045, 0.07), (0.0, 0.135), (-0.045, 0.07), (-0.066, -0.04)]
    b.add(hull_spheres([(x, y, z) for (x, z) in sole for y in (0.006, 0.016)], 0.006), "Iron_Sole",
          mat("iron_sole", STEEL, 0.25, 0.9))
    body_pts = [(x * 0.97, 0.03, z * 0.97) for (x, z) in sole] + [(x * 0.62, 0.07, z * 0.62 - 0.025) for (x, z) in sole]
    b.add(hull_spheres(body_pts, 0.012), "Iron_Body", mat("iron_body", SKY, 0.4))
    hp = spline([(0, 0.075, -0.085), (0, 0.13, -0.08), (0, 0.15, -0.03), (0, 0.145, 0.03), (0, 0.085, 0.06)], 50)
    b.add(round_tube(hp, 0.014, 18), "Iron_Handle", mat("iron_handle", WHITE, 0.5))
    dg = b.group("Iron_Dial", M=T(0, 0.084, -0.02))
    b.add(revolve(fillet([(0, 0), (0.02, 0), (0.02, 0.008), (0.016, 0.014), (0, 0.014)], 0.003)), "Iron_Dial_Knob",
          mat("iron_dial", MUSTARD, 0.45), dg)
    b.add(rbox(0.004, 0.006, 0.022, 0.002, (0, 0.014, 0.0)), "Iron_Dial_Mark", mat("kettle_black", DARK, 0.5), dg)
    b.add(revolve(fillet([(0, 0), (0.008, 0), (0.008, 0.012), (0, 0.012)], 0.002), 16), "Iron_Light",
          mat("iron_light", (255, 120, 80), 0.3, emissive=[0.6, 0.15, 0.05]), M=T(0.0, 0.086, 0.038))
    cord = spline([(0, 0.05, -0.12), (0, 0.04, -0.17), (0.04, 0.01, -0.22), (0.12, 0.008, -0.24),
                   (0.18, 0.008, -0.18), (0.16, 0.008, -0.1), (0.22, 0.008, -0.05)], 80)
    b.add(round_tube(cord, 0.0055, 12), "Iron_Cord", mat("cord_white", (235, 232, 225), 0.6))
    pg = b.group("Iron_Plug", M=T(0.22, 0.016, -0.05) @ R(-90, [0, 1, 0]))
    b.add(rbox(0.032, 0.032, 0.042, 0.008, (0, 0, 0.01)), "Iron_Plug_Body", mat("cord_white", (235, 232, 225)), pg)
    pins = [round_tube([(sx, 0, -0.01), (sx, 0, -0.03)], 0.0022, 10) for sx in (-0.0095, 0.0095)]
    b.add(merge(pins), "Iron_Plug_Pins", mat("brass", (215, 175, 90), 0.3, 0.9), pg)
    return b


def outlet():
    b = Builder("outlet")
    b.add(rbox(0.086, 0.086, 0.012, 0.012, (0, 0, 0.006)), "Outlet_Plate", mat("outlet_plastic", WHITE, 0.45))
    sock = revolve(fillet([(0, 0.0), (0.03, 0.0), (0.03, 0.004), (0.027, 0.008), (0, 0.006)], 0.0025), 48, axis='z')
    b.add(sock, "Outlet_Socket", mat("outlet_inner", (232, 228, 220), 0.5), M=T(0, 0, 0.012))
    for side, x in (("L", -0.0095), ("R", 0.0095)):
        h = revolve([(0, 0), (0.0032, 0), (0.0032, 0.0025), (0, 0.0025)], 16, axis='z')
        b.add(h, f"Outlet_Hole_{side}", mat("hole_dark", (25, 25, 28), 0.9), M=T(x, 0, 0.0175))
    clips = [rbox(0.012, 0.004, 0.004, 0.0015, (0, s * 0.026, 0.019)) for s in (-1, 1)]
    b.add(merge(clips), "Outlet_Ground", mat("steel", STEEL, 0.25, 0.9))
    return b


def wire():
    b = Builder("wire")
    r = 0.0065
    ctrl = [(-0.32, r, 0.05), (-0.2, r, -0.04), (-0.06, r, 0.06), (0.06, r, -0.02), (0.15, r, 0.04), (0.22, r, 0.0)]
    path = spline(ctrl, 120)
    b.add(round_tube(path, r, 18), "Wire_Cable", mat("cable_grey", (70, 72, 80), 0.6))
    end = path[-1]; d = path[-1] - path[-2]; d /= np.linalg.norm(d)
    side = np.cross(d, [0, 1, 0]); side /= np.linalg.norm(side)
    copper = []
    for name, col, s, lift in (("Brown", (150, 85, 45), 1, 0.006), ("Blue", (70, 120, 200), -1, 0.003)):
        p0 = end - d * 0.004 + side * s * 0.0028
        p1 = end + d * 0.02 + side * s * 0.006
        p2 = end + d * 0.045 + side * s * 0.016 + np.array([0, lift, 0])
        core = spline([p0, p1, p2], 20)
        b.add(round_tube(core, 0.0028, 12), f"Wire_Core_{name}", mat(f"core_{name.lower()}", col, 0.55))
        cd = core[-1] - core[-2]; cd /= np.linalg.norm(cd)
        rng = np.random.default_rng(3 if s > 0 else 7)
        for k in range(7):
            spread = rng.normal(0, 1, 3) * 0.004; spread[1] = abs(spread[1]) * 0.8
            q0 = core[-1] - cd * 0.002 + (rng.random(3) - 0.5) * 0.0025
            q2 = core[-1] + cd * (0.02 + rng.random() * 0.012) + spread * 2.2
            q1 = (q0 + q2) / 2 + spread * 0.4
            copper.append(round_tube(spline([q0, q1, q2], 8), 0.0007, 6))
    b.add(merge(copper), "Wire_Copper", mat("copper", (225, 135, 80), 0.3, 0.9, emissive=[0.12, 0.05, 0.0]))
    return b


def matches():
    b = Builder("matches")
    X, Y, Z, t = 0.056, 0.017, 0.038, 0.0012
    sg = b.group("Matches_Sleeve")
    sleeve = [box(X, t, Z, (0, Y - t / 2, 0)), box(X, t, Z, (0, t / 2, 0)),
              box(X, Y, t, (0, Y / 2, Z / 2 - t / 2)), box(X, Y, t, (0, Y / 2, -Z / 2 + t / 2))]
    b.add(merge(sleeve), "Matches_Sleeve_Card", mat("match_box", MUSTARD, 0.7), sg)
    b.add(merge([box(X * 0.92, Y * 0.7, 0.0006, (0, Y / 2, s * (Z / 2 + 0.0003))) for s in (-1, 1)]),
          "Matches_Striker", mat("striker", (110, 65, 45), 0.95), sg)
    b.add(rbox(0.03, 0.0008, 0.024, 0.0003, (0, Y + 0.0004, 0), 1), "Matches_Label", mat("match_label", RED, 0.6), sg)
    b.add(revolve([(0, 0), (0.007, 0), (0.007, 0.0006), (0, 0.0006)], 24), "Matches_Label_Dot",
          mat("match_label_dot", CREAM, 0.6), sg, M=T(0, Y + 0.0008, 0))
    tg = b.group("Matches_Tray", M=T(0.024, 0, 0))
    ti = 0.0008; x0, x1, z0, z1 = -X / 2 + 0.0015, X / 2 - 0.0015, -Z / 2 + t + 0.0003, Z / 2 - t - 0.0003
    tray = [box_mm(x0, x1, t, t + ti, z0, z1), box_mm(x0, x0 + ti, t, Y - t - 0.0005, z0, z1),
            box_mm(x1 - ti, x1, t, Y - t - 0.0005, z0, z1), box_mm(x0, x1, t, Y - t - 0.0005, z0, z0 + ti),
            box_mm(x0, x1, t, Y - t - 0.0005, z1 - ti, z1)]
    b.add(merge(tray), "Matches_Tray_Card", mat("match_tray", (235, 225, 205), 0.8), tg)
    sticks, heads = [], []
    for i, z in enumerate(np.linspace(z0 + 0.003, z1 - 0.003, 9)):
        y = t + ti + 0.0012 + (i % 2) * 0.0024
        xs = -0.022 if i % 2 else -0.024
        sticks.append(box(0.044, 0.0022, 0.0022, (xs + 0.022, y, z)))
        heads.append(hull_spheres([(xs + 0.045, y, z), (xs + 0.048, y, z)], 0.0019, 1))
    b.add(merge(sticks), "Matches_Sticks", mat("match_wood", (240, 215, 165), 0.8), tg)
    b.add(merge(heads), "Matches_Heads", mat("match_head", RED, 0.6), tg)
    lg = b.group("Match_Loose", M=T(0.005, 0.0011, 0.04) @ R(18, [0, 1, 0]))
    b.add(box(0.044, 0.0022, 0.0022, (0, 0, 0)), "Match_Loose_Stick", mat("match_wood", (240, 215, 165)), lg)
    b.add(hull_spheres([(0.0225, 0, 0), (0.0255, 0, 0)], 0.0019, 1), "Match_Loose_Head", mat("match_head", RED), lg)
    return b


def pills():
    b = Builder("pills")
    bg = b.group("Pills_Bottle")
    b.add(revolve(fillet([(0, 0), (0.024, 0), (0.024, 0.07), (0.016, 0.078), (0.016, 0.086), (0, 0.086)],
                         [0, 0.005, 0.008, 0.002, 0.001, 0], 6), 48), "Pills_Bottle_Body",
          mat("pill_bottle", (232, 140, 60), 0.3, alpha=0.88), bg)
    b.add(revolve([(0, 0.016), (0.0245, 0.016), (0.0245, 0.058), (0, 0.058)], 48), "Pills_Label",
          mat("pill_label", WHITE, 0.6), bg)
    cross = [rbox(0.016, 0.005, 0.002, 0.001, (0, 0.037, 0.0248)), rbox(0.005, 0.016, 0.002, 0.001, (0, 0.037, 0.0248))]
    b.add(merge(cross), "Pills_Label_Cross", mat("pill_cross", RED, 0.5), bg)
    cap = revolve(fillet([(0, 0.074), (0.0205, 0.074), (0.0205, 0.096), (0, 0.098)], [0, 0.002, 0.004, 0], 5), 48)
    ribs = [rbox(0.0025, 0.016, 0.0025, 0.001, (np.cos(a) * 0.0205, 0.085, np.sin(a) * 0.0205))
            for a in np.linspace(0, 2 * np.pi, 24, endpoint=False)]
    b.add(merge([cap] + ribs), "Pills_Cap", mat("pill_cap", WHITE, 0.45), bg)
    # blister pack lying next to the bottle
    xg = b.group("Pills_Blister", M=T(0.075, 0, 0.01) @ R(-20, [0, 1, 0]))
    b.add(rbox(0.09, 0.0025, 0.05, 0.004, (0, 0.00125, 0)), "Pills_Blister_Foil", mat("foil", (215, 218, 225), 0.3, 0.8), xg)
    bubbles, tabs = [], []
    for i in range(5):
        for j in range(2):
            x, z = -0.034 + i * 0.017, -0.011 + j * 0.022
            bub = revolve(fillet([(0, 0), (0.0068, 0), (0.0066, 0.004), (0, 0.0058)], [0, 0.001, 0.003, 0], 6), 24)
            bub.apply_translation((x, 0.0025, z)); bubbles.append(bub)
            if not (i == 4 and j == 1):
                tb = revolve(fillet([(0, 0), (0.0055, 0), (0.0055, 0.003), (0, 0.0038)], [0, 0.0012, 0.0015, 0], 5), 24)
                tb.apply_translation((x, 0.0026, z)); tabs.append(tb)
    b.add(merge(bubbles), "Pills_Blister_Bubbles", mat("blister_plastic", (235, 245, 255), 0.1, alpha=0.45), xg)
    b.add(merge(tabs), "Pills_Tablets", mat("pill_pink", (245, 170, 185), 0.5), xg)
    return b


def tower():
    """Toy block tower: every block is a separate node with its own centre as pivot (for physics)."""
    b = Builder("tower")
    s = 0.065
    cols = [RED, MUSTARD, SKY, MINT, (245, 150, 70), LAV]
    decal_col = [WHITE, WHITE, WHITE, WHITE, WHITE, WHITE]
    rng = np.random.default_rng(5)
    y = 0.0
    shapes = ["circle", "triangle", "square", "diamond", "circle", "triangle"]
    for i in range(6):
        y_c = y + s / 2
        dx, dz = rng.uniform(-0.006, 0.006, 2)
        rot = rng.uniform(-14, 14)
        g = b.group(f"Block_{i + 1:02d}", M=T(dx, y_c, dz) @ R(rot, [0, 1, 0]))
        b.add(rbox(s, s, s, 0.009), f"Block_{i + 1:02d}_Cube", mat(f"block_{i}", cols[i], 0.55), g)
        decs = []
        for face in range(4):
            sh = shapes[(i + face) % len(shapes)]
            if sh == "circle":
                d = revolve([(0, 0), (0.018, 0), (0.018, 0.002), (0, 0.002)], 32, axis='z')
            else:
                pts2 = {"triangle": [(-0.019, -0.015), (0.019, -0.015), (0, 0.019)],
                        "square": [(-0.016, -0.016), (0.016, -0.016), (0.016, 0.016), (-0.016, 0.016)],
                        "diamond": [(0, -0.02), (0.02, 0), (0, 0.02), (-0.02, 0)]}[sh]
                d = hull_spheres([(x, yy, zz) for (x, yy) in pts2 for zz in (0.0005, 0.0015)], 0.0015, 1)
            d.apply_translation((0, 0, s / 2 - 0.0002))
            d.apply_transform(R(90 * face, [0, 1, 0]))
            decs.append(d)
        b.add(merge(decs), f"Block_{i + 1:02d}_Decal", mat("block_decal", WHITE, 0.5), g)
        y += s
    # roof block (triangular prism) on top
    g = b.group("Block_07", M=T(rng.uniform(-0.004, 0.004), y + 0.0, 0) @ R(rng.uniform(-10, 10), [0, 1, 0]))
    pr = [(x, yy, z) for (x, yy) in ((-s / 2, 0), (s / 2, 0), (0, s * 0.62)) for z in (-s / 2, s / 2)]
    roof = hull_spheres(np.array(pr) * [0.86, 0.8, 0.86] + [0, 0.009, 0], 0.009)
    roof.apply_translation((0, -roof.bounds[0][1], 0))
    b.add(roof, "Block_07_Roof", mat("block_roof", CORAL, 0.55), g)
    return b


def cardbox():
    b = Builder("box")
    L, Wd, H, t = 0.42, 0.32, 0.28, 0.006
    cm = mat("cardboard", KRAFT, 0.9, double=True)
    b.add(rbox(L, t, Wd, 0.002, (0, t / 2, 0)), "Box_Bottom", cm)
    b.add(rbox(L, H, t, 0.002, (0, H / 2, Wd / 2 - t / 2)), "Box_Wall_Front", cm)
    b.add(rbox(L, H, t, 0.002, (0, H / 2, -Wd / 2 + t / 2)), "Box_Wall_Back", cm)
    b.add(rbox(t, H, Wd - 2 * t, 0.002, (L / 2 - t / 2, H / 2, 0)), "Box_Wall_Right", cm)
    b.add(rbox(t, H, Wd - 2 * t, 0.002, (-L / 2 + t / 2, H / 2, 0)), "Box_Wall_Left", cm)
    fm = mat("cardboard_flap", (212, 168, 115), 0.9, double=True)
    # flaps: pivot node on top edge, flap hangs outward
    for name, M, size, ang, axis in (
            ("Front", T(0, H, Wd / 2), (L - 0.004, t, Wd / 2 - 0.004), 118, [1, 0, 0]),
            ("Back", T(0, H, -Wd / 2) @ R(180, [0, 1, 0]), (L - 0.004, t, Wd / 2 - 0.004), 104, [1, 0, 0]),
            ("Right", T(L / 2, H, 0) @ R(90, [0, 1, 0]), (Wd - 0.004, t, Wd / 2 - 0.02), 125, [1, 0, 0]),
            ("Left", T(-L / 2, H, 0) @ R(-90, [0, 1, 0]), (Wd - 0.004, t, Wd / 2 - 0.02), 98, [1, 0, 0])):
        g = b.group(f"Box_Flap_{name}", M=M @ R(ang, axis))
        b.add(rbox(size[0], size[1], size[2], 0.002, (0, 0, -size[2] / 2)), f"Box_Flap_{name}_Mesh", fm, g)
    b.add(rbox(0.05, 0.0015, Wd + 0.004, 0.0006, (0, -0.0004, 0), 1), "Box_Tape",
          mat("tape", (225, 190, 120), 0.35, alpha=0.9))
    b.add(merge([rbox(0.0015, 0.08, 0.05, 0.0006, (s * (L / 2 + 0.0004), 0.04, 0), 1) for s in (-1, 1)]),
          "Box_Tape_Sides", mat("tape", (225, 190, 120), 0.35, alpha=0.9))
    # simple printed "this side up" arrows on the front
    arrows = []
    for x in (-0.03, 0.03):
        arrows.append(rbox(0.012, 0.05, 0.0012, 0.0005, (x, 0.13, Wd / 2 + 0.0004), 1))
        arrows.append(hull_spheres([(x - 0.018, 0.155, Wd / 2 + 0.0004), (x + 0.018, 0.155, Wd / 2 + 0.0004),
                                    (x, 0.18, Wd / 2 + 0.0004)], 0.0008, 1))
    b.add(merge(arrows), "Box_Print", mat("box_print", (120, 75, 45), 0.9))
    return b


def flashlight():
    b = Builder("flashlight")
    Rh = 0.03
    yc = Rh + 0.001          # axis height so the head rests on the floor
    body = fillet([(0, -0.10), (0.017, -0.10), (0.018, -0.09), (0.018, 0.04), (0.027, 0.075), (0.03, 0.08),
                   (0.03, 0.118), (0.024, 0.122), (0, 0.122)], [0, 0.004, 0.003, 0.004, 0.01, 0.004, 0.003, 0.002, 0], 6)
    m = revolve(body, 48, axis='x')
    b.add(m, "Flashlight_Body", mat("flash_body", SKY, 0.4), M=T(0, yc, 0) )
    rings = []
    for x in np.linspace(-0.07, 0.01, 6):
        rings.append(tube(arc((0, 0, 0), 0.0185, 0, 360, 'zy', 32)[:-1] + [x, 0, 0], 0.0018, 8, closed=True))
    b.add(merge(rings), "Flashlight_Grip", mat("rubber_dark", DARK, 0.9), M=T(0, yc, 0) )
    bez = revolve(fillet([(0.0255, 0.116), (0.0325, 0.116), (0.0325, 0.128), (0.0255, 0.128)], 0.003, 5) .tolist()
                  + [(0.0255, 0.116)], 48, axis='x')
    b.add(bez, "Flashlight_Bezel", mat("flash_bezel", MUSTARD, 0.35, 0.3), M=T(0, yc, 0) )
    # reflector (inside) + lens (separate part named "lens")
    refl = revolve([(0.004, 0.105), (0.025, 0.121), (0.025, 0.1215), (0.0035, 0.1055)], 48, axis='x')
    b.add(refl, "Flashlight_Reflector", mat("chrome", (230, 232, 236), 0.1, 1.0, double=True), M=T(0, yc, 0) )
    lens = revolve(fillet([(0, 0.121), (0.026, 0.121), (0.026, 0.1245), (0, 0.1262)], [0, 0.0008, 0.002, 0], 5), 48, axis='x')
    b.add(lens, "lens", mat("lens_glass", (255, 248, 215), 0.05, alpha=0.75, emissive=[0.0, 0.0, 0.0]),
          M=T(0, yc, 0) )
    bg = b.group("Flashlight_Button", M=T(0, yc, 0)  @ T(0.025, 0.018, 0))
    b.add(rbox(0.022, 0.008, 0.013, 0.004, (0, 0.002, 0)), "Flashlight_Button_Cap", mat("flash_button", CORAL, 0.5), bg)
    loop = spline([(-0.1, 0.0, 0.006), (-0.118, 0.0, 0.009), (-0.13, 0.0, 0.0), (-0.118, 0.0, -0.009), (-0.1, 0.0, -0.006)], 24)
    b.add(round_tube(loop, 0.0022, 10), "Flashlight_Strap", mat("strap", MINT, 0.7), M=T(0, yc, 0) )
    return b


ITEMS = {"stove": stove, "kettle": kettle, "pot": pot, "knife": knife, "iron": iron, "outlet": outlet,
         "wire": wire, "matches": matches, "pills": pills, "tower": tower, "box": cardbox, "flashlight": flashlight}
