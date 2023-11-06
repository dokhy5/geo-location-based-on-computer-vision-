import re
import operator
from collections import Counter
import time
import cv2
import torch
from PIL import Image
from datetime import datetime
import collections


class ObjectDetection:
    def __init__(self, model_path):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
        self.camera = cv2.VideoCapture(0)
        self.highest_letters = []
        self.highest_digits = []

    def parse_detection_line(self, line):
        """
        Parse a detection line and extract the relevant information.
        Returns a tuple: (class_label, confidence, xmin, xmax, ymin, ymax)
        """
        parts = line.strip().split(", ")
        class_label, confidence = parts[0].split(": ")
        coordinates = [float(x.split("=")[1]) for x in parts[1:]]
        return class_label, float(confidence), *coordinates

    def sort_detections_by_xmin(self, detections):
        """
        Sort the list of detections based on xmin in ascending order.
        """
        return sorted(detections, key=lambda det: det[2])

    def detect_objects(self):
        start_time = time.time()
        while True:
            ret, frame = self.camera.read()
            if not ret:
                print("Failed to capture frame from camera")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            results = self.model(pil_image)

            detections = []

            for detection in results.pandas().xyxy[0].iterrows():
                _, data = detection
                class_label = data["name"]
                confidence = data["confidence"]
                xmin, ymin, xmax, ymax = data[["xmin", "ymin", "xmax", "ymax"]]
                detections.append((class_label, confidence, xmin, xmax, ymin, ymax))

                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
                cv2.putText(frame, f"{class_label}: {confidence:.2f}", (int(xmin), int(ymin) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            detections.sort(key=lambda x: (x[2], x[4]))  # Sort detections by xmin and ymin

            with open("detected_objects.txt", "a") as f:
                for det in detections:
                    f.write(f"{det[0]}: {det[1]:.2f}, xmin={det[2]}, xmax={det[3]}, ymin={det[4]}, ymax={det[5]}\n")

            # Read and parse the detections from the file
            detections = []
            with open("detected_objects.txt", "r") as file:
                for line in file:
                    detection = self.parse_detection_line(line)
                    detections.append(detection)

            # Sort the detections based on xmin in ascending order
            sorted_detections = self.sort_detections_by_xmin(detections)

            # Find the most frequent class labels and their xmin percentages
            class_label_counts = Counter(detection[0] for detection in sorted_detections)
            class_label_percentages = {}
            for label, count in class_label_counts.items():
                xmin_sum = sum(detection[2] for detection in sorted_detections if detection[0] == label)
                xmin_percentage = xmin_sum
                class_label_percentages[label] = xmin_percentage

            # Sort class labels by their xmin percentages in ascending order
            sorted_labels = sorted(class_label_percentages.items(), key=operator.itemgetter(1))

            # Get the highest three digits and highest three letters
            highest_digits = [label for label, _ in sorted_labels if label.isdigit()][-3:]
            highest_letters = [label for label, _ in sorted_labels if label.isalpha()][-3:]

            # Print the highest three digits and letters

            # Save the new text file
            with open("detected_1.txt", "w") as f:
                for detection in sorted_detections:
                    class_label, confidence, xmin, xmax, ymin, ymax = detection
                    f.write(f"{class_label}: {confidence:.2f}, xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}\n")

            # Append the highest three digits and letters to the file
            with open("Highest.txt", "w") as f:
                result = " ".join(map(str, highest_digits)) + ' ' + ' '.join(map(str, highest_letters))
                f.write(result)
                # f.write(' '.join(highest_letters) + "\n")

            cv2.imshow("YOLOv5 Object Detection", frame)
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time >= 30:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.camera.release()
        cv2.destroyAllWindows()
        print(result)


model_path = r'C:\Users\Dokhy\Desktop\yolov5\best.pt'
object_detection = ObjectDetection(model_path)
object_detection.detect_objects()