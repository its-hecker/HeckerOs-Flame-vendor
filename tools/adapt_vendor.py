#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Apply the reviewed Coral install-ownership fixes to the stock Flame vendor."""

import argparse
import json
from pathlib import Path
import re
import subprocess


SOURCE = "a57f01d5642a55250e48b244f51be9322659eeed"
SERVICE = "android.hardware.camera.provider@2.7-service-google"
REPLACED = (
    "android.hardware.keymaster@4.1-impl.nos", "libface-calibration-proto",
    "libface-enroll-proto", "libfaceauth-util", "libairbrush-pixel",
    "android.hardware.keymaster@4.1-service.citadel",
    "android.hardware.neuralnetworks@1.2-service-noronha",
    "vendor.google.airbrush@1.0-service",
)


def adapt(root):
    root = Path(root)
    # Bind the adaptation to the exact unmodified upstream metadata, even when
    # the workflow's HEAD is the bootstrap rather than the fetched source.
    for name in ("Android.bp", "flame-vendor.mk"):
        expected = subprocess.check_output(["git", "-C", str(root), "show", SOURCE + ":" + name])
        if (root / name).read_bytes() != expected:
            raise ValueError("Review changed upstream metadata before adapting " + name)
    bp = (root / "Android.bp").read_text()
    for name in REPLACED:
        pattern = (r'(?ms)^cc_prebuilt_(?:binary|library_shared)\s*\{\s*name:\s*"'
                   + re.escape(name) + r'",.*?^\}')
        blocks = list(re.finditer(pattern, bp))
        if len(blocks) != 1 or "no_full_install:" in blocks[0].group():
            raise ValueError("Review changed stock module " + name)
        block = blocks[0]
        updated = block.group().replace('    name: "' + name + '",',
                                       '    name: "' + name + '",\n    no_full_install: true,', 1)
        bp = bp[:block.start()] + updated + bp[block.end():]
    needle = '    name: "' + SERVICE + '",'
    if bp.count(needle) != 1:
        raise ValueError("Review changed stock camera module")
    bp = bp.replace(needle, '    name: "' + SERVICE + '-flame",\n'
                    '    overrides: ["' + SERVICE + '"],\n'
                    '    stem: "' + SERVICE + '",\n'
                    '    init_rc: ["proprietary/vendor/etc/init/' + SERVICE + '.rc"],', 1)
    make = (root / "flame-vendor.mk").read_text()
    make, count = re.subn(r'(?m)^(\s*)' + re.escape(SERVICE) + r'(\s*\\?)$',
                         lambda m: m[1] + SERVICE + "-flame" + m[2], make)
    if count != 1:
        raise ValueError("Review changed camera PRODUCT_PACKAGES")
    prefix = "vendor/google/flame/proprietary/vendor/etc/init/" + SERVICE + ".rc:"
    lines = make.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.lstrip().startswith(prefix)]
    if len(matches) != 1 or not lines[matches[0]].rstrip().endswith("\\"):
        raise ValueError("Review changed camera init copy ownership")
    del lines[matches[0]]
    (root / "Android.bp").write_text(bp)
    (root / "flame-vendor.mk").write_text("".join(lines))
    origin = {
        "repository": "Nahida-Prjkt/proprietary_vendor_google_flame",
        "branch": "lineage-24.0", "revision": SOURCE, "target": "flame",
        "adaptation": "Coral camera/init and eight FaceID full-install ownership fixes; proprietary bytes unchanged",
        "rom_features": "Shared with Coral in its-hecker/HeckerOS feat/suite-polish",
        "coral_reference": "its-hecker/heckeros-coral-vendor@60b0c615e939cd09ce956e6fe6df5d5aa6ccbdd4",
    }
    (root / "UPSTREAM_SOURCE.json").write_text(json.dumps(origin, indent=2) + "\n")
    print("Flame vendor camera/init and FaceID install ownership adapted; binary inputs unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path.cwd())
    adapt(parser.parse_args().source_root)
