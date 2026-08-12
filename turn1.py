"""RGB/depth click-to-coordinate experiment with a rotation-only transform."""

from __future__ import annotations

import argparse
import math

import cv2
import numpy as np
import pyrealsense2 as rs

from capture_utils import (
    enable_selected_device,
    prepare_class_directories,
    save_image_checked,
)

click_point: tuple[int, int] | None = None
manual_angles = [0.0, 0.0, 0.0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="captures")
    parser.add_argument("--device-serial")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument(
        "--angles",
        type=float,
        nargs=3,
        metavar=("RX", "RY", "RZ"),
        help="Initial roll/pitch/yaw in degrees; otherwise prompt in the terminal.",
    )
    return parser.parse_args()


def rotation_matrix(rx: float, ry: float, rz: float) -> np.ndarray:
    """Return the historical rotation convention used by this experiment."""
    rx_rad, ry_rad, rz_rad = map(math.radians, (rx, ry, rz))
    cr, sr = math.cos(rx_rad), math.sin(rx_rad)
    cp, sp = math.cos(ry_rad), math.sin(ry_rad)
    cy, sy = math.cos(rz_rad), math.sin(rz_rad)
    return np.array(
        [
            [cy * cp, sy * cp, -sp],
            [cy * sp * sr - sy * cr, sy * sp * sr + cy * cr, cp * sr],
            [cy * sp * cr + sy * sr, sy * sp * cr - cy * sr, cp * cr],
        ]
    )


def rotate_camera_point(camera_point, matrix: np.ndarray) -> np.ndarray:
    """Rotate a camera-frame point; no translation or robot TF is applied."""
    return matrix.T @ np.asarray(camera_point, dtype=float)


def deproject_click(depth_frame, color_intrinsics, x: int, y: int):
    depth_m = depth_frame.get_distance(x, y)
    if not 0.1 <= depth_m <= 5.0:
        return None
    return rs.rs2_deproject_pixel_to_point(color_intrinsics, [x, y], depth_m)


def mouse_callback(event, x, y, _flags, _param) -> None:
    global click_point
    if event == cv2.EVENT_LBUTTONDOWN:
        click_point = (x, y)


def prompt_angles() -> list[float]:
    print("Enter camera rotation in degrees (0 0 0 for no rotation).")
    try:
        return [
            float(input("Roll Rx: ")),
            float(input("Pitch Ry: ")),
            float(input("Yaw Rz: ")),
        ]
    except ValueError:
        print("Invalid number; using 0 0 0.")
        return [0.0, 0.0, 0.0]


def main() -> int:
    global click_point, manual_angles
    args = parse_args()
    if args.angles is not None:
        manual_angles = list(args.angles)
    else:
        manual_angles = prompt_angles()

    real_dir, fake_dir = prepare_class_directories(args.output_dir)
    pipeline = rs.pipeline()
    config = rs.config()
    enable_selected_device(config, args.device_serial)
    config.enable_stream(
        rs.stream.color, args.width, args.height, rs.format.bgr8, args.fps
    )
    config.enable_stream(
        rs.stream.depth, args.width, args.height, rs.format.z16, args.fps
    )
    align = rs.align(rs.stream.color)

    started = False
    try:
        pipeline.start(config)
        started = True
        cv2.namedWindow("Color Stream", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Color Stream", mouse_callback)
        print("Click=color coordinate | a=angles | r/f=save raw RGB | q=quit")
        print("Warning: the rotated coordinate is not a calibrated world coordinate.")

        while True:
            aligned = align.process(pipeline.wait_for_frames(timeout_ms=3000))
            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()
            if not color_frame or not depth_frame:
                continue

            raw_image = np.asanyarray(color_frame.get_data())
            depth_data = np.asanyarray(depth_frame.get_data())
            preview = raw_image.copy()
            cv2.putText(
                preview,
                f"Angles: {manual_angles} | click=point | a=reset",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )
            cv2.putText(
                preview,
                "r=REAL | f=FAKE | q=quit (saves raw RGB)",
                (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

            if click_point is not None:
                x, y = click_point
                click_point = None
                intrinsics = (
                    color_frame.profile.as_video_stream_profile().get_intrinsics()
                )
                camera_point = deproject_click(depth_frame, intrinsics, x, y)
                if camera_point is None:
                    print(f"No valid depth at pixel ({x}, {y}).")
                else:
                    rotated_point = rotate_camera_point(
                        camera_point, rotation_matrix(*manual_angles)
                    )
                    print(
                        "Camera frame [m]: "
                        f"X={camera_point[0]:.3f}, Y={camera_point[1]:.3f}, "
                        f"Z={camera_point[2]:.3f}"
                    )
                    print(
                        "Rotation-only frame [m]: "
                        f"X={rotated_point[0]:.3f}, Y={rotated_point[1]:.3f}, "
                        f"Z={rotated_point[2]:.3f}"
                    )
                    cv2.circle(preview, (x, y), 4, (0, 0, 255), -1)

            depth_preview = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_data, alpha=0.1), cv2.COLORMAP_JET
            )
            cv2.imshow("Depth Stream", depth_preview)
            cv2.imshow("Color Stream", preview)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("a"):
                manual_angles = prompt_angles()
                continue
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
