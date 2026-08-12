"""Minimal two-class RealSense RGB collector kept for learning and debugging."""

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
    parser.add_argument("--output-dir", default="captures")
    parser.add_argument("--device-serial")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=30)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    real_dir, fake_dir = prepare_class_directories(args.output_dir)
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
        print("r=REAL, f=FAKE, q=quit")
        while True:
            color_frame = pipeline.wait_for_frames().get_color_frame()
            if not color_frame:
                continue
            raw_image = np.asanyarray(color_frame.get_data())
            preview = raw_image.copy()
            cv2.putText(
                preview,
                "r=REAL | f=FAKE | q=quit",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.imshow("RealSense RGB Stream", preview)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            try:
                if key == ord("r"):
                    print(save_image_checked(raw_image, real_dir, "real", "png"))
                elif key == ord("f"):
                    print(save_image_checked(raw_image, fake_dir, "fake", "png"))
            except OSError as exc:
                print(f"Save failed: {exc}")
        return 0
    except RuntimeError as exc:
        print(f"RealSense error: {exc}")
        return 1
    finally:
        if started:
            pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    raise SystemExit(main())
