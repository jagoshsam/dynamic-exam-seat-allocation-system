import { apiRequest } from "./client"

export async function getAuditLogs() {
  return apiRequest("/audit-logs/")
}