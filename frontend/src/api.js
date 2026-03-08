const API_BASE = 'http://localhost:8000';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function loadDemo() {
  const res = await fetch(`${API_BASE}/demo`);
  if (!res.ok) throw new Error('Failed to load demo');
  return res.json();
}

export async function uploadFiles(modelFile, datasetFile, modelName = "My AI Model") {
  const formData = new FormData();
  formData.append('model', modelFile);
  formData.append('dataset', datasetFile);
  formData.append('model_name', modelName);

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Failed to upload files');
  return res.json();
}

export async function runAudit(protectedAttrs) {
  const res = await fetch(`${API_BASE}/audit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ protected_attrs: protectedAttrs })
  });
  if (!res.ok) throw new Error('Failed to run audit');
  return res.json();
}

export async function runIntersectional(attrs, minSize = 20) {
  const res = await fetch(`${API_BASE}/intersectional`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ attrs, min_size: minSize })
  });
  if (!res.ok) throw new Error('Failed to run intersectional analysis');
  return res.json();
}

export async function runDebias(sensitiveAttr, testSize = 0.2) {
  const res = await fetch(`${API_BASE}/debias`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sensitive_attr: sensitiveAttr, test_size: testSize })
  });
  if (!res.ok) throw new Error('Failed to run debiasing');
  return res.json();
}

export async function getCompliance() {
  const res = await fetch(`${API_BASE}/compliance`);
  if (!res.ok) throw new Error('Failed to get compliance');
  return res.json();
}

export const getReportPdfUrl = () => `${API_BASE}/report/pdf`;
export const getCertificateUrl = () => `${API_BASE}/report/certificate`;
