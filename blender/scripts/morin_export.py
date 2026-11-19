"""morin_export.py — script di export FBX ufficiale del progetto "Morin Rush".

Preset verificato in UEFN (docs/scala.md, giro 3):
    FBX_SCALE_NONE + bake_space_transform=True + axis_forward='-Y', axis_up='Z'
    + rotazione di -90 gradi attorno a Z applicata SOLO durante l'export.
Risultato in UEFN: Blender +X -> UE +X, Blender +Y -> UE -Y, Blender +Z -> UE +Z,
1 m = 100 uu. Regola posizioni: UE = (B_X*100, -B_Y*100, B_Z*100); yaw UE = -rotZ Blender.

Cosa fa export_fbx():
  1. Controlli bloccanti: Object Mode, unita METRIC con scale_length 1.0, percorso .fbx dentro
     <progetto>/exports/, file non gia esistente (salvo overwrite=True), in modo "asset" radici
     con origine in (0,0,0) world.
  2. Avvisi: nomi non SM_/UCX_, scala diversa da 1, mesh senza UCX, UCX orfani, vincoli/animazioni.
  3. Aggiunge in automatico gli UCX_<Nome>_NN degli oggetti esportati presenti nella scena.
  4. Premoltiplica matrix_world delle sole radici (oggetti senza parent nell'insieme esportato)
     per Rz(-90), esporta, e in un blocco try/finally ripristina le trasformazioni originali
     (location / rotazione / scala esatte), visibilita, selezione e oggetto attivo.
     Nessun transform_apply, nessun operatore che lascia passi di undo. Il .blend risulta
     "dirty" (sono state toccate proprieta) ma i dati tornano identici.
  5. Report (dict + stampa): file, byte, oggetti, triangoli per mesh valutati con i
     modificatori, confronto con i budget di CLAUDE.md §4, bounding box in metri e in uu UE.

Modi:
  mode="asset"  asset istanziati (palma, bitta, ponte...): le radici devono stare in (0,0,0)
                world, altrimenti errore e nessuna modifica. Ruota attorno all'origine.
  mode="scene"  blockout gia posizionati sull'origine comune del progetto (imbocco del ponte):
                ruota tutto attorno all'origine world (0,0,0), le posizioni restano quelle reali.

Uso via MCP (import come modulo):
    import sys, importlib
    p = r"C:/Users/matti/Documents/LaSpeziaFortnite/LaSpezia-Fortnite/blender/scripts"
    if p not in sys.path: sys.path.append(p)
    import morin_export; importlib.reload(morin_export)
    rep = morin_export.export_fbx([bpy.data.objects["SM_Morin_PalmaA"]],
                                  "//../exports/vegetazione/SM_Morin_PalmaA.fbx", mode="asset")

Uso via exec del file o dal Text Editor (apri il file e Run Script, poi nella console):
    exec(open(r".../blender/scripts/morin_export.py", encoding="utf-8").read())
    export_selected(r".../exports/blockout/SM_Blockout_Ponte.fbx", mode="scene")

I percorsi possono essere assoluti o relativi al .blend ("//..."). Gli errori bloccanti
sollevano MorinExportError e non modificano nulla.
"""

import math
import os
import re

import bpy
from mathutils import Matrix, Vector

__all__ = ["export_fbx", "export_selected", "MorinExportError", "BUDGETS", "FBX_PRESET"]

# --------------------------------------------------------------------------------------------
# Costanti di progetto
# --------------------------------------------------------------------------------------------

# Budget triangoli (CLAUDE.md §4). Parola chiave nel nome -> budget. Il primo match vince.
BUDGETS = (
    # Aggiornati il 2026-11-19 ai budget LOD0 PC/console di CLAUDE.md §4.
    ("Ponte", 120000),
    ("Battello", 30000),
    ("Palma", 10000),
    ("Bitta", 4000),       # prop
    ("Scaletta", 4000),    # prop
    ("Banchina", 2000),    # modulo banchina
)

# Rotazione applicata solo in export (docs/scala.md, giro 3).
EXPORT_ROTATION = Matrix.Rotation(math.radians(-90.0), 4, "Z")

# Parametri FBX, tutti espliciti (CLAUDE.md §4 + docs/scala.md).
FBX_PRESET = dict(
    use_selection=True,
    use_visible=False,
    use_active_collection=False,
    batch_mode="OFF",
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options="FBX_SCALE_NONE",
    use_space_transform=True,
    bake_space_transform=True,
    axis_forward="-Y",
    axis_up="Z",
    use_mesh_modifiers=True,
    use_mesh_modifiers_render=True,
    mesh_smooth_type="FACE",
    use_triangles=False,
    use_tspace=False,
    use_custom_props=False,
    add_leaf_bones=False,
    bake_anim=False,
    path_mode="COPY",
    embed_textures=True,
    use_metadata=True,
    check_existing=False,
)

ORIGIN_TOL = 1e-4      # m, tolleranza per "origine in (0,0,0)"
SCALE_TOL = 1e-5
UCX_RE = re.compile(r"^UCX_(?P<base>.+)_(?P<num>\d{2})$")


class MorinExportError(Exception):
    """Errore bloccante: l'export non e stato eseguito e la scena non e stata modificata."""


# --------------------------------------------------------------------------------------------
# Utilita
# --------------------------------------------------------------------------------------------

def _find_project_root():
    """Cartella che contiene CLAUDE.md: prima dal percorso dello script, poi dal .blend."""
    starts = []
    try:
        starts.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    if bpy.data.filepath:
        starts.append(os.path.dirname(bpy.data.filepath))
    for start in starts:
        d = start
        for _ in range(8):
            if os.path.isfile(os.path.join(d, "CLAUDE.md")) and os.path.isdir(os.path.join(d, "exports")):
                return d
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    return None


def _budget_for(name):
    for key, value in BUDGETS:
        if key.lower() in name.lower():
            return key, value
    return None, None


def _is_ucx(obj):
    return obj.name.startswith("UCX_")


def _ucx_for(name, scene_objects):
    """UCX_<name>_NN presenti nella scena per il mesh <name>."""
    out = []
    for o in scene_objects:
        m = UCX_RE.match(o.name)
        if m and m.group("base") == name and o.type == "MESH":
            out.append(o)
    return sorted(out, key=lambda o: o.name)


def _tri_count(obj, depsgraph):
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    try:
        mesh.calc_loop_triangles()
        return len(mesh.loop_triangles)
    finally:
        ev.to_mesh_clear()


def _world_bbox(objs, depsgraph):
    """Bounding box world (metri) degli oggetti valutati, coordinate Blender."""
    lo = Vector((math.inf,) * 3)
    hi = Vector((-math.inf,) * 3)
    for o in objs:
        ev = o.evaluated_get(depsgraph)
        mw = ev.matrix_world
        for c in ev.bound_box:
            p = mw @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
    if lo.x == math.inf:
        return None
    return {
        "min": tuple(round(v, 4) for v in lo),
        "max": tuple(round(v, 4) for v in hi),
        "size": tuple(round(h - l, 4) for l, h in zip(lo, hi)),
        # Previsione in UE (uu) con la regola UE = (X*100, -Y*100, Z*100)
        "ue_uu": {
            "X": (round(lo.x * 100, 2), round(hi.x * 100, 2)),
            "Y": (round(-hi.y * 100, 2), round(-lo.y * 100, 2)),
            "Z": (round(lo.z * 100, 2), round(hi.z * 100, 2)),
        },
    }


def _snapshot_transform(o):
    return dict(
        location=o.location.copy(),
        rotation_mode=o.rotation_mode,
        rotation_euler=o.rotation_euler.copy(),
        rotation_quaternion=o.rotation_quaternion.copy(),
        rotation_axis_angle=tuple(o.rotation_axis_angle),
        scale=o.scale.copy(),
    )


def _restore_transform(o, s):
    o.rotation_mode = s["rotation_mode"]
    o.location = s["location"]
    o.rotation_euler = s["rotation_euler"]
    o.rotation_quaternion = s["rotation_quaternion"]
    o.rotation_axis_angle = s["rotation_axis_angle"]
    o.scale = s["scale"]


def _resolve_path(filepath, project_root):
    path = bpy.path.abspath(filepath) if filepath.startswith("//") else filepath
    path = os.path.normpath(os.path.abspath(path))
    if not path.lower().endswith(".fbx"):
        raise MorinExportError(f"Il percorso deve terminare con .fbx: {path}")
    if project_root is None:
        raise MorinExportError("Cartella di progetto non trovata (nessun CLAUDE.md + exports/ risalendo "
                               "dallo script o dal .blend). Passa project_root=...")
    exports = os.path.normcase(os.path.join(os.path.normpath(project_root), "exports"))
    if os.path.commonpath([os.path.normcase(path), exports]) != exports:
        raise MorinExportError(f"Il file deve stare dentro {exports}: {path}")
    return path


# --------------------------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------------------------

def export_fbx(objects, filepath, mode="asset", object_types=frozenset({"MESH"}),
               include_ucx=True, overwrite=False, project_root=None, verbose=True):
    """Esporta `objects` (+ i loro UCX_) in `filepath` col preset del progetto.

    objects       lista di bpy.types.Object (i figli NON vengono aggiunti in automatico).
    filepath      .fbx dentro <progetto>/exports/ (assoluto o "//relativo al .blend").
    mode          "asset" (radici in 0,0,0) oppure "scene" (blockout gia posizionato).
    object_types  tipi FBX esportati, default {'MESH'}; es. {'MESH','EMPTY'}.
    include_ucx   aggiunge gli UCX_<Nome>_NN presenti nella scena.
    overwrite     False: errore se il file esiste gia (CLAUDE.md §6).
    Ritorna il dict di report. Solleva MorinExportError per gli errori bloccanti.
    """
    ctx = bpy.context
    scene = ctx.scene
    view_layer = ctx.view_layer
    warnings = []

    # ---------------- controlli bloccanti (nessuna modifica alla scena) ----------------
    if mode not in ("asset", "scene"):
        raise MorinExportError(f"mode deve essere 'asset' o 'scene', non {mode!r}")
    if ctx.mode != "OBJECT":
        raise MorinExportError(f"Serve Object Mode (ora: {ctx.mode}).")
    us = scene.unit_settings
    if us.system != "METRIC" or abs(us.scale_length - 1.0) > 1e-9:
        raise MorinExportError(f"Unita della scena non conformi: system={us.system}, "
                               f"scale_length={us.scale_length} (servono METRIC e 1.0).")
    object_types = set(object_types)
    valid_types = {e.identifier for e in
                   bpy.ops.export_scene.fbx.get_rna_type().properties["object_types"].enum_items}
    if not object_types or not object_types <= valid_types:
        raise MorinExportError(f"object_types non valido: {object_types} (validi: {valid_types})")

    project_root = project_root or _find_project_root()
    path = _resolve_path(filepath, project_root)
    if os.path.exists(path) and not overwrite:
        raise MorinExportError(f"Il file esiste gia, non lo sovrascrivo: {path} (overwrite=True per forzare)")

    objs = []
    for o in objects or []:
        if isinstance(o, str):
            o = bpy.data.objects.get(o)
        if o is None:
            raise MorinExportError("Oggetto inesistente nella lista da esportare.")
        if o not in objs:
            objs.append(o)
    if not objs:
        raise MorinExportError("Nessun oggetto da esportare.")

    scene_objs = list(scene.objects)
    for o in objs:
        if o.name not in scene.objects:
            raise MorinExportError(f"{o.name} non e nella scena attiva.")
        if o.type not in object_types:
            warnings.append(f"{o.name}: tipo {o.type} non in object_types {sorted(object_types)}, "
                            f"non sara esportato.")

    # UCX automatici
    if include_ucx:
        for o in list(objs):
            if o.type == "MESH" and not _is_ucx(o):
                for u in _ucx_for(o.name, scene_objs):
                    if u not in objs:
                        objs.append(u)
    names = {o.name for o in objs}
    meshes = [o for o in objs if o.type == "MESH" and not _is_ucx(o) and o.type in object_types]
    ucxs = [o for o in objs if o.type == "MESH" and _is_ucx(o)]
    for o in meshes:
        if not any(UCX_RE.match(u.name) and UCX_RE.match(u.name).group("base") == o.name for u in ucxs):
            warnings.append(f"{o.name}: nessun UCX_{o.name}_NN, in UEFN niente collisione semplice dedicata.")
    for u in ucxs:
        m = UCX_RE.match(u.name)
        if not m:
            warnings.append(f"{u.name}: nome UCX non conforme (atteso UCX_<Mesh>_NN).")
        elif m.group("base") not in names:
            warnings.append(f"{u.name}: il mesh {m.group('base')} non e nell'export (UCX orfano).")
        if u.modifiers:
            warnings.append(f"{u.name}: UCX con modificatori, verifica che resti convesso.")

    # naming, scala, vincoli, animazioni
    for o in objs:
        if o.type == "MESH" and not (o.name.startswith("SM_") or _is_ucx(o)):
            warnings.append(f"{o.name}: nome non conforme (atteso SM_... o UCX_...).")
        if any(abs(s - 1.0) > SCALE_TOL for s in o.scale):
            warnings.append(f"{o.name}: scala non applicata {tuple(round(s, 4) for s in o.scale)}.")
        if o.constraints:
            warnings.append(f"{o.name}: ha vincoli, la rotazione di export potrebbe non applicarsi correttamente.")
        if o.animation_data and (o.animation_data.action or o.animation_data.drivers):
            warnings.append(f"{o.name}: ha animazioni o driver (bake_anim=False).")

    roots = [o for o in objs if o.parent is None or o.parent.name not in names]

    if mode == "asset":
        bad = [(o.name, tuple(round(v, 5) for v in o.matrix_world.translation))
               for o in roots if o.matrix_world.translation.length > ORIGIN_TOL]
        if bad:
            raise MorinExportError("mode='asset': la radice dell'asset deve avere origine in (0,0,0) world. "
                                   f"Fuori origine: {bad}. Sposta l'oggetto (o la sua origine) "
                                   "oppure usa mode='scene'.")
        ident = Matrix.Identity(3)
        for o in roots:
            r = o.matrix_world.to_3x3().normalized()
            if any(abs(r[i][j] - ident[i][j]) > 1e-6 for i in range(3) for j in range(3)):
                warnings.append(f"{o.name}: asset con rotazione non nulla; l'istanza in UEFN la eredita.")

    # oggetti nascosti: vanno resi visibili per poterli selezionare
    for o in objs:
        if not o.visible_get(view_layer=view_layer) and not (o.hide_get(view_layer=view_layer) or o.hide_viewport):
            raise MorinExportError(f"{o.name} non e visibile (collezione esclusa o nascosta): "
                                   "riattivala prima dell'export.")

    depsgraph = ctx.evaluated_depsgraph_get()
    tris = {o.name: _tri_count(o, depsgraph) for o in objs if o.type == "MESH"}
    bbox_blender = _world_bbox(meshes, depsgraph)

    # ---------------- stato da ripristinare ----------------
    prev_selected = [o for o in view_layer.objects if o.select_get(view_layer=view_layer)]
    prev_active = view_layer.objects.active
    prev_hide = {o.name: (o.hide_get(view_layer=view_layer), o.hide_viewport) for o in objs}
    prev_tf = {o.name: _snapshot_transform(o) for o in roots}
    was_dirty = bpy.data.is_dirty

    result = None
    error = None
    try:
        for o in objs:
            if o.hide_viewport:
                o.hide_viewport = False
            if o.hide_get(view_layer=view_layer):
                o.hide_set(False, view_layer=view_layer)
        for o in view_layer.objects:
            if o.select_get(view_layer=view_layer):
                o.select_set(False, view_layer=view_layer)
        for o in objs:
            o.select_set(True, view_layer=view_layer)
        view_layer.objects.active = objs[0]

        for o in roots:
            o.matrix_world = EXPORT_ROTATION @ o.matrix_world
        view_layer.update()

        os.makedirs(os.path.dirname(path), exist_ok=True)
        kwargs = dict(FBX_PRESET)
        kwargs["object_types"] = object_types
        result = bpy.ops.export_scene.fbx(filepath=path, **kwargs)
    except Exception as exc:  # ripristino garantito dal finally, poi rilancio
        error = exc
    finally:
        for o in roots:
            _restore_transform(o, prev_tf[o.name])
        for o in objs:
            h, hv = prev_hide[o.name]
            if o.hide_viewport != hv:
                o.hide_viewport = hv
            if o.hide_get(view_layer=view_layer) != h:
                o.hide_set(h, view_layer=view_layer)
        for o in view_layer.objects:
            want = o in prev_selected
            if o.select_get(view_layer=view_layer) != want:
                o.select_set(want, view_layer=view_layer)
        view_layer.objects.active = prev_active
        view_layer.update()

    if error is not None:
        raise MorinExportError(f"Export fallito, scena ripristinata: {error!r}") from error
    if result != {"FINISHED"} or not os.path.isfile(path):
        raise MorinExportError(f"Export non completato ({result}), scena ripristinata.")

    # ---------------- report ----------------
    per_mesh = []
    for o in objs:
        if o.type != "MESH":
            continue
        key, budget = (None, None) if _is_ucx(o) else _budget_for(o.name)
        per_mesh.append(dict(
            name=o.name,
            role="collisione" if _is_ucx(o) else "mesh",
            tris=tris[o.name],
            budget=budget,
            budget_key=key,
            within_budget=None if budget is None else tris[o.name] <= budget,
        ))
    visible_tris = sum(m["tris"] for m in per_mesh if m["role"] == "mesh")
    fkey, fbudget = _budget_for(os.path.basename(path))
    for m in per_mesh:
        if m["within_budget"] is False:
            warnings.append(f"{m['name']}: {m['tris']} tri oltre il budget {m['budget']} ({m['budget_key']}).")
    if fbudget is not None and visible_tris > fbudget:
        warnings.append(f"File: {visible_tris} tri visibili oltre il budget {fbudget} ({fkey}).")

    report = dict(
        file=path,
        bytes=os.path.getsize(path),
        mode=mode,
        objects=[o.name for o in objs],
        roots=[o.name for o in roots],
        meshes=per_mesh,
        tris_visible_total=visible_tris,
        file_budget=fbudget,
        file_budget_key=fkey,
        bbox_m=bbox_blender,
        warnings=warnings,
        is_dirty_before=was_dirty,
        is_dirty_after=bpy.data.is_dirty,
        preset=dict(FBX_PRESET, object_types=sorted(object_types), export_rotation_z_deg=-90.0),
    )
    if verbose:
        _print_report(report)
    return report


def export_selected(filepath, mode="asset", **kwargs):
    """Esporta gli oggetti selezionati (+ UCX) con export_fbx()."""
    sel = list(bpy.context.selected_objects)
    if not sel:
        raise MorinExportError("Nessun oggetto selezionato.")
    return export_fbx(sel, filepath, mode=mode, **kwargs)


def _print_report(r):
    print("=" * 72)
    print(f"[morin_export] {r['file']}  ({r['bytes']} byte, mode={r['mode']})")
    for m in r["meshes"]:
        b = "" if m["budget"] is None else f"  budget {m['budget']} ({m['budget_key']}): " \
                                           f"{'OK' if m['within_budget'] else 'SUPERATO'}"
        print(f"  {m['name']:<40} {m['role']:<10} {m['tris']:>7} tri{b}")
    fb = "" if r["file_budget"] is None else f" / budget file {r['file_budget']}"
    print(f"  Totale tri visibili: {r['tris_visible_total']}{fb}")
    bb = r["bbox_m"]
    if bb:
        print(f"  BBox Blender (m): min {bb['min']} max {bb['max']} size {bb['size']}")
        print(f"  BBox prevista UE (uu): {bb['ue_uu']}")
    for w in r["warnings"]:
        print(f"  AVVISO: {w}")
    print(f"  is_dirty prima/dopo: {r['is_dirty_before']} / {r['is_dirty_after']}")
    print("=" * 72)
