<script setup>
import { reactive, ref, watch } from "vue";
import { api } from "../api";

const props = defineProps({
  application: { type: Object, default: null },
});
const emit = defineEmits(["close", "save", "delete"]);
const attachments = ref([]);
const attachmentError = ref("");
const uploading = ref(false);
const supportedFileTypes = ".pdf,.doc,.docx,.rtf,.odt,.txt";

// Format date to readable string
function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

const form = reactive({
  company: "",
  role: "",
  url: "",
  status: "wishlist",
  date_applied: "",
  follow_up_date: "",
  contact_name: "",
  description: "",
  notes: "",
});

watch(
  () => props.application,
  (app) => {
    Object.assign(form, {
      company: app?.company || "",
      role: app?.role || "",
      url: app?.url || "",
      status: app?.status || "wishlist",
      date_applied: app?.date_applied || "",
      follow_up_date: app?.follow_up_date || "",
      contact_name: app?.contact_name || "",
      description: app?.description || "",
      notes: app?.notes || "",
    });
  },
  { immediate: true }
);

watch(
  () => props.application?.id,
  async (applicationId) => {
    attachments.value = [];
    attachmentError.value = "";
    if (!applicationId) return;
    try {
      attachments.value = await api.listApplicationDocuments(applicationId);
    } catch (error) {
      attachmentError.value = error.message;
    }
  },
  { immediate: true }
);

async function uploadDocument(event, documentType) {
  const file = event.target.files?.[0];
  event.target.value = "";
  if (!file || !props.application?.id) return;
  attachmentError.value = "";
  if (file.size > 10 * 1024 * 1024) {
    attachmentError.value = "File exceeds the 10 MB limit.";
    return;
  }
  uploading.value = true;
  try {
    const item = await api.uploadApplicationDocument(props.application.id, documentType, file);
    attachments.value = [item, ...attachments.value];
  } catch (error) {
    attachmentError.value = error.message;
  } finally {
    uploading.value = false;
  }
}

function submit() {
  const payload = { ...form };
  Object.keys(payload).forEach((key) => {
    if (payload[key] === "") payload[key] = null;
  });
  emit("save", payload);
}
</script>

<template>
  <div class="fixed inset-0 bg-slate-900/40 flex items-center justify-center z-50 p-4">
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="app-modal-title"
      class="bg-white rounded-xl shadow-lg border border-slate-200 w-full max-w-lg max-h-[90vh] overflow-y-auto p-6"
    >
      <h2 id="app-modal-title" class="text-lg font-semibold text-slate-800 mb-4">
        {{ application ? "Edit Application" : "New Application" }}
      </h2>

      <form class="space-y-3" @submit.prevent="submit">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <label class="text-sm font-medium text-slate-700 flex flex-col gap-1">
            Company
            <input
              id="company"
              v-model="form.company"
              required
              class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40"
            />
          </label>
          <label class="text-sm font-medium text-slate-700 flex flex-col gap-1">
            Role
            <input
              id="role"
              v-model="form.role"
              required
              class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40"
            />
          </label>
        </div>

        <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label class="flex-1 text-sm font-medium text-slate-700 flex flex-col gap-1">
            Job posting URL
            <input
              id="url"
              v-model="form.url"
              class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base flex-1 focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40"
            />
          </label>
          <a
            v-if="form.url"
            :href="form.url"
            target="_blank"
            rel="noopener noreferrer"
            class="px-3.5 py-2 text-sm rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 shrink-0 flex items-center gap-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
          >
            Open
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>

        <label class="text-sm font-medium text-slate-700 flex flex-col gap-1">
          Status
          <select
            id="status"
            v-model="form.status"
            class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base w-full bg-white focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40"
          >
          <option value="wishlist">Wishlist</option>
          <option value="applied">Applied</option>
          <option value="interviewing">Interviewing</option>
          <option value="offer">Offer</option>
          <option value="rejected">Rejected</option>
          <option value="cancelled">Cancelled</option>
          </select>
        </label>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <label for="date_applied" class="text-sm font-medium text-slate-700 flex flex-col gap-1">
            Date applied
            <input id="date_applied" v-model="form.date_applied" type="date"
              class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40" />
          </label>
          <label for="follow_up_date" class="text-sm font-medium text-slate-700 flex flex-col gap-1">
            Follow up on
            <input id="follow_up_date" v-model="form.follow_up_date" type="date"
              class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40" />
          </label>
        </div>

        <label class="text-sm font-medium text-slate-700 flex flex-col gap-1">
          Contact name
          <input
            id="contact_name"
            v-model="form.contact_name"
            class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base w-full focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40"
          />
        </label>

        <label for="description" class="text-sm font-medium text-slate-700 flex flex-col gap-1">
          Job description
          <textarea
            id="description"
            v-model="form.description"
            placeholder="Paste full job posting description here..."
            rows="5"
            class="border border-slate-300 rounded-md px-3 py-2 text-sm sm:text-base w-full text-slate-800 focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40"
          ></textarea>
        </label>

        <section aria-labelledby="attachments-title" class="rounded-lg border border-slate-200 bg-slate-50 p-4 space-y-4">
          <header class="flex items-start justify-between gap-4">
            <div>
              <h3 id="attachments-title" class="text-sm font-semibold text-slate-800">Documents</h3>
              <p class="text-xs text-slate-500">Attach PDF, Word, RTF, ODT, or TXT files (up to 10 MB). Create the application before uploading.</p>
            </div>
            <p v-if="application" class="text-xs text-slate-600">{{ attachments.length }} {{ attachments.length === 1 ? 'attachment' : 'attachments' }}</p>
          </header>

          <div v-if="!application" class="text-xs text-amber-800">Save this application first to attach documents.</div>
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label v-for="kind in [{ value: 'resume', label: 'Resume' }, { value: 'cover_letter', label: 'Cover letter' }]" :key="kind.value" class="block">
              <span class="text-xs font-medium text-slate-700 block mb-1">{{ kind.label }}</span>
              <input type="file" :accept="supportedFileTypes" :disabled="uploading" @change="uploadDocument($event, kind.value)" class="block w-full text-xs border border-slate-200 rounded-md px-2 py-1.5 text-slate-600 bg-white focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/20" />
            </label>
          </div>

          <div v-if="uploading" role="status" class="text-xs text-slate-500">Uploading…</div>
          <div v-if="attachmentError" role="alert" class="text-xs text-red-600">{{ attachmentError }}</div>
          <ul v-if="attachments.length" role="list" aria-label="Attached documents" class="border-t border-slate-200 pt-3 space-y-2">
            <li v-for="document in attachments" :key="document.id" class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2 min-w-0">
                <span class="text-xs px-2 py-1 rounded-md bg-slate-100 text-slate-600 font-medium truncate max-w-[160px]">
                  {{ document.document_type === 'resume' ? 'Resume' : 'Cover letter' }}
                </span>
                <span class="text-xs text-slate-500 truncate">{{ document.filename }}</span>
                <span class="text-xs text-slate-400">• {{ formatDate(document.created_at) }}</span>
              </div>
              <a
                :href="api.applicationDocumentDownloadUrl(application.id, document.id)"
                :download="document.filename"
                class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-amber-600 hover:border-amber-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-1 transition-colors"
                :aria-label="`Download ${document.document_type === 'resume' ? 'Resume' : 'Cover letter'}: ${document.filename}`"
              >
                Download
              </a>
            </li>
          </ul>
        </section>

        <label for="notes" class="text-sm font-medium text-slate-700 flex flex-col gap-1">
          Notes
          <textarea
            id="notes"
            v-model="form.notes"
            placeholder="Personal notes, thoughts, referral details..."
            rows="3"
            class="border border-slate-300 rounded-md px-3 py-2 text-sm sm:text-base w-full text-slate-800 focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-500/40"
          ></textarea>
        </label>

        <div class="flex flex-wrap items-center gap-2 pt-2">
          <button
            v-if="application"
            type="button"
            class="px-3.5 py-2 text-sm rounded-md border border-red-300 text-red-600 hover:bg-red-50 transition-colors font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-red-400"
            @click="emit('delete', application.id)"
          >
            Delete Application
          </button>
          <div class="flex flex-wrap gap-2 ml-auto">
            <button type="button" class="px-4 py-2 text-sm sm:text-base font-medium rounded-md border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-1"
              @click="emit('close')">
              Discard
            </button>
            <button type="submit" class="px-4 py-2 text-sm sm:text-base font-medium rounded-md bg-amber-600 text-white hover:bg-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-1">
              Save Application
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>
