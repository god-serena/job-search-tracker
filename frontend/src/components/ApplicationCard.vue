<script setup>
import { computed } from "vue";

const props = defineProps({
  application: { type: Object, required: true },
});
const emit = defineEmits(["edit", "dragstart", "tailor"]);

const isCancelled = computed(() => props.application.status === "cancelled");

const companyInitial = computed(() => {
  const name = props.application.company || "?";
  return name.charAt(0).toUpperCase();
});

const avatarColors = [
  'bg-indigo-100 text-indigo-700',
  'bg-violet-100 text-violet-700',
  'bg-sky-100 text-sky-700',
  'bg-emerald-100 text-emerald-700',
  'bg-amber-100 text-amber-700',
  'bg-rose-100 text-rose-700',
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
    return { label: `Overdue (${date})`, classes: "bg-red-50 text-red-700 border border-red-200" };
  }
  if (date === today) {
    return { label: "Due today", classes: "bg-amber-100 text-amber-800 border border-amber-200" };
  }
  return { label: `Follow up ${date}`, classes: "bg-slate-100 text-slate-600 border border-slate-200" };
});
</script>

<template>
  <div
    class="bg-white rounded-xl border border-slate-200 shadow-sm p-3.5 mb-3 cursor-grab active:cursor-grabbing hover:shadow-md hover:border-slate-300 transition-all"
    draggable="true"
    @dragstart="emit('dragstart', application, $event)"
    @click="emit('edit', application)"
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
          class="font-semibold text-slate-900 text-base hover:text-amber-600 hover:underline inline-flex items-center gap-1 group leading-tight"
          @click.stop
        >
          <span class="truncate">{{ application.company }}</span>
          <svg class="w-3.5 h-3.5 text-slate-400 group-hover:text-amber-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
        <p v-else class="font-semibold text-slate-900 text-base leading-tight truncate">{{ application.company }}</p>
      </div>
    </div>

    <p class="text-slate-500 text-sm mb-2 font-medium pl-10">{{ application.role }}</p>

    <p
      v-if="application.description && !isCancelled"
      class="text-slate-600 text-sm mb-2.5 line-clamp-2 bg-slate-50 rounded-md p-2 border border-slate-100 italic"
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
          class="px-2.5 py-1 rounded-md text-xs font-semibold inline-flex items-center gap-1"
          :class="followUpStatus.classes"
        >
          {{ followUpStatus.label }}
        </span>
        <span v-else></span>

        <button
          type="button"
          class="p-1.5 rounded-md bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 ring-1 ring-amber-100 transition-colors ml-auto"
          title="Tailor resume for this application"
          @click.stop="emit('tailor', application)"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
