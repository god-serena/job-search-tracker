<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({
  content: { type: String, default: "" },
  title: { type: String, default: "Resume" },
});

const emit = defineEmits(["close"]);

const selectedTemplate = ref("ats"); // "ats" | "modern" | "executive"

function handlePrint() {
  window.print();
}

function handleKeyDown(event) {
  if (event.key === "Escape") {
    emit("close");
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyDown);
});

// Helper for formatting inline markdown: bold, italic, links
function formatInline(text) {
  if (!text) return "";
  let safe = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Bold: **text** or __text__
  safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-current">$1</strong>');
  safe = safe.replace(/__(.*?)__/g, '<strong class="font-bold text-current">$1</strong>');

  // Italic: *text* or _text_
  safe = safe.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, '<em class="italic text-current">$1</em>');
  safe = safe.replace(/(?<!_)_(?!_)(.*?)(?<!_)_(?!_)/g, '<em class="italic text-current">$1</em>');

  // Markdown links: [text](url)
  safe = safe.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="underline text-current">$1</a>');

  return safe;
}

// Split subheading into primary title and secondary (date / location)
function splitSubheading(text) {
  if (!text) return { primary: "", secondary: "" };

  const pipeIdx = text.lastIndexOf(" | ");
  if (pipeIdx !== -1) {
    return {
      primary: text.substring(0, pipeIdx).trim(),
      secondary: text.substring(pipeIdx + 3).trim(),
    };
  }
  const emDashIdx = text.lastIndexOf(" — ");
  if (emDashIdx !== -1) {
    return {
      primary: text.substring(0, emDashIdx).trim(),
      secondary: text.substring(emDashIdx + 3).trim(),
    };
  }
  const enDashIdx = text.lastIndexOf(" – ");
  if (enDashIdx !== -1) {
    return {
      primary: text.substring(0, enDashIdx).trim(),
      secondary: text.substring(enDashIdx + 3).trim(),
    };
  }
  return { primary: text, secondary: "" };
}

function isSkillsSection(title) {
  if (!title) return false;
  const t = title.toLowerCase();
  return (
    t.includes("skill") ||
    t.includes("technolog") ||
    t.includes("competenc") ||
    t.includes("tool") ||
    t.includes("stack")
  );
}

function parseCategorySkills(text) {
  if (!text) return { label: "", skills: [] };
  if (text.includes(":")) {
    const colonIdx = text.indexOf(":");
    const label = text.substring(0, colonIdx).replace(/\*\*/g, "").trim();
    const rest = text.substring(colonIdx + 1).trim();
    const skills = rest
      .split(/[,|•]/)
      .map((s) => s.trim())
      .filter(Boolean);
    return { label, skills };
  }
  const skills = text
    .split(/[,|•]/)
    .map((s) => s.trim())
    .filter(Boolean);
  return { label: "", skills };
}

const parsedResume = computed(() => {
  const raw = (props.content || "").trim();
  if (!raw) {
    return {
      name: props.title || "Resume",
      contactLines: [],
      sections: [],
    };
  }

  const lines = props.content.split("\n");
  let name = "";
  const contactLines = [];
  const sections = [];
  let currentSection = null;
  let inHeader = true;

  function ensureCurrentSection() {
    if (!currentSection) {
      currentSection = {
        title: "",
        blocks: [],
      };
      sections.push(currentSection);
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    if (!trimmed) continue;

    // Header 1: # Candidate Name
    if (trimmed.startsWith("# ") && !trimmed.startsWith("## ")) {
      name = trimmed.replace(/^#\s+/, "").trim();
      inHeader = true;
      continue;
    }

    // Header 2: ## Section Title
    if (trimmed.startsWith("## ")) {
      inHeader = false;
      const secTitle = trimmed.replace(/^##\s+/, "").trim();
      currentSection = {
        title: secTitle,
        blocks: [],
      };
      sections.push(currentSection);
      continue;
    }

    // Header contact lines
    if (inHeader && !currentSection) {
      contactLines.push(trimmed);
      continue;
    }

    ensureCurrentSection();

    // Header 3: ### Subtitle / Role
    if (trimmed.startsWith("### ")) {
      const sub = trimmed.replace(/^###\s+/, "").trim();
      const split = splitSubheading(sub);
      currentSection.blocks.push({
        type: "subheading",
        raw: sub,
        primary: split.primary,
        secondary: split.secondary,
      });
      continue;
    }

    // Bullet point: - ... or * ... or • ...
    if (/^[-*•]\s+/.test(trimmed)) {
      const bulletText = trimmed.replace(/^[-*•]\s+/, "").trim();
      const lastBlock = currentSection.blocks[currentSection.blocks.length - 1];
      if (lastBlock && lastBlock.type === "bullets") {
        lastBlock.items.push(bulletText);
      } else {
        currentSection.blocks.push({
          type: "bullets",
          items: [bulletText],
        });
      }
      continue;
    }

    // Regular paragraph
    currentSection.blocks.push({
      type: "paragraph",
      raw: trimmed,
    });
  }

  if (!name) {
    name = props.title || "Resume";
  }

  return {
    name,
    contactLines,
    sections,
  };
});
</script>

<template>
  <div
    class="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex flex-col items-center justify-start overflow-y-auto p-4 sm:p-6 preview-modal-backdrop"
    @click.self="emit('close')"
  >
    <!-- Sticky Header Toolbar (Hidden during print) -->
    <header
      class="no-print sticky top-0 z-10 w-full max-w-4xl bg-slate-900/95 backdrop-blur-md text-white rounded-xl shadow-xl px-4 py-3 mb-6 flex flex-wrap items-center justify-between gap-3 border border-slate-700/80"
    >
      <!-- Title & Template Switcher -->
      <div class="flex items-center gap-3 flex-wrap">
        <span class="text-sm font-semibold uppercase tracking-wider text-slate-400">
          Template:
        </span>
        <div class="flex items-center bg-slate-800 p-0.5 rounded-lg border border-slate-700">
          <button
            type="button"
            class="px-3.5 py-1.5 text-sm font-medium rounded-md transition-all"
            :class="
              selectedTemplate === 'ats'
                ? 'bg-white text-slate-900 font-semibold shadow-xs'
                : 'text-slate-300 hover:text-white'
            "
            @click="selectedTemplate = 'ats'"
          >
            ATS Standard
          </button>
          <button
            type="button"
            class="px-3.5 py-1.5 text-sm font-medium rounded-md transition-all"
            :class="
              selectedTemplate === 'modern'
                ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                : 'text-slate-300 hover:text-white'
            "
            @click="selectedTemplate = 'modern'"
          >
            Modern Minimalist
          </button>
          <button
            type="button"
            class="px-3.5 py-1.5 text-sm font-medium rounded-md transition-all"
            :class="
              selectedTemplate === 'executive'
                ? 'bg-indigo-600 text-white font-semibold shadow-xs'
                : 'text-slate-300 hover:text-white'
            "
            @click="selectedTemplate = 'executive'"
          >
            Executive
          </button>
        </div>
      </div>

      <!-- Actions: Print and Close -->
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="px-4 py-1.5 text-sm font-semibold rounded-md bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer"
          @click="handlePrint"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
            />
          </svg>
          <span>Print / Save as PDF</span>
        </button>

        <button
          type="button"
          class="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-md transition-colors leading-none"
          @click="emit('close')"
          aria-label="Close"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Printable Resume Sheet Container -->
    <div class="w-full flex justify-center preview-sheet-wrapper">
      <!-- ==================== TEMPLATE 1: ATS STANDARD ==================== -->
      <article
        v-if="selectedTemplate === 'ats'"
        class="resume-sheet w-full max-w-[850px] min-h-[1050px] bg-white text-black p-8 sm:p-12 shadow-2xl rounded-sm font-sans"
      >
        <!-- Header -->
        <header class="text-center border-b border-black pb-3 mb-4">
          <h1 class="text-2xl font-bold uppercase tracking-wider text-black">
            {{ parsedResume.name }}
          </h1>
          <div
            v-if="parsedResume.contactLines.length"
            class="text-xs text-black mt-1.5 space-y-0.5 leading-normal"
          >
            <div
              v-for="(cLine, idx) in parsedResume.contactLines"
              :key="idx"
              v-html="formatInline(cLine)"
            ></div>
          </div>
        </header>

        <!-- Sections -->
        <div class="space-y-4">
          <section
            v-for="(sec, sIdx) in parsedResume.sections"
            :key="sIdx"
            class="section-block"
          >
            <h2
              v-if="sec.title"
              class="text-xs font-bold uppercase tracking-widest text-black border-b border-black pb-0.5 mb-2"
            >
              {{ sec.title }}
            </h2>

            <div class="space-y-2">
              <template v-for="(block, bIdx) in sec.blocks" :key="bIdx">
                <!-- Subheading -->
                <div
                  v-if="block.type === 'subheading'"
                  class="flex justify-between items-baseline text-xs font-bold text-black pt-1"
                >
                  <span v-html="formatInline(block.primary)"></span>
                  <span
                    v-if="block.secondary"
                    class="font-normal text-right shrink-0 ml-4"
                    v-html="formatInline(block.secondary)"
                  ></span>
                </div>

                <!-- Bullets -->
                <ul
                  v-else-if="block.type === 'bullets'"
                  class="list-disc list-outside ml-4 space-y-1 text-xs text-black leading-relaxed"
                >
                  <li
                    v-for="(bullet, itemIdx) in block.items"
                    :key="itemIdx"
                    v-html="formatInline(bullet)"
                  ></li>
                </ul>

                <!-- Paragraph -->
                <p
                  v-else-if="block.type === 'paragraph'"
                  class="text-xs text-black leading-relaxed"
                  v-html="formatInline(block.raw)"
                ></p>
              </template>
            </div>
          </section>
        </div>
      </article>

      <!-- ==================== TEMPLATE 2: MODERN MINIMALIST ==================== -->
      <article
        v-else-if="selectedTemplate === 'modern'"
        class="resume-sheet w-full max-w-[850px] min-h-[1050px] bg-white text-slate-800 p-8 sm:p-12 shadow-2xl rounded-sm font-sans"
      >
        <!-- Header -->
        <header class="border-b border-slate-200 pb-4 mb-5">
          <div class="flex items-center justify-between gap-4 flex-wrap">
            <div>
              <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">
                {{ parsedResume.name }}
              </h1>
              <div class="h-1 w-12 bg-amber-500 rounded mt-1.5 mb-2"></div>
            </div>
          </div>
          <div
            v-if="parsedResume.contactLines.length"
            class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-600 mt-2"
          >
            <div
              v-for="(cLine, idx) in parsedResume.contactLines"
              :key="idx"
              class="flex items-center gap-2"
            >
              <span v-if="idx > 0" class="text-amber-500 font-bold">•</span>
              <span v-html="formatInline(cLine)"></span>
            </div>
          </div>
        </header>

        <!-- Sections -->
        <div class="space-y-5">
          <section
            v-for="(sec, sIdx) in parsedResume.sections"
            :key="sIdx"
            class="section-block"
          >
            <div
              v-if="sec.title"
              class="border-b-2 border-amber-500 pb-1 mb-2.5 flex items-center justify-between"
            >
              <h2 class="text-xs font-bold uppercase tracking-wider text-slate-900">
                {{ sec.title }}
              </h2>
            </div>

            <div class="space-y-2">
              <template v-for="(block, bIdx) in sec.blocks" :key="bIdx">
                <!-- Subheading -->
                <div
                  v-if="block.type === 'subheading'"
                  class="flex justify-between items-baseline text-xs pt-1.5"
                >
                  <span
                    class="font-bold text-slate-900"
                    v-html="formatInline(block.primary)"
                  ></span>
                  <span
                    v-if="block.secondary"
                    class="text-amber-800 font-medium text-[11px] shrink-0 ml-4"
                    v-html="formatInline(block.secondary)"
                  ></span>
                </div>

                <!-- Skills section badges -->
                <div
                  v-else-if="block.type === 'bullets' && isSkillsSection(sec.title)"
                  class="flex flex-wrap gap-1.5 py-1"
                >
                  <span
                    v-for="(bullet, itemIdx) in block.items"
                    :key="itemIdx"
                    class="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-900 border border-amber-200/70"
                    v-html="formatInline(bullet)"
                  ></span>
                </div>

                <!-- Bullets -->
                <ul
                  v-else-if="block.type === 'bullets'"
                  class="list-disc list-outside ml-4 space-y-1 text-xs text-slate-700 leading-relaxed marker:text-amber-500"
                >
                  <li
                    v-for="(bullet, itemIdx) in block.items"
                    :key="itemIdx"
                    v-html="formatInline(bullet)"
                  ></li>
                </ul>

                <!-- Skills paragraph with badges -->
                <div
                  v-else-if="block.type === 'paragraph' && isSkillsSection(sec.title) && parseCategorySkills(block.raw).skills.length > 1"
                  class="text-xs py-1"
                >
                  <span
                    v-if="parseCategorySkills(block.raw).label"
                    class="font-semibold text-slate-800 mr-2"
                  >
                    {{ parseCategorySkills(block.raw).label }}:
                  </span>
                  <div class="inline-flex flex-wrap gap-1.5 mt-0.5">
                    <span
                      v-for="(skill, skIdx) in parseCategorySkills(block.raw).skills"
                      :key="skIdx"
                      class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50/80 text-amber-900 border border-amber-200/60"
                      v-html="formatInline(skill)"
                    ></span>
                  </div>
                </div>

                <!-- Paragraph -->
                <p
                  v-else-if="block.type === 'paragraph'"
                  class="text-xs text-slate-700 leading-relaxed"
                  v-html="formatInline(block.raw)"
                ></p>
              </template>
            </div>
          </section>
        </div>
      </article>

      <!-- ==================== TEMPLATE 3: EXECUTIVE ==================== -->
      <article
        v-else-if="selectedTemplate === 'executive'"
        class="resume-sheet w-full max-w-[850px] min-h-[1050px] bg-white text-slate-900 p-8 sm:p-12 shadow-2xl rounded-sm font-sans"
      >
        <!-- Elegant Header Bar -->
        <header
          class="bg-slate-900 text-white -mx-8 sm:-mx-12 -mt-8 sm:-mt-12 p-8 sm:p-10 mb-6 print:mx-0 print:mt-0 print:p-5 print:rounded-none"
        >
          <div class="flex items-start justify-between flex-wrap gap-4">
            <div>
              <h1 class="text-2xl sm:text-3xl font-serif font-bold text-white tracking-wide">
                {{ parsedResume.name }}
              </h1>
              <div
                v-if="parsedResume.contactLines.length"
                class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-300 mt-2 font-sans"
              >
                <div
                  v-for="(cLine, idx) in parsedResume.contactLines"
                  :key="idx"
                  class="flex items-center gap-2"
                >
                  <span v-if="idx > 0" class="text-slate-500">•</span>
                  <span v-html="formatInline(cLine)"></span>
                </div>
              </div>
            </div>
          </div>
        </header>

        <!-- Sections -->
        <div class="space-y-4">
          <section
            v-for="(sec, sIdx) in parsedResume.sections"
            :key="sIdx"
            class="section-block"
          >
            <h2
              v-if="sec.title"
              class="font-serif text-xs font-bold uppercase tracking-widest text-slate-900 border-b-2 border-slate-300 pb-1 mb-2"
            >
              {{ sec.title }}
            </h2>

            <div class="space-y-1.5">
              <template v-for="(block, bIdx) in sec.blocks" :key="bIdx">
                <!-- Subheading with Right-aligned Date -->
                <div
                  v-if="block.type === 'subheading'"
                  class="flex justify-between items-baseline text-xs pt-1.5"
                >
                  <span
                    class="font-semibold text-slate-900 font-sans"
                    v-html="formatInline(block.primary)"
                  ></span>
                  <span
                    v-if="block.secondary"
                    class="font-mono text-[11px] text-slate-600 font-medium shrink-0 ml-4"
                    v-html="formatInline(block.secondary)"
                  ></span>
                </div>

                <!-- Bullets -->
                <ul
                  v-else-if="block.type === 'bullets'"
                  class="list-disc list-outside ml-4 space-y-0.5 text-xs text-slate-800 leading-normal"
                >
                  <li
                    v-for="(bullet, itemIdx) in block.items"
                    :key="itemIdx"
                    v-html="formatInline(bullet)"
                  ></li>
                </ul>

                <!-- Paragraph -->
                <p
                  v-else-if="block.type === 'paragraph'"
                  class="text-xs text-slate-800 leading-normal"
                  v-html="formatInline(block.raw)"
                ></p>
              </template>
            </div>
          </section>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
@media print {
  /* Hide all interactive app elements */
  .no-print {
    display: none !important;
  }

  /* Reset outer container */
  .preview-modal-backdrop {
    position: static !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: visible !important;
    display: block !important;
    height: auto !important;
    width: auto !important;
    inset: auto !important;
    z-index: auto !important;
  }

  .preview-sheet-wrapper {
    padding: 0 !important;
    margin: 0 !important;
    overflow: visible !important;
    display: block !important;
    width: 100% !important;
    max-width: 100% !important;
    height: auto !important;
  }

  .resume-sheet {
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    min-height: auto !important;
    border-radius: 0 !important;
    page-break-after: avoid;
    background: white !important;
  }

  .section-block {
    page-break-inside: avoid;
  }

  @page {
    size: auto;
    margin: 15mm;
  }
}
</style>
