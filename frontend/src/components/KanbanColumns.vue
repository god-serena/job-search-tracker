<script setup>
import ApplicationCard from "./ApplicationCard.vue";

const props = defineProps({
  columns: { type: Array, required: true },
  grouped: { type: Object, required: true },
  colStyle: { type: Object, required: true },
});

const emit = defineEmits(["drop", "edit", "dragstart", "tailor"]);
</script>

<template>
  <!-- Horizontal scroll container — fills remaining vertical space, scrolls horizontally -->
  <div class="overflow-x-auto h-full px-6 pb-4">
    <!-- Inner flex row — never wraps -->
    <div class="flex gap-3 h-full" style="min-width: max-content;">
      <div
        v-for="col in columns"
        :key="col.key"
        class="flex flex-col bg-slate-50 rounded-lg p-3 border-l-2 shrink-0"
        style="width: 320px; min-width: 320px;"
        :class="colStyle[col.key]?.border"
        @dragover.prevent
        @drop="emit('drop', col.key)"
      >
        <!-- Column header -->
        <h3
          class="text-base font-bold mb-3 shrink-0"
          :class="colStyle[col.key]?.label"
        >
          {{ col.label }}
        </h3>

        <!-- Cards area — scrolls vertically if column overflows -->
        <div class="flex-1 overflow-y-auto pr-0.5">
          <ApplicationCard
            v-for="app in grouped[col.key]"
            :key="app.id"
            :application="app"
            @edit="emit('edit', $event)"
            @dragstart="emit('dragstart', $event)"
            @tailor="emit('tailor', $event)"
          />
          <p
            v-if="!grouped[col.key]?.length"
            class="text-sm text-slate-400 italic"
          >
            No applications yet
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
