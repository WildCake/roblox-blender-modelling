# Official Roblox import and installation contract

Read this when preparing publication, changing the importer, deduplicating uploaded geometry, replacing an installed library or repairing import coordinates/materials.

## Source ownership and publication

Read the current project map before finding files. Use the canonical source, established build pipeline and installed official Roblox Blender add-on. Authoring and numerical checks can run headlessly. Do not assume every add-on operation has a headless API; inspect its supported path and reuse the project's working publication method.

Preserve unrelated scene objects. One writer owns each `.blend`; read-only validators must not save it. Keep staging copies, normalized export transforms and temporary collections outside the master transaction. Remove superseded own implementations after the replacement is accepted.

Freeze source and texture hashes for a publication batch. Publish each proven unique prototype once. Record upload operation ID/status and continue that operation while pending; do not submit the same geometry again because the upload has not completed. Stop on a real error and fix its cause.

Publishing needs the user's authorization and the correct asset owner. Missing authentication or a real GUI-only add-on step requires the specific operator action. This skill does not authorize account access, desktop control or a substitute importer. Do not store credentials in build scripts, sidecars or reports.

## Manifest responsibilities

Keep the manifest narrow: source/texture identity, units, envelope, group/prototype mapping, normalized local frames, pivots, semantic markers, motion ownership and collision/material policy. Runtime code consumes this contract; it should not reverse-engineer arbitrary Blender object suffixes.

Count separately:

| Quantity | What it proves |
|---|---|
| Prepared mesh objects | Export organization in the saved source |
| Visible instances | Installed render objects that actually move/place independently |
| Unique geometry/prototypes | Proven source reuse before upload |
| Unique installed MeshIds | Actual reuse after publication |
| Native colliding groups | Visible groups participating in physical contacts |
| Collision-only objects/assets | Compliance with the project's collision policy |
| Dry/resource mass bodies | Physical ownership independent of visual complexity |

A source hash is not a geometry-equivalence proof. Compare the full oriented geometry, UV corners, sharp/smooth boundaries, normals and required material state in a stable local frame. Select numerical tolerances from scene precision; a candidate hash only narrows comparisons. Do not conflate mirrored geometry, differently oriented text or incompatible texture layouts.

## Verify coordinates and appearance

Export stable geometry-local axes with intended rest placement stored separately. Preserve rig pivots and avoid negative/nonuniform delivery scale where it would invalidate the mapping or physics contract.

After insertion, compare dimensions, positions, orientations, pivots, markers, material bindings and texture orientation to the manifest. Prove the basis with asymmetric geometry and a rotated prototype. Correct centre positions alone do not prove that local vertices or normals survived the export convention.

If needed, sample actual installed mesh vertices/UVs through permitted scene APIs and compare them with the saved source. Verify one common conversion and apply it consistently. Do not introduce guessed per-asset rotations, stretch the imported model to mask a mismatch or relax tolerances until an error passes.

For a file export, reopen it in a fresh Blender process and compare the actual result. A file round trip is valuable but does not validate the official add-on's upload or Roblox's native collision. Inspect the real installed prototype separately.

UV checks include the intended single UV set, physical density, directional detail, correct stacking, normal-map convention and filtering at seams. One compatible material per delivered mesh must preserve required colour/PBR differences. A successful import notification does not certify that material consolidation preserved appearance.

## Collision, mass and moving groups

Follow the project's policy. When collision-only MeshParts or separate collision asset IDs are prohibited, their count is zero; keep collision on the approved principal visible meshes. Do not copy a generic COLLISION-proxy collection from an upstream game-engine workflow into that project.

Hull is appropriate for closed forms where concavity is not useful. PreciseConvexDecomposition is approximate and should serve a real opening, seat clearance or other gameplay need. Verify both surfaces that should hit and useful openings that should remain open in the actual imported representation. Do not turn off all query/collision to make an opening test pass.

Respect the declared colliding-group budget. Decorative mechanisms do not acquire physical collision merely because their appearance moves. Raycast support geometry must not simultaneously introduce native contact constraints that fight the intended support simulation.

Separate appearance from mass ownership. A modular vehicle may have one dry-mass owner with cosmetic meshes Massless, while consumable resources preserve their real centres of mass. Other projects may use real articulated physical bodies; do not merge their dynamics to reduce appearance counts. Use the authoritative engine-boundary unit conversion and verify density, volume, mass, COM and inertia together.

One owner controls each transform. Do not retain a complete server decorative mechanism and a second client copy for the same motion without a defined collision/query role. Keep visual lifecycle and damage cleanup explicit. Bones provide visual articulation, not a moving collision hull.

## Install transactionally

Validate a complete candidate before replacing a working template. For owned assets that should be ordinary Models, remove the imported `PackageLink` immediately after insertion, before renaming or configuring descendants. Preserve source asset, mesh and texture IDs; do not disable Studio warnings globally.

Validate instance attributes against the actual runtime mode, not only Edit-mode acceptance. Keep long/full metadata in local sidecars when runtime attribute limits cannot carry it. Use a single documented representation rather than lossy truncation or compatibility branches.

Reuse installed prototypes only when geometry, texture identity, frame conventions and required collision fidelity are compatible. Repair metadata without republishing unchanged geometry. Update the project asset registry and affected rig contract together.

Game code remains in native Studio Script Sync files. Scene/data commands must not read/write Script.Source, install loaders or create executable instances unless explicitly requested. A new directory on disk does not prove a new dependency exists in Studio. Preserve the configured sync roots and ask for the concrete missing synchronization when needed.

Restore any temporary editor state and leave cameras/input free as the project requires. Report source preparation, publication, installation and runtime acceptance separately. Physics driving, gameplay, network behaviour and FPS require their own authorized evidence.

References: [Roblox Blender add-on](https://create.roblox.com/docs/art/modeling/roblox-blender-plugin), [Studio importer](https://create.roblox.com/docs/studio/importer), [CollisionFidelity](https://create.roblox.com/docs/reference/engine/enums/CollisionFidelity), [physics units](https://create.roblox.com/docs/physics/units), [native Script Sync](https://create.roblox.com/docs/scripting/sync).
