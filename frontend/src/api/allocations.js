import { apiRequest } from "./client"


// =========================================================
// RUN ALLOCATION
// =========================================================

export async function runAllocation(
  examId,
  allocation
) {
  return apiRequest(
    `/allocations/run/${examId}`,
    {
      method: "POST",
      body: JSON.stringify(allocation),
    }
  )
}


// =========================================================
// GET SAVED ALLOCATION
// =========================================================

export async function getAllocation(
  examId
) {
  return apiRequest(
    `/allocations/${examId}`
  )
}


// =========================================================
// DELTA REALLOCATION
// =========================================================

export async function deltaReallocation(
  examId,
  data
) {
  return apiRequest(
    `/allocations/delta/${examId}`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  )
}