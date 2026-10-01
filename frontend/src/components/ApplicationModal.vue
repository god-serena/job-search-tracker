<script setup>
import { reactive, watch } from "vue";

const props = defineProps({
  application: { type: Object, default: null },
});
const emit = defineEmits(["close", "save", "delete"]);

const form = reactive({
  company: "",
  role: "",
  url: "",
  status: "wishlist",
  date_applied: "",
  follow_up_date: "",
  contact_name: "",
  description: "",
  notes: "",
});

watch(
  () => props.application,
  (app) => {
    Object.assign(form, {
      company: app?.company || "",
      role: app?.role || "",
      url: app?.url || "",
      status: app?.status || "wishlist",
      date_applied: app?.date_applied || "",
      follow_up_date: app?.follow_up_date || "",
      contact_name: app?.contact_name || "",
      description: app?.description || "",
      notes: app?.notes || "",
    });
  },
  { immediate: true }
);

function submit() {
  const payload = { ...form };
  Object.keys(payload).forEach((key) => {
    if (payload[key] === "") payload[key] = null;
  });
  emit("save", payload);
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
      <h2 class="text-xl font-bold text-slate-800 mb-4">
        {{ application ? "Edit Application" : "New Application" }}
      </h2>

      <form class="space-y-3" @submit.prevent="submit">
        <div class="grid grid-cols-2 gap-3">
          <input v-model="form.company" required placeholder="Company"
            class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base col-span-1" />
          <input v-model="form.role" required placeholder="Role"
            class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base col-span-1" />
        </div>

        <div class="flex items-center gap-2">
          <input v-model="form.url" placeholder="Job posting URL"
            class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base flex-1" />
          <a
            v-if="form.url"
            :href="form.url"
            target="_blank"
            rel="noopener noreferrer"
            class="px-3.5 py-2 text-sm rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 shrink-0 flex items-center gap-1"
          >
            Open
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>

        <select v-model="form.status"
          class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base w-full">
          <option value="wishlist">Wishlist</option>
          <option value="applied">Applied</option>
          <option value="interviewing">Interviewing</option>
          <option value="offer">Offer</option>
          <option value="rejected">Rejected</option>
          <option value="cancelled">Cancelled</option>
        </select>

        <div class="grid grid-cols-2 gap-3">
          <label class="text-sm font-medium text-slate-700 flex flex-col gap-1">
            Date applied
            <input v-model="form.date_applied" type="date"
              class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base" />
          </label>
          <label class="text-sm font-medium text-slate-700 flex flex-col gap-1">
            Follow up on
            <input v-model="form.follow_up_date" type="date"
              class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base" />
          </label>
        </div>

        <input v-model="form.contact_name" placeholder="Contact name"
          class="border border-slate-300 rounded-md px-3 py-2.5 text-sm sm:text-base w-full" />

        <label class="text-sm font-medium text-slate-700 flex flex-col gap-1">
          Job description
          <textarea
            v-model="form.description"
            placeholder="Paste full job posting description here..."
            rows="5"
            class="border border-slate-300 rounded-md px-3 py-2 text-sm sm:text-base w-full text-slate-800"
          ></textarea>
        </label>

        <label class="text-sm font-medium text-slate-700 flex flex-col gap-1">
          Notes
          <textarea
            v-model="form.notes"
            placeholder="Personal notes, thoughts, referral details..."
            rows="3"
            class="border border-slate-300 rounded-md px-3 py-2 text-sm sm:text-base w-full text-slate-800"
          ></textarea>
        </label>

        <div class="flex items-center justify-between pt-2">
          <button
            v-if="application"
            type="button"
            class="px-3.5 py-2 text-sm rounded-md border border-red-300 text-red-600 hover:bg-red-50 transition-colors font-medium"
            @click="emit('delete', application.id)"
          >
            Delete Application
          </button>
          <div class="flex gap-2 ml-auto">
            <button type="button" class="px-4 py-2 text-sm sm:text-base font-medium rounded-md text-slate-600 hover:bg-slate-100"
              @click="emit('close')">
              Discard
            </button>
            <button type="submit" class="px-4 py-2 text-sm sm:text-base font-medium rounded-md bg-slate-900 text-white hover:bg-slate-800">
              Save Application
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>
