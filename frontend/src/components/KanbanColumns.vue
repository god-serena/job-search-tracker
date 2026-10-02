<script setup>
import ApplicationCard from "./ApplicationCard.vue";

const props = defineProps({
  columns: { type: Array, required: true },
  grouped: { type: Object, required: true },
  colStyle: { type: Object, required: true },
});

const emit = defineEmits(["drop", "edit", "dragstart", "tailor"]);

const dotColor = {
  wishlist:     'bg-sky-400',
  applied:      'bg-indigo-400',
  interviewing: 'bg-violet-400',
  offer:        'bg-emerald-400',
  rejected:     'bg-rose-400',
  cancelled:    'bg-slate-400',
};
</script>

<template>
  <div class="overflow-x-auto h-full px-6 pb-4">
    <div class="flex gap-3 h-full" style="min-width: max-content;">
      <div
        v-for="col in columns"
        :key="col.key"
        class="flex flex-col bg-white rounded-xl border border-slate-200 p-3 border-l-4 shrink-0 shadow-sm"
        style="width: 320px; min-width: 320px;"
        :class="colStyle[col.key]?.border"
        @dragover.prevent
        @drop="emit('drop', col.key)"
      >
        <!-- Column header: dot + label + count badge -->
        <div class="flex items-center gap-2 mb-3 shrink-0">
          <span class="w-2 h-2 rounded-full shrink-0" :class="dotColor[col.key]" />
          <h3 class="text-sm font-bold flex-1" :class="colStyle[col.key]?.label">
            {{ col.label }}
          </h3>
          <span class="bg-slate-100 text-slate-600 text-xs font-semibold rounded-full px-2 py-0.5">
            {{ grouped[col.key]?.length || 0 }}
          </span>
        </div>

        <!-- Cards area -->
        <div class="flex-1 overflow-y-auto pr-0.5">
          <ApplicationCard
            v-for="app in grouped[col.key]"
            :key="app.id"
            :application="app"
            @edit="emit('edit', $event)"
            @dragstart="emit('dragstart', $event)"
            @tailor="emit('tailor', $event)"
          />
          <p v-if="!grouped[col.key]?.length" class="text-sm text-slate-400 italic">
            No applications yet
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
