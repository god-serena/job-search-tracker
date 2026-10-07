<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const props = defineProps({
  application: { type: Object, required: true },
  onSelectStatus: { type: Function, required: true },
  onClose: { type: Function, required: true }
});

// All valid board statuses except the application's current one, so
// saving always results in an actual status change.
const statuses = [
  { key: "wishlist", label: "Wishlist" },
  { key: "applied", label: "Applied" },
  { key: "interviewing", label: "Interviewing" },
  { key: "offer", label: "Offer" },
  { key: "rejected", label: "Rejected" },
  { key: "cancelled", label: "Cancelled" },
].filter((s) => s.key !== props.application.status);

const selectedStatus = ref(statuses[0]?.key ?? props.application.status);
const dialogRef = ref(null);
const selectRef = ref(null);

// Focusable elements inside the dialog, used to keep focus contained
// while the dialog is open (no focus-trap dependency).
const FOCUSABLE_SELECTOR =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

function getFocusableElements() {
  if (!dialogRef.value) return [];
  return Array.from(dialogRef.value.querySelectorAll(FOCUSABLE_SELECTOR));
}

function onSave() {
  props.onSelectStatus(selectedStatus.value);
  props.onClose();
}

function onKeydown(e) {
  if (e.key === "Escape") {
    props.onClose();
    return;
  }
  if (e.key !== "Tab") return;

  // Wrap Tab/Shift+Tab among the dialog's focusable elements. If none
  // are focusable, swallow Tab so focus cannot leave the dialog.
  const focusable = getFocusableElements();
  if (!focusable.length) {
    e.preventDefault();
    return;
  }
  const index = focusable.indexOf(document.activeElement);
  if (e.shiftKey) {
    if (index <= 0) {
      e.preventDefault();
      focusable[focusable.length - 1].focus();
    }
  } else if (index === -1 || index === focusable.length - 1) {
    e.preventDefault();
    focusable[0].focus();
  }
}

onMounted(() => {
  document.addEventListener("keydown", onKeydown);
  selectRef.value?.focus();
});

onUnmounted(() => {
  document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4"
    @click.self="onClose"
  >
    <div
      ref="dialogRef"
      role="dialog"
      aria-modal="true"
      aria-labelledby="keyboard-status-title"
      class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full max-w-md"
    >
      <header class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
        <h3 id="keyboard-status-title" class="text-sm font-semibold text-slate-800 dark:text-slate-100">Change Status</h3>
        <button
          type="button"
          class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-slate-800 rounded"
          :aria-label="'Close status dialog'"
          @click="onClose"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </header>

      <div class="p-4">
        <label for="status-select" class="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
          Select a status
        </label>
        <select
          ref="selectRef"
          id="status-select"
          v-model="selectedStatus"
          class="w-full max-w-xs px-3 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-500 bg-white dark:bg-slate-700 dark:text-slate-100 dark:border-slate-600"
        >
          <option v-for="item in statuses" :key="item.key" :value="item.key">
            {{ item.label }}
          </option>
        </select>
      </div>

      <footer class="flex justify-end gap-2 px-4 py-3 border-t border-slate-200 dark:border-slate-700">
        <button
          type="button"
          class="px-3.5 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-md hover:bg-slate-50 dark:hover:bg-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-slate-800"
          @click="onClose"
        >
          Cancel
        </button>
        <button
          type="button"
          class="px-3.5 py-2 text-sm font-medium text-white bg-amber-600 rounded-md hover:bg-amber-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!statuses.length"
          @click="onSave"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>
