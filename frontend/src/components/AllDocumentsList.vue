<script setup>
import { computed } from "vue";
import { api } from "../api";

const props = defineProps({
  application: {
    type: Object,
    default: null,
  },
});

const documents = ref([]);
const loading = ref(true);
const error = ref("");

async function loadDocuments() {
  if (!props.application?.id) {
    documents.value = [];
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    documents.value = await api.listApplicationDocuments(props.application.id);
  } catch (e) {
    error.value = e.message;
    documents.value = [];
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

const docStyle = {
  border: "border-slate-200",
  bg: "bg-white",
  label: "text-slate-700",
  title: "text-slate-900",
  meta: "text-xs text-slate-500",
  link: "text-amber-600 hover:text-amber-800 hover:underline",
};
</script>

<template>
  <section class="border border-slate-200 rounded-xl overflow-hidden bg-white" aria-labelledby="documents-heading">
    <div class="flex items-center justify-between px-4 py-3 sm:px-6 border-b border-slate-100">
      <h3 id="documents-heading" class="text-base font-semibold text-slate-800">
        Documents
      </h3>
      <span class="text-xs text-slate-500">
        {{ documents.length }} attached
      </span>
    </div>
    <div v-if="loading" class="px-4 sm:px-6 py-8 text-center">
      <p class="text-sm text-slate-500">Loading documents...</p>
    </div>
    <div v-else-if="error" role="alert" class="px-4 sm:px-6 py-4">
      <p class="text-sm text-red-600">{{ error }}</p>
    </div>
    <ul v-else-if="documents.length" role="list" aria-label="Application documents">
      <li v-for="doc in documents" :key="doc.id" class="grid grid-cols-12 gap-3 sm:gap-4 px-4 sm:px-6 py-3 border-b last:border-b-0 border-slate-100 hover:bg-slate-50 transition-colors">
        <!-- Type -->
        <div class="col-span-5 sm:col-span-4 flex items-center justify-center">
          <span class="text-xs font-semibold px-2 py-1 rounded bg-slate-100 text-slate-600">
            {{ formatDocType(doc.document_type) }}
          </span>
        </div>
        <!-- Filename -->
        <div class="col-span-5 sm:col-span-4">
          <p class="text-sm font-medium text-slate-900 truncate" title="Filename">{{ doc.filename }}</p>
          <p class="text-xs text-slate-500">{{ formatDate(doc.created_at) }}</p>
        </div>
        <!-- Company/Role -->
        <div class="col-span-2 sm:col-span-2 flex items-center">
          <p class="text-xs text-slate-500 truncate">
            <span class="font-medium text-slate-700">{{ doc.company }}</span> / {{ doc.role }}
          </p>
        </div>
        <!-- Download -->
        <div class="col-span-3 sm:col-span-2">
          <a
            :href="api.applicationDocumentDownloadUrl(props.application.id, doc.id)"
            :download="doc.filename"
            class="text-xs sm:text-sm font-medium px-2.5 py-1.5 rounded-md border border-slate-200 hover:border-amber-400 hover:bg-amber-50 text-slate-700 hover:text-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-1 transition-colors text-right"
            :aria-label="`Download ${doc.filename} (${formatDocType(doc.document_type)})`"
          >
            Download
          </a>
        </div>
      </li>
    </ul>
    <div v-else class="px-4 sm:px-6 py-8 text-center">
      <p class="text-sm text-slate-500">No documents attached.</p>
    </div>
  </section>
</template>
