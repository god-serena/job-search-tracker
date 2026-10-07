<script setup>
import { computed, ref } from "vue";
import KeyboardStatusModal from "./KeyboardStatusModal.vue";

const props = defineProps({
  application: { type: Object, required: true },
  documents: { type: Array, default: () => [] }
});
const emit = defineEmits(["dragstart", "tailor"]);

const isCancelled = computed(() => props.application.status === "cancelled");

const companyInitial = computed(() => {
  const name = props.application.company || "?";
  return name.charAt(0).toUpperCase();
});

const avatarColors = [
  'bg-slate-100 text-slate-700',
  'bg-amber-100 text-amber-800',
  'bg-stone-100 text-stone-600',
  'bg-amber-50 text-amber-700',
];
const avatarColor = computed(() => {
  const idx = (props.application.company?.length || 0) % avatarColors.length;
  return avatarColors[idx];
});

const followUpStatus = computed(() => {
  if (!props.application.follow_up_date) return null;
  const today = new Date().toISOString().split("T")[0];
  const date = props.application.follow_up_date;
  if (date < today) {
    return { label: `Overdue (${date})`, classes: "bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-200 border border-red-200 dark:border-red-800", dot: "bg-red-500" };
  }
  if (date === today) {
    return { label: "Due today", classes: "bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200 border border-amber-200 dark:border-amber-700", dot: "bg-amber-500" };
  }
  return { label: `Follow up ${date}`, classes: "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-200 border border-slate-200 dark:border-slate-600", dot: "bg-slate-400" };
});

</script>

<template>
  <div
    class="p-3.5 mb-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm cursor-grab active:cursor-grabbing hover:shadow-md hover:border-slate-300 dark:hover:border-slate-600 transition-all focus-within:ring-2 focus-within:ring-amber-400"
    draggable="true"
    @dragstart="emit('dragstart', application, $event)"
  >

    <!-- Company row: avatar + name -->
    <div class="flex items-start gap-2.5 mb-1.5">
      <div
        class="w-8 h-8 rounded-lg font-bold text-sm flex items-center justify-center shrink-0 select-none"
        :class="avatarColor"
      >
        {{ companyInitial }}
      </div>
      <div class="flex-1 min-w-0 pt-0.5">
        <a
          v-if="application.url"
          :href="application.url"
          target="_blank"
          rel="noopener noreferrer"
          class="font-semibold text-slate-900 dark:text-slate-100 text-lg hover:text-amber-700 dark:hover:text-amber-300 hover:underline inline-flex items-center gap-1 group leading-tight rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400"
          @click.stop
        >
          <span class="truncate">{{ application.company }}</span>
          <svg class="w-3.5 h-3.5 text-slate-400 group-hover:text-amber-600 dark:group-hover:text-amber-300 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
        <p v-else class="font-semibold text-slate-900 dark:text-slate-100 text-lg leading-tight truncate">{{ application.company }}</p>
      </div>
    </div>

    <p class="text-slate-500 text-sm mb-2 font-medium">{{ application.role }}</p>

    <p
      v-if="application.description && !isCancelled"
      class="text-slate-600 dark:text-slate-300 text-sm mb-2.5 line-clamp-2 bg-slate-50 dark:bg-slate-700 rounded-md p-2 border border-slate-100 dark:border-slate-600 italic"
    >
      {{ application.description.slice(0, 80) }}{{ application.description.length > 80 ? '\u2026' : '' }}
    </p>

    <!-- Footer -->
    <div class="pt-2.5 border-t border-slate-100 mt-2 flex flex-col gap-2">
      <!-- Date row -->
      <div class="text-xs text-slate-500 flex items-center gap-1">
        <svg class="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span v-if="application.date_applied">Applied {{ application.date_applied }}</span>
        <span v-else class="italic text-slate-400">Not applied yet</span>
      </div>

      <!-- Follow-up badge + Tailor button (hidden if cancelled) -->
      <div v-if="!isCancelled" class="flex items-center justify-between gap-2">
        <span
          v-if="followUpStatus"
          class="px-2.5 py-1 rounded-md text-xs font-semibold inline-flex items-center gap-1.5"
          :class="followUpStatus.classes"
        >
          <span class="h-1.5 w-1.5 rounded-full inline-block" :class="followUpStatus.dot"></span>
          {{ followUpStatus.label }}
        </span>
        <span v-else></span>

        <button
          type="button"
          aria-label="Tailor resume for this application"
          class="p-1.5 rounded-md bg-amber-50 dark:bg-amber-900 hover:bg-amber-100 dark:hover:bg-amber-800 text-amber-700 dark:text-amber-200 border border-amber-200 dark:border-amber-700 ring-1 ring-amber-100 dark:ring-amber-800 transition-colors ml-auto focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400"
          title="Tailor resume for this application"
          @click.stop="emit('tailor', application)"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
          </svg>
        </button>
      </div>

      <!-- Document list-->
      <div class="flex flex-col gap-2">
        <ul v-if="documents.length" role="list" aria-label="Attached documents" class="flex flex-wrap gap-2">
          <li v-for="doc in documents" :key="doc.id" class="inline-flex items-center w-full gap-1.5 px-2 py-1 rounded-md bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-xs text-slate-600 dark:text-slate-200">
            <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 5H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <span class="truncate w-full">{{ doc.document_type === 'resume' ? 'Resume' : 'Cover letter' }}: {{ doc.filename }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
