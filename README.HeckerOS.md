# HeckerOS Pixel 4 (Flame) vendor

Based on the exact PixelOS-compatible `Nahida-Prjkt/proprietary_vendor_google_flame`
`lineage-24.0` snapshot recorded in `UPSTREAM_SOURCE.json`. All original proprietary
files, symlinks, radio pointers, file modes and attribution are retained.

The camera provider uses a distinct `-flame` Soong module and the original executable
stem, AIDL V1 dependencies, init script and VINTF declaration. The eight stock FaceID
support modules remain available for dependency resolution with their full install
rules suppressed; the shared HeckerOS FaceID plugin owns their replacements. These
are the same install-ownership fixes used on Coral.

Radio files use the upstream LFS endpoint preserved in `.lfsconfig`. Initialize Repo
with `--git-lfs`, then run `git -C vendor/google/flame lfs pull`. The build helper
checks all eleven radio payloads against their SHA-1 values in `Android.mk`.

Use [HeckerOS Flame local manifest](https://github.com/its-hecker/HeckerOs-Flame-localmanifest/tree/cnb_latest_stable).
The shared [HeckerOS](https://github.com/its-hecker/HeckerOS/tree/flame-cnb_latest_stable)
integration supplies every Coral ROM feature, including Suite, native Settings and
SystemUI customizations, launcher, GameSpace, Dolby, GCam, Motion Sense, 3D Face Unlock,
charging/AOD, NetLab and boot/recovery branding. Source parity does not establish
Flame boot or hardware validation; the first full build and phone tests are pending.

## Stable SIM Manager

The stable vendor branch ships the Google-signed SIM Manager
`D.2.1.989982212-google` (306110) extracted from the shared Flame ROM. The
Flame product keeps its presigned privileged import, and the Suite supplies
the remaining permissions. See `provenance/EuiccGoogle.json` for the APK
hash, signer and permission audit.
