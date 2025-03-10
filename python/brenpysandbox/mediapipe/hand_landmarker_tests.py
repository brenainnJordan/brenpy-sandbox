import time
import cv2
import numpy as np
# from IPython import display
# import PIL

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe import packet_creator

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green


def cv2_imshow(a):
    """A replacement for cv2.imshow() for use in Jupyter notebooks.

    Args:
      a: np.ndarray. shape (N, M) or (N, M, 1) is an NxM grayscale image. For
        example, a shape of (N, M, 3) is an NxM BGR color image, and a shape of
        (N, M, 4) is an NxM BGRA color image.
    """
    a = a.clip(0, 255).astype('uint8')
    # cv2 stores colors as BGR; convert to RGB
    if a.ndim == 3:
        if a.shape[2] == 4:
            a = cv2.cvtColor(a, cv2.COLOR_BGRA2RGBA)
        else:
            a = cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
    display.display(PIL.Image.fromarray(a))


def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()

        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])

        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style()
        )

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (left or right hand) on the image.
        cv2.putText(annotated_image, f"{handedness[0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return annotated_image


def detect_image_test():
    # STEP 2: Create an HandLandmarker object.
    base_options = python.BaseOptions(
        # model_asset_path='hand_landmarker.task'
        model_asset_path=r"D:\Dev\sourced\mediapipe\hand_landmarker.task"
    )

    options = vision.HandLandmarkerOptions(
        base_options=base_options, num_hands=2
    )

    detector = vision.HandLandmarker.create_from_options(options)

    # STEP 3: Load the input image.
    image = mp.Image.create_from_file(
        r"D:\Dev\sourced\mediapipe\woman_hands.jpg"
    )

    # STEP 4: Detect hand landmarks from the input image.
    detection_result = detector.detect(image)

    # STEP 5: Process the classification result. In this case, visualize it.
    annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)
    # cv2_imshow(cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

    # view result
    cv2.imshow('image', cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return True


def webcam_test():
    # Open the default camera
    cam = cv2.VideoCapture(0)

    # Get the default frame width and height
    # frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    # frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

    while True:
        ret, frame = cam.read()

        # Write the frame to the output file
        # out.write(frame)

        # Display the captured frame
        cv2.imshow('Camera', frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the capture and writer objects
    cam.release()
    out.release()
    cv2.destroyAllWindows()


def webcam_detect():
    cam = cv2.VideoCapture(0)

    # STEP 2: Create an HandLandmarker object.
    base_options = python.BaseOptions(
        # model_asset_path='hand_landmarker.task'
        model_asset_path=r"D:\Dev\sourced\mediapipe\hand_landmarker.task"
    )

    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        result_callback=None,
        running_mode = vision.RunningMode.VIDEO, # IMAGE, VIDEO or LIVE_STREAM
    )

    detector = vision.HandLandmarker.create_from_options(options)

    while True:
        time_ns = time.time_ns()
        timestamp_ms = int(time_ns / 1000)

        ret, frame = cam.read()

        image = mp.Image(mp.ImageFormat.SRGB, frame)

        # image_packet = packet_creator.create_image(image, image_format=mp.ImageFormat.SRGB)
        # print(image_packet.timestamp)

        detection_result = detector.detect_for_video(image, timestamp_ms)

        annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)

        # image = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)

        cv2.imshow('Camera', annotated_image)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the capture and writer objects
    cam.release()
    cv2.destroyAllWindows()

    return True


if __name__ == "__main__":
    # detect_image_test()
    # webcam_test()
    webcam_detect()
    # print(help(mp))
    # print(dir(mp))
    # print(time.time())