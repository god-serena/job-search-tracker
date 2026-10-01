<script setup>
import { computed, onMounted, ref } from "vue";
import { api } from "../api";
import ApplicationCard from "./ApplicationCard.vue";
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
  wishlist:     { border: 'border-sky-300',     label: 'text-sky-700' },
  applied:      { border: 'border-indigo-300',  label: 'text-indigo-700' },
  interviewing: { border: 'border-violet-300',  label: 'text-violet-700' },
  offer:        { border: 'border-emerald-300', label: 'text-emerald-700' },
  rejected:     { border: 'border-rose-300',    label: 'text-rose-700' },
  cancelled:    { border: 'border-slate-300',   label: 'text-slate-500' },
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

const counts = computed(() =>
  Object.fromEntries(columns.map((c) => [c.key, grouped.value[c.key].length]))
);

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

async function saveApplication(payload) {
  try {
    if (editingApplication.value) {
      await api.update(editingApplication.value.id, payload);
    } else {
      await api.create(payload);
    }
    modalOpen.value = false;
    await Promise.all([loadApplications(), loadStats()]);
  } catch (e) {
    error.value = e.message;
  }
}

async function deleteApplication(id) {
  try {
    await api.remove(id);
    modalOpen.value = false;
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

onMounted(() => {
  loadApplications();
  loadStats();
});
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="px-6 pt-4 pb-2 shrink-0 flex flex-col gap-3">
      <!-- Analytics Stats Bar -->
      <StatsBar
        :stats="stats"
        @select-filter="(filter) => selectedFilter = filter"
      />

      <!-- Column Counts & Add Action -->
      <div class="flex items-center justify-between">
        <div class="flex gap-4 text-sm sm:text-base text-slate-500 flex-wrap">
          <span v-for="c in columns" :key="c.key">
            {{ c.label }}: <strong class="text-slate-700">{{ counts[c.key] }}</strong>
          </span>
        </div>
        <button
          class="bg-indigo-600 text-white text-sm sm:text-base px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors font-medium"
          @click="openCreateModal"
        >
          ＋ New Application
        </button>
      </div>

      <!-- Search, Filter & Sort Toolbar -->
      <div class="bg-white border border-slate-200 rounded-lg p-3 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex flex-1 items-center gap-3 flex-wrap">
          <!-- Search input -->
          <div class="relative flex-1 min-w-[200px] max-w-xs">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search company, role, notes..."
              class="w-full pl-9 pr-8 py-2 text-sm bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-400 focus:bg-white transition-colors"
            />
            <button
              v-if="searchQuery"
              @click="searchQuery = ''"
              class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-slate-400 hover:text-slate-600 text-xs"
              title="Clear search"
            >
              ✕
            </button>
          </div>

          <!-- Filter pills -->
          <div class="flex items-center gap-1.5">
            <button
              v-for="opt in filterOptions"
              :key="opt.key"
              @click="selectedFilter = opt.key"
              class="px-3 py-1.5 text-sm font-medium rounded-full transition-colors border"
              :class="selectedFilter === opt.key 
                ? 'bg-indigo-600 text-white border-indigo-600' 
                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- Sort dropdown & Active filter status -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <label for="sort-select" class="text-sm font-medium text-slate-500 whitespace-nowrap">Sort by:</label>
            <select
              id="sort-select"
              v-model="sortBy"
              class="text-sm bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-1 focus:ring-slate-400 focus:bg-white transition-colors"
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
          class="text-indigo-600 hover:text-indigo-800 font-medium text-sm"
        >
          Clear filters
        </button>
      </div>
    </div>

    <p v-if="error" class="text-red-500 text-sm px-6">{{ error }}</p>
    <p v-if="loading" class="text-slate-400 text-sm px-6">Loading…</p>

    <KanbanColumns
      v-if="!loading && !error"
      :columns="columns"
      :grouped="grouped"
      :col-style="colStyle"
      class="flex-1 min-h-0"
      @drop="onDrop"
      @edit="openEditModal"
      @dragstart="onDragStart"
      @tailor="openTailorModal"
    />

    <ApplicationModal
      v-if="modalOpen"
      :application="editingApplication"
      @close="modalOpen = false"
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
