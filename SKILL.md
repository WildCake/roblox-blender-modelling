---
name: roblox-blender-modelling
description: Model, UV unwrap, consolidate and prepare Blender assets for Roblox. Use for props, vehicles, mechanisms and static environments; reference reconstruction; stretched textures, inconsistent texel density or unintended UV overlap; excessive MeshParts, segmented exports and duplicate mesh uploads. Covers the official Roblox Blender add-on and import validation, not general gameplay or UI implementation.
---

# Roblox Blender Modelling

Build an editable, correctly scaled model with readable texture detail and an export organized by actual motion. A Blender object, material slot or disconnected island is not a reason for another Roblox MeshPart.

## Read the project contract first

Read the active project rules and map. Locate the canonical `.blend`, build scripts, model specifications, texture policy, motion/port sidecars, importer and asset registry. Keep their units, approved design and budgets authoritative. This skill does not authorize publication, desktop control, subagents, Play, physics tests or performance measurements.

Prefer headless Blender for authoring and numerical checks. Use the installed official Roblox Blender add-on for publication when the project specifies that pipeline. A genuinely interactive add-on step or missing account access is a concrete blocker; do not replace it with another importer or take control of the operator's windows.

Read references only for the responsibility being changed:

- [Model construction](references/model-construction.md): reference analysis, scale, silhouette, meaningful connections and moving clearances.
- [UV quality](references/uv-quality.md): unwrapping, physical texture scale, distortion, seams and intentional stacking.
- [Motion and export](references/motion-and-export.md): merging, continuous surfaces, prototype reuse and export budgets.
- [Import contract](references/import-contract.md): the official add-on, source identity, coordinate validation, collision and installation.

## Establish measurable acceptance

Before building, record the asset's real dimensions, axis roles, pivots, useful openings, articulation range and target viewing distance. Separate measured facts from inferred hidden geometry. Match reference cameras; a perspective image is not an orthographic dimension drawing.

Set a texture policy in pixels per metre, with any deliberate priority regions, density tolerance and acceptable distortion. Choose it for the expected game view and texture resolution. Read the existing policy instead of inventing another palette or atlas. UV quality matters for individual textures, trim sheets and atlases alike.

Write an export budget by semantic motion group, before export. Count visible instances, unique published prototypes, native colliding groups and mass owners separately. Require a reason for every split. Do not use upstream game-engine triangle or material budgets as Roblox limits.

## Construct the form before the detail

1. Calibrate references and place pivots. Block out proportions, negative space and major articulation.
2. Build the actual shell and structural transitions using profiles, section loops, bridges, extrusions, curves and appropriate native modifiers. Replace temporary blockout where the final surface needs connected geometry.
3. Resolve joints, supports, seams, thickness and full travel. Remove duplicate external faces and unexplained interpenetration in the owning geometry.
4. Add readable detail after the primary shape and clearance checks pass. Choose bevel widths by physical scale and edge role; a global bevel cannot repair the form.
5. Preserve a reproducible saved source. Authoring pieces may remain separate for editing; prepare consolidated delivery copies without altering foreign objects.

Use phase checks proportional to the affected risk. Dimension ratios, silhouette comparisons from matched views and cross-section profiles catch different errors. A matching silhouette alone does not prove depth or surface quality. Keep visual acceptance unverified when the current task prohibits renders.

## Make UV quality explicit

- **Measure scale.** Calculate density from the final evaluated surface in real units and the actual image dimensions. Object scale, curvature, bevels and unequal texture width/height affect the result. Judge the checker at the intended game distance.
- **Measure stretch.** Area coverage alone can hide a long, narrow distortion. Check directional scale as well as area density; repair seams, island shape or topology when the checker is elongated. Increasing image resolution does not repair stretching.
- **Stack deliberately.** Repeated islands may share texture only when the intended pattern, handedness, relative scale and wear permit it. Record the stacked set. Keep text, directional markings, unique damage and incompatible normal detail unique. Undeclared positive-area overlap or an island folding over itself fails the UV gate.
- **Vary repeated fittings.** Use reproducible per-part UV offsets and permitted rotations within the same logical texture region so identical plates or bolts do not all repeat one stain. Preserve density, chart continuity and filtering gutters; keep directional artwork correctly oriented. See the UV reference for prototype-reuse limits.
- **Place seams by construction.** Put them on real breaks, hidden edges and changes in surface direction. Keep focal faces, visible bends and adjoining panels readable. Check the actual texture across joins, not just an unlabelled UV layout.
- **Pad for filtering.** Give islands and region boundaries enough space and dilation for the lowest useful mip. Derive the margin from image resolution and expected filtering; a universal pixel count is not a policy.
- **Preserve the export map.** Roblox uses a single UV set in 0:1. The prepared mesh must have the intended set, one compatible material/texture set and preserved UV corners after merging and triangulation. Sharing a texture is not a reason to make another mesh.

The optional [UV metrics script](scripts/uv_metrics.py) reports per-triangle texel density and directional distortion from a saved `.blend`. It detects missing/collapsed UVs, invalid coordinates and configured density/stretch failures. It does **not** certify island overlap, seam appearance, texture orientation, padding or visual quality; follow the UV reference for those checks.

## Export by motion, not by construction history

**One visible mesh per genuinely independent rigid motion group.** Merge stationary covers, bolts, welds, mounts, decorations and disconnected islands that follow the same transform. Collapse compatible materials into the chosen texture representation before publication. Do not split on material, source object, polygon island, procedural segment or exporter convenience.

For a connected road, bowl, ramp or loop, join and weld the designed continuous seams, remove internal end caps and duplicate faces, and preserve continuous thickness and normals. `Join` alone does not make adjoining segments a continuous surface. A disconnected bolt in the same mesh is valid; an unwelded road seam is not.

Keep independent wheel spin, steering, suspension, turret yaw/pitch and recoil separate where their transforms actually differ. For two or three rigid groups, ordinary MeshParts usually keep the contract simple. For many purely visual moving pieces, evaluate skinning when appropriate; bones do not provide moving native collision. Fewer instances alone do not prove better performance.

Publish each proven unique geometry once, then instantiate the imported prototype. Repeated uploads and Blender linked data do not prove shared Roblox MeshIds. Ports and muzzle markers are sidecar data or Attachments, not extra render meshes. A moving assembly is not one rigid mesh merely because its pieces touch.

The optional [export-plan check](scripts/check_export.py) compares the saved export collection with the declared motion-group plan, triangle budget and single-material/UV requirements. It catches extra objects and multiple objects assigned to one rigid group; it cannot establish real kinematics or installed MeshId reuse.

## Validate publication and installation separately

Freeze the source and texture hashes, prototype list and local frames. Use normalized delivery copies and the established add-on path. Reopen a file export in a fresh Blender process when that is part of the pipeline; compare dimensions, normals, UVs, material bindings and part counts. Then inspect the actual Studio result: a file round trip does not prove the add-on upload or native collision.

Preserve useful openings with native collision on the approved visible groups. In a project that prohibits collision-only meshes, their count must be zero. Use Hull for closed forms; use more detailed native decomposition only for a meaningful gameplay opening and verify the imported shape. Take colliding-group budgets and mass ownership from the project contract. Keep source code in native Script Sync files; scene operations must not read/write Script.Source or install loaders.

Configure and validate a complete candidate before replacing the current template. Preserve unrelated scene data and the previous valid template on a failed transaction. Report the specific failure; do not introduce a legacy implementation or republish unchanged geometry to repair metadata.

## Deliver evidence with its limits

Report source revision, final dimensions, UV density/stretch results, overlap/stacking decisions, seam/padding review, visible groups, unique prototypes, installed MeshIds, colliding groups and mass owners. Identify what was authored, exported, published, installed and accepted in runtime. Reuse evidence for unchanged input hashes; rerun only checks invalidated by a change.

Do not claim visual approval from numerical checks, Roblox correctness from a Blender screenshot, physics from an import gate or FPS from a reduced object count. Preserve current authorization limits on rendering, gameplay and measurements.

## Sources

Check the current [Roblox geometry specifications](https://create.roblox.com/docs/art/modeling/specifications), [texture and UV specifications](https://create.roblox.com/docs/art/modeling/texture-specifications), [Roblox Blender add-on](https://create.roblox.com/docs/art/modeling/roblox-blender-plugin), [collision fidelity](https://create.roblox.com/docs/reference/engine/enums/CollisionFidelity) and [physical units](https://create.roblox.com/docs/physics/units) for the affected platform question. Reconcile conflicting documentation rather than inventing a new limit.

This skill adapts selected workflow ideas from [Blender Game Skills](https://github.com/majidmanzarpour/blender-game-skills). See [upstream attribution](UPSTREAM.md) for the pinned source, adaptation boundaries and license notice.
