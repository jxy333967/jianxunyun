# XeGfx rendering fixes: row pitch and render-barrier snapshots

2026-11-10: on a real Meteor Lake `8086:7D55` system running Sequoia 15.8.1 (24H32), the user confirmed that small ghosting, window/card missing corners, translucent regions rendered fully transparent, and abnormal color blocks disappeared after the render-barrier correction and a normal reboot. The loaded WindowServer plugin UUID/hash and actual barrier-refresh logs were checked; submission failures remained zero. This is one machine/boot plus the interfaces tested, not a blanket Metal conformance claim.

## Root cause and patch scope

`setFragmentTexture:` substitutes a pre-pass `_snap` when a render target samples itself. Previously `textureBarrier` and `memoryBarrierWithScope:RenderTargets` only emitted a Vulkan barrier: subsequent fragment reads could still access the old snapshot. Synchronization alone cannot make the separate snapshot contain new pixels.

For the guarded single-color, single-sample root-image path, the fix ends the physical Vulkan pass, copies the current target into the same snapshot, resumes with LOAD, and retains the logical Metal encoder/state. Depth, stencil, MSAA, resolves, queries, target views/subresources/mips/multiple layers/attachments and direct-feedback paths are excluded; other paths retain existing behavior. See `patches/0002-*` for just this change on the prior row-pitch candidate. The non-overlapping 32x32 repro reads left-half pixels into a distinct right-half region; original512/1024 wrong, patched0.

The earlier bounded row-pitch fallback is also included: a real WindowServer request for36x21 BGRA8, row144 returned nil. Read-only CPU-backed shader-read views can use a256-byte-aligned backing, preserving public buffer/offset/row metadata and syncing source rows before submissions. Bounds include actual host length. Writable textures are not emulated. This earlier fix alone did not visibly resolve the four reported problems.

## Reproduce without installing a driver

Base: [WTLIntelGfx v0.0.47](https://github.com/watchthelight-labs/WTLIntelGfx/tree/a3fd73ed68ae82af7d3c6a80ec4336507e944ed7), commit `a3fd73ed68ae82af7d3c6a80ec4336507e944ed7`.

1. Obtain that source and use its normal build prerequisites. `python3 tools/apply.py /path/to/WTLIntelGfx` dry-checks the full patch. Add `--apply` to back up the two source files and apply it. Do not apply both patches. If other downstream changes conflict, stop and review; never force-apply.
2. Build the plugin with the upstream/[samwu07](https://github.com/samwu07/xegfx-thinkbook14plus-mtl) stack and required runtime dependencies. This package does not redistribute those dependencies, rewrite signatures, install a global plugin or alter system security. A plugin binary hash is provided as evidence, not a reproducible-build guarantee.
3. On an already-working, guarded XeGfx test system: `python3 tools/run-tests.py /absolute/path/to/candidate/NVMTLDriver`. Tests compile into separate directories with basename `nvmtltest` (existing upstream diagnostic allowlist). They read back only their own authored offscreen targets, not screen pixels. They use the real GPU and may expose experimental-driver bugs; keep your working renderer and recovery route. No display/GPU initialization is attempted by the runner.

Harnesses intentionally require build24H32 and an existing NMXAccel service. For other builds/services, review the ABI before adapting them. For an unpatched baseline the legacy snapshot test is expected to fail512 pixels; do not run it as a production application. The runner stops at the first failure.

## Evidence and limitations

Four barrier paths (legacy/modern/prebound/repeated),7 blend/scissor/discard/sRGB/write-mask regressions, and row updates/lifetime/bounds checks passed. Final signed binary loaded in isolated Sequoia QEMU and exposed the expected method; VM loading is not hardware acceleration proof. The real WindowServer then executed the new snapshot-refresh path and the user confirmed the visual improvement. See `results/validation.json` and compact authored-test outputs.

Accessibility settings were unchanged across the successful comparison: reduceTransparency=1, reduceMotion=1. An increaseContrast experiment gave no improvement and was restored. We do not claim native background-blur/vibrancy is fully implemented.75Hz/modesetting, first-login activation/reload, sleep/wake, multihead and all other Metal contracts remain outside this fix. No change to EFI, kexts, AuxKC, SIP, AMFI or Windows was required for this patch trial.

## Attribution and license

Thanks to samwu07 for the working Meteor Lake stack, watchthelight for XeGfx/WTLIntelGfx, and NullMoth Systems for the driver/plugin foundation. New tools/docs/tests are BSD-2-Clause. Patches to the upstream plugin retain **PolyForm Noncommercial1.0.0**, with its noncommercial restriction; this source publication is not a relicensing of the driver to an OSI-approved license. Read NOTICE and the included license. Prepared with Codex assistance and user hardware testing.

No EFI identities, account credentials, user files, raw logs, firmware, Apple binaries or third-party driver binaries are included. No automated system installation or restart.
