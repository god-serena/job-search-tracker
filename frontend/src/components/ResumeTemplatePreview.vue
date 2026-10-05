<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({
  content: { type: String, default: "" },
  title: { type: String, default: "Resume" },
});

const emit = defineEmits(["close"]);

// State
const selectedTemplate = ref("ats"); // "ats" | "modern" | "executive"
const pageMode = ref("fit"); // "fit" | "multi"
const selectedDensity = ref("compact"); // "compact" | "normal"


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

// Simple Fit Screen zoom function
function fitZoom() {
  return Math.max(0.4, Math.min(0.8, Math.floor(((window.innerWidth - 32) / 794) * 10) / 10));
}

const zoom = ref(fitZoom());

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

// Calculate multi-page section splits based on realistic height estimations
const pages = computed(() => {
  const sections = parsedResume.value.sections || [];
  if (pageMode.value === "fit" || sections.length === 0) {
    return [sections];
  }

  const isCompact = selectedDensity.value === "compact";
  const itemH = isCompact ? 22 : 28;
  const subH = isCompact ? 24 : 30;
  const titleH = isCompact ? 30 : 36;
  const headerH = 120 + (parsedResume.value.contactLines?.length || 0) * 16;
  const PAGE_1_BUDGET = 950;

  let currentH = headerH;
  const page1 = [];
  const page2 = [];
  let onPage2 = false;

  for (let sIdx = 0; sIdx < sections.length; sIdx++) {
    const sec = sections[sIdx];
    if (onPage2) {
      page2.push(sec);
      continue;
    }

    // Estimate this section's height
    let secH = titleH;
    for (const b of sec.blocks) {
      if (b.type === "subheading") {
        secH += subH;
      } else if (b.type === "bullets") {
        secH += (b.items?.length || 0) * itemH;
      } else if (b.type === "paragraph") {
        const lines = Math.max(1, Math.ceil((b.raw || "").length / 75));
        secH += lines * (isCompact ? 18 : 22) + 8;
      }
    }

    if (currentH + secH <= PAGE_1_BUDGET) {
      page1.push(sec);
      currentH += secH;
    } else {
      // Exceeds remaining Page 1 budget
      const remainingSpace = PAGE_1_BUDGET - currentH;
      if (remainingSpace > 180 && sec.blocks.length > 1) {
        const p1Blocks = [];
        const p2Blocks = [];
        let blockHSum = titleH;

        for (const b of sec.blocks) {
          let bH = 0;
          if (b.type === "subheading") bH = subH;
          else if (b.type === "bullets") bH = (b.items?.length || 0) * itemH;
          else if (b.type === "paragraph") {
            const lines = Math.max(1, Math.ceil((b.raw || "").length / 75));
            bH = lines * (isCompact ? 18 : 22) + 8;
          }

          if (blockHSum + bH <= remainingSpace) {
            p1Blocks.push(b);
            blockHSum += bH;
          } else {
            p2Blocks.push(b);
          }
        }

        if (p1Blocks.length > 0 && p2Blocks.length > 0) {
          page1.push({ title: sec.title, blocks: p1Blocks });
          page2.push({ title: `${sec.title} (Continued)`, blocks: p2Blocks });
          onPage2 = true;
          continue;
        }
      }

      if (page1.length === 0) {
        page1.push(sec);
      } else {
        page2.push(sec);
      }
      onPage2 = true;
    }
  }

  if (page2.length === 0) {
    return [page1];
  }
  return [page1, page2];
});

const pageCount = computed(() => pages.value.length);

// Isolated 1:1 Print Engine using hidden iframe
function handlePrint() {
  const originalTitle = document.title;
  const resumeName = parsedResume.value.name
    ? `${parsedResume.value.name} - Resume`
    : props.title || "Resume";
  document.title = resumeName;

  const sheets = document.querySelectorAll("#resume-print-root .a4-page-sheet");
  if (!sheets || sheets.length === 0) {
    window.print();
    document.title = originalTitle;
    return;
  }

  // Collect compiled stylesheets from current document
  let stylesHtml = "";
  document.querySelectorAll('link[rel="stylesheet"], style').forEach((el) => {
    stylesHtml += el.outerHTML;
  });

  let sheetsHtml = "";
  sheets.forEach((sheet) => {
    sheetsHtml += sheet.outerHTML;
  });

  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.right = "0";
  iframe.style.bottom = "0";
  iframe.style.width = "0";
  iframe.style.height = "0";
  iframe.style.border = "0";
  iframe.setAttribute("aria-hidden", "true");
  document.body.appendChild(iframe);

  const frameDoc = iframe.contentWindow.document;
  frameDoc.open();
  frameDoc.write(`<!doctype html>
  <html>
  <head>
    <meta charset="UTF-8" />
    <title>${resumeName}</title>
    ${stylesHtml}
    <style>
      @page {
        size: A4 portrait;
        margin: 0;
      }
      html, body {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        margin: 0 !important;
        padding: 0 !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
      .print-frame-body {
        width: 100%;
        margin: 0 !important;
        padding: 0 !important;
        background: #ffffff !important;
        display: flex;
        flex-direction: column;
        align-items: center;
      }
      .a4-page-sheet {
        box-sizing: border-box !important;
        width: 210mm !important;
        height: 297mm !important;
        min-height: 297mm !important;
        max-height: 297mm !important;
        margin: 0 auto !important;
        background: #ffffff !important;
        background-color: #ffffff !important;
        box-shadow: none !important;
        border: none !important;
        border-radius: 0 !important;
        overflow: hidden !important;
        page-break-after: always !important;
        break-after: page !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
      .a4-page-sheet:last-of-type,
      .a4-page-sheet:last-child {
        page-break-after: avoid !important;
        break-after: avoid !important;
      }
      h1, h2, h3, header, .subheading-item {
        page-break-after: avoid !important;
        break-after: avoid !important;
      }
      li {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
    </style>
  </head>
  <body class="print-frame-body">
    ${sheetsHtml}
  </body>
  </html>`);
  frameDoc.close();

  setTimeout(() => {
    iframe.contentWindow.focus();
    iframe.contentWindow.print();
    document.title = originalTitle;
    setTimeout(() => {
      if (document.body.contains(iframe)) {
        document.body.removeChild(iframe);
      }
    }, 2000);
  }, 250);
}
</script>

<template>
  <Teleport to="body">
    <div
      id="resume-print-root"
      role="dialog"
      aria-modal="true"
      aria-label="Resume preview and print"
      class="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-sm flex flex-col items-center overflow-y-auto p-4 sm:p-6 preview-modal-backdrop"
      @click.self="emit('close')"
    >
      <!-- Control Toolbar (Sticky Top, no-print) -->
      <header
        aria-label="Preview controls"
        class="no-print sticky top-0 z-30 w-full max-w-5xl bg-slate-900/95 backdrop-blur-md text-white rounded-2xl shadow-2xl p-3 sm:p-4 mb-6 [&_button]:focus-visible:outline-none [&_button]:focus-visible:ring-2 [&_button]:focus-visible:ring-amber-400 border border-slate-700/80 transition-all"
      >
        <!-- Tier 1: Document Title, Status Badge & Primary Actions -->
        <div class="flex flex-wrap items-center justify-between gap-x-4 gap-y-2.5 pb-2.5 border-b border-slate-800/80">
          <!-- Left: Title & Page Badge -->
          <div class="flex items-center gap-3 min-w-0">
            <div class="flex items-center gap-2 truncate">
              <svg class="w-5 h-5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span class="text-sm sm:text-base font-semibold text-slate-100 truncate">
                {{ parsedResume.name ? `${parsedResume.name} — Resume` : props.title || 'Resume Preview' }}
              </span>
            </div>

            <!-- Live Page Badge -->
            <span
              v-if="pageCount === 1"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-600/40 shadow-xs shrink-0"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
              </svg>
              <span>✓ 1 Page (A4)</span>
            </span>
            <span
              v-else
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-950/80 text-indigo-300 border border-indigo-600/40 shadow-xs shrink-0"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>2 Pages (A4)</span>
            </span>
          </div>

          <!-- Right: Print CTA & Modal Close -->
          <div class="flex items-center gap-2.5 shrink-0">
            <button
              type="button"
              class="px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-2 transition-all shadow-md hover:shadow-emerald-600/20 active:scale-95 cursor-pointer"
              @click="handlePrint"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              <span>Print / Save as PDF</span>
            </button>

            <div class="h-6 w-px bg-slate-700/80 mx-1"></div>

            <button
              type="button"
              class="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
              @click="emit('close')"
              aria-label="Close"
              title="Close Preview (Esc)"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Tier 2: Formatting & View Toolbar -->
        <div class="flex items-center justify-between gap-4 flex-wrap">
          <!-- Left: Template, Mode, Density Clusters -->
          <div class="flex items-center gap-3 flex-wrap">
            <!-- Cluster 1: Template Switcher -->
            <div class="flex flex-wrap items-center gap-1 bg-slate-800/90 p-1 rounded-xl border border-slate-700/80 shadow-xs">
              <button
                type="button"
                class="px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all cursor-pointer"
                :class="selectedTemplate === 'ats' ? 'bg-white text-slate-900 font-semibold shadow-xs' : 'text-slate-300 hover:text-white'"
                :aria-pressed="selectedTemplate === 'ats'"
                @click="selectedTemplate = 'ats'"
              >
                ATS Standard
              </button>
              <button
                type="button"
                class="px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all cursor-pointer"
                :class="selectedTemplate === 'modern' ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs' : 'text-slate-300 hover:text-white'"
                :aria-pressed="selectedTemplate === 'modern'"
                @click="selectedTemplate = 'modern'"
              >
                Modern Minimalist
              </button>
              <button
                type="button"
                class="px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all cursor-pointer"
                :class="selectedTemplate === 'executive' ? 'bg-slate-700 text-white font-semibold shadow-xs' : 'text-slate-300 hover:text-white'"
                :aria-pressed="selectedTemplate === 'executive'"
                @click="selectedTemplate = 'executive'"
              >
                Executive
              </button>
            </div>

            <div class="hidden sm:block h-5 w-px bg-slate-700/80"></div>

            <!-- Cluster 2: Layout (Page Mode & Density) -->
            <div class="flex items-center gap-2 flex-wrap gap-1">
              <!-- Page Mode -->
              <div class="flex items-center bg-slate-800/90 p-1 rounded-xl border border-slate-700/80 shadow-xs">
                <button
                  type="button"
                  class="px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all flex items-center gap-1.5 cursor-pointer"
                  :class="pageMode === 'fit' ? 'bg-slate-700 text-white font-semibold shadow-xs' : 'text-slate-300 hover:text-white'"
                  :aria-pressed="pageMode === 'fit'"
                  @click="pageMode = 'fit'"
                >
                  <span>📄 Fit 1 Page</span>
                </button>
                <button
                  type="button"
                  class="px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all flex items-center gap-1.5 cursor-pointer"
                  :class="pageMode === 'multi' ? 'bg-slate-700 text-white font-semibold shadow-xs' : 'text-slate-300 hover:text-white'"
                  :aria-pressed="pageMode === 'multi'"
                  @click="pageMode = 'multi'"
                >
                  <span>📑 Multi-Page</span>
                </button>
              </div>

              <!-- Density -->
              <div class="flex items-center bg-slate-800/90 p-1 rounded-xl border border-slate-700/80 shadow-xs">
                <button
                  type="button"
                  class="px-2.5 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all cursor-pointer"
                  :class="selectedDensity === 'compact' ? 'bg-slate-700 text-white font-semibold shadow-xs' : 'text-slate-300 hover:text-white'"
                  :aria-pressed="selectedDensity === 'compact'"
                  @click="selectedDensity = 'compact'"
                >
                  Compact
                </button>
                <button
                  type="button"
                  class="px-2.5 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all cursor-pointer"
                  :class="selectedDensity === 'normal' ? 'bg-slate-700 text-white font-semibold shadow-xs' : 'text-slate-300 hover:text-white'"
                  :aria-pressed="selectedDensity === 'normal'"
                  @click="selectedDensity = 'normal'"
                >
                  Normal
                </button>
              </div>
            </div>
          </div>

          <!-- Right: Zoom Controls -->
          <div class="flex items-center bg-slate-800/90 p-1 rounded-xl border border-slate-700/80 shadow-xs ml-auto">
            <button
              type="button"
              class="px-2.5 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400"
              :class="Math.abs(zoom - fitZoom()) < 0.01 ? 'bg-slate-700 text-white font-semibold' : 'text-slate-300 hover:text-white'"
              :aria-pressed="Math.abs(zoom - fitZoom()) < 0.01"
              title="Fit Screen"
              @click="zoom = fitZoom()"
            >
              Fit Screen
            </button>
            <button
              type="button"
              class="p-1.5 text-slate-300 hover:text-white rounded-lg transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 disabled:opacity-30"
              :disabled="zoom <= 0.4"
              title="Zoom Out (10%)"
              @click="zoom = Math.max(0.4, Math.round((zoom - 0.1) * 10) / 10)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
              </svg>
            </button>
            <button
              type="button"
              class="px-2 py-1.5 text-xs sm:text-sm font-mono font-medium rounded-lg transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400"
              :class="Math.round(zoom * 100) === 100 ? 'bg-slate-700 text-white font-semibold' : 'text-slate-300 hover:text-white'"
              title="Reset to 100%"
              @click="zoom = 1.0"
            >
              {{ Math.round(zoom * 100) }}%
            </button>
            <button
              type="button"
              class="p-1.5 text-slate-300 hover:text-white rounded-lg transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 disabled:opacity-30"
              :disabled="zoom >= 1.6"
              title="Zoom In (10%)"
              @click="zoom = Math.min(1.6, Math.round((zoom + 0.1) * 10) / 10)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <!-- Printable Resume Sheet Container -->
      <div
        class="preview-sheet-wrapper flex flex-col items-center pb-12 origin-top"
        :style="{
          transform: `scale(${zoom})`,
          transformOrigin: 'top center'
        }"
      >
        <template v-for="(pageSections, pageIndex) in pages" :key="pageIndex">
          <!-- Multi-Page Divider on Screen (Hidden in print) -->
          <div
            v-if="pageIndex > 0"
            class="no-print my-6 flex items-center justify-center gap-3 text-xs font-semibold uppercase tracking-widest text-slate-400 select-none"
          >
            <span class="text-slate-600 font-mono">———</span>
            <span>Page {{ pageIndex + 1 }} of {{ pages.length }}</span>
            <span class="text-slate-600 font-mono">———</span>
          </div>

          <!-- True A4 Physical Sheet (210mm x 297mm) -->
          <article
            class="a4-page-sheet shadow-2xl relative select-text"
            :class="[
              `template-${selectedTemplate}`,
              `density-${selectedDensity}`,
              { 'fit-one-page': pageMode === 'fit' }
            ]"
            :data-page="pageIndex + 1"
          >
            <!-- ==================== TEMPLATE 1: ATS STANDARD ==================== -->
            <div v-if="selectedTemplate === 'ats'" class="font-sans text-black">
              <!-- Page 1 ATS Header -->
              <header v-if="pageIndex === 0" class="text-center border-b border-black pb-2.5 mb-3.5 ats-header">
                <h1 class="text-2xl font-bold uppercase tracking-wider text-black">
                  {{ parsedResume.name }}
                </h1>
                <div
                  v-if="parsedResume.contactLines.length"
                  class="text-xs text-black mt-1 space-y-0.5 leading-normal ats-contact"
                >
                  <div
                    v-for="(cLine, idx) in parsedResume.contactLines"
                    :key="idx"
                    v-html="formatInline(cLine)"
                  ></div>
                </div>
              </header>

              <!-- Page 2 ATS Running Header -->
              <header
                v-else
                class="border-b border-black pb-1.5 mb-3 flex items-center justify-between text-xs text-black ats-page2-header"
              >
                <span class="font-bold uppercase tracking-wider">{{ parsedResume.name }}</span>
                <span class="text-[11px] text-slate-600 font-mono">Page {{ pageIndex + 1 }} of {{ pages.length }}</span>
              </header>

              <!-- Sections -->
              <div class="space-y-3">
                <section
                  v-for="(sec, sIdx) in pageSections"
                  :key="sIdx"
                  class="section-block"
                >
                  <h2
                    v-if="sec.title"
                    class="text-xs font-bold uppercase tracking-widest text-black border-b border-black pb-0.5 mb-1.5"
                  >
                    {{ sec.title }}
                  </h2>

                  <div class="space-y-1.5">
                    <template v-for="(block, bIdx) in sec.blocks" :key="bIdx">
                      <!-- Subheading -->
                      <div
                        v-if="block.type === 'subheading'"
                        class="subheading-item flex justify-between items-baseline text-xs font-bold text-black pt-0.5"
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
                        class="list-disc list-outside ml-4 space-y-0.5 text-xs text-black leading-relaxed"
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
            </div>

            <!-- ==================== TEMPLATE 2: MODERN MINIMALIST ==================== -->
            <div v-else-if="selectedTemplate === 'modern'" class="font-sans text-slate-800">
              <!-- Page 1 Modern Header -->
              <header v-if="pageIndex === 0" class="border-b border-slate-200 pb-3 mb-3.5 modern-header">
                <div class="flex items-center justify-between gap-4 flex-wrap">
                  <div>
                    <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">
                      {{ parsedResume.name }}
                    </h1>
                    <div class="h-1 w-12 bg-amber-500 rounded mt-1 mb-1.5"></div>
                  </div>
                </div>
                <div
                  v-if="parsedResume.contactLines.length"
                  class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-600 mt-1"
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

              <!-- Page 2 Modern Running Header -->
              <header
                v-else
                class="border-b border-amber-500/40 pb-1.5 mb-3 flex items-center justify-between text-xs modern-page2-header"
              >
                <div class="flex items-center gap-2">
                  <span class="font-bold text-slate-900">{{ parsedResume.name }}</span>
                  <span class="h-1 w-3 bg-amber-500 rounded inline-block"></span>
                </div>
                <span class="text-[11px] font-medium text-amber-800">Page {{ pageIndex + 1 }} of {{ pages.length }}</span>
              </header>

              <!-- Sections -->
              <div class="space-y-3">
                <section
                  v-for="(sec, sIdx) in pageSections"
                  :key="sIdx"
                  class="section-block"
                >
                  <div
                    v-if="sec.title"
                    class="border-b-2 border-amber-500 pb-0.5 mb-1.5 flex items-center justify-between"
                  >
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-900">
                      {{ sec.title }}
                    </h2>
                  </div>

                  <div class="space-y-1.5">
                    <template v-for="(block, bIdx) in sec.blocks" :key="bIdx">
                      <!-- Subheading -->
                      <div
                        v-if="block.type === 'subheading'"
                        class="subheading-item flex justify-between items-baseline text-xs pt-0.5"
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

                      <!-- Skills Section Badges for Bullets -->
                      <div
                        v-else-if="block.type === 'bullets' && isSkillsSection(sec.title)"
                        class="flex flex-wrap gap-1.5 py-0.5"
                      >
                        <span
                          v-for="(bullet, itemIdx) in block.items"
                          :key="itemIdx"
                          class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-900 border border-amber-200/70"
                          v-html="formatInline(bullet)"
                        ></span>
                      </div>

                      <!-- Bullets -->
                      <ul
                        v-else-if="block.type === 'bullets'"
                        class="list-disc list-outside ml-4 space-y-0.5 text-xs text-slate-700 leading-relaxed marker:text-amber-500"
                      >
                        <li
                          v-for="(bullet, itemIdx) in block.items"
                          :key="itemIdx"
                          v-html="formatInline(bullet)"
                        ></li>
                      </ul>

                      <!-- Skills Paragraph with Badges -->
                      <div
                        v-else-if="block.type === 'paragraph' && isSkillsSection(sec.title) && parseCategorySkills(block.raw).skills.length > 1"
                        class="text-xs py-0.5"
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
            </div>

            <!-- ==================== TEMPLATE 3: EXECUTIVE ==================== -->
            <div v-else-if="selectedTemplate === 'executive'" class="font-sans text-slate-900">
              <!-- Page 1 Executive Banner -->
              <header
                v-if="pageIndex === 0"
                class="bg-slate-900 text-white executive-header"
                :style="{
                  marginLeft: selectedDensity === 'compact' || pageMode === 'fit' ? '-10mm' : '-14mm',
                  marginRight: selectedDensity === 'compact' || pageMode === 'fit' ? '-10mm' : '-14mm',
                  marginTop: pageMode === 'fit' ? '-8mm' : (selectedDensity === 'compact' ? '-10mm' : '-14mm'),
                  padding: selectedDensity === 'compact' || pageMode === 'fit' ? '18px 24px' : '22px 30px',
                  marginBottom: selectedDensity === 'compact' || pageMode === 'fit' ? '12px' : '16px'
                }"
              >
                <div class="flex items-start justify-between flex-wrap gap-4">
                  <div>
                    <h1 class="text-2xl sm:text-3xl font-serif font-bold text-white tracking-wide">
                      {{ parsedResume.name }}
                    </h1>
                    <div
                      v-if="parsedResume.contactLines.length"
                      class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-300 mt-1 font-sans"
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

              <!-- Page 2 Executive Running Header -->
              <header
                v-else
                class="border-b-2 border-slate-300 pb-1.5 mb-3 flex items-center justify-between text-xs text-slate-900 executive-page2-header"
              >
                <span class="font-serif font-bold text-slate-900 tracking-wide">{{ parsedResume.name }}</span>
                <span class="font-mono text-[11px] text-slate-600">Page {{ pageIndex + 1 }} of {{ pages.length }}</span>
              </header>

              <!-- Sections -->
              <div class="space-y-3">
                <section
                  v-for="(sec, sIdx) in pageSections"
                  :key="sIdx"
                  class="section-block"
                >
                  <h2
                    v-if="sec.title"
                    class="font-serif text-xs font-bold uppercase tracking-widest text-slate-900 border-b-2 border-slate-300 pb-0.5 mb-1.5"
                  >
                    {{ sec.title }}
                  </h2>

                  <div class="space-y-1">
                    <template v-for="(block, bIdx) in sec.blocks" :key="bIdx">
                      <!-- Subheading with Right-aligned Date -->
                      <div
                        v-if="block.type === 'subheading'"
                        class="subheading-item flex justify-between items-baseline text-xs pt-0.5"
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
            </div>
          </article>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* True A4 Physical Sheet */
.a4-page-sheet {
  box-sizing: border-box;
  width: 210mm;
  height: 297mm;
  min-height: 297mm;
  max-height: 297mm;
  overflow: hidden;
  background: #ffffff;
  position: relative;
}

/* Density: Normal (14mm margins, 10.5pt text, 1.35 line-height) */
.a4-page-sheet.density-normal {
  padding: 14mm;
  font-size: 10.5pt;
  line-height: 1.35;
}
.a4-page-sheet.density-normal h1 {
  font-size: 22pt;
  line-height: 1.2;
}
.a4-page-sheet.density-normal h2 {
  font-size: 11pt;
}
.a4-page-sheet.density-normal li {
  margin-bottom: 1.4mm;
}

/* Density: Compact (10mm margins, 9.5pt text, 1.25 line-height) */
.a4-page-sheet.density-compact {
  padding: 10mm;
  font-size: 9.5pt;
  line-height: 1.25;
}
.a4-page-sheet.density-compact h1 {
  font-size: 18pt;
  line-height: 1.15;
}
.a4-page-sheet.density-compact h2 {
  font-size: 10pt;
}
.a4-page-sheet.density-compact li {
  margin-bottom: 0.8mm;
}

/* Fit to 1 Page Compression */
.a4-page-sheet.fit-one-page {
  padding: 8mm 10mm !important;
  font-size: 9pt !important;
  line-height: 1.22 !important;
}
.a4-page-sheet.fit-one-page header.ats-header,
.a4-page-sheet.fit-one-page header.modern-header {
  margin-bottom: 2.5mm !important;
  padding-bottom: 1.5mm !important;
}
.a4-page-sheet.fit-one-page h1 {
  font-size: 16pt !important;
  line-height: 1.15 !important;
  margin-bottom: 1mm !important;
}
.a4-page-sheet.fit-one-page h2 {
  font-size: 9.5pt !important;
  margin-bottom: 1.2mm !important;
  padding-bottom: 0.5mm !important;
}
.a4-page-sheet.fit-one-page .section-block {
  margin-bottom: 2mm !important;
}
.a4-page-sheet.fit-one-page li {
  font-size: 8.5pt !important;
  line-height: 1.22 !important;
  margin-bottom: 0.4mm !important;
}

@media print {
  .no-print {
    display: none !important;
  }
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
    transform: none !important;
  }
  .a4-page-sheet {
    box-shadow: none !important;
    border: none !important;
    border-radius: 0 !important;
    width: 210mm !important;
    height: 297mm !important;
    min-height: 297mm !important;
    max-height: 297mm !important;
    margin: 0 auto !important;
    overflow: hidden !important;
    page-break-after: always !important;
    break-after: page !important;
    background: #ffffff !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  .a4-page-sheet:last-of-type,
  .a4-page-sheet:last-child {
    page-break-after: avoid !important;
    break-after: avoid !important;
  }
  h1, h2, h3, header, .subheading-item {
    page-break-after: avoid !important;
    break-after: avoid !important;
  }
  li {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
  }
  @page {
    size: A4 portrait;
    margin: 0;
  }
}
</style>
