"""Recommended basic two-class RealSense RGB image collector."""

from __future__ import annotations

import argparse

import cv2
import numpy as np
import pyrealsense2 as rs

from capture_utils import (
    enable_selected_device,
    prepare_class_directories,
    save_image_checked,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="captures",
        help="Output root containing real/ and fake/ (default: captures).",
    )
    parser.add_argument("--device-serial", help="Optional RealSense serial number.")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--timeout-ms", type=int, default=3000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    real_dir, fake_dir = prepare_class_directories(args.output_dir)

    context = rs.context()
    if len(context.query_devices()) == 0:
        print("No RealSense device detected. Check USB, permissions, and drivers.")
        return 1

    pipeline = rs.pipeline()
    config = rs.config()
    enable_selected_device(config, args.device_serial)
    config.enable_stream(
        rs.stream.color, args.width, args.height, rs.format.bgr8, args.fps
    )

    started = False
    try:
        pipeline.start(config)
        started = True
        print("=== Basic RealSense RGB collector ===")
        print("r=REAL, f=FAKE, q=quit")
        print(f"Output root: {real_dir.parent.resolve()}")

        while True:
            frames = pipeline.wait_for_frames(timeout_ms=args.timeout_ms)
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            raw_image = np.asanyarray(color_frame.get_data())
            preview = raw_image.copy()
            cv2.putText(
                preview,
                "r=REAL | f=FAKE | q=quit (saved image has no overlay)",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
            )
            cv2.imshow("RealSense RGB Stream", preview)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            try:
                if key == ord("r"):
                    path = save_image_checked(raw_image, real_dir, "real", "png")
                    print(f"Saved REAL: {path}")
                elif key == ord("f"):
                    path = save_image_checked(raw_image, fake_dir, "fake", "png")
                    print(f"Saved FAKE: {path}")
            except OSError as exc:
                print(f"Save failed: {exc}")
        return 0
    except RuntimeError as exc:
        print(f"RealSense error: {exc}")
        print("Confirm device access and close other camera applications.")
        return 1
    finally:
        if started:
            pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    raise SystemExit(main())
