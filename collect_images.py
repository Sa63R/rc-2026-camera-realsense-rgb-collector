"""Two-class RGB collector with frame timeout retries and counters."""

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
        help="Output root; images go to REAL/Fake subdirectories (default: captures).",
    )
    parser.add_argument("--device-serial", help="Optional RealSense serial number.")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--timeout-ms", type=int, default=2000)
    parser.add_argument("--max-retries", type=int, default=3)
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
    real_count = 0
    fake_count = 0
    try:
        pipeline.start(config)
        started = True
        print("=== RealSense RGB image collector ===")
        print("r=REAL, f=FAKE, q=quit")
        print(f"Output root: {real_dir.parent.resolve()}")

        while True:
            frames = None
            for attempt in range(1, args.max_retries + 1):
                try:
                    frames = pipeline.wait_for_frames(timeout_ms=args.timeout_ms)
                    break
                except RuntimeError as exc:
                    print(f"Frame timeout {attempt}/{args.max_retries}: {exc}")

            if frames is None:
                print("Could not receive a frame after all retries.")
                return 1

            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            raw_image = np.asanyarray(color_frame.get_data())
            preview = raw_image.copy()
            cv2.putText(
                preview,
                f"REAL: {real_count} | FAKE: {fake_count} | r/f=save, q=quit",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
            )
            cv2.imshow("RealSense RGB Collector", preview)

            key = cv2.waitKey(1) & 0xFF
            try:
                if key == ord("r"):
                    path = save_image_checked(raw_image, real_dir, "real", "jpg")
                    real_count += 1
                    print(f"Saved REAL #{real_count}: {path}")
                elif key == ord("f"):
                    path = save_image_checked(raw_image, fake_dir, "fake", "jpg")
                    fake_count += 1
                    print(f"Saved FAKE #{fake_count}: {path}")
                elif key == ord("q"):
                    break
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
        print(f"Finished: REAL={real_count}, FAKE={fake_count}")


if __name__ == "__main__":
    raise SystemExit(main())
