<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { api } from "../api";
import ResumeTemplatePreview from "./ResumeTemplatePreview.vue";

const emit = defineEmits(["close"]);

const content = ref("");
const loading = ref(true);
const saving = ref(false);
const extracting = ref(false);
const error = ref(null);
const extractionError = ref(null);
const successMessage = ref(null);
const extractedInfo = ref(null);
const isDragging = ref(false);
const fileInput = ref(null);
const showPreview = ref(false);

async function loadResume() {
  loading.value = true;
  error.value = null;
  try {
    const data = await api.getResume();
    content.value = data?.content || "";
  } catch (err) {
    error.value = err.message || "Failed to load resume";
  } finally {
    loading.value = false;
  }
}

async function handleSave() {
  saving.value = true;
  error.value = null;
  successMessage.value = null;
  try {
    await api.saveResume(content.value);
    successMessage.value = "Resume saved successfully";
    setTimeout(() => {
      emit("close");
    }, 400);
  } catch (err) {
    error.value = err.message || "Failed to save resume";
  } finally {
    saving.value = false;
  }
}

async function processFile(file) {
  if (!file) return;
  extracting.value = true;
  extractionError.value = null;
  extractedInfo.value = null;
  try {
    const data = await api.extractResumePreview(file);
    content.value = data.content || "";
    extractedInfo.value = {
      filename: data.filename || file.name,
      char_count: data.char_count ?? (data.content ? data.content.length : 0),
    };
  } catch (err) {
    extractionError.value = err.message || "Failed to extract text from file";
  } finally {
    extracting.value = false;
    if (fileInput.value) {
      fileInput.value.value = "";
    }
  }
}

function handleFileChange(event) {
  const file = event.target.files?.[0];
  if (file) {
    processFile(file);
  }
}

function handleDrop(event) {
  isDragging.value = false;
  const file = event.dataTransfer.files?.[0];
  if (file) {
    processFile(file);
  }
}

function triggerFileInput() {
  fileInput.value?.click();
}

function handleKeyDown(event) {
  if (event.key === "Escape") {
    if (showPreview.value) {
      showPreview.value = false;
      return;
    }
    emit("close");
  }
}

onMounted(() => {
  loadResume();
  window.addEventListener("keydown", handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyDown);
});
</script>

<template>
  <div
    class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
    @click.self="emit('close')"
  >
    <div
      class="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 flex flex-col gap-4"
    >
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Master Resume</h2>
          <p class="text-sm text-slate-500">
            This base resume will be reused across all tailoring prompts.
          </p>
        </div>
        <button
          type="button"
          class="text-slate-400 hover:text-slate-600 text-lg leading-none p-1"
          @click="emit('close')"
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      <div
        v-if="error"
        class="bg-red-50 border border-red-200 text-red-600 text-sm px-3 py-2 rounded-md"
      >
        {{ error }}
      </div>

      <div
        v-if="successMessage"
        class="bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm px-3 py-2 rounded-md"
      >
        {{ successMessage }}
      </div>

      <div v-if="loading" class="py-12 text-center text-sm text-slate-400">
        Loading resume...
      </div>

      <div v-else class="flex flex-col gap-3">
        <!-- File Drop / Upload Zone -->
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.docx,.txt"
          class="hidden"
          @change="handleFileChange"
        />

        <div
          class="border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors"
          :class="[
            isDragging
              ? 'border-indigo-500 bg-indigo-50/50'
              : 'border-slate-300 hover:border-slate-400 bg-slate-50/60',
          ]"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <div v-if="extracting" class="flex items-center justify-center gap-2 py-1 text-sm text-slate-600">
            <svg
              class="animate-spin h-4 w-4 text-indigo-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span>Extracting text from file...</span>
          </div>
          <div v-else class="flex flex-col items-center justify-center gap-1">
            <div class="text-sm text-slate-600">
              <span class="font-medium text-indigo-600 hover:underline">Upload a file</span>
              or drag & drop
            </div>
            <p class="text-xs text-slate-400">PDF, DOCX, or TXT</p>
          </div>
        </div>

        <div
          v-if="extractionError"
          class="bg-red-50 border border-red-200 text-red-600 text-sm px-3 py-2 rounded-md"
        >
          {{ extractionError }}
        </div>

        <div
          v-if="extractedInfo"
          class="bg-indigo-50 border border-indigo-200 text-indigo-700 text-sm px-3.5 py-2 rounded-md flex items-center justify-between"
        >
          <span>Extracted from {{ extractedInfo.filename }} ({{ extractedInfo.char_count }} chars)</span>
          <button
            type="button"
            class="text-indigo-500 hover:text-indigo-700 ml-2 font-bold"
            @click="extractedInfo = null"
          >
            ✕
          </button>
        </div>

        <textarea
          v-model="content"
          rows="14"
          placeholder="Paste or write your full master resume here (markdown or plain text)..."
          class="w-full border border-slate-300 rounded-md p-3.5 text-sm sm:text-base font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-500 resize-y"
        ></textarea>
      </div>

      <div class="flex items-center justify-between gap-2 pt-2 border-t border-slate-100">
        <div>
          <button
            type="button"
            class="px-3.5 py-2 text-sm sm:text-base font-medium rounded-md border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50 flex items-center gap-1.5 transition-colors cursor-pointer"
            :disabled="!content || loading || extracting"
            @click="showPreview = true"
          >
            <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span>Preview &amp; Print</span>
          </button>
        </div>
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="px-4 py-2 text-sm sm:text-base font-medium rounded-md text-slate-600 hover:bg-slate-100"
            @click="emit('close')"
          >
            Discard
          </button>
          <button
            type="button"
            class="px-4 py-2 text-sm sm:text-base font-medium rounded-md bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-50 flex items-center gap-1.5 font-medium"
            :disabled="saving || loading || extracting"
            @click="handleSave"
          >
            <span v-if="saving">Saving…</span>
            <span v-else>Save Resume</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Resume Template Preview Modal -->
    <ResumeTemplatePreview
      v-if="showPreview"
      :content="content"
      title="Master Resume"
      @close="showPreview = false"
    />
  </div>
</template>
