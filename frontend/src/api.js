const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const isFormData = options.body instanceof FormData;
  const headers = isFormData
    ? { ...(options.headers || {}) }
    : { "Content-Type": "application/json", ...(options.headers || {}) };
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok && res.status !== 204) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  getStats: () => request("/api/stats"),
  list: (status) =>
    request(`/api/applications/${status ? `?status=${status}` : ""}`),
  create: (data) =>
    request("/api/applications/", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) =>
    request(`/api/applications/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  remove: (id) => request(`/api/applications/${id}`, { method: "DELETE" }),
  getResume: () => request("/api/resume"),
  saveResume: (content) =>
    request("/api/resume", {
      method: "PUT",
      body: JSON.stringify({ content }),
    }),
  extractResumePreview: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/api/resume/extract-preview", {
      method: "POST",
      body: formData,
    });
  },
  uploadResumeFile: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/api/resume/upload", {
      method: "POST",
      body: formData,
    });
  },
  getTailorPrompt: (applicationId) =>
    request(`/api/applications/${applicationId}/tailor-prompt`),
  listTailoredResumes: (applicationId) =>
    request(`/api/applications/${applicationId}/tailored-resumes`),
  saveTailoredResume: (applicationId, data) =>
    request(`/api/applications/${applicationId}/tailored-resumes`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  generateLocalTailoredResume: (applicationId, model) =>
    request(`/api/applications/${applicationId}/tailored-resumes/generate-local`, {
      method: "POST",
      body: JSON.stringify({ model }),
    }),
  getCoverLetterPrompt: (applicationId) =>
    request(`/api/applications/${applicationId}/cover-letter/prompt`),
  generateLocalCoverLetter: (applicationId, model) =>
    request(`/api/applications/${applicationId}/cover-letter/generate-local`, {
      method: "POST",
      body: JSON.stringify({ model }),
    }),
  listApplicationDocuments: (applicationId) =>
    request(`/api/applications/${applicationId}/documents`),
  getAllApplicationDocuments: () => request("/api/application-documents/"),
  uploadApplicationDocument: (applicationId, documentType, file) => {
    const formData = new FormData();
    formData.append("document_type", documentType);
    formData.append("file", file);
    return request(`/api/applications/${applicationId}/documents`, {
      method: "POST",
      body: formData,
    });
  },
  applicationDocumentDownloadUrl: (applicationId, documentId) =>
    `${API_URL}/api/applications/${applicationId}/documents/${documentId}/download`,
  getOutreachPrompt: (applicationId, templateType = "cold_outreach") =>
    request(
      `/api/applications/${applicationId}/outreach/prompt?template_type=${templateType}`
    ),
  generateLocalOutreach: (applicationId, templateType, model) =>
    request(`/api/applications/${applicationId}/outreach/generate-local`, {
      method: "POST",
      body: JSON.stringify({ template_type: templateType, model }),
    }),
};
