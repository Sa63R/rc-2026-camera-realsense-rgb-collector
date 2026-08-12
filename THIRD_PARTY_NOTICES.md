# Third-party dependency notices

This repository imports three external Python packages through `requirements.txt`. They are not copied into this source tree, and their licenses do not grant a license for this project's own scripts. Conversely, any future project `LICENSE` cannot replace or narrow the notices and conditions attached to third-party packages.

This file is a practical dependency inventory, not legal advice and not a complete bill of materials. The exact wheel or system package installed on each supported platform is authoritative. Before distributing an application image, executable bundle, container, offline wheelhouse, or installer, inspect the licenses shipped inside those exact artifacts and preserve all required notices.

## NumPy

- Imported as: `numpy`
- Purpose here: expose RealSense frame buffers as arrays and perform small coordinate/matrix calculations.
- Upstream project: <https://numpy.org/>
- Official source: <https://github.com/numpy/numpy>
- Upstream license information: <https://numpy.org/doc/stable/license.html>

NumPy states that its code is distributed under the BSD 3-Clause license. NumPy distributions can also include or link to separately licensed numerical libraries. If NumPy itself is bundled rather than merely listed as an install-time dependency, retain the license material delivered with the selected distribution and audit that distribution's bundled components.

## OpenCV and the opencv-python distribution

- Imported as: `cv2`
- Requirement name: `opencv-python`
- Purpose here: GUI preview, text/circle overlays on preview copies, keyboard/mouse input, depth visualization, and image encoding.
- OpenCV source: <https://github.com/opencv/opencv>
- `opencv-python` packaging source and licensing summary: <https://github.com/opencv/opencv-python>
- Official wheel third-party notices: <https://github.com/opencv/opencv-python/blob/4.x/LICENSE-3RD-PARTY.txt>

The `opencv-python` maintainers state that the packaging scripts are MIT-licensed and OpenCV itself is Apache-2.0. Prebuilt wheels also contain platform-dependent third-party binaries with their own terms. The official notices currently identify components such as FFmpeg in all wheels and Qt in non-headless Linux wheels, among others. Do not summarize the wheel as “Apache-2.0 only,” and do not replace its included `LICENSE.txt` or `LICENSE-3RD-PARTY.txt` when redistributing the wheel.

This project intentionally requires the non-headless package because the scripts call `cv2.imshow`. Installing both headless and non-headless OpenCV wheel variants into one environment is unsupported by the packaging project and can make the actual dependency set ambiguous.

## RealSense SDK and pyrealsense2

- Imported as: `pyrealsense2`
- Purpose here: discover/select devices, configure streams, receive frames, align depth, read intrinsics/depth, and deproject pixels.
- Official SDK source: <https://github.com/realsenseai/librealsense>
- Python binding documentation: <https://github.com/realsenseai/librealsense/tree/master/wrappers/python>
- Upstream license: <https://github.com/realsenseai/librealsense/blob/master/LICENSE>

`pyrealsense2` is the Python binding distributed from the librealsense project. The upstream SDK repository identifies Apache License 2.0, but an installed PyPI wheel or system package may contain compiled native code and notices that must travel with redistribution. Keep its own license/notice files and audit the exact release and packaging channel used for each platform. Camera firmware, kernel drivers, USB rules, and vendor utilities are outside this repository and may have separate terms.

## What this notice does not cover

- Python itself, `pip`, virtual-environment tooling, operating-system packages, GUI backends, USB/udev components, camera firmware, and drivers.
- Tools used only during development or release preparation.
- Any future dependency added to the code or lock file.
- Photographs, labels, generated media, model weights, or other datasets. Those require separate provenance and review under [DATASET_POLICY.md](DATASET_POLICY.md).

## Release-maintainer checklist

1. Freeze and record the exact dependency versions used for the release platform.
2. Download/build the exact artifacts to be redistributed and inspect their embedded license and notice files.
3. Produce a software bill of materials or license report for the complete environment, including transitive native libraries.
4. Copy required third-party notices into the distribution in the form required by each license.
5. Keep third-party notices separate from the project license and do not imply endorsement by upstream vendors.
6. Re-run this review whenever a requirement, platform, wheel variant, or build option changes.

No project-level `LICENSE` is intentionally supplied in this staged copy until an authorized owner chooses one; see [LEGAL_NOTICE.md](LEGAL_NOTICE.md).
