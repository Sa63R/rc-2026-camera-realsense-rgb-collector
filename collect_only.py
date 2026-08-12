"""Low-bandwidth, single-class RealSense RGB photo collector."""

from __future__ import annotations

import argparse
import time

import cv2
import numpy as np
import pyrealsense2 as rs

from capture_utils import (
    enable_selected_device,
    prepare_directory,
    save_image_checked,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="captures/real",
        help="Directory for the single captured class (default: captures/real).",
    )
    parser.add_argument("--device-serial", help="Optional RealSense serial number.")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--format", choices=("jpg", "png"), default="jpg")
    parser.add_argument("--jpeg-quality", type=int, choices=range(1, 101), default=80)
    parser.add_argument(
        "--manual-exposure",
        type=float,
        help="Disable auto exposure and request this sensor exposure value.",
    )
    return parser.parse_args()


def start_camera(args: argparse.Namespace):
    pipeline = rs.pipeline()
    config = rs.config()
    enable_selected_device(config, args.device_serial)
    config.enable_stream(
        rs.stream.color, args.width, args.height, rs.format.bgr8, args.fps
    )

    last_error = None
    profile = None
    for attempt in range(1, 4):
        try:
            profile = pipeline.start(config)
            break
        except RuntimeError as exc:
            last_error = exc
            print(f"Camera start failed ({attempt}/3): {exc}")
            time.sleep(1)
    if profile is None:
        raise RuntimeError(f"Camera failed to start after 3 attempts: {last_error}")

    try:
        sensor = profile.get_device().first_color_sensor()
        if args.manual_exposure is None:
            sensor.set_option(rs.option.enable_auto_exposure, 1)
        else:
            sensor.set_option(rs.option.enable_auto_exposure, 0)
            sensor.set_option(rs.option.exposure, args.manual_exposure)
    except RuntimeError:
        pipeline.stop()
        raise
    return pipeline


def capture_photos(pipeline, args: argparse.Namespace, output_dir) -> None:
    print("Space=save image, Esc=quit")
    print(f"Output: {output_dir.resolve()}")
    cv2.namedWindow("Capture", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Capture", args.width, args.height)
    count = 0

    while True:
        color_frame = None
        for attempt in range(1, 4):
            try:
                frames = pipeline.wait_for_frames(timeout_ms=10_000)
                color_frame = frames.get_color_frame()
                if color_frame:
                    break
            except RuntimeError as exc:
                print(f"Frame wait failed ({attempt}/3): {exc}")

        if not color_frame:
            print("No color frame received; retrying.")
            continue

        raw_image = np.asanyarray(color_frame.get_data())
        preview = raw_image.copy()
        cv2.putText(
            preview,
            f"Saved: {count} | Space=save | Esc=quit",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2,
        )
        cv2.imshow("Capture", preview)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        if key == 32:
            params = None
            if args.format == "jpg":
                params = [cv2.IMWRITE_JPEG_QUALITY, args.jpeg_quality]
            try:
                path = save_image_checked(
                    raw_image, output_dir, "real_photo", args.format, params
                )
                count += 1
                print(f"Saved #{count}: {path}")
            except OSError as exc:
                print(f"Save failed: {exc}")


def main() -> int:
    args = parse_args()
    output_dir = prepare_directory(args.output_dir)
    pipeline = None
    try:
        pipeline = start_camera(args)
        capture_photos(pipeline, args, output_dir)
        return 0
    except RuntimeError as exc:
        print(f"RealSense error: {exc}")
        return 1
    finally:
        if pipeline is not None:
            pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    raise SystemExit(main())
