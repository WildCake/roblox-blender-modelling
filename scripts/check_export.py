"""Read-only check of a saved Blender export collection against a motion plan."""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

import bpy


def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def component_count(mesh):
    neighbours = [[] for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        neighbours[a].append(b)
        neighbours[b].append(a)
    seen = set()
    count = 0
    for start in range(len(neighbours)):
        if start in seen:
            continue
        count += 1
        stack = [start]
        seen.add(start)
        while stack:
            vertex = stack.pop()
            for other in neighbours[vertex]:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
    return count


def audit_mesh(obj, group, triangle_budget):
    errors = []
    if min(obj.scale) <= 0 or obj.matrix_world.determinant() <= 0:
        errors.append("negative or zero delivery scale")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    try:
        mesh.calc_loop_triangles()
        triangles = len(mesh.loop_triangles)
        if not 0 < triangles <= triangle_budget:
            errors.append("empty mesh or triangle budget exceeded")
        if any(t.area <= 0 for t in mesh.loop_triangles):
            errors.append("zero-area triangles")
        if len(mesh.materials) > 1 or any(p.material_index != 0 for p in mesh.polygons):
            errors.append("multiple or unnormalized delivery material slots")
        uv_count = len(mesh.uv_layers)
        if uv_count > 1 or (group.get("requires_uv", True) and uv_count != 1):
            errors.append("delivery requires a single intended UV set")
        used = {v for polygon in mesh.polygons for v in polygon.vertices}
        if len(used) != len(mesh.vertices):
            errors.append("loose vertices or wire-only geometry")
        components = component_count(mesh)
        if group.get("continuous_surface", False) and components != 1:
            errors.append("designed continuous surface is not welded into one component")
        return {"object": obj.name, "motion_group": group["motion_group"],
                "triangles": triangles, "uv_sets": uv_count,
                "material_slots": len(mesh.materials), "connected_components": components,
                "passed": not errors, "errors": errors}
    finally:
        evaluated.to_mesh_clear()


def audit_plan(plan):
    errors = []
    groups = plan.get("groups")
    if not isinstance(groups, list) or not groups:
        raise ValueError("plan.groups must be a nonempty list")
    budget = plan.get("max_triangles_per_mesh")
    if type(budget) is not int or budget < 1:
        raise ValueError("provide a positive current max_triangles_per_mesh budget")
    names, by_motion = set(), defaultdict(list)
    for group in groups:
        if not isinstance(group, dict):
            raise ValueError("each group must be an object")
        for key in ("object", "motion_group", "motion"):
            if not isinstance(group.get(key), str) or not group[key].strip():
                raise ValueError("each group requires nonempty object, motion_group and motion")
        if group["object"] in names:
            errors.append("duplicate planned object: " + group["object"])
        names.add(group["object"])
        by_motion[group["motion_group"]].append(group)
        if group["motion"] not in {"static", "rotation", "translation", "deformation"}:
            errors.append("unknown motion: " + group["object"])
        evidence = group.get("motion_evidence")
        if group["motion"] != "static" and not (isinstance(evidence, str) and evidence.strip()):
            errors.append("missing independent-motion evidence: " + group["object"])
        for flag in ("requires_uv", "continuous_surface"):
            if flag in group and type(group[flag]) is not bool:
                raise ValueError(flag + " must be a Boolean")
    for motion, members in by_motion.items():
        if len(members) > 1 and not all(
            g.get("split_reason") in {"platform_limit", "useful_collision_opening"}
            and isinstance(g.get("split_evidence"), str) and g["split_evidence"].strip()
            for g in members
        ):
            errors.append("unjustified segmentation of motion group: " + motion)
    collection = bpy.data.collections.get(plan.get("export_collection", ""))
    if collection is None:
        errors.append("declared export collection is missing")
        return {"passed": False, "errors": errors, "groups": []}
    objects = {o.name: o for o in collection.all_objects if o.type == "MESH"}
    unexpected = sorted(set(objects) - names)
    missing = sorted(names - set(objects))
    if unexpected:
        errors.append("unplanned exported mesh objects: " + ", ".join(unexpected))
    if missing:
        errors.append("missing planned mesh objects: " + ", ".join(missing))
    unsupported = [o.name for o in collection.all_objects if o.type not in {"MESH", "ARMATURE", "EMPTY"}]
    if unsupported:
        errors.append("non-asset objects in export collection: " + ", ".join(sorted(unsupported)))
    reports = [audit_mesh(objects[g["object"]], g, budget) for g in groups if g["object"] in objects]
    return {"passed": not errors and all(r["passed"] for r in reports), "errors": errors,
            "planned_meshes": len(names), "actual_meshes": len(objects),
            "declared_motion_groups": len(by_motion), "groups": reports,
            "unverified": ["actual_kinematics", "geometry_equivalence", "installed_mesh_ids",
                           "native_collision", "mass_ownership", "roblox_import"]}


def main():
    if not bpy.app.background:
        raise RuntimeError("run saved-file checks in an isolated background Blender process")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blend", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    args.blend, args.plan, args.out = (p.resolve() for p in (args.blend, args.plan, args.out))
    if args.out in {args.blend, args.plan}:
        parser.error("report must not overwrite the source or plan")
    source_hash, plan_hash = file_hash(args.blend), file_hash(args.plan)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(args.blend))
    report = audit_plan(plan)
    if file_hash(args.blend) != source_hash or file_hash(args.plan) != plan_hash:
        raise RuntimeError("source or plan changed during inspection; discard this report")
    report.update({"source": str(args.blend), "source_sha256": source_hash,
                   "plan_sha256": plan_hash, "blender_version": bpy.app.version_string})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Export gate {'PASS' if report['passed'] else 'FAIL'}: {args.out}")
    if not report["passed"]:
        raise RuntimeError("prepared export gate failed; inspect the JSON report")


if __name__ == "__main__":
    main()
