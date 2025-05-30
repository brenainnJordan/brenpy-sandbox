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
MODEL_ASSET_PATH = r"D:\Dev\sourced\mediapipe\face_landmarker_v2_with_blendshapes.task"

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
    face_landmarks_list = detection_result.face_landmarks
    annotated_image = np.copy(rgb_image)

    # Loop through the detected faces to visualize.
    for face_landmarks in face_landmarks_list:

        # Draw the face landmarks.
        face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()

        face_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z)
            for landmark in face_landmarks
        ])

        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_tesselation_style()
        )

        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_contours_style()
        )

        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_iris_connections_style()
        )

    return annotated_image


def plot_face_blendshapes_bar_graph(face_blendshapes):
    # Extract the face blendshapes category names and scores.
    face_blendshapes_names = [face_blendshapes_category.category_name for face_blendshapes_category in face_blendshapes]
    face_blendshapes_scores = [face_blendshapes_category.score for face_blendshapes_category in face_blendshapes]
    # The blendshapes are ordered in decreasing score value.
    face_blendshapes_ranks = range(len(face_blendshapes_names))

    fig, ax = plt.subplots(figsize=(12, 12))
    bar = ax.barh(face_blendshapes_ranks, face_blendshapes_scores, label=[str(x) for x in face_blendshapes_ranks])
    ax.set_yticks(face_blendshapes_ranks, face_blendshapes_names)
    ax.invert_yaxis()

    # Label each bar with values
    for score, patch in zip(face_blendshapes_scores, bar.patches):
        plt.text(patch.get_x() + patch.get_width(), patch.get_y(), f"{score:.4f}", va="top")

    ax.set_xlabel('Score')
    ax.set_title("Face Blendshapes")
    plt.tight_layout()
    plt.show()


def detect_image_test(img_filepath):
    # STEP 2: Create an HandLandmarker object.
    base_options = python.BaseOptions(model_asset_path=MODEL_ASSET_PATH)

    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1,
        running_mode=vision.RunningMode.IMAGE,  # IMAGE, VIDEO or LIVE_STREAM
    )

    detector = vision.FaceLandmarker.create_from_options(options)

    # STEP 3: Load the input image.
    image = mp.Image.create_from_file(img_filepath)

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

    base_options = python.BaseOptions(model_asset_path=MODEL_ASSET_PATH)

    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1,
        running_mode=vision.RunningMode.VIDEO,  # IMAGE, VIDEO or LIVE_STREAM
    )

    detector = vision.FaceLandmarker.create_from_options(options)

    previous_time_ms = int(time.time_ns()/1000)

    while True:
        time_ns = time.time_ns()
        timestamp_ms = int(time_ns / 1000)

        if timestamp_ms <= previous_time_ms:
            continue

        previous_time_ms = timestamp_ms

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
    # detect_image_test(r"D:\Dev\test_data\face_capture_basic_expressions_01\face_capture_basic_expressions_01.0001.jpg")
    detect_image_test(r"D:\Dev\test_data\big_guy_face_gray.JPG")
    # webcam_test()
    # webcam_detect()
    # print(help(mp))
    # print(dir(mp))
    # print(time.time())
