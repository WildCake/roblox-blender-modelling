"""Read-only physical UV metrics. Run with Blender --background --python."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy


def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def triangle_metrics(points, uvs, texture_size):
    """Return area, pixel density and singular-value ratio in the tangent plane."""
    edge1, edge2 = points[1] - points[0], points[2] - points[0]
    length = edge1.length
    double_area = edge1.cross(edge2).length
    if length <= 0 or double_area <= 0:
        raise ValueError("zero-area geometry")
    x2 = edge2.dot(edge1) / length
    y2 = double_area / length
    width, height = texture_size
    u1 = (uvs[1][0] - uvs[0][0]) * width
    v1 = (uvs[1][1] - uvs[0][1]) * height
    u2 = (uvs[2][0] - uvs[0][0]) * width
    v2 = (uvs[2][1] - uvs[0][1]) * height
    a, c = u1 / length, v1 / length
    b, d = (u2 - a * x2) / y2, (v2 - c * x2) / y2
    determinant = a * d - b * c
    area = double_area / 2
    if determinant == 0:
        return area, 0.0, None, False
    diagonal1, diagonal2 = a * a + c * c, b * b + d * d
    cross = a * b + c * d
    largest_eigenvalue = (diagonal1 + diagonal2 + math.hypot(
        diagonal1 - diagonal2, 2 * cross
    )) / 2
    density = math.sqrt(abs(determinant))
    stretch = largest_eigenvalue / abs(determinant)
    if not all(math.isfinite(v) for v in (area, density, stretch)):
        raise ValueError("nonfinite mapping metric")
    return area, density, max(1.0, stretch), determinant < 0


def audit_object(obj, texture_size, meters_per_unit, target_density,
                 density_tolerance, max_stretch, uv_layer=None,
                 constant_attribute=None):
    report = {"object": obj.name, "errors": [], "failures": {}, "examples": []}
    if obj.type != "MESH":
        report["errors"].append("selected object is not a mesh")
        report["passed"] = False
        return report
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    try:
        layer = mesh.uv_layers.get(uv_layer) if uv_layer else (
            mesh.uv_layers[0] if len(mesh.uv_layers) == 1 else None
        )
        if layer is None:
            report["errors"].append("missing requested UV layer or ambiguous UV sets")
            report["passed"] = False
            return report
        constant = mesh.attributes.get(constant_attribute) if constant_attribute else None
        if constant_attribute and (constant is None or constant.domain != "FACE"
                                   or constant.data_type != "BOOLEAN"):
            report["errors"].append("constant-colour attribute must be BOOLEAN on FACE domain")
            report["passed"] = False
            return report
        mesh.calc_loop_triangles()
        if not mesh.loop_triangles:
            report["errors"].append("empty evaluated mesh")
            report["passed"] = False
            return report
        result = measure_triangles(mesh, evaluated.matrix_world, layer, constant,
                                   texture_size, meters_per_unit, target_density,
                                   density_tolerance, max_stretch)
        report.update(result)
        report["uv_layer"] = layer.name
        report["passed"] = not report["failures"] and not report["errors"]
        return report
    finally:
        evaluated.to_mesh_clear()


def measure_triangles(mesh, matrix, layer, constant, texture_size,
                      meters_per_unit, target_density, tolerance, max_stretch):
    failures, examples = {}, []
    density_values, stretch_values = [], []
    surface_area = textured_area = pixel_area = 0.0
    mirrored = constant_count = failing_triangles = 0
    lower, upper = target_density * (1 - tolerance), target_density * (1 + tolerance)
    for triangle in mesh.loop_triangles:
        points = [(matrix @ mesh.vertices[i].co) * meters_per_unit for i in triangle.vertices]
        uvs = [tuple(layer.data[i].uv) for i in triangle.loops]
        reasons = []
        if not all(math.isfinite(v) for p in points for v in p):
            reasons.append("nonfinite_geometry")
        if not all(math.isfinite(v) for uv in uvs for v in uv):
            reasons.append("nonfinite_uv")
        elif any(v < 0 or v > 1 for uv in uvs for v in uv):
            reasons.append("uv_outside_0_1")
        uniform_colour = bool(constant and constant.data[triangle.polygon_index].value)
        if "nonfinite_geometry" not in reasons and "nonfinite_uv" not in reasons:
            try:
                area, density, stretch, is_mirrored = triangle_metrics(points, uvs, texture_size)
                surface_area += area
                if uniform_colour:
                    constant_count += 1
                else:
                    textured_area += area
                    if stretch is None:
                        reasons.append("collapsed_textured_uv")
                    else:
                        density_values.append(density)
                        stretch_values.append(stretch)
                        pixel_area += area * density * density
                        mirrored += int(is_mirrored)
                        if not lower <= density <= upper:
                            reasons.append("density_out_of_range")
                        if stretch > max_stretch:
                            reasons.append("directional_stretch")
            except ValueError as error:
                reasons.append(str(error))
        if reasons:
            failing_triangles += 1
            for reason in reasons:
                failures[reason] = failures.get(reason, 0) + 1
            if len(examples) < 12:
                examples.append({"polygon": triangle.polygon_index,
                                 "vertices": list(triangle.vertices), "reasons": reasons})
    return {
        "triangles": len(mesh.loop_triangles), "surface_area_m2": surface_area,
        "textured_surface_area_m2": textured_area,
        "constant_colour_triangles": constant_count, "mirrored_triangles": mirrored,
        "density_min_px_m": min(density_values) if density_values else None,
        "density_max_px_m": max(density_values) if density_values else None,
        "area_weighted_density_px_m": math.sqrt(pixel_area / textured_area) if textured_area else None,
        "stretch_max": max(stretch_values) if stretch_values else None,
        "failing_triangles": failing_triangles, "failures": failures, "examples": examples,
    }


def main():
    if not bpy.app.background:
        raise RuntimeError("run saved-file checks in an isolated background Blender process")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blend", type=Path, required=True)
    parser.add_argument("--objects", nargs="+", required=True)
    parser.add_argument("--uv-layer")
    parser.add_argument("--texture-size", nargs=2, type=int, required=True)
    parser.add_argument("--meters-per-unit", type=float, required=True)
    parser.add_argument("--target-density", type=float, required=True)
    parser.add_argument("--density-tolerance", type=float, required=True)
    parser.add_argument("--max-stretch", type=float, required=True)
    parser.add_argument("--constant-attribute")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    numeric = (args.meters_per_unit, args.target_density, args.density_tolerance, args.max_stretch)
    if (not all(math.isfinite(v) for v in numeric) or min(args.texture_size) < 1
            or args.meters_per_unit <= 0 or args.target_density <= 0
            or not 0 <= args.density_tolerance < 1 or args.max_stretch < 1):
        parser.error("invalid texture size, physical scale or UV thresholds")
    if len(set(args.objects)) != len(args.objects):
        parser.error("duplicate selected object names")
    args.blend, args.out = args.blend.resolve(), args.out.resolve()
    if args.out == args.blend:
        parser.error("report path must not overwrite the source")
    source_hash = file_hash(args.blend)
    bpy.ops.wm.open_mainfile(filepath=str(args.blend))
    reports = []
    for name in args.objects:
        obj = bpy.data.objects.get(name)
        if obj is None:
            reports.append({"object": name, "passed": False, "errors": ["object missing"]})
        else:
            reports.append(audit_object(obj, args.texture_size, args.meters_per_unit,
                                        args.target_density, args.density_tolerance,
                                        args.max_stretch, args.uv_layer, args.constant_attribute))
    if file_hash(args.blend) != source_hash:
        raise RuntimeError("source changed while being inspected; discard this report")
    result = {"passed": all(r["passed"] for r in reports), "source": str(args.blend),
              "source_sha256": source_hash, "blender_version": bpy.app.version_string,
              "frame": bpy.context.scene.frame_current,
              "settings": {"texture_size": args.texture_size, "meters_per_unit": args.meters_per_unit,
                           "target_density_px_m": args.target_density,
                           "density_tolerance": args.density_tolerance,
                           "max_stretch": args.max_stretch, "constant_attribute": args.constant_attribute},
              "objects": reports,
              "unverified": ["island_overlap", "seam_appearance", "artwork_orientation",
                             "padding_and_filtering", "normal_maps", "roblox_import"]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"UV gate {'PASS' if result['passed'] else 'FAIL'}: {args.out}")
    if not result["passed"]:
        raise RuntimeError("configured UV quality gate failed; inspect the JSON report")


if __name__ == "__main__":
    main()
