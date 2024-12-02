<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-6xl mx-auto">
      <button @click="connectToSerialDevice" class="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
        Connect to Serial
      </button>
      <!-- Header -->
      <header class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800">PosturePal</h1>
        <p class="text-gray-600">Your AI posture assistant</p>
        <p v-if="postureQuality" class="text-gray-500">
          Posture Quality:
          <span
            :class="
              postureQuality === 'Good' ? 'text-blue-500' : 'text-red-500'
            "
            >{{ postureQuality }}</span>
        </p>
        <p 
            :class="
              offsetWarning ?  'text-red-500':'text-transparent'
            ">
              Please line up with the camera!
        </p>
      </header>

      <!-- Main content -->
      <div class="bg-white rounded-lg shadow-lg p-6">
        <!-- Webcam container -->
        <div
          class="relative aspect-video bg-gray-100 rounded-lg overflow-hidden mb-6"
        >
          <video
            id="webcam"
            class="w-full h-full object-cover"
            :class="{ 'opacity-50': !isStreaming }"
            autoplay
            playsinline
            ref="webcamRef"
          ></video>
          <canvas
            ref="canvasRef"
            class="absolute inset-0 w-full h-full"
            :class="{
              'border-8 border-blue-500': postureQuality === 'Good',
              'border-8 border-red-500': postureQuality === 'Bad',
            }"
          ></canvas>

          <!-- Loading state -->
          <div
            v-if="!isStreaming"
            class="absolute inset-0 flex items-center justify-center"
          >
            <div class="text-center">
              <div
                class="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mb-4"
              ></div>
              <p class="text-gray-700">
                {{ streamingError || "Initializing camera..." }}
              </p>
            </div>
          </div>

          <!-- Posture notification -->
          <Transition
            enter-active-class="transition duration-300 ease-out"
            enter-from-class="transform -translate-y-4 opacity-0"
            enter-to-class="transform translate-y-0 opacity-100"
            leave-active-class="transition duration-200 ease-in"
            leave-from-class="transform translate-y-0 opacity-100"
            leave-to-class="transform -translate-y-4 opacity-0"
          >
            <div
              v-if="showPostureNotification"
              class="absolute top-4 left-4 bg-emerald-500 text-white px-4 py-2 rounded-full shadow-lg"
            >
              Nice posture!
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import {
  PoseLandmarker,
  FilesetResolver,
  DrawingUtils,
} from "@mediapipe/tasks-vision";

// Refs & Reactive State
const webcamRef = ref(null);
const canvasRef = ref(null);
const offsetWarning = ref(false);
let canvasCtx = null;
let drawingUtils = null;
const isStreaming = ref(false);
const isPaused = ref(false);
const streamingError = ref("");
const showPostureNotification = ref(false);
const sessionDuration = ref(0);
const goodPostureTime = ref(0);
const postureCorrections = ref(0);
const postureQuality = ref(null);
let poseLandmarker = undefined;

// Serial communication state
let port = null;
let serialWriter = null;

// Helpers
function findDistance(x1, y1, x2, y2) {
  const dist = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
  return dist;
}

function findAngle(x1, y1, x2, y2) {
  const theta = Math.acos(
    ((y2 - y1) * -y1) / (Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * y1)
  );
  const degree = Math.floor(180 / Math.PI) * theta;
  return degree;
}

// Serial Communication Functions
const connectToSerialDevice = async () => {
  try {
    // If there's an existing connection, clean it up first
    if (port) {
      if (serialWriter) {
        await serialWriter.close();
        serialWriter = null;
      }
      await port.close();
      port = null;
    }

    // Request new port
    port = await navigator.serial.requestPort();
    console.log("Port selected:", port);
    
    // Open port with standard settings for Pico
    await port.open({ 
      baudRate: 9600,
      dataBits: 8,
      stopBits: 1,
      parity: "none",
      flowControl: "none"
    });
    console.log("Port opened successfully");

    // Get writer
    serialWriter = port.writable.getWriter();
    console.log("Writer obtained successfully");

    // Start reading
    readFromSerial();

    // Test the connection
    await sendDataToSerial("print('hi')");
    await sendDataToSerial("from machine import Pin");
    await sendDataToSerial("motor = Pin(16, Pin.OUT)");

    
  } catch (err) {
    console.error("Error in connectToSerialDevice:", err);
    alert("Failed to connect to serial device. Check console for details.");
  }
};

const sendDataToSerial = async (data) => {
  try {
    if (!serialWriter) {
      console.warn("No serial writer available");
      return;
    }

    // Add carriage return and newline
    const dataWithNewline = data + "\r\n";
    const encoder = new TextEncoder();
    const encoded = encoder.encode(dataWithNewline);
    
    await serialWriter.write(encoded);
    console.log("Successfully sent data:", data);
    
  } catch (error) {
    console.error("Error in sendDataToSerial:", error);
    // If there's an error, try to reconnect
    serialWriter = null;
    if (port) {
      try {
        await port.close();
      } catch (e) {
        console.error("Error closing port:", e);
      }
      port = null;
    }
  }
};

const readFromSerial = async () => {
  try {
    while (port && port.readable) {
      const reader = port.readable.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      try {
        while (true) {
          const { value, done } = await reader.read();
          if (done) {
            console.log("Serial read complete");
            break;
          }

          // Decode the received data
          const text = decoder.decode(value);
          buffer += text;

          // Split by newlines and process complete messages
          const lines = buffer.split('\n');
          buffer = lines.pop() || ""; // Keep the incomplete line in buffer

          for (const line of lines) {
            const cleanLine = line.trim();
            if (cleanLine) {
              console.log("Received serial data:", cleanLine);
              // Here you can process the received data
              // For example:
              if (cleanLine === "OK") {
                console.log("Device acknowledged command");
              }
            }
          }
        }
      } catch (error) {
        console.error("Error while reading:", error);
      } finally {
        reader.releaseLock();
      }
    }
  } catch (error) {
    console.error("Fatal reading error:", error);
  }
};

const reconnectSerial = async () => {
  try {
    if (serialWriter) {
      serialWriter.releaseLock();
    }
    if (port) {
      await port.close();
    }
    await connectToSerialDevice();
  } catch (error) {
    console.error("Error reconnecting to serial:", error);
  }
};

// Initialize PoseLandmarker
const createPoseLandmarker = async () => {
  const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm"
  );
  poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task`,
      delegate: "GPU",
    },
    runningMode: "VIDEO",
    numPoses: 2,
  });
};

function calculatePosture(landmarks) {
  if (!landmarks) return;
  const w = canvasRef.value.clientWidth;
  const h = canvasRef.value.clientHeight;

  // Left shoulder
  const leftShoulderX = Math.floor(landmarks[12].x * w);
  const leftShoulderY = Math.floor(landmarks[12].y * h);

  // Right shoulder
  const rightShoulderX = Math.floor(landmarks[11].x * w);
  const rightShoulderY = Math.floor(landmarks[11].y * h);

  // Left ear
  const leftEarX = Math.floor(landmarks[8].x * w);
  const leftEarY = Math.floor(landmarks[8].y * h);

  // Left hip
  const leftHipX = Math.floor(landmarks[24].x * w);
  const leftHipY = Math.floor(landmarks[24].y * h);

  // Calculate angles
  const neckInclination = findAngle(
    leftShoulderX,
    leftShoulderY,
    leftEarX,
    leftEarY
  );
  const torsoInclination = findAngle(
    leftHipX,
    leftHipY,
    leftShoulderX,
    leftShoulderY
  );

  const offset = findDistance(
    leftShoulderX,
    leftShoulderY,
    rightShoulderX,
    rightShoulderY
  );

  if (offset > 100) {
    offsetWarning.value = true;
  } else {
    offsetWarning.value = false;
  }

  if (neckInclination < 40 && torsoInclination < 10) {
    postureQuality.value = "Good";
    sendDataToSerial("motor.off()");
    showPostureNotification.value = true;
    setTimeout(() => {
      showPostureNotification.value = false;
    }, 2000);
  } else {
    postureQuality.value = "Bad";
    sendDataToSerial("motor.on()");
    postureCorrections.value++;
  }
}

// Initialize Webcam
const initializeWebcam = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
    });
    webcamRef.value.srcObject = stream;
    canvasCtx = canvasRef.value.getContext("2d");
    drawingUtils = new DrawingUtils(canvasCtx);

    await createPoseLandmarker();
    await predictWebcam();
    isStreaming.value = true;
  } catch (err) {
    console.error("Error accessing webcam:", err);
    streamingError.value = "Unable to access camera. Please check permissions.";
  }
};

let lastVideoTime = -1;
async function predictWebcam() {
  let startTimeMs = performance.now();
  if (lastVideoTime !== webcamRef.value.currentTime) {
    lastVideoTime = webcamRef.value.currentTime;
    poseLandmarker.detectForVideo(webcamRef.value, startTimeMs, (result) => {
      canvasCtx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
      for (const landmark of result.landmarks) {
        drawingUtils.drawLandmarks(landmark, {
          radius: 1,
        });
        drawingUtils.drawConnectors(landmark, PoseLandmarker.POSE_CONNECTIONS);
      }
      calculatePosture(result.landmarks[0]);
    });
  }

  window.requestAnimationFrame(predictWebcam);
}

// Lifecycle hooks
onMounted(() => {
  initializeWebcam();
});

onBeforeUnmount(async () => {
  if (serialWriter) {
    try {
      await serialWriter.close();
    } catch (error) {
      console.error("Error closing serial writer:", error);
    }
  }
  if (port) {
    try {
      await port.close();
    } catch (error) {
      console.error("Error closing port:", error);
    }
  }
});
</script>