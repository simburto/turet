import org.bytedeco.opencv.opencv_core.*;
import org.bytedeco.opencv.opencv_videoio.VideoCapture;
import org.bytedeco.opencv.global.opencv_imgproc;
import org.bytedeco.opencv.global.opencv_imgcodecs;
import org.bytedeco.opencv.global.opencv_videoio;
import org.bytedeco.javacv.*;
import org.bytedeco.javacpp.Loader;
import org.bytedeco.javacpp.Pointer;
import org.bytedeco.opencv.opencv_objdetect.CvHaarClassifierCascade;
import org.bytedeco.opencv.opencv_objdetect.CvRect;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.nio.ByteBuffer;

public class main {
    // Constants
    private static final String RASPBERRY_PICO_IP = "192.158.1.113";
    private static final int PORT = 12345;
    private static final double MIN_DETECTION_CONFIDENCE = 0.7;
    private static final double MIN_TRACKING_CONFIDENCE = 0.5;
    private static final Scalar FONT_COLOR = new Scalar(0, 0, 255, 0);
    private static final Scalar RECTANGLE_COLOR = new Scalar(0, 255, 0, 0);
    private static final Scalar CENTER_DOT_COLOR = new Scalar(0, 0, 255, 0);
    private static final int TEXT_OFFSET = 30;

    public static void main(String[] args) {
        // Initialize OpenCV and MediaPipe
        Loader.load(opencv_objdetect.class);
        Loader.load(opencv_imgproc.class);

        // Initialize pose estimator
        OpenCVFrameConverter.ToMat frameConverter = new OpenCVFrameConverter.ToMat();
        FrameGrabber grabber = new OpenCVFrameGrabber(0);
        try {
            grabber.start();
        } catch (FrameGrabber.Exception e) {
            e.printStackTrace();
        }

        // Initialize torso landmark IDs
        int[] torsoLandmarks = {
                mp_pose.PoseLandmark.LEFT_SHOULDER.ordinal(),
                mp_pose.PoseLandmark.RIGHT_SHOULDER.ordinal(),
                mp_pose.PoseLandmark.LEFT_HIP.ordinal(),
                mp_pose.PoseLandmark.RIGHT_HIP.ordinal()
        };

        // Initialize inside flag
        boolean inside = false;

        // Create a socket for UDP communication
        DatagramSocket socket = null;
        try {
            socket = new DatagramSocket();
        } catch (SocketException e) {
            e.printStackTrace();
        }

        // Initialize constants
        while (true) {
            Frame frame = null;
            try {
                frame = grabber.grab();
            } catch (FrameGrabber.Exception e) {
                e.printStackTrace();
            }
            if (frame == null) {
                break;
            }

            // Convert to Mat
            Mat mat = frameConverter.convert(frame);

            // Draw "crosshair"
            int w = mat.cols();
            int h = mat.rows();
            Point truecen = new Point(w / 2, h / 2);
            opencv_imgproc.circle(mat, truecen, 7, CENTER_DOT_COLOR, 1, 0, 0);

            // Process the frame for pose detection
            // (Replace this with your MediaPipe Pose estimation code)

            // Detect a single person and calculate bounding box coordinates for the torso
            // (Replace this with your torso detection code)

            // Calculate angles to turn the camera
            // (Replace this with your angle calculation code)

            // Convert angles to strings for drawing
            // (Replace this with your angle conversion code)

            // Send instructions to Raspberry Pi
            String hsend = "h" + horizontal_angle_str;
            String vsend = "v" + vertical_angle_str;

            // Draw angles on the frame
            opencv_imgproc.putText(mat, vertical_angle_str, new Point(30, TEXT_OFFSET), FONT, 1.0, FONT_COLOR, 1, 0, false);
            opencv_imgproc.putText(mat, horizontal_angle_str, new Point(30, TEXT_OFFSET * 2), FONT, 1.0, FONT_COLOR, 1, 0, false);

            // Draw bounding box around the torso
            // (Replace this with your bounding box drawing code)

            // Check if the center dot is inside the bounding box
            // (Replace this with your collision detection code)

            // Send instructions to Raspberry Pi
            if (inside) {
                String csend = "c";
                byte[] sendData = csend.getBytes();
                DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, InetAddress.getByName(RASPBERRY_PICO_IP), PORT);
                try {
                    socket.send(sendPacket);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            } else {
                byte[] sendData1 = vsend.getBytes();
                DatagramPacket sendPacket1 = new DatagramPacket(sendData1, sendData1.length, InetAddress.getByName(RASPBERRY_PICO_IP), PORT);
                try {
                    socket.send(sendPacket1);
                } catch (IOException e) {
                    e.printStackTrace();
                }
                try {
                    Thread.sleep(50); // Sleep for 50 milliseconds
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                byte[] sendData2 = hsend.getBytes();
                DatagramPacket sendPacket2 = new DatagramPacket(sendData2, sendData2.length, InetAddress.getByName(RASPBERRY_PICO_IP), PORT);
                try {
                    socket.send(sendPacket2);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }

            // Display the frame
            CanvasFrame canvas = new CanvasFrame("Output", CanvasFrame.getDefaultGamma() / grabber.getGamma());
            if (canvas.isResizable()) {
                canvas.setCanvasSize(mat.cols(), mat.rows());
            }
            canvas.showImage(frameConverter.convert(mat));

            // Break the loop on 'q' key press
            char key = (char) canvas.waitKey(1);
            if (key == 'q') {
                break;
            }
        }

        // Release resources
        grabber.stop();
        grabber.release();
        socket.close();
        System.exit(0);
    }
}
