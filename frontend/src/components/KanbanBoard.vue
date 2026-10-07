<script setup>
import { computed, onMounted, ref } from "vue";
import { api } from "../api";
import ApplicationModal from "./ApplicationModal.vue";
import StatsBar from "./StatsBar.vue";
import TailorModal from "./TailorModal.vue";
import KanbanColumns from "./KanbanColumns.vue";

const columns = [
  { key: "wishlist", label: "Wishlist" },
  { key: "applied", label: "Applied" },
  { key: "interviewing", label: "Interviewing" },
  { key: "offer", label: "Offer" },
  { key: "rejected", label: "Rejected" },
  { key: "cancelled", label: "Cancelled" },
];

const colStyle = {
  wishlist:     { border: 'border-sky-300',     label: 'text-sky-700 dark:text-sky-300' },
  applied:      { border: 'border-amber-300',   label: 'text-amber-700 dark:text-amber-300' },
  interviewing: { border: 'border-violet-300',  label: 'text-violet-700 dark:text-violet-300' },
  offer:        { border: 'border-emerald-300', label: 'text-emerald-700 dark:text-emerald-300' },
  rejected:     { border: 'border-rose-300',    label: 'text-rose-700 dark:text-rose-300' },
  cancelled:    { border: 'border-slate-300',   label: 'text-slate-500 dark:text-slate-400' },
};

const applications = ref([]);
const stats = ref(null);
const loading = ref(true);
const error = ref("");
const modalOpen = ref(false);
const editingApplication = ref(null);
const draggedId = ref(null);

const tailorModalOpen = ref(false);
const tailorApplication = ref(null);

const documentMap = ref({});

function loadAllDocuments() {
  // Fetch all application documents once; errors are non-fatal
  api.getAllApplicationDocuments().then((docs) => {
    const grouped = {};
    for (const doc of docs) {
      if (!grouped[doc.application_id]) grouped[doc.application_id] = [];
      grouped[doc.application_id].push(doc);
    }
    // Reorder by most recent first (created_at)
    for (const appId of Object.keys(grouped)) {
      grouped[appId].sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""));
    }
    documentMap.value = grouped;
  }).catch((e) => console.error("Failed to load application documents:", e));
}

// Search, filtering, and sorting state
const searchQuery = ref("");
const selectedFilter = ref("all"); // 'all' | 'needs_followup' | 'has_description'
const sortBy = ref("updated_desc"); // 'updated_desc' | 'applied_desc' | 'company_asc'

const filterOptions = [
  { key: "all", label: "All" },
  { key: "needs_followup", label: "Follow-up Due" },
  { key: "has_description", label: "Has Description" },
];

const sortOptions = [
  { value: "updated_desc", label: "Recently Updated" },
  { value: "applied_desc", label: "Date Applied" },
  { value: "company_asc", label: "Company (A-Z)" },
];

const isFiltered = computed(() => {
  return searchQuery.value.trim() !== "" || selectedFilter.value !== "all";
});

function resetFilters() {
  searchQuery.value = "";
  selectedFilter.value = "all";
}

const filteredApplications = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  const today = new Date().toISOString().split("T")[0];

  return applications.value.filter((app) => {
    // 1. Search Query Filter
    if (query) {
      const matchCompany = (app.company || "").toLowerCase().includes(query);
      const matchRole = (app.role || "").toLowerCase().includes(query);
      const matchNotes = (app.notes || "").toLowerCase().includes(query);
      const matchContact = (app.contact_name || "").toLowerCase().includes(query);
      if (!matchCompany && !matchRole && !matchNotes && !matchContact) {
        return false;
      }
    }

    // 2. Selected Filter Preset
    if (selectedFilter.value === "needs_followup") {
      const isDue = app.follow_up_date && app.follow_up_date <= today;
      const isClosed =
        app.status === "offer" ||
        app.status === "rejected" ||
        app.status === "cancelled";
      if (!isDue || isClosed) {
        return false;
      }
    } else if (selectedFilter.value === "has_description") {
      if (!app.description || !app.description.trim()) {
        return false;
      }
    }

    return true;
  });
});

const filteredCount = computed(() => filteredApplications.value.length);
const noMatches = computed(() => isFiltered.value && filteredCount.value === 0);

const grouped = computed(() => {
  const map = Object.fromEntries(columns.map((c) => [c.key, []]));
  
  for (const app of filteredApplications.value) {
    (map[app.status] || map.wishlist).push(app);
  }

  // Sort applications within each column
  for (const colKey of Object.keys(map)) {
    map[colKey].sort((a, b) => {
      if (sortBy.value === "updated_desc") {
        const dateA = a.updated_at ? new Date(a.updated_at).getTime() : 0;
        const dateB = b.updated_at ? new Date(b.updated_at).getTime() : 0;
        return dateB - dateA;
      } else if (sortBy.value === "applied_desc") {
        if (!a.date_applied && !b.date_applied) return 0;
        if (!a.date_applied) return 1;
        if (!b.date_applied) return -1;
        return new Date(b.date_applied).getTime() - new Date(a.date_applied).getTime();
      } else if (sortBy.value === "company_asc") {
        return (a.company || "").localeCompare(b.company || "", undefined, {
          sensitivity: "base",
        });
      }
      return 0;
    });
  }

  return map;
});

async function loadApplications() {
  loading.value = true;
  error.value = "";
  try {
    applications.value = await api.list();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function loadStats() {
  try {
    stats.value = await api.getStats();
  } catch (e) {
    console.error("Failed to load stats:", e);
  }
}

function openCreateModal() {
  editingApplication.value = null;
  modalOpen.value = true;
}

function openEditModal(application) {
  editingApplication.value = application;
  modalOpen.value = true;
}

function openTailorModal(application) {
  tailorApplication.value = application;
  tailorModalOpen.value = true;
}

function onModalClose() {
  modalOpen.value = false;
  loadAllDocuments();
}

async function deleteApplication(id) {
  try {
    await api.remove(id);
    onModalClose();
    await Promise.all([loadApplications(), loadStats()]);
  } catch (e) {
    error.value = e.message;
  }
}

async function saveApplication(payload) {
  try {
    if (editingApplication.value) {
      await api.update(editingApplication.value.id, payload);
    } else {
      await api.create(payload);
    }
    onModalClose();
    await Promise.all([loadApplications(), loadStats()]);
  } catch (e) {
    error.value = e.message;
  }
}

function onDragStart(application) {
  draggedId.value = application.id;
}

async function onDrop(status) {
  if (!draggedId.value) return;
  const id = draggedId.value;
  draggedId.value = null;
  const app = applications.value.find((a) => a.id === id);
  if (!app || app.status === status) return;
  app.status = status; // optimistic update
  try {
    await api.update(id, { status });
    await loadStats();
  } catch (e) {
    error.value = e.message;
    await Promise.all([loadApplications(), loadStats()]);
  }
}

async function onStatusChanged(status, id) {
  const app = applications.value.find((a) => a.id === id);
  if (!app || app.status === status) return;
  const previousStatus = app.status;
  app.status = status;
  try {
    await api.update(id, { status });
    await loadStats();
  } catch (e) {
    app.status = previousStatus;
    console.error("Failed to update status:", e);
  }
}

onMounted(() => {
  loadApplications();
  loadStats();
  loadAllDocuments();
});

// Exposed so App.vue can trigger the create modal from the header button.
defineExpose({ openCreateModal });

</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="px-4 sm:px-6 pt-3 pb-2 shrink-0 max-h-[40%] sm:max-h-[45%] md:max-h-[50%] lg:max-h-[55%] [@media(max-height:700px)]:max-h-[40%] overflow-y-auto flex flex-col gap-2 sm:gap-3">
      <!-- Board heading -->
      <h2 class="text-lg font-semibold text-slate-800">Job Board</h2>

      <!-- Analytics Stats Bar -->
      <StatsBar
        :stats="stats"
        @select-filter="(filter) => selectedFilter = filter"
        class="order-last sm:order-none shrink-0"
      />

      <!-- Search, Filter & Sort Toolbar -->
      <div class="bg-slate-50/80 dark:bg-slate-800/80 border border-slate-200 rounded-lg p-3 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex flex-1 items-center gap-3 flex-wrap">
          <!-- Search input -->
          <div class="relative flex-1 min-w-[200px] max-w-none sm:max-w-xs">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              aria-label="Search applications"
              placeholder="Search company, role, notes..."
              class="w-full pl-9 pr-8 py-2 text-sm bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-400 focus-visible:ring-2 focus-visible:ring-amber-500 focus:bg-white transition-colors"
            />
            <button
              v-if="searchQuery"
              @click="searchQuery = ''"
              aria-label="Clear search"
              class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-slate-400 hover:text-slate-600 text-xs rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              title="Clear search"
            >
              ✕
            </button>
          </div>

          <!-- Filter pills -->
          <div class="flex flex-wrap items-center gap-1.5">
            <button
              v-for="opt in filterOptions"
              :key="opt.key"
              :aria-pressed="selectedFilter === opt.key"
              @click="selectedFilter = opt.key"
              class="px-3 py-1.5 text-sm font-medium rounded-full transition-colors border focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              :class="selectedFilter === opt.key
                ? 'bg-amber-600 text-white border-amber-600'
                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- Sort dropdown & Active filter status -->
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <label for="sort-select" class="text-sm font-medium text-slate-500 whitespace-nowrap flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
              </svg>
              Sort by:
            </label>
            <select
              id="sort-select"
              v-model="sortBy"
              class="text-sm bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-slate-400 focus-visible:ring-2 focus-visible:ring-amber-500 focus:bg-white transition-colors"
            >
              <option v-for="sort in sortOptions" :key="sort.value" :value="sort.value">
                {{ sort.label }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Active Filter Indicator Banner -->
      <div v-if="isFiltered" class="flex items-center justify-between text-sm text-slate-500 bg-slate-50 px-3 py-2 rounded-md border border-slate-100">
        <span>
          Showing <strong class="text-slate-700">{{ filteredCount }}</strong> of <strong class="text-slate-700">{{ applications.length }}</strong> applications
        </span>
        <button
          @click="resetFilters"
          class="text-amber-700 dark:text-amber-300 hover:text-amber-900 dark:hover:text-amber-200 font-medium text-sm rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
        >
          Clear filters
        </button>
      </div>
    </div>

    <p v-if="error" role="alert" class="text-red-600 dark:text-red-400 text-sm px-4 sm:px-6 shrink-0">{{ error }}</p>
    <p v-if="loading" role="status" class="text-slate-500 text-sm px-4 sm:px-6 shrink-0">Loading…</p>

    <KanbanColumns
      v-if="!loading && !error && !noMatches"
      :columns="columns"
      :grouped="grouped"
      :documents-map="documentMap"
      :col-style="colStyle"
      class="flex-1 min-h-0"
      @drop="onDrop"
      @edit="openEditModal"
      @dragstart="onDragStart"
      @tailor="openTailorModal"
      @status-changed="onStatusChanged"
    />

    <div
      v-else-if="!loading && !error"
      class="flex-1 min-h-0 flex items-center justify-center p-4 sm:px-6"
    >
      <div
        role="status"
        class="w-full max-w-md bg-white border border-slate-200 rounded-xl p-6 sm:p-8 text-center shadow-sm"
      >
        <svg class="mx-auto h-10 w-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <h3 class="mt-3 text-base font-semibold text-slate-800">No matching applications</h3>
        <p class="mt-1 text-sm text-slate-500">
          No applications match your current search and filters.
          <template v-if="searchQuery.trim()">
            Try a different term for &ldquo;{{ searchQuery.trim() }}&rdquo;.
          </template>
        </p>
        <button
          type="button"
          @click="resetFilters"
          class="mt-4 bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-md hover:bg-amber-700 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-1"
        >
          Clear search &amp; filters
        </button>
      </div>
    </div>

    <ApplicationModal
      v-if="modalOpen"
      :application="editingApplication"
      @close="onModalClose"
      @save="saveApplication"
      @delete="deleteApplication"
    />

    <TailorModal
      v-if="tailorModalOpen"
      :application="tailorApplication"
      @close="tailorModalOpen = false"
    />
  </div>
</template>
