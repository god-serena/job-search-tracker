<script setup>
import { ref } from "vue";
import { setTheme, useTheme } from "./theme.js";
import KanbanBoard from "./components/KanbanBoard.vue";
import ResumeModal from "./components/ResumeModal.vue";
import AllDocumentsListModal from "./components/AllDocumentsListModal.vue";

const isResumeOpen = ref(false);
const isDocsModalOpen = ref(false);
const boardRef = ref(null);
const theme = useTheme();

function toggleTheme() {
  setTheme(theme.value === "dark" ? "light" : "dark");
}
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden bg-slate-100">
    <header class="bg-slate-900 border-b border-slate-800 shrink-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between gap-3">
        <div class="min-w-0">
          <h1 class="text-lg sm:text-2xl font-bold text-white flex items-center gap-2">
            <svg class="w-5 h-5 sm:w-6 sm:h-6 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span class="truncate sm:block">Job Search</span>
            <span class="hidden sm:inline">Dashboard</span>
          </h1>
          <p class="hidden sm:block text-sm text-slate-400">Track every application, one board.</p>
        </div>
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="shrink-0 border border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white text-sm sm:text-base font-medium p-2 sm:px-4 sm:py-2 rounded-lg flex items-center gap-2 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900"
            aria-label="Dark mode"
            :aria-pressed="theme === 'dark'"
            @click="toggleTheme"
          >
            <svg class="w-5 h-5 sm:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <span class="hidden sm:inline">{{ theme === "dark" ? "Light theme" : "Dark theme" }}</span>
          </button>
          <button
            type="button"
            class="shrink-0 border border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white text-sm sm:text-base font-medium px-3 sm:px-4 py-2 rounded-lg flex items-center gap-2 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900"
            @click="isResumeOpen = true"
          >
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Master Resume</span>
          </button>
          <button
            type="button"
            class="shrink-0 border border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white text-sm sm:text-base font-medium px-3 sm:px-4 py-2 rounded-lg flex items-center gap-2 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900"
            @click="isDocsModalOpen = !isDocsModalOpen"
          >
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>All Documents</span>
          </button>
          <button
            type="button"
            class="shrink-0 ml-2 sm:ml-3 bg-amber-600 text-white hover:bg-amber-700 transition-colors text-sm sm:text-base font-semibold px-3 sm:px-4 py-2 rounded-lg flex items-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900"
            @click="boardRef?.openCreateModal()"
          >
            <span>&#xFF0B; New Application</span>
          </button>
        </div>
      </div>
    </header>

    <main class="flex-1 flex flex-col overflow-hidden min-h-0">
      <KanbanBoard ref="boardRef" />
    </main>

    <AllDocumentsListModal v-if="isDocsModalOpen" @close="isDocsModalOpen = false" />

    <ResumeModal v-if="isResumeOpen" @close="isResumeOpen = false" />
  </div>
</template>