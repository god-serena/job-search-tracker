<script setup>
import { api } from "../api";

const emit = defineEmits(["close"]);

const allDocuments = ref([]);
const loading = ref(true);
const error = ref("");

async function loadDocuments() {
  loading.value = true;
  error.value = "";
  try {
    allDocuments.value = await api.getAllApplicationDocuments();
  } catch (e) {
    error.value = e.message;
    allDocuments.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(loadDocuments);

// Format document type for display
function formatDocType(type) {
  return type === "resume" ? "Resume" : type === "cover_letter" ? "Cover letter" : type;
}

// Format date to readable string
function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

// Build a compact app label (company/role)
function appLabel(doc) {
  return `${doc.company} / ${doc.role}`;
}

// Get download URL (global endpoint serves any app's docs)
function getDownloadUrl(doc, id) {
  return `${api.API_URL}/api/applications/${doc.application_id}/documents/${id}/download`;
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div
      class="absolute inset-0 bg-slate-900/60"
      aria-hidden="true"
      @click="emit('close')"
    ></div>
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="docs-modal-title"
      class="relative bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-3 border-b border-slate-200 bg-slate-50">
        <h2 id="docs-modal-title" class="text-base sm:text-lg font-semibold text-slate-800">
          Application Documents
        </h2>
        <div class="flex items-center gap-3">
          <span class="text-xs text-slate-500">
            {{ allDocuments.length }} document{{ allDocuments.length !== 1 ? "s" : "" }}
          </span>
          <button
            type="button"
            class="text-slate-400 hover:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 rounded p-1"
            @click="emit('close')"
            aria-label="Close"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-auto p-5 space-y-4">
        <div v-if="loading" class="flex flex-col items-center justify-center py-8">
          <p class="text-sm text-slate-500">Loading documents...</p>
        </div>
        <div v-else-if="error" role="alert" class="p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm">
          {{ error }}
        </div>
        <div v-else-if="allDocuments.length === 0" class="flex flex-col items-center justify-center py-8">
          <p class="text-sm text-slate-500">No documents uploaded yet.</p>
        </div>
        <ul v-else role="list" aria-label="Document list" class="grid grid-cols-12 gap-3 sm:gap-4">
          <li v-for="doc in allDocuments" :key="doc.id" class="border border-slate-200 rounded-lg p-3 hover:border-amber-300 hover:bg-amber-50 transition-colors">
            <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-2 sm:gap-0">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-xs font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                    {{ formatDocType(doc.document_type) }}
                  </span>
                  <span class="text-xs text-slate-400">
                    • {{ formatDate(doc.created_at) }}
                  </span>
                </div>
                <p class="text-sm font-medium text-slate-800 truncate">{{ doc.filename }}</p>
              </div>
              <a
                :href="getDownloadUrl(doc, doc.id)"
                :download="doc.filename"
                class="text-xs sm:text-sm font-medium px-2.5 py-1.5 rounded-md border border-slate-200 hover:border-amber-400 hover:bg-amber-50 text-slate-700 hover:text-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-1 transition-colors whitespace-nowrap"
                :aria-label="`Download ${doc.filename} (${formatDocType(doc.document_type)}) from ${appLabel(doc)}`"
              >
                Download
              </a>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
