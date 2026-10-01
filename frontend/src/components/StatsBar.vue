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
  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
    <!-- Total Applications -->
    <div class="bg-white border border-slate-200 rounded-lg p-3 shadow-sm flex flex-col justify-between">
      <span class="text-sm font-medium text-slate-500">Total Applications</span>
      <div class="mt-1 flex items-baseline">
        <span class="text-3xl font-extrabold text-slate-800">
          {{ stats !== null ? stats.total_applications : '-' }}
        </span>
      </div>
    </div>

    <!-- Active Pipeline -->
    <div class="bg-white border border-slate-200 rounded-lg p-3 shadow-sm flex flex-col justify-between">
      <div>
        <span class="text-sm font-medium text-slate-500">Active Pipeline</span>
        <p class="text-xs text-slate-400">Applied & Interviewing</p>
      </div>
      <div class="mt-1 flex items-baseline">
        <span class="text-3xl font-extrabold text-slate-800">
          {{ stats !== null ? stats.active_pipeline : '-' }}
        </span>
      </div>
    </div>

    <!-- Interview Rate -->
    <div class="bg-white border border-slate-200 rounded-lg p-3 shadow-sm flex flex-col justify-between">
      <span class="text-sm font-medium text-slate-500">Interview Rate</span>
      <div class="mt-1 flex items-baseline">
        <span class="text-3xl font-extrabold text-slate-800">
          {{ stats !== null ? `${stats.interview_rate}%` : '-' }}
        </span>
      </div>
    </div>

    <!-- Offers -->
    <div class="bg-white border border-slate-200 rounded-lg p-3 shadow-sm flex flex-col justify-between">
      <span class="text-sm font-medium text-slate-500">Offers</span>
      <div class="mt-1 flex items-baseline">
        <span class="text-3xl font-extrabold text-emerald-600">
          {{ stats !== null ? (stats.by_status?.offer || 0) : '-' }}
        </span>
      </div>
    </div>

    <!-- Follow-ups Due -->
    <div
      class="border rounded-lg p-3 shadow-sm flex flex-col justify-between transition-all cursor-pointer group"
      :class="stats && stats.follow_ups_due > 0 
        ? 'bg-amber-50/50 border-amber-200 hover:border-amber-400 hover:bg-amber-50' 
        : 'bg-white border-slate-200 hover:border-slate-300'"
      @click="emit('select-filter', 'needs_followup')"
      title="Filter by applications needing follow-up"
    >
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-slate-500 group-hover:text-amber-700">Follow-ups Due</span>
        <span
          v-if="stats && stats.follow_ups_due > 0"
          class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300"
        >
          Action needed
        </span>
      </div>
      <div class="mt-1 flex items-baseline justify-between">
        <span
          class="text-3xl font-extrabold"
          :class="stats && stats.follow_ups_due > 0 ? 'text-amber-700' : 'text-slate-800'"
        >
          {{ stats !== null ? stats.follow_ups_due : '-' }}
        </span>
        <span class="text-sm text-amber-600 font-medium group-hover:underline flex items-center gap-0.5">
          View
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </span>
      </div>
    </div>
  </div>
</template>
