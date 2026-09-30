# Constructing reference-driven Roblox assets

Read this when creating or changing shape, reference reconstruction, joins or articulation clearances. UV/export corrections do not automatically justify rebuilding an approved model.

## Calibrate what the references actually establish

Record real size, scale cues, view type, camera direction and axis roles. Distinguish an orthographic blueprint from a perspective concept. Save useful reference views and mark hidden dimensions as inferred. Match several views through the same world landmarks; do not independently stretch images until each seems plausible.

Measure a small set of important ratios before blockout: wheelbase/body length, opening width/height, shell thickness, mounting offsets or whatever gives this particular asset its identity. Derive thresholds from the specification and reference reliability. Generic silhouette-IoU targets are useful examples, not universal proof of quality.

Plan the actual parts, supports and motion ownership. A wheel belongs below its supported load, a hinge needs clearance, a gun needs the correct yaw/pitch/recoil axes and a seat needs space for the character. Put those relationships into the blockout before ornaments.

## Build at three meaningful scales

1. **Primary form:** envelope, silhouette, major volume and negative space.
2. **Structural form:** cross-section changes, thickness, slopes, frames, joints, transitions and supports.
3. **Functional detail:** mounts, handles, ports, ribs, fasteners and surface markings that remain readable at the target view.

Do not add bolts over the wrong proportions or treat a constant-thickness silhouette extrusion as a fully shaped object. Check section widths and heights along the principal axis as well as front/side/top outlines. Thin, organic or curved shapes may need additional perspective views.

Choose construction from the part's actual geometry:

- Revolve a genuine radial profile; use an array for genuinely repeated units.
- Extrude a designed profile for a prismatic part, then vary section loops where the form changes.
- Bridge matching loops for transitions and use continuous curve profiles for rails and pipes.
- Use a subdivision cage with deliberate control flow when the shape needs a smooth shell.
- Use Boolean/remesh/sculpt operations when appropriate, then repair topology for the required shading, deformation and export.

Keep modifiers and material previews useful for design, but evaluate their real output for the final gate. Match bevel radii to real scale and the edge's function. Smooth shading or a normal trick is not evidence that a chamfer, thickness or transition exists.

## Make connections physically legible

Classify each join as a continuous surface, fused solid, mechanical seam, embedded component, physical contact or intentionally separate part. Build the appropriate interface: welded loops, a cleaned union, a designed clearance, a receiving recess or a contact surface.

Overlapping boxes are acceptable blockout in some cases; unexplained deep interpenetration is not a finished joint. Avoid coincident external faces, internal end caps at continuous joins, clipped fasteners and open thin shells where volume is required. Check geometry at the actual supported motion extremes.

For a chamfer or improved ground clearance, remodel the owning shell/rail and its supporting fixtures. Confirm the leading/trailing contact profile along the real travel direction. Mass clipping of a finished assembly can leave sliced fittings and a hidden sharp catch beneath the cosmetic bevel.

Do not use material offsets, render bias or changed collision flags to conceal a geometry defect. Correct the relevant source and keep pivots, ports and the rest of the approved model stable.

## Reproducible authoring and proportionate gates

Keep one canonical saved `.blend` with reproducible build scripts when the project uses scripted modelling. A build script may rebuild only the objects it owns; do not delete the entire scene or another author's work. Keep names, dimensions and unit conversion in the responsible owner rather than scattered hardcoded values.

After a meaningful form change, check the affected dimensions, silhouette, section profile, connected topology, normals, clearances and useful openings. For allowed visual acceptance, use headless renders of the saved real geometry and materials from suitable diagnostic views. A concept image, black minimized viewport or numerical manifold report cannot certify the intended appearance.

Do not automatically run a complete render suite after every assignment. Reuse valid evidence for the same input revision and check only the risk changed. If rendering or gameplay is reserved for the operator, deliver numerical evidence and identify the outstanding acceptance.

Adapted workflow ideas: [Blender Game Skills, pinned initial release](https://github.com/majidmanzarpour/blender-game-skills/tree/f0ef29385a03de139957e6f700b801cdc00b7e29). See the repository's attribution notice; this reference uses Roblox/project budgets rather than its generic game-engine delivery defaults.
