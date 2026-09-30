"""Numerical fixtures only; requires an isolated background Blender process."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import bpy

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import check_export
import uv_metrics

SQUARE_UV = [(0, 0), (0.25, 0), (0.25, 0.25), (0, 0.25)]


def make_quad(name="Body", uvs=SQUARE_UV):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [], [(0, 1, 2, 3)])
    mesh.update()
    layer = mesh.uv_layers.new(name="UVMap")
    for loop in mesh.loops:
        layer.data[loop.index].uv = uvs[loop.vertex_index]
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections["EXPORT"].objects.link(obj)
    return obj


def measure(obj, **changes):
    settings = dict(texture_size=(256, 256), meters_per_unit=1,
                    target_density=64, density_tolerance=0.05,
                    max_stretch=1.5, uv_layer="UVMap")
    settings.update(changes)
    bpy.context.view_layer.update()
    return uv_metrics.audit_object(obj, **settings)


def plan_for(*names, continuous=False):
    return {"export_collection": "EXPORT", "max_triangles_per_mesh": 20000,
            "groups": [{"object": name, "motion_group": name, "motion": "static",
                        "continuous_surface": continuous} for name in names]}


class Checks(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        collection = bpy.data.collections.new("EXPORT")
        bpy.context.scene.collection.children.link(collection)

    def test_uniform_density(self):
        result = measure(make_quad())
        self.assertTrue(result["passed"], result)
        self.assertAlmostEqual(result["area_weighted_density_px_m"], 64, places=4)
        self.assertAlmostEqual(result["stretch_max"], 1, places=4)

    def test_area_preserving_stretch_is_rejected(self):
        stretched = [(0, 0), (0.5, 0), (0.5, 0.125), (0, 0.125)]
        result = measure(make_quad(uvs=stretched))
        self.assertAlmostEqual(result["area_weighted_density_px_m"], 64, places=4)
        self.assertAlmostEqual(result["stretch_max"], 4, places=4)
        self.assertFalse(result["passed"])
        self.assertIn("directional_stretch", result["failures"])

    def test_actual_world_scale_changes_density(self):
        obj = make_quad()
        obj.scale = (2, 2, 2)
        result = measure(obj)
        self.assertAlmostEqual(result["area_weighted_density_px_m"], 32, places=4)
        self.assertIn("density_out_of_range", result["failures"])
        self.assertTrue(measure(obj, target_density=32)["passed"])

    def test_physical_unit_conversion_changes_density(self):
        result = measure(make_quad(), meters_per_unit=0.5, target_density=128)
        self.assertTrue(result["passed"], result)
        self.assertAlmostEqual(result["area_weighted_density_px_m"], 128, places=4)

    def test_rectangular_texture_needs_directional_correction(self):
        obj = make_quad()
        result = measure(obj, texture_size=(512, 128))
        self.assertAlmostEqual(result["area_weighted_density_px_m"], 64, places=4)
        self.assertFalse(result["passed"])
        for loop in obj.data.loops:
            u, v = SQUARE_UV[loop.vertex_index]
            obj.data.uv_layers[0].data[loop.index].uv = (u / 2, v * 2)
        self.assertTrue(measure(obj, texture_size=(512, 128))["passed"])

    def test_collapsed_uv_requires_explicit_uniform_colour(self):
        obj = make_quad(uvs=[(0.25, 0.25)] * 4)
        self.assertIn("collapsed_textured_uv", measure(obj)["failures"])
        attribute = obj.data.attributes.new(name="UniformColour", type="BOOLEAN", domain="FACE")
        attribute.data[0].value = True
        result = measure(obj, constant_attribute="UniformColour")
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["constant_colour_triangles"], 2)

    def test_missing_and_outside_uvs_fail(self):
        obj = make_quad()
        obj.data.uv_layers[0].data[0].uv = (1.1, 0)
        self.assertIn("uv_outside_0_1", measure(obj)["failures"])
        obj.data.uv_layers.remove(obj.data.uv_layers[0])
        self.assertFalse(measure(obj)["passed"])

    def test_empty_geometry_fails(self):
        mesh = bpy.data.meshes.new("Empty")
        mesh.uv_layers.new(name="UVMap")
        obj = bpy.data.objects.new("Empty", mesh)
        bpy.data.collections["EXPORT"].objects.link(obj)
        self.assertFalse(measure(obj)["passed"])

    def test_extra_export_object_fails(self):
        make_quad()
        make_quad("UnexpectedBolt")
        result = check_export.audit_plan(plan_for("Body"))
        self.assertFalse(result["passed"])
        self.assertTrue(any("unplanned" in e for e in result["errors"]))

    def test_same_motion_owner_segmentation_fails(self):
        make_quad()
        make_quad("BodySegment")
        plan = plan_for("Body", "BodySegment")
        for group in plan["groups"]:
            group["motion_group"] = "body"
        result = check_export.audit_plan(plan)
        self.assertFalse(result["passed"])
        self.assertTrue(any("unjustified segmentation" in e for e in result["errors"]))
        for group in plan["groups"]:
            group.update(split_reason="platform_limit", split_evidence="Reviewed limit-specific partition")
        self.assertTrue(check_export.audit_plan(plan)["passed"])

    def test_unwelded_continuous_surface_fails(self):
        obj = make_quad("Road")
        points = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                  (1, 0, 0), (2, 0, 0), (2, 1, 0), (1, 1, 0)]
        obj.data.clear_geometry()
        obj.data.from_pydata(points, [], [(0, 1, 2, 3), (4, 5, 6, 7)])
        obj.data.uv_layers.new(name="UVMap")
        result = check_export.audit_plan(plan_for("Road", continuous=True))
        self.assertFalse(result["passed"])
        self.assertEqual(result["groups"][0]["connected_components"], 2)

    def test_independent_motion_and_merged_islands_allowed(self):
        make_quad()
        make_quad("Wheel")
        plan = plan_for("Body", "Wheel")
        plan["groups"][1].update(motion="rotation", motion_evidence="Independent wheel axle")
        self.assertTrue(check_export.audit_plan(plan)["passed"])
        obj = bpy.data.objects["Body"]
        points = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                  (2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)]
        obj.data.clear_geometry()
        obj.data.from_pydata(points, [], [(0, 1, 2, 3), (4, 5, 6, 7)])
        obj.data.uv_layers.new(name="UVMap")
        self.assertTrue(check_export.audit_plan(plan)["passed"])

    def test_triangle_uv_and_material_budgets(self):
        obj = make_quad()
        plan = plan_for("Body")
        plan["max_triangles_per_mesh"] = 1
        self.assertFalse(check_export.audit_plan(plan)["passed"])
        plan["max_triangles_per_mesh"] = 20000
        obj.data.uv_layers.new(name="UnwantedSecondSet")
        self.assertFalse(check_export.audit_plan(plan)["passed"])
        obj.data.uv_layers.remove(obj.data.uv_layers[-1])
        obj.data.materials.append(bpy.data.materials.new("A"))
        obj.data.materials.append(bpy.data.materials.new("B"))
        self.assertFalse(check_export.audit_plan(plan)["passed"])

    def test_cli_failure_status_and_source_immutability(self):
        make_quad()
        temp_root = Path(tempfile.gettempdir()).resolve()
        with tempfile.TemporaryDirectory(prefix="roblox-blender-check-", dir=temp_root) as folder:
            root = Path(folder).resolve()
            self.assertEqual(root.parent, temp_root)
            source, plan_path = root / "fixture.blend", root / "plan.json"
            bpy.ops.wm.save_as_mainfile(filepath=str(source))
            source_hash = uv_metrics.file_hash(source)
            plan_path.write_text(json.dumps(plan_for("Body")), encoding="utf-8")
            uv_args = ["--blend", str(source), "--objects", "Body", "--uv-layer", "UVMap",
                       "--texture-size", "256", "256", "--meters-per-unit", "1",
                       "--target-density", "64", "--density-tolerance", "0.05", "--max-stretch", "1.5"]
            export_args = ["--blend", str(source), "--plan", str(plan_path)]
            self.run_cli("uv_metrics.py", uv_args, root / "uv.json", True)
            self.run_cli("check_export.py", export_args, root / "export.json", True)
            uv_args[uv_args.index("--target-density") + 1] = "128"
            self.run_cli("uv_metrics.py", uv_args, root / "uv-fail.json", False)
            plan_path.write_text(json.dumps(plan_for("Missing")), encoding="utf-8")
            self.run_cli("check_export.py", export_args, root / "export-fail.json", False)
            self.assertEqual(uv_metrics.file_hash(source), source_hash)

    def run_cli(self, script, arguments, output, should_pass):
        command = [bpy.app.binary_path, "--background", "--factory-startup",
                   "--python-exit-code", "2", "--python", str(SCRIPT_DIR / script),
                   "--", *arguments, "--out", str(output)]
        result = subprocess.run(command, capture_output=True, timeout=45)
        self.assertEqual(result.returncode, 0 if should_pass else 2,
                         result.stdout[-2000:].decode("utf-8", errors="replace"))
        self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["passed"], should_pass)


if __name__ == "__main__":
    if not bpy.app.background:
        raise RuntimeError("tests must run in an isolated background Blender process")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("Blender numerical fixture checks failed")
