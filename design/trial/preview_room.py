import trimesh, numpy as np, sys
from render import render
import room, items
b, A = room.build()
sc = b.scene
for k, M in A.items():
    ib = items.ITEMS[k]()
    for node in ib.scene.graph.nodes_geometry:
        Mi, g = ib.scene.graph[node]
        sc.add_geometry(ib.scene.geometry[g], node_name='P_'+node, geom_name='P_'+g, transform=M @ Mi)
# hide ceiling + front wall for the overview
for n in ['Ceiling','Wall_Front']:
    sc.graph.transforms.remove_node(n) if False else None
sc.delete_geometry(['Ceiling_mesh','Wall_Front_Surface_mesh','Wall_Front_Baseboard_mesh','Wall_Front_Cornice_mesh'])
views = {
 'room_overview': ((1.2, 4.2, 5.6), (-0.3, 0.8, -0.8), 60),
 'room_kitchen': ((-0.6, 1.7, 0.2), (-2.6, 1.0, -1.9), 55),
 'room_window': ((1.4, 1.5, 0.4), (-0.2, 1.0, -2.6), 55),
 'room_door': ((1.8, 1.6, -1.2), (-2.8, 1.0, 1.4), 60),
}
for name,(e,t,fov) in views.items():
    if len(sys.argv)>1 and name not in sys.argv[1:]: continue
    render(sc, e, t, (1000, 700), fov=fov, path=f'prev/{name}.png'); print(name)
