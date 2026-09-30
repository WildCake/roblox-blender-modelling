# Motion groups, consolidation and prototype publication

Read this before splitting a model, merging objects, repairing an excessive MeshPart count or changing the export/publication path.

## Decide the export groups before modelling detail

Make a small table with the render group, transform owner, relative movement, prototype identity, collision responsibility and intended instances. The table is a budget and a kinematic contract. A list of Blender objects is not that contract.

| Geometry | Expected treatment |
|---|---|
| Hull, stationary covers, rivets, sockets and trim | One mesh following the hull transform |
| Wheel tyre, rim and co-rotating details | One mesh following wheel spin |
| Steering knuckle versus wheel | Separate only when their transforms differ |
| Turret yaw body, pitching gun, recoiling slide | Split at the real axes of relative movement |
| Static road, bowl or loop built from generator segments | One continuous welded surface within applicable limits |
| Repeated identical rollers or track shoes | One published prototype, positioned instances |
| Muzzle and connector markers | Sidecar frames or Roblox Attachments |

Do not split because of a source object name, colour, material slot, UV island, panel seam, disconnected component, procedural iteration or selected export segment. None proves independent movement.

Do not merge independent physical bodies or pivots to hide the count. For a large articulated visual system, skinning may be appropriate, but it needs an explicit skeleton/motion contract. A skinned appearance does not move native collision surfaces.

## Prepare a delivery copy

Keep editable construction pieces and modifiers in the master. Build a temporary delivery collection from the evaluated approved geometry. Preserve group pivots, UV corners, sharp boundaries and the intended normals. Do not mutate unrelated objects or save export staging over the master.

Consolidate by transform owner. Bake compatible material differences into the chosen single colour/PBR texture set and remove unused material slots on the delivery copy. Fix the UV representation instead of creating one MeshPart per material. Preserve required roughness, metalness and normal detail; a flat colour replacement is a design change.

For disconnected manufactured details, one object may correctly contain many islands. For a surface designed to be continuous, weld its intended boundaries and remove internal segment caps and duplicate faces. Validate thickness, tangent transitions and saved normals. Joining objects alone does not weld a generator's road seams.

Check all supported steering, suspension, recoil and hinge positions. Correct the local geometry when mounts interpenetrate or adjacent faces have positive coincident area. Material changes and epsilon offsets do not repair that geometry.

## Respect real limits without gratuitous segmentation

Check the current target asset class and Roblox documentation. The general modelling specifications checked on 2026-09-30 state 20,000 triangles per mesh; avatars and accessories have additional class-specific requirements. Recheck the affected limit when publishing instead of treating a stale number as permanent.

First reduce waste in the owning geometry while preserving the approved silhouette and detail. If a genuine platform limit or required native collision opening still requires a split, document the exact constraint, partition and resulting instance/asset budget. A split into every source segment is not a solution just because each piece falls below the limit.

For a static connected asset, choose partitions at meaningful boundaries and preserve their geometric and UV continuity. Explain remaining boundaries explicitly. For approved repeated modular environment pieces, reuse a prototype; do not confuse intentional modular construction with accidental export fragmentation.

## Publish prototypes, instantiate repetitions

Prove equivalence in a stable local frame using topology, oriented corners, UVs, normals and required texture state. Object names, bounds or a hash alone do not establish equivalence. Mirrored text, asymmetric tread or different UV placement can invalidate apparent reuse.

Publish one prototype for each proven unique geometry. Keep instance placement, scale and animation roles in the sidecar. A Blender linked mesh can still be uploaded multiple times, and repeated official imports can produce different asset IDs. After import, verify the actual Roblox MeshIds and compatible texture/material IDs are shared.

Keep three counts distinct: source construction objects, exported unique prototypes and installed visible instances. A wheel prototype can serve several independently rotating wheels without another upload. Asset reuse is not a guarantee that Roblox renders the instances in one draw call.

## Optional export-plan check

Save an explicit plan for the prepared collection:

```json
{
  "export_collection": "EXPORT",
  "max_triangles_per_mesh": 20000,
  "groups": [
    {"object": "Body", "motion_group": "body", "motion": "static", "continuous_surface": true},
    {"object": "WheelPrototype", "motion_group": "wheel-spin", "motion": "rotation", "motion_evidence": "Tyre and rim rotate together around the wheel axle"}
  ]
}
```

Use the actual project names and current budget. For a documented split within one motion group, every affected entry must carry `split_reason` (`platform_limit` or `useful_collision_opening`) and nonempty `split_evidence`. These fields record a reviewed reason; the script cannot prove that an exception was necessary.

```text
blender --background --factory-startup --python-exit-code 2 --python /path/to/skill/scripts/check_export.py -- --blend /path/to/model.blend --plan /path/to/export-plan.json --out /path/to/export-report.json
```

The script reads the saved file without saving it. It checks actual versus planned mesh objects, multiple objects following the same declared rigid motion group, one UV set and at most one material, final triangle budgets, positive object scale and connected topology where requested. A plain untextured group can explicitly use `requires_uv: false`.

This is a prepared-source gate. It does not prove the group has a real independent transform, every surface has a meaningful shape, add-on publication preserved the collection, native collision is correct or installed instances share MeshIds. Those remain explicit import/runtime responsibilities.

References: [Roblox modelling specifications](https://create.roblox.com/docs/art/modeling/specifications), [texture specifications](https://create.roblox.com/docs/art/modeling/texture-specifications), [performance guidance](https://create.roblox.com/docs/performance-optimization/improve).
