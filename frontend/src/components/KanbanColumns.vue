<script setup>
import ApplicationCard from "./ApplicationCard.vue";

const props = defineProps({
  columns: { type: Array, required: true },
  grouped: { type: Object, required: true },
  colStyle: { type: Object, required: true },
  documentsMap: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["drop", "edit", "dragstart", "tailor"]);

const dotColor = {
  wishlist:     'bg-sky-300',
  applied:      'bg-amber-300',
  interviewing: 'bg-violet-300',
  offer:        'bg-emerald-300',
  rejected:     'bg-rose-300',
  cancelled:    'bg-slate-300',
};
</script>

<template>
  <section role="region" aria-label="Job applications board" class="h-full">
    <div class="relative h-full">
      <div class="h-full overflow-auto px-4 sm:px-6 pb-4">
        <div class="flex h-full min-h-[280px] w-max gap-3">
          <div
            v-for="col in columns"
            :key="col.key"
            class="flex h-full min-h-0 w-[min(85vw,320px)] shrink-0 flex-col rounded-xl border border-slate-200 bg-white p-3 border-l-4 shadow-sm"
            :class="colStyle[col.key]?.border"
            @dragover.prevent
            @drop="emit('drop', col.key)"
          >
            <!-- Column header: dot + label + count badge -->
            <header class="mb-3 flex shrink-0 items-center gap-2">
              <span aria-hidden="true" class="h-2 w-2 shrink-0 rounded-full" :class="dotColor[col.key]" />
              <h3 class="flex-1 text-sm font-semibold text-slate-700" :class="colStyle[col.key]?.label">
                {{ col.label }}
              </h3>
              <span class="rounded-full bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700 ring-1 ring-inset ring-amber-200">
                {{ grouped[col.key]?.length || 0 }}
              </span>
            </header>

            <!-- Cards area -->
            <div class="min-h-0 flex-1 overflow-y-auto pr-0.5">
              <ApplicationCard
                v-for="app in grouped[col.key]"
                :key="app.id"
                :application="app"
                :documents="documentsMap[app.id] || []"
                @edit="emit('edit', $event)"
                @dragstart="emit('dragstart', $event)"
                @tailor="emit('tailor', $event)"
              />
              <p
                v-if="!grouped[col.key]?.length"
                class="mx-1 mt-1 rounded-lg border border-dashed border-slate-300 px-3 py-4 text-center text-sm text-slate-400"
              >
                No applications in this column yet
              </p>
            </div>
          </div>
        </div>
      </div>
      <!-- Subtle right-edge fade hinting that more columns are scrollable -->
      <div
        aria-hidden="true"
        class="pointer-events-none absolute inset-y-0 right-0 w-10 bg-gradient-to-l from-white to-transparent"
      />
    </div>
  </section>
</template>
