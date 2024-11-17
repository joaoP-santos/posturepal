<!-- PosturePal.vue -->
<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <header class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800">PosturePal</h1>
        <p class="text-gray-600">Your AI posture assistant</p>
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
              v-if="showPostureNotification && settings.enableNotifications"
              class="absolute top-4 left-4 bg-emerald-500 text-white px-4 py-2 rounded-full shadow-lg"
            >
              Nice posture!
            </div>
          </Transition>

          <!-- Controls -->
          <div
            v-if="isStreaming"
            class="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/50 rounded-full px-4 py-2 flex items-center space-x-4"
          >
            <button
              @click="toggleStream"
              class="text-white hover:text-gray-200 transition-colors"
              :title="isPaused ? 'Resume' : 'Pause'"
            >
              <svg
                v-if="isPaused"
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <svg
                v-else
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </button>
            <button
              @click="toggleAudio"
              class="text-white hover:text-gray-200 transition-colors"
              :title="settings.enableSound ? 'Mute' : 'Unmute'"
            >
              <svg
                v-if="settings.enableSound"
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15.536 15.536A5 5 0 0015 12v-2a4 4 0 00-4-4V5a7 7 0 017 7v2a5 5 0 01-.536 2.536z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 12v-2a7 7 0 017-7v1a4 4 0 00-4 4v2a5 5 0 01-.536 2.536L5 12z"
                />
              </svg>
              <svg
                v-else
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Statistics and Settings -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="p-4 bg-gray-50 rounded-lg">
            <h2 class="font-semibold mb-2">Posture Statistics</h2>
            <div class="space-y-2">
              <p class="text-sm text-gray-600">
                Session duration: {{ formatTime(sessionDuration) }}
              </p>
              <p class="text-sm text-gray-600">
                Good posture time: {{ formatTime(goodPostureTime) }}
              </p>
              <p class="text-sm text-gray-600">
                Posture corrections: {{ postureCorrections }}
              </p>
              <div class="mt-4">
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    class="bg-emerald-500 h-2.5 rounded-full transition-all duration-300"
                    :style="{
                      width: `${
                        (goodPostureTime / sessionDuration) * 100 || 0
                      }%`,
                    }"
                  ></div>
                </div>
                <p class="text-xs text-gray-500 mt-1">Posture Score</p>
              </div>
            </div>
          </div>
          <div class="p-4 bg-gray-50 rounded-lg">
            <h2 class="font-semibold mb-2">Settings</h2>
            <div class="space-y-3">
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="settings.enableNotifications"
                  class="form-checkbox rounded text-emerald-500"
                />
                <span class="ml-2 text-sm text-gray-600"
                  >Enable notifications</span
                >
              </label>
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="settings.enableSound"
                  class="form-checkbox rounded text-emerald-500"
                />
                <span class="ml-2 text-sm text-gray-600">Sound alerts</span>
              </label>

              <div class="pt-2">
                <button
                  @click="resetSession"
                  class="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm transition-colors"
                >
                  Reset Session
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from "vue";

// Refs & Reactive State
const webcamRef = ref(null);
const isStreaming = ref(false);
const isPaused = ref(false);
const streamingError = ref("");
const showPostureNotification = ref(false);
const sessionDuration = ref(0);
const goodPostureTime = ref(0);
const postureCorrections = ref(0);

const settings = reactive({
  enableNotifications: true,
  enableSound: true,
  autoRestart: false,
});

// Timers
let sessionTimer = null;
let notificationTimer = null;

// Methods
const initializeWebcam = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
    });
    webcamRef.value.srcObject = stream;
    isStreaming.value = true;
    startSession();
  } catch (err) {
    console.error("Error accessing webcam:", err);
    streamingError.value = "Unable to access camera. Please check permissions.";
  }
};

const startSession = () => {
  sessionTimer = setInterval(() => {
    sessionDuration.value++;
    // Simulate good posture time (replace with actual AI model inference)
    if (Math.random() > 0.3) {
      goodPostureTime.value++;
      if (!showPostureNotification.value) {
        showPostureNotification.value = true;
        if (settings.enableSound) {
          playNotificationSound();
        }
        // Hide notification after 3 seconds
        notificationTimer = setTimeout(() => {
          showPostureNotification.value = false;
        }, 3000);
      }
    } else {
      showPostureNotification.value = false;
      postureCorrections.value++;
    }
  }, 1000);
};

const toggleStream = () => {
  isPaused.value = !isPaused.value;
  const stream = webcamRef.value.srcObject;
  const tracks = stream.getTracks();

  if (isPaused.value) {
    tracks.forEach((track) => (track.enabled = false));
    clearInterval(sessionTimer);
  } else {
    tracks.forEach((track) => (track.enabled = true));
    startSession();
  }
};

const toggleAudio = () => {
  settings.enableSound = !settings.enableSound;
};

const resetSession = () => {
  sessionDuration.value = 0;
  goodPostureTime.value = 0;
  postureCorrections.value = 0;
  showPostureNotification.value = false;
};

const playNotificationSound = () => {
  // You can implement actual sound playing here
  console.log("Playing notification sound");
};

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
};

// Lifecycle hooks
onMounted(() => {
  initializeWebcam();
});

onUnmounted(() => {
  if (webcamRef.value?.srcObject) {
    webcamRef.value.srcObject.getTracks().forEach((track) => track.stop());
  }
  clearInterval(sessionTimer);
  clearTimeout(notificationTimer);
});
</script>
