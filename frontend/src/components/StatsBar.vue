<script setup>
defineProps({
  stats: {
    type: Object,
    default: () => null,
  },
});

const emit = defineEmits(["select-filter"]);
</script>

<template>
  <div class="flex overflow-x-auto gap-3 snap-x sm:grid sm:overflow-visible sm:grid-cols-3 lg:grid-cols-5">
    <!-- Total Applications -->
    <div class="min-w-[170px] shrink-0 snap-start bg-white dark:bg-slate-800 border border-slate-200 border-l-4 border-l-slate-400 rounded-lg p-3 shadow-sm flex flex-col justify-between">
      <div class="flex items-start justify-between">
        <span class="text-sm font-medium text-slate-500 dark:text-slate-300">Total Applications</span>
        <svg class="w-5 h-5 text-slate-300 dark:text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <div class="mt-1 flex items-baseline">
        <span class="text-2xl font-bold text-slate-800 dark:text-white">
          {{ stats !== null ? stats.total_applications : '-' }}
        </span>
      </div>
    </div>

    <!-- Active Pipeline -->
    <div class="min-w-[170px] shrink-0 snap-start bg-white dark:bg-slate-800 border border-slate-200 border-l-4 border-l-slate-400 rounded-lg p-3 shadow-sm flex flex-col justify-between">
      <div class="flex items-start justify-between">
        <div>
          <span class="text-sm font-medium text-slate-500 dark:text-slate-300">Active Pipeline</span>
          <p class="text-xs text-slate-400 dark:text-slate-400">Applied &amp; Interviewing</p>
        </div>
        <svg class="w-5 h-5 text-slate-300 dark:text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <div class="mt-1 flex items-baseline">
        <span class="text-2xl font-bold text-slate-800 dark:text-white">
          {{ stats !== null ? stats.active_pipeline : '-' }}
        </span>
      </div>
    </div>

    <!-- Interview Rate -->
    <div class="min-w-[170px] shrink-0 snap-start bg-white dark:bg-slate-800 border border-slate-200 border-l-4 border-l-slate-400 rounded-lg p-3 shadow-sm flex flex-col justify-between">
      <div class="flex items-start justify-between">
        <span class="text-sm font-medium text-slate-500 dark:text-slate-300">Interview Rate</span>
        <svg class="w-5 h-5 text-slate-300 dark:text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      </div>
      <div class="mt-1 flex items-baseline">
        <span class="text-2xl font-bold text-slate-800 dark:text-white">
          {{ stats !== null ? `${stats.interview_rate}%` : '-' }}
        </span>
      </div>
    </div>

    <!-- Offers -->
    <div class="min-w-[170px] shrink-0 snap-start bg-white dark:bg-slate-800 border border-slate-200 border-l-4 border-l-slate-400 rounded-lg p-3 shadow-sm flex flex-col justify-between">
      <div class="flex items-start justify-between">
        <span class="text-sm font-medium text-slate-500 dark:text-slate-300">Offers</span>
        <svg class="w-5 h-5 text-slate-300 dark:text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
        </svg>
      </div>
      <div class="mt-1 flex items-baseline">
        <span class="text-2xl font-bold text-slate-800 dark:text-white">
          {{ stats !== null ? (stats.by_status?.offer || 0) : '-' }}
        </span>
      </div>
    </div>

    <!-- Follow-ups Due -->
    <button
      type="button"
      class="border rounded-lg p-3 shadow-sm flex flex-col justify-between transition-all cursor-pointer group border-l-4 text-left
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus-visible:ring-offset-2"
      :class="stats && stats.follow_ups_due > 0
        ? 'bg-amber-50/50 dark:bg-amber-950/40 border-amber-200 border-l-amber-400 hover:border-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950/60'
        : 'bg-white dark:bg-slate-800 border-slate-200 border-l-slate-300 hover:border-slate-300'"
      :aria-label="`View applications needing follow-up: ${stats ? stats.follow_ups_due : 0} due`"
      @click="emit('select-filter', 'needs_followup')"
    >
      <div class="flex items-start justify-between">
        <span class="text-sm font-medium text-slate-500 dark:text-slate-300 group-hover:text-amber-700 dark:group-hover:text-amber-300">Follow-ups Due</span>
        <div class="flex items-center gap-1">
          <svg class="w-5 h-5 shrink-0" :class="stats && stats.follow_ups_due > 0 ? 'text-amber-300 dark:text-amber-300' : 'text-slate-200 dark:text-slate-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </div>
      </div>
      <div class="mt-1 flex items-baseline justify-between">
        <span
          class="text-2xl font-bold"
          :class="stats && stats.follow_ups_due > 0 ? 'text-amber-700 dark:text-amber-300' : 'text-slate-800 dark:text-white'"
        >
          {{ stats !== null ? stats.follow_ups_due : '-' }}
        </span>
        <span class="text-sm text-amber-600 dark:text-amber-300 font-medium group-hover:underline flex items-center gap-0.5">
          View
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </span>
      </div>
    </button>
  </div>
</template>
