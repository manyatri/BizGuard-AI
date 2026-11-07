// Smart resilient API Client
// Handles Next.js rewrites, localhost vs 127.0.0.1 IPv6/IPv4 mismatches, and automatic fallbacks

const getBaseCandidates = (): string[] => {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (envUrl) return [envUrl];

  if (typeof window !== 'undefined') {
    const host = window.location.hostname || 'localhost';
    return [
      '', // Try Next.js rewrite proxy first (zero CORS, zero port mismatch)
      `http://${host}:8000`,
      'http://127.0.0.1:8000',
      'http://localhost:8000',
    ];
  }
  return ['http://127.0.0.1:8000', 'http://localhost:8000'];
};

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const candidates = getBaseCandidates();
  let lastError: Error | null = null;

  for (const base of candidates) {
    try {
      const url = `${base}${path}`;
      const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options?.headers },
        ...options,
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errJson.detail || `HTTP Error ${res.status}: ${res.statusText}`);
      }

      return await res.json();
    } catch (e: any) {
      lastError = e;
      // If error was an explicit HTTP 4xx/5xx from the server, don't keep trying other URLs
      if (e.message && e.message.startsWith('HTTP Error')) {
        throw e;
      }
      // If network failure / connection refused, try next candidate
      continue;
    }
  }

  throw lastError || new Error(`Unable to connect to BizGuard AI backend server. Please verify backend is running on port 8000.`);
}

export const api = {
  // Analytics
  getDashboardMetrics: () => apiFetch<any>('/api/v1/analytics/dashboard'),
  getInventoryHealth: () => apiFetch<any>('/api/v1/analytics/inventory/health'),
  getIncidentTimeline: (days = 30) => apiFetch<any>(`/api/v1/analytics/incidents/timeline?days=${days}`),
  getWorkflowStats: () => apiFetch<any>('/api/v1/analytics/workflows/stats'),

  // Products / Catalog
  getProducts: () => apiFetch<any>('/api/v1/catalog/products'),
  getProduct: (id: string) => apiFetch<any>(`/api/v1/catalog/products/${id}`),
  getCategories: () => apiFetch<any>('/api/v1/catalog/categories'),

  // Inventory
  getInventory: () => apiFetch<any>('/api/v1/inventory'),
  getLowStock: () => apiFetch<any>('/api/v1/inventory/low-stock'),
  getOutOfStock: () => apiFetch<any>('/api/v1/inventory/out-of-stock'),
  adjustInventory: (variantId: string, body: { quantity_delta: number; reason: string }) =>
    apiFetch<any>(`/api/v1/inventory/${variantId}/adjust`, { method: 'PUT', body: JSON.stringify(body) }),

  // Orders
  getOrders: (status?: string) =>
    apiFetch<any>(`/api/v1/orders${status ? `?status=${status}` : ''}`),
  getOrder: (id: string) => apiFetch<any>(`/api/v1/orders/${id}`),
  createOrder: (body: any) =>
    apiFetch<any>('/api/v1/orders', { method: 'POST', body: JSON.stringify(body) }),
  cancelOrder: (id: string) =>
    apiFetch<any>(`/api/v1/orders/${id}/cancel`, { method: 'POST' }),

  // Workflows
  getWorkflows: () => apiFetch<any>('/api/v1/workflows'),
  getWorkflow: (id: string) => apiFetch<any>(`/api/v1/workflows/${id}`),

  // Shipments
  getShipments: () => apiFetch<any>('/api/v1/shipments'),
  createShipment: (body: { order_id: string; carrier?: string }) =>
    apiFetch<any>('/api/v1/shipments', { method: 'POST', body: JSON.stringify(body) }),
  updateShipmentStatus: (id: string, status: string) =>
    apiFetch<any>(`/api/v1/shipments/${id}/status`, { method: 'PUT', body: JSON.stringify({ status }) }),

  // Returns
  getReturns: () => apiFetch<any>('/api/v1/returns'),
  createReturn: (body: { order_id: string; reason: string }) =>
    apiFetch<any>(`/api/v1/returns`, { method: 'POST', body: JSON.stringify(body) }),
  approveReturn: (id: string) =>
    apiFetch<any>(`/api/v1/returns/${id}/approve`, { method: 'PUT', body: JSON.stringify({ restock: true }) }),
  rejectReturn: (id: string) =>
    apiFetch<any>(`/api/v1/returns/${id}/reject`, { method: 'PUT' }),

  // Bug Detection / Incidents
  detectBugs: () => apiFetch<any>('/api/v1/bugs/detect'),
  getIncidents: () => apiFetch<any>('/api/v1/bugs/incidents'),
  getIncident: (id: string) => apiFetch<any>(`/api/v1/bugs/incidents/${id}`),

  // Simulation
  getScenarios: () => apiFetch<any>('/api/v1/simulation/scenarios'),
  injectScenario: (scenario: string) =>
    apiFetch<any>('/api/v1/simulation/inject-scenario', { method: 'POST', body: JSON.stringify({ scenario }) }),
  injectBug: () => apiFetch<any>('/api/v1/simulation/inject-bug', { method: 'POST' }),
  resetSimulation: () => apiFetch<any>('/api/v1/simulation/reset', { method: 'POST' }),
  getSimulationStatus: () => apiFetch<any>('/api/v1/simulation/status'),

  // Switch Integration
  getSwitchStatus: () => apiFetch<any>('/api/v1/switch/status'),

  // War Room
  getWarRoomMessages: (incidentId: string) =>
    apiFetch<any>(`/api/v1/war-room/${incidentId}/messages`),
  getAgentTasks: (incidentId: string) =>
    apiFetch<any>(`/api/v1/war-room/${incidentId}/tasks`),
  triggerInvestigation: (incidentId: string) =>
    apiFetch<any>(`/api/v1/war-room/${incidentId}/investigate`, { method: 'POST' }),

  // Recovery & Approvals
  getProposals: () => apiFetch<any>('/api/v1/recovery/proposals'),
  getProposal: (id: string) => apiFetch<any>(`/api/v1/recovery/proposals/${id}`),
  runPreChecks: (proposalId: string) =>
    apiFetch<any>(`/api/v1/recovery/proposals/${proposalId}/pre-check`, { method: 'POST' }),
  getPendingApprovals: () => apiFetch<any>('/api/v1/approvals/pending'),
  getApprovalHistory: () => apiFetch<any>('/api/v1/approvals/history'),
  decideApproval: (proposalId: string, body: { decision: 'APPROVED' | 'REJECTED'; approver_user: string; comments?: string }) =>
    apiFetch<any>(`/api/v1/approvals/${proposalId}/decide`, { method: 'POST', body: JSON.stringify(body) }),
  executeProposal: (proposalId: string, approvedBy: string) =>
    apiFetch<any>(`/api/v1/recovery/proposals/${proposalId}/execute`, {
      method: 'POST',
      body: JSON.stringify({ approved_by: approvedBy }),
    }),
};
