# Upstream attribution and adaptation

Selected modelling and delivery workflow ideas are adapted from **Blender Game Skills** by **Majid Manzarpour**:

- Repository: https://github.com/majidmanzarpour/blender-game-skills
- Pinned commit: [`f0ef29385a03de139957e6f700b801cdc00b7e29`](https://github.com/majidmanzarpour/blender-game-skills/commit/f0ef29385a03de139957e6f700b801cdc00b7e29), published 2026-09-24.
- Consulted materials: `skills/blender-image-to-3d/SKILL.md`, `references/delivery-and-acceptance.md` and `references/blender-5-notes.md` at that commit.
- License: MIT; the complete upstream notice is retained in [LICENSE-UPSTREAM](LICENSE-UPSTREAM).

Retained ideas include calibrated references, primary form before detail, explicit inference, reproducible headless authoring, measured phase evidence, texture-scale/seam review, export manifests and reopening exported files to inspect the actual delivery.

The adaptation uses Roblox/project budgets, the established official Roblox Blender add-on and native Script Sync ownership. It does not carry over the upstream's default collision-proxy collection, generic GLB/FBX-first installation path, non-Roblox triangle budgets or multi-material group budgets.

The UV density/directional-distortion calculator, export-plan checker and numerical fixture tests in this repository are newly implemented. They are not copies of the upstream helper scripts. The motion-group, prototype-reuse and native-collision guidance also incorporates an existing Roblox-specific workflow, generalized without private project code, model files, asset IDs, account credentials or local owner data.

This is an independent adaptation, not an official Roblox or Blender product. Upstream changes are not pulled automatically; review the relevant changes and update the pinned attribution when deliberately adopting them.
