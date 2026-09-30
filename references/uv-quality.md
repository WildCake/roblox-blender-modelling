# UV quality: scale, stretch, seams and stacking

Read this for new unwraps, stretched textures, inconsistent texture scale, overlapping UV islands, material consolidation or export changes that touch UVs. The purpose is readable, correctly scaled texture mapping. A common atlas is one possible texture policy, not the definition of good UVs.

## 1. Establish scale before unwrapping

- Record the object's intended dimensions, Blender coordinate units and conversion to the game's units. Use the project's authoritative conversion. Roblox's standard physical scale is 0.28 metres per stud; do not assume the project's Blender coordinates are already metres or studs.
- Inspect nonuniform and negative scale, parent transforms and evaluated dimensions. Normalize the delivery copy at a deliberate stage while preserving its position, pivots and rig. An arbitrary Apply Transform on the master can break articulation.
- Measure the final evaluated geometry. A later bevel, subdivision, deformation or scale change can invalidate an earlier unwrap. Keep a reusable UV plan only when those inputs remain compatible.
- Match checker squares to the real surface. Equal UV area on a small bolt and a large panel is unequal physical texture scale. Deliberate hero regions may have more detail, but state the priority rather than letting scale drift accidentally.

Choose a density in pixels per metre and a permitted range for the asset family. Record the actual width and height of each image. A rectangular texture changes directional pixel scale even when the UV island looks square.

For a triangle with real surface area `A_m2` and UV area `A_uv` on an image of `W x H` pixels:

```text
pixel_area = A_uv * W * H
area_density_px_per_m = sqrt(pixel_area / A_m2)
```

This gives an area scale, not a distortion verdict. A mapping can preserve area while stretching one direction tenfold and compressing the other tenfold.

## 2. Detect and repair distortion

Use a labelled, directional checker for the review. Inspect focal panels, long rails, curved bends, end caps and the smallest readable details. Check at the intended game distance and under a view that exposes the surface; a distant beauty shot can conceal stretching.

Measure the two singular values of the triangle's mapping from its physical tangent plane to texture pixels. Their ratio is directional distortion, where 1 is locally isotropic. The optional metrics script computes this without a render. Choose the allowed ratio for the affected surface; do not claim one universal threshold fits cylinders, organic shells and tiny bevels.

Repair in the owning mapping or geometry:

- Add a seam at a physical break or on a less visible edge when a long curved island cannot flatten cleanly.
- Use a cylindrical or profile-following unwrap for appropriate rails, pipes and revolved surfaces. Match circumferential and longitudinal density rather than stretching an end cap across the entire sheet.
- Relax or rebuild distorted islands and restore the intended density afterwards.
- Shape topology where a folded face, sliver or inconsistent cross-section is the actual cause. More image pixels do not fix the geometric mapping.
- Keep visible adjoining parts at compatible physical scale. A cover may need separate UV topology while remaining part of the same exported mesh.

A collapsed textured triangle fails. A face deliberately sampling a uniform colour region may be exempt only when its full sampled texture set is spatially uniform there and no tangent-space normal detail depends on its mapping. Mark those faces explicitly; do not excuse a collapsed decal, wood grain, tread or label as a palette face.

## 3. Distinguish useful stacking from errors

Record each intended stacked set, its texture set, physical scale, orientation and reason. Repeated identical brackets or nondirectional panels can share UV space; asymmetry, text, arrows, unique wear, handed tread and baked lighting can make that incorrect.

Check these cases separately:

| Case | Decision |
|---|---|
| Shared UV edge, with no positive-area intersection | A seam boundary, not an overlap failure |
| Same island crossing over itself | Fix the fold or topology |
| Unrelated islands intersecting | Fix layout unless the overlap is explicitly intentional |
| Repeated surfaces using the same nondirectional pattern | Stack with matching physical density and recorded ownership |
| Mirrored UVs on text or directional markings | Keep them unique or change the intended artwork |
| Mirrored normal-mapped detail | Verify tangent handedness and shading in the installed Roblox asset |
| Multiple parts using a uniform colour sample | Deliberate sharing; keep away from nonuniform neighbouring texels |

Do not reject all overlap: Roblox permits overlapping UVs. Do not accept all overlap either. Check triangle intersections for positive area or inspect an island-ID overlay; AABB overlap alone only identifies candidates. Compare equivalent UV footprints and actual sampled artwork for declared stacks. With several texture sets, compare overlap only inside the same set.

Keep final UVs in 0:1. Do not introduce UDIMs or out-of-range tiling into a pipeline that cannot deliver them. Do not mirror geometry solely to make an unrelated UV or prototype comparison pass.

## 4. Seams, orientation and padding

- Place seams according to manufacture and visibility: underside, panel breaks, sharp changes and hidden joints. Keep a hero face readable and a directional pattern consistent across adjoining pieces.
- Orient grain, tread, brushing, labels and arrows by their real part axes. A checker that has numbers and arrows exposes rotations and mirroring that a plain grid misses.
- Preserve local scale around corners. On a continuous road or loop, check the path direction, turns, transitions and joins together; segmented authoring must not reset texture scale at every segment.
- Pack after deciding density and stacking. Do not scale every island independently just to fill empty space. Occupancy is secondary to readability and a coherent physical scale.
- Choose inter-island padding and texture dilation for the actual image resolution and the smallest useful mip. Lower-resolution sampling needs a wider base-level margin. Inspect the final texture with filtering; a nominal padding number alone does not prove freedom from bleed.
- In an existing atlas or trim sheet, keep islands within the usable region and its gutter. Preserve approved cells and old UVs; edit the shared layout only when the project permits it.

## 5. Preserve the complete texture contract

Roblox's texture documentation specifies one assigned material per mesh, one UV set and 0:1 coordinates. Unify compatible Blender materials into the chosen colour/PBR representation on a delivery copy instead of turning each material into a new MeshPart. Verify the delivered UV set; active viewport/render choices do not prove which set the export retained.

For PBR, keep base colour, roughness, metalness and tangent-space normal maps registered to the same unwrap. Use appropriate colour spaces and Roblox's supported OpenGL tangent normal convention. Preserve the unpacked source maps. Do not call an RGB colour image a normal map or assume an engine-specific packed map is portable.

Bake by matching part groups or a controlled cage when neighbouring geometry would project onto the wrong surface. Derive cage/ray distances from the actual gap and scale. Review the UV seams and hard edges before merging texture sets. Do not bake directional scene lighting into the base colour.

After consolidation and final triangulation, compare UV corners, island orientation, normal/tangent shading and image bindings. Reopen a file export when available, then inspect the actual official add-on import. The prepared mesh must preserve the mapping even if Blender's source materials were numerous.

## Optional numerical check

Run in an isolated background Blender process:

```text
blender --background --factory-startup --python-exit-code 2 --python /path/to/skill/scripts/uv_metrics.py -- --blend /path/to/model.blend --objects Body Wheel --uv-layer UVMap --texture-size 2048 2048 --meters-per-unit 1 --target-density 256 --density-tolerance 0.20 --max-stretch 1.5 --out /path/to/uv-report.json
```

These values are an example, not defaults for every Roblox asset. Supply the real unit conversion, selected texture set and project thresholds. For explicitly uniform colour faces, `--constant-attribute ATTRIBUTE` reads a Boolean FACE-domain attribute; every excluded face must satisfy the exception above. No geometry is changed and the source is not saved.

The report includes input hash, Blender version, selected objects, thresholds, real surface area, density range, area-weighted density, directional distortion and failing triangle counts. Numerical UV quality is not proof of overlap, correct artwork, seam visibility, padding, normal-map compatibility or Roblox acceptance.

## Evidence to deliver

Record the physical scale and texture size; density target and measured range; worst affected surfaces; distortion limits and violations; declared stacked sets; unique directional regions; seam/padding review; final exported UV set; and the installed result when available. State which visual checks remain unverified under the current task's permissions.

References: [Roblox texture and UV specifications](https://create.roblox.com/docs/art/modeling/texture-specifications), [Blender UV layouts](https://docs.blender.org/manual/en/latest/modeling/meshes/uv/workflows/layout.html), [Blender texture baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html).
