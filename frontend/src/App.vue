<script setup>
import { ref } from "vue";
import KanbanBoard from "./components/KanbanBoard.vue";
import ResumeModal from "./components/ResumeModal.vue";

const isResumeOpen = ref(false);
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden bg-slate-100">
    <header class="bg-gradient-to-r from-slate-900 to-slate-800 border-b border-slate-800 shrink-0">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white flex items-center gap-2">
            <svg class="w-6 h-6 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Job Search Dashboard
          </h1>
          <p class="text-base text-slate-400">Track every application, one board.</p>
        </div>
        <button
          type="button"
          class="border border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white text-base font-medium px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          @click="isResumeOpen = true"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Master Resume
        </button>
      </div>
    </header>

    <main class="flex-1 flex flex-col overflow-hidden">
      <KanbanBoard />
    </main>

    <ResumeModal v-if="isResumeOpen" @close="isResumeOpen = false" />
  </div>
</template>
