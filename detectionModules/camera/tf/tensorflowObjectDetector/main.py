import tensorflow as tf
import numpy as np
import time


class TensorflowObjectDetector():
    # all the models would have been built and frozen at a checkpoint, it contains the checkpoint, protonbuffer,and configs used to train
    def __init__(self, path_to_checkpoint):
        print("LOADING MODEL......")
        self.path_to_checkpoint = path_to_checkpoint
        self.detection_graph = tf.Graph()

        with self.detection_graph.as_default():
            object_detection_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(self.path_to_checkpoint, 'rb') as fid:
                serialized_graph = fid.read()
                object_detection_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(object_detection_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.compat.v1.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name(
            'image_tensor:0')

        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name(
            'detection_boxes:0')

        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name(
            'detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name(
            'detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name(
            'num_detections:0')
        print("LOADED")

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)

        # Actual detection.
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores,
                self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})

        im_height, im_width, _ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0, i, 0] * im_height),
                             int(boxes[0, i, 1]*im_width),
                             int(boxes[0, i, 2] * im_height),
                             int(boxes[0, i, 3]*im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()
