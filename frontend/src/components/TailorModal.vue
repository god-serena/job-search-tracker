<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { api } from "../api";
import ResumeTemplatePreview from "./ResumeTemplatePreview.vue";

const props = defineProps({
  application: { type: Object, required: true },
});

const emit = defineEmits(["close"]);

// Active Tab
const previewContent = ref(null);
const previewModalOpen = ref(false);
const latestGeneratedResume = ref(null);

function openPreview(c) {
  previewContent.value = c || "";
  previewModalOpen.value = true;
}

const activeTab = ref("resume"); // "resume" | "cover-letter" | "outreach"

// ==================== TAB 1: TAILORED RESUME STATE ====================
const prompt = ref("");
const loadingPrompt = ref(true);
const promptError = ref(null);
const copiedPrompt = ref(false);

const localModel = ref("Swift-1.5-Qwen3.8-27B-GSQ-RCO");
const generatingLocal = ref(false);
const localError = ref(null);
const localSuccess = ref(null);

const sources = ["ChatGPT", "Claude", "Gemini", "Other"];
const selectedSource = ref("ChatGPT");
const pastedResume = ref("");
const savingVersion = ref(false);
const saveError = ref(null);
const saveSuccess = ref(null);

const versions = ref([]);
const loadingVersions = ref(true);
const versionsError = ref(null);
const copiedVersionId = ref(null);
const expandedVersionIds = ref(new Set());

// ==================== TAB 2: COVER LETTER STATE ====================
const coverLetterModel = ref("Swift-1.5-Qwen3.8-27B-GSQ-RCO");
const generatingCoverLetter = ref(false);
const coverLetterError = ref(null);
const coverLetterSuccess = ref(null);
const generatedCoverLetter = ref("");
const copiedCoverLetter = ref(false);

const coverLetterPrompt = ref("");
const loadingCoverLetterPrompt = ref(false);
const coverLetterPromptError = ref(null);
const copiedCoverLetterPrompt = ref(false);
const showCoverLetterPrompt = ref(false);

// ==================== TAB 3: OUTREACH & FOLLOW-UP STATE ====================
const outreachTemplateType = ref("cold_outreach");
const outreachTemplates = [
  { value: "cold_outreach", label: "Cold Outreach" },
  { value: "thank_you", label: "Post-Interview Thank You" },
  { value: "follow_up", label: "Status Follow-up" },
];
const outreachModel = ref("Swift-1.5-Qwen3.8-27B-GSQ-RCO");
const generatingOutreach = ref(false);
const outreachError = ref(null);
const outreachSuccess = ref(null);
const generatedOutreach = ref("");
const copiedOutreach = ref(false);

const outreachPrompt = ref("");
const loadingOutreachPrompt = ref(false);
const outreachPromptError = ref(null);
const copiedOutreachPrompt = ref(false);
const showOutreachPrompt = ref(false);

// ==================== COMPUTED PROPERTIES ====================
const isResumeMissing = computed(() => {
  return (
    promptError.value &&
    (promptError.value.toLowerCase().includes("base resume") ||
      promptError.value.toLowerCase().includes("master resume"))
  );
});

const isDescriptionMissing = computed(() => {
  return (
    promptError.value &&
    promptError.value.toLowerCase().includes("job description")
  );
});

const sortedVersions = computed(() => {
  return [...versions.value].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );
});

// ==================== RESUME METHODS ====================
async function loadPrompt() {
  loadingPrompt.value = true;
  promptError.value = null;
  try {
    const res = await api.getTailorPrompt(props.application.id);
    prompt.value = res.prompt;
  } catch (err) {
    promptError.value = err.message || "Failed to load tailoring prompt";
  } finally {
    loadingPrompt.value = false;
  }
}

async function loadVersions() {
  loadingVersions.value = true;
  versionsError.value = null;
  try {
    const res = await api.listTailoredResumes(props.application.id);
    versions.value = Array.isArray(res) ? res : [];
  } catch (err) {
    versionsError.value = err.message || "Failed to load tailored resume history";
  } finally {
    loadingVersions.value = false;
  }
}

async function copyPrompt() {
  if (!prompt.value) return;
  try {
    await navigator.clipboard.writeText(prompt.value);
    copiedPrompt.value = true;
    setTimeout(() => {
      copiedPrompt.value = false;
    }, 2000);
  } catch (err) {
    console.error("Failed to copy prompt to clipboard", err);
  }
}

async function generateLocalResume() {
  if (generatingLocal.value) return;
  generatingLocal.value = true;
  localError.value = null;
  localSuccess.value = null;

  try {
    const modelParam = localModel.value.trim() || undefined;
    const res = await api.generateLocalTailoredResume(props.application.id, modelParam);
    latestGeneratedResume.value = res?.content || null;
    localSuccess.value = "Tailored resume generated and saved successfully!";
    setTimeout(() => {
      localSuccess.value = null;
    }, 4000);
    await loadVersions();
  } catch (err) {
    localError.value = err.message || "Failed to generate tailored resume with local LLM";
  } finally {
    generatingLocal.value = false;
  }
}

async function saveVersion() {
  if (!pastedResume.value.trim() || savingVersion.value) return;
  savingVersion.value = true;
  saveError.value = null;
  saveSuccess.value = null;

  try {
    await api.saveTailoredResume(props.application.id, {
      content: pastedResume.value.trim(),
      source: selectedSource.value,
    });
    pastedResume.value = "";
    saveSuccess.value = "Tailored version saved successfully!";
    setTimeout(() => {
      saveSuccess.value = null;
    }, 3000);
    await loadVersions();
  } catch (err) {
    saveError.value = err.message || "Failed to save tailored resume";
  } finally {
    savingVersion.value = false;
  }
}

async function copyVersion(item) {
  if (!item?.content) return;
  try {
    await navigator.clipboard.writeText(item.content);
    copiedVersionId.value = item.id;
    setTimeout(() => {
      if (copiedVersionId.value === item.id) {
        copiedVersionId.value = null;
      }
    }, 2000);
  } catch (err) {
    console.error("Failed to copy version content", err);
  }
}

function toggleExpand(id) {
  const updated = new Set(expandedVersionIds.value);
  if (updated.has(id)) {
    updated.delete(id);
  } else {
    updated.add(id);
  }
  expandedVersionIds.value = updated;
}

function formatDate(isoString) {
  if (!isoString) return "";
  try {
    const d = new Date(isoString);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return isoString;
  }
}

function getSourceBadgeClass(source) {
  if (source && source.startsWith("local:")) {
    return "bg-indigo-50 text-indigo-700 border-indigo-200";
  }
  switch (source) {
    case "ChatGPT":
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
    case "Claude":
      return "bg-amber-50 text-amber-800 border-amber-200";
    case "Gemini":
      return "bg-sky-50 text-sky-700 border-sky-200";
    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}

// ==================== COVER LETTER METHODS ====================
async function loadCoverLetterPrompt() {
  loadingCoverLetterPrompt.value = true;
  coverLetterPromptError.value = null;
  try {
    const res = await api.getCoverLetterPrompt(props.application.id);
    coverLetterPrompt.value = res.prompt;
  } catch (err) {
    coverLetterPromptError.value =
      err.message || "Failed to load cover letter prompt";
  } finally {
    loadingCoverLetterPrompt.value = false;
  }
}

async function copyCoverLetterPrompt() {
  if (!coverLetterPrompt.value) return;
  try {
    await navigator.clipboard.writeText(coverLetterPrompt.value);
    copiedCoverLetterPrompt.value = true;
    setTimeout(() => {
      copiedCoverLetterPrompt.value = false;
    }, 2000);
  } catch (err) {
    console.error("Failed to copy cover letter prompt", err);
  }
}

async function generateCoverLetter() {
  if (generatingCoverLetter.value) return;
  generatingCoverLetter.value = true;
  coverLetterError.value = null;
  coverLetterSuccess.value = null;

  try {
    const modelParam = coverLetterModel.value.trim() || undefined;
    const res = await api.generateLocalCoverLetter(
      props.application.id,
      modelParam
    );
    generatedCoverLetter.value = res.content;
    coverLetterSuccess.value = "Cover letter generated successfully!";
    setTimeout(() => {
      coverLetterSuccess.value = null;
    }, 4000);
  } catch (err) {
    coverLetterError.value =
      err.message || "Failed to generate cover letter with local LLM";
  } finally {
    generatingCoverLetter.value = false;
  }
}

async function copyCoverLetter() {
  if (!generatedCoverLetter.value) return;
  try {
    await navigator.clipboard.writeText(generatedCoverLetter.value);
    copiedCoverLetter.value = true;
    setTimeout(() => {
      copiedCoverLetter.value = false;
    }, 2000);
  } catch (err) {
    console.error("Failed to copy cover letter", err);
  }
}

// ==================== OUTREACH METHODS ====================
async function loadOutreachPrompt() {
  loadingOutreachPrompt.value = true;
  outreachPromptError.value = null;
  try {
    const res = await api.getOutreachPrompt(
      props.application.id,
      outreachTemplateType.value
    );
    outreachPrompt.value = res.prompt;
  } catch (err) {
    outreachPromptError.value =
      err.message || "Failed to load outreach prompt";
  } finally {
    loadingOutreachPrompt.value = false;
  }
}

async function copyOutreachPrompt() {
  if (!outreachPrompt.value) return;
  try {
    await navigator.clipboard.writeText(outreachPrompt.value);
    copiedOutreachPrompt.value = true;
    setTimeout(() => {
      copiedOutreachPrompt.value = false;
    }, 2000);
  } catch (err) {
    console.error("Failed to copy outreach prompt", err);
  }
}

function onSelectTemplate(template) {
  outreachTemplateType.value = template;
  loadOutreachPrompt();
}

async function generateOutreach() {
  if (generatingOutreach.value) return;
  generatingOutreach.value = true;
  outreachError.value = null;
  outreachSuccess.value = null;

  try {
    const modelParam = outreachModel.value.trim() || undefined;
    const res = await api.generateLocalOutreach(
      props.application.id,
      outreachTemplateType.value,
      modelParam
    );
    generatedOutreach.value = res.content;
    outreachSuccess.value = "Outreach message generated successfully!";
    setTimeout(() => {
      outreachSuccess.value = null;
    }, 4000);
  } catch (err) {
    outreachError.value =
      err.message || "Failed to generate outreach message with local LLM";
  } finally {
    generatingOutreach.value = false;
  }
}

async function copyOutreach() {
  if (!generatedOutreach.value) return;
  try {
    await navigator.clipboard.writeText(generatedOutreach.value);
    copiedOutreach.value = true;
    setTimeout(() => {
      copiedOutreach.value = false;
    }, 2000);
  } catch (err) {
    console.error("Failed to copy outreach message", err);
  }
}

// Watch tab change to lazy-load prompts
watch(activeTab, (newTab) => {
  if (newTab === "cover-letter" && !coverLetterPrompt.value && !loadingCoverLetterPrompt.value) {
    loadCoverLetterPrompt();
  } else if (newTab === "outreach" && !outreachPrompt.value && !loadingOutreachPrompt.value) {
    loadOutreachPrompt();
  }
});

function handleKeyDown(event) {
  if (event.key === "Escape") {
    if (previewModalOpen.value) {
      previewModalOpen.value = false;
      return;
    }
    emit("close");
  }
}

onMounted(() => {
  loadPrompt();
  loadVersions();
  window.addEventListener("keydown", handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyDown);
});
</script>

<template>
  <div
    class="fixed inset-0 bg-black/40 flex items-start justify-center overflow-y-auto z-50 p-4 sm:p-6"
    @click.self="emit('close')"
  >
    <div
      class="bg-white rounded-xl shadow-xl w-full max-w-3xl my-6 sm:my-8 p-6 flex flex-col gap-5"
    >
      <!-- Header -->
      <div class="flex items-start justify-between border-b border-slate-100 pb-3">
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-xl font-bold text-slate-800">
              AI Application Copilot
            </h2>
            <span class="text-sm bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">
              {{ application.company }}
            </span>
          </div>
          <p class="text-sm text-slate-500 mt-0.5">
            {{ application.role }}
          </p>
        </div>
        <button
          type="button"
          class="text-slate-400 hover:text-slate-600 text-lg leading-none p-1 rounded hover:bg-slate-100 transition-colors"
          @click="emit('close')"
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      <!-- Tab Navigation -->
      <div class="flex border-b border-slate-200 gap-1 -mt-2">
        <button
          type="button"
          class="px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors flex items-center gap-1.5"
          :class="
            activeTab === 'resume'
              ? 'border-amber-600 text-amber-900 font-semibold'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
          "
          @click="activeTab = 'resume'"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Tailored Resume
        </button>
        <button
          type="button"
          class="px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors flex items-center gap-1.5"
          :class="
            activeTab === 'cover-letter'
              ? 'border-amber-600 text-amber-900 font-semibold'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
          "
          @click="activeTab = 'cover-letter'"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Cover Letter
        </button>
        <button
          type="button"
          class="px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors flex items-center gap-1.5"
          :class="
            activeTab === 'outreach'
              ? 'border-amber-600 text-amber-900 font-semibold'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
          "
          @click="activeTab = 'outreach'"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          Outreach & Follow-up
        </button>
      </div>

      <!-- ==================== TAB 1: TAILORED RESUME CONTENT ==================== -->
      <div v-show="activeTab === 'resume'" class="flex flex-col gap-6">
        <!-- Section 1: Generated Prompt -->
        <section class="flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-base font-bold text-slate-800">
                Tailoring Prompt
              </h3>
              <p class="text-sm text-slate-500">
                Copy this prompt and paste it into your AI assistant, or generate directly below with local LLM.
              </p>
            </div>
            <button
              v-if="!promptError && !loadingPrompt"
              type="button"
              class="px-3 py-1.5 text-sm font-medium rounded-md flex items-center gap-1.5 transition-colors shadow-sm"
              :class="copiedPrompt ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-white hover:bg-slate-700'"
              @click="copyPrompt"
            >
              <svg v-if="copiedPrompt" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              <span>{{ copiedPrompt ? 'Copied!' : 'Copy Prompt' }}</span>
            </button>
          </div>

          <!-- Prompt Loading -->
          <div v-if="loadingPrompt" class="py-8 text-center text-sm text-slate-400 bg-slate-50 rounded-lg border border-slate-200">
            Generating tailoring prompt...
          </div>

          <!-- Prompt Error Alert Box -->
          <div
            v-else-if="promptError"
            class="p-4 bg-amber-50 border border-amber-200 rounded-lg text-sm flex flex-col gap-2"
          >
            <div class="flex items-start gap-2.5">
              <svg class="w-4 h-4 text-amber-600 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div class="flex-1">
                <p class="font-semibold text-amber-900">{{ promptError }}</p>
                <p v-if="isResumeMissing" class="mt-1 text-amber-800 leading-relaxed">
                  A base resume is required to build tailoring prompts. Please click the <strong>Resume</strong> button in the top navigation bar to configure your master resume first.
                </p>
                <p v-else-if="isDescriptionMissing" class="mt-1 text-amber-800 leading-relaxed">
                  This application requires a job description. Please edit this application on the board and paste the job description text.
                </p>
                <p v-else class="mt-1 text-amber-800 leading-relaxed">
                  Please verify application details and base resume configuration.
                </p>
              </div>
              <button
                type="button"
                class="px-2.5 py-1 text-sm font-medium bg-amber-100 hover:bg-amber-200 text-amber-900 rounded shrink-0 border border-amber-300 transition-colors"
                @click="loadPrompt"
              >
                View Prompt
              </button>
            </div>
          </div>

          <!-- Prompt Display -->
          <div v-else>
            <textarea
              readonly
              :value="prompt"
              rows="6"
              class="w-full bg-slate-50 border border-slate-300 rounded-md p-3 text-sm font-mono text-slate-800 focus:outline-none resize-y selection:bg-amber-200"
            ></textarea>
          </div>
        </section>

        <!-- Section 2: Generate with Local LLM -->
        <section class="flex flex-col gap-3 pt-3 border-t border-slate-100">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h3 class="text-base font-bold text-slate-800 flex items-center gap-1.5">
                <span>Generate with Local LLM</span>
                <span class="text-xs font-normal bg-indigo-50 text-indigo-700 border border-indigo-200 px-1.5 py-0.5 rounded">
                  Direct Integration
                </span>
              </h3>
              <p class="text-sm text-slate-500">
                Run prompt directly through a local Ollama or compatible LLM instance.
              </p>
            </div>
          </div>

          <!-- Local Generation Error Alert Banner -->
          <div
            v-if="localError"
            class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800 flex items-start gap-2.5"
          >
            <svg class="w-4 h-4 text-red-600 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div class="flex-1">
              <p class="font-semibold">{{ localError }}</p>
              <p class="mt-0.5 text-red-600 text-xs">
                Ensure your local LLM service (Ollama) is active at the configured endpoint and the specified model is installed.
              </p>
            </div>
            <button
              type="button"
              class="text-red-500 hover:text-red-700 text-sm font-bold leading-none px-1"
              @click="localError = null"
              aria-label="Dismiss error"
            >
              ✕
            </button>
          </div>

          <!-- Local Generation Success Alert Banner -->
          <div
            v-if="localSuccess"
            class="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-800 flex items-center justify-between gap-2 flex-wrap"
          >
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="font-medium">{{ localSuccess }}</span>
            </div>
            <button
              v-if="latestGeneratedResume"
              type="button"
              class="px-2.5 py-1 text-sm font-medium rounded bg-emerald-700 hover:bg-emerald-800 text-white flex items-center gap-1 transition-colors cursor-pointer"
              @click="openPreview(latestGeneratedResume)"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              <span>Preview &amp; Print</span>
            </button>
          </div>

          <div class="flex items-center gap-3 flex-wrap">
            <div class="flex items-center gap-2 flex-1 min-w-[200px]">
              <label for="local-llm-model" class="text-sm text-slate-600 font-medium whitespace-nowrap">
                Model:
              </label>
              <input
                id="local-llm-model"
                v-model="localModel"
                type="text"
                placeholder="Swift-1.5-Qwen3.8-27B-GSQ-RCO"
                class="w-full border border-slate-300 rounded-md px-3 py-1.5 text-sm text-slate-800 focus:outline-none focus:ring-1 focus:ring-slate-400 placeholder:text-slate-400"
                :disabled="generatingLocal"
              />
            </div>

            <button
              type="button"
              class="px-4 py-1.5 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors shadow-sm shrink-0"
              :disabled="generatingLocal || Boolean(promptError)"
              @click="generateLocalResume"
            >
              <svg
                v-if="generatingLocal"
                class="w-3.5 h-3.5 animate-spin"
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
              <svg
                v-else
                class="w-3.5 h-3.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              <span>{{ generatingLocal ? "Generating…" : "Generate Tailored Resume" }}</span>
            </button>
          </div>

          <!-- Generating in-progress info box -->
          <div
            v-if="generatingLocal"
            class="p-3 bg-indigo-50 border border-indigo-100 rounded-lg text-sm text-indigo-700 flex items-center gap-2.5 animate-pulse"
          >
            <svg class="w-4 h-4 animate-spin text-indigo-600 shrink-0" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <div>
              <p class="font-medium">Sending prompt to local LLM ({{ localModel || 'llama3' }})...</p>
              <p class="text-xs text-indigo-600">Local generation may take several seconds depending on your hardware.</p>
            </div>
          </div>
        </section>

        <!-- Section 3: Paste-back Section -->
        <section class="flex flex-col gap-3 pt-3 border-t border-slate-100">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-base font-bold text-slate-800">
                Save Tailored Result Manually
              </h3>
              <p class="text-sm text-slate-500">
                Paste the AI-tailored resume here to store it in this application's history.
              </p>
            </div>

            <!-- Source dropdown -->
            <div class="flex items-center gap-2">
              <label for="ai-source" class="text-sm text-slate-500 font-medium">Source:</label>
              <select
                id="ai-source"
                v-model="selectedSource"
                class="border border-slate-300 rounded-md px-2.5 py-1 text-sm bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-slate-400"
              >
                <option v-for="s in sources" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
          </div>

          <div v-if="saveError" class="bg-red-50 border border-red-200 text-red-600 text-sm px-3 py-2 rounded-md">
            {{ saveError }}
          </div>

          <div v-if="saveSuccess" class="bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm px-3 py-2 rounded-md">
            {{ saveSuccess }}
          </div>

          <textarea
            v-model="pastedResume"
            rows="5"
            placeholder="Paste the generated tailored resume here (Markdown or plain text)..."
            class="w-full border border-slate-300 rounded-md p-3 text-sm font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-500 resize-y"
          ></textarea>

          <div class="flex items-center justify-end gap-2">
            <button
              type="button"
              class="px-4 py-1.5 text-sm font-medium rounded-md bg-amber-600 text-white hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 transition-colors shadow-sm"
              :disabled="!pastedResume.trim() || savingVersion"
              @click="saveVersion"
            >
              <svg v-if="savingVersion" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ savingVersion ? "Saving..." : "Save to History" }}</span>
            </button>
          </div>
        </section>

        <!-- Section 4: Version History Section -->
        <section class="flex flex-col gap-3 pt-3 border-t border-slate-100">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <h3 class="text-base font-bold text-slate-800">
                Version History
              </h3>
              <span
                v-if="sortedVersions.length"
                class="text-sm bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium"
              >
                {{ sortedVersions.length }}
              </span>
            </div>
            <button
              type="button"
              class="text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors"
              @click="loadVersions"
            >
              Refresh History
            </button>
          </div>

          <div v-if="versionsError" class="text-sm text-red-600 bg-red-50 p-2.5 rounded border border-red-200">
            {{ versionsError }}
          </div>

          <div v-if="loadingVersions" class="py-6 text-center text-sm text-slate-400">
            Loading history...
          </div>

          <div
            v-else-if="!sortedVersions.length"
            class="py-6 text-center text-sm text-slate-400 italic bg-slate-50 rounded-lg border border-slate-100"
          >
            No tailored resume versions saved yet. Generate one with local LLM or paste one above to get started.
          </div>

          <!-- Versions list -->
          <div v-else class="flex flex-col gap-2.5">
            <div
              v-for="v in sortedVersions"
              :key="v.id"
              class="border border-slate-200 rounded-lg p-3 bg-white shadow-xs hover:border-slate-300 transition-colors flex flex-col gap-2"
            >
              <div class="flex items-center justify-between gap-2 flex-wrap">
                <div class="flex items-center gap-2">
                  <span
                    class="px-2 py-0.5 rounded text-xs font-semibold border"
                    :class="getSourceBadgeClass(v.source)"
                  >
                    {{ v.source }}
                  </span>
                  <span class="text-sm text-slate-400">
                    {{ formatDate(v.created_at) }}
                  </span>
                </div>

                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2.5 py-1 text-sm font-medium rounded border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center gap-1 transition-colors"
                    title="Preview formatted template or print to PDF"
                    @click="openPreview(v.content)"
                  >
                    <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                    <span>Preview &amp; Print</span>
                  </button>

                  <button
                    type="button"
                    class="px-2.5 py-1 text-sm font-medium rounded border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center gap-1 transition-colors"
                    @click="copyVersion(v)"
                  >
                    <svg v-if="copiedVersionId === v.id" class="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <svg v-else class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                    </svg>
                    <span>{{ copiedVersionId === v.id ? 'Copied!' : 'Copy' }}</span>
                  </button>

                  <button
                    type="button"
                    class="px-2.5 py-1 text-sm font-medium rounded border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center gap-1 transition-colors"
                    @click="toggleExpand(v.id)"
                  >
                    <span>{{ expandedVersionIds.has(v.id) ? 'Collapse' : 'Expand' }}</span>
                    <svg
                      class="w-3.5 h-3.5 text-slate-400 transform transition-transform"
                      :class="{ 'rotate-180': expandedVersionIds.has(v.id) }"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Content preview -->
              <pre
                v-if="expandedVersionIds.has(v.id)"
                class="mt-1 p-3 bg-slate-50 border border-slate-200 rounded text-sm font-mono text-slate-800 whitespace-pre-wrap max-h-80 overflow-y-auto"
              >{{ v.content }}</pre>
              <p
                v-else
                class="text-sm text-slate-500 font-mono bg-slate-50 px-2.5 py-1.5 rounded border border-slate-100 line-clamp-2 truncate"
              >
                {{ v.content }}
              </p>
            </div>
          </div>
        </section>
      </div>

      <!-- ==================== TAB 2: COVER LETTER CONTENT ==================== -->
      <div v-show="activeTab === 'cover-letter'" class="flex flex-col gap-5">
        <div>
          <h3 class="text-base font-bold text-slate-800">
            AI Cover Letter Generator
          </h3>
          <p class="text-sm text-slate-500">
            Generate a personalized, professional 3-4 paragraph cover letter linking your master resume to this role.
          </p>
        </div>

        <!-- Error Banner -->
        <div
          v-if="coverLetterError"
          class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800 flex items-start gap-2.5"
        >
          <svg class="w-4 h-4 text-red-600 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div class="flex-1">
            <p class="font-semibold">{{ coverLetterError }}</p>
            <p class="mt-0.5 text-red-600 text-xs">
              Ensure your master resume and this application's job description are provided, and local LLM is running.
            </p>
          </div>
          <button
            type="button"
            class="text-red-500 hover:text-red-700 text-sm font-bold leading-none px-1"
            @click="coverLetterError = null"
          >
            ✕
          </button>
        </div>

        <!-- Success Banner -->
        <div
          v-if="coverLetterSuccess"
          class="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-800 flex items-center gap-2"
        >
          <svg class="w-4 h-4 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span class="font-medium flex-1">{{ coverLetterSuccess }}</span>
        </div>

        <!-- Generation Controls -->
        <div class="flex items-center gap-3 flex-wrap bg-slate-50 p-3.5 rounded-lg border border-slate-200">
          <div class="flex items-center gap-2 flex-1 min-w-[200px]">
            <label for="cover-letter-model" class="text-sm text-slate-600 font-medium whitespace-nowrap">
              Model:
            </label>
            <input
              id="cover-letter-model"
              v-model="coverLetterModel"
              type="text"
              placeholder="Swift-1.5-Qwen3.8-27B-GSQ-RCO"
              class="w-full border border-slate-300 rounded-md px-3 py-1.5 text-sm text-slate-800 bg-white focus:outline-none focus:ring-1 focus:ring-slate-400"
              :disabled="generatingCoverLetter"
            />
          </div>

          <button
            type="button"
            class="px-4 py-1.5 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors shadow-sm shrink-0"
            :disabled="generatingCoverLetter"
            @click="generateCoverLetter"
          >
            <svg
              v-if="generatingCoverLetter"
              class="w-3.5 h-3.5 animate-spin"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg
              v-else
              class="w-3.5 h-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>{{ generatingCoverLetter ? "Generating Cover Letter..." : "Generate Cover Letter" }}</span>
          </button>
        </div>

        <!-- Generated Cover Letter Output -->
        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <label class="text-sm font-semibold text-slate-700">
              Generated Cover Letter:
            </label>
            <button
              v-if="generatedCoverLetter"
              type="button"
              class="px-3 py-1 text-sm font-medium rounded-md flex items-center gap-1.5 transition-colors shadow-sm"
              :class="copiedCoverLetter ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-white hover:bg-slate-700'"
              @click="copyCoverLetter"
            >
              <svg v-if="copiedCoverLetter" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              <span>{{ copiedCoverLetter ? "Copied!" : "Copy to Clipboard" }}</span>
            </button>
          </div>

          <textarea
            v-model="generatedCoverLetter"
            rows="10"
            placeholder="Generated cover letter will appear here. You can also edit it directly..."
            class="w-full border border-slate-300 rounded-md p-3 text-sm font-sans text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500 resize-y leading-relaxed"
          ></textarea>
        </div>

        <!-- Prompt Expansion Toggle & View -->
        <div class="border-t border-slate-100 pt-3 flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <button
              type="button"
              class="text-sm font-medium text-slate-600 hover:text-slate-800 flex items-center gap-1.5 transition-colors"
              @click="showCoverLetterPrompt = !showCoverLetterPrompt"
            >
              <svg
                class="w-3.5 h-3.5 text-slate-400 transform transition-transform"
                :class="{ 'rotate-90': showCoverLetterPrompt }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              <span>{{ showCoverLetterPrompt ? "Hide Prompt for External AI" : "Show Prompt for External AI (ChatGPT / Claude)" }}</span>
            </button>

            <button
              v-if="showCoverLetterPrompt && coverLetterPrompt && !coverLetterPromptError"
              type="button"
              class="px-2.5 py-1 text-sm font-medium rounded border border-slate-200 text-slate-700 hover:bg-slate-50 flex items-center gap-1 transition-colors"
              @click="copyCoverLetterPrompt"
            >
              <svg v-if="copiedCoverLetterPrompt" class="w-3 h-3 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              <span>{{ copiedCoverLetterPrompt ? "Copied!" : "Copy Prompt" }}</span>
            </button>
          </div>

          <div v-if="showCoverLetterPrompt" class="mt-1">
            <div v-if="loadingCoverLetterPrompt" class="py-4 text-center text-sm text-slate-400 bg-slate-50 rounded">
              Loading prompt...
            </div>
            <div v-else-if="coverLetterPromptError" class="p-3 bg-amber-50 border border-amber-200 rounded text-sm text-amber-800">
              {{ coverLetterPromptError }}
            </div>
            <textarea
              v-else
              readonly
              :value="coverLetterPrompt"
              rows="5"
              class="w-full bg-slate-50 border border-slate-200 rounded-md p-2.5 text-sm font-mono text-slate-700 focus:outline-none resize-y"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- ==================== TAB 3: OUTREACH & FOLLOW-UP CONTENT ==================== -->
      <div v-show="activeTab === 'outreach'" class="flex flex-col gap-5">
        <div>
          <h3 class="text-base font-bold text-slate-800">
            Outreach & Follow-up Assistant
          </h3>
          <p class="text-sm text-slate-500">
            Generate customized cold outreach emails, post-interview thank you notes, or status inquiries.
          </p>
        </div>

        <!-- Template Selector -->
        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-semibold text-slate-700">Email Type:</label>
          <div class="flex items-center gap-2 flex-wrap">
            <button
              v-for="t in outreachTemplates"
              :key="t.value"
              type="button"
              class="px-3 py-1.5 text-sm font-medium rounded-md border transition-all"
              :class="
                outreachTemplateType === t.value
                  ? 'bg-amber-50 border-amber-500 text-amber-900 font-semibold shadow-xs'
                  : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300'
              "
              @click="onSelectTemplate(t.value)"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <!-- Error Banner -->
        <div
          v-if="outreachError"
          class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800 flex items-start gap-2.5"
        >
          <svg class="w-4 h-4 text-red-600 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div class="flex-1">
            <p class="font-semibold">{{ outreachError }}</p>
            <p class="mt-0.5 text-red-600 text-xs">
              Ensure the local LLM service is active at the configured endpoint.
            </p>
          </div>
          <button
            type="button"
            class="text-red-500 hover:text-red-700 text-sm font-bold leading-none px-1"
            @click="outreachError = null"
          >
            ✕
          </button>
        </div>

        <!-- Success Banner -->
        <div
          v-if="outreachSuccess"
          class="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-800 flex items-center gap-2"
        >
          <svg class="w-4 h-4 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span class="font-medium flex-1">{{ outreachSuccess }}</span>
        </div>

        <!-- Generation Controls -->
        <div class="flex items-center gap-3 flex-wrap bg-slate-50 p-3.5 rounded-lg border border-slate-200">
          <div class="flex items-center gap-2 flex-1 min-w-[200px]">
            <label for="outreach-model" class="text-sm text-slate-600 font-medium whitespace-nowrap">
              Model:
            </label>
            <input
              id="outreach-model"
              v-model="outreachModel"
              type="text"
              placeholder="Swift-1.5-Qwen3.8-27B-GSQ-RCO"
              class="w-full border border-slate-300 rounded-md px-3 py-1.5 text-sm text-slate-800 bg-white focus:outline-none focus:ring-1 focus:ring-slate-400"
              :disabled="generatingOutreach"
            />
          </div>

          <button
            type="button"
            class="px-4 py-1.5 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors shadow-sm shrink-0"
            :disabled="generatingOutreach"
            @click="generateOutreach"
          >
            <svg
              v-if="generatingOutreach"
              class="w-3.5 h-3.5 animate-spin"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg
              v-else
              class="w-3.5 h-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>{{ generatingOutreach ? "Generating Email..." : "Generate Email" }}</span>
          </button>
        </div>

        <!-- Generated Outreach Output -->
        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <label class="text-sm font-semibold text-slate-700">
              Generated Message:
            </label>
            <button
              v-if="generatedOutreach"
              type="button"
              class="px-3 py-1 text-sm font-medium rounded-md flex items-center gap-1.5 transition-colors shadow-sm"
              :class="copiedOutreach ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-white hover:bg-slate-700'"
              @click="copyOutreach"
            >
              <svg v-if="copiedOutreach" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              <span>{{ copiedOutreach ? "Copied!" : "Copy to Clipboard" }}</span>
            </button>
          </div>

          <textarea
            v-model="generatedOutreach"
            rows="8"
            placeholder="Generated email or outreach message will appear here. You can also edit it directly..."
            class="w-full border border-slate-300 rounded-md p-3 text-sm font-sans text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500 resize-y leading-relaxed"
          ></textarea>
        </div>

        <!-- Prompt Expansion Toggle & View -->
        <div class="border-t border-slate-100 pt-3 flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <button
              type="button"
              class="text-sm font-medium text-slate-600 hover:text-slate-800 flex items-center gap-1.5 transition-colors"
              @click="showOutreachPrompt = !showOutreachPrompt"
            >
              <svg
                class="w-3.5 h-3.5 text-slate-400 transform transition-transform"
                :class="{ 'rotate-90': showOutreachPrompt }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              <span>{{ showOutreachPrompt ? "Hide Prompt for External AI" : "Show Prompt for External AI (ChatGPT / Claude)" }}</span>
            </button>

            <button
              v-if="showOutreachPrompt && outreachPrompt && !outreachPromptError"
              type="button"
              class="px-2.5 py-1 text-sm font-medium rounded border border-slate-200 text-slate-700 hover:bg-slate-50 flex items-center gap-1 transition-colors"
              @click="copyOutreachPrompt"
            >
              <svg v-if="copiedOutreachPrompt" class="w-3 h-3 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              <span>{{ copiedOutreachPrompt ? "Copied!" : "Copy Prompt" }}</span>
            </button>
          </div>

          <div v-if="showOutreachPrompt" class="mt-1">
            <div v-if="loadingOutreachPrompt" class="py-4 text-center text-sm text-slate-400 bg-slate-50 rounded">
              Loading prompt...
            </div>
            <div v-else-if="outreachPromptError" class="p-3 bg-amber-50 border border-amber-200 rounded text-sm text-amber-800">
              {{ outreachPromptError }}
            </div>
            <textarea
              v-else
              readonly
              :value="outreachPrompt"
              rows="5"
              class="w-full bg-slate-50 border border-slate-200 rounded-md p-2.5 text-sm font-mono text-slate-700 focus:outline-none resize-y"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end pt-3 border-t border-slate-100">
        <button
          type="button"
          class="px-4 py-2 text-sm rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 font-medium transition-colors"
          @click="emit('close')"
        >
          Close
        </button>
      </div>
    </div>

    <!-- Resume Template Preview Modal -->
    <ResumeTemplatePreview
      v-if="previewModalOpen"
      :content="previewContent"
      :title="'Tailored Resume - ' + application.company"
      @close="previewModalOpen = false"
    />
  </div>
</template>
