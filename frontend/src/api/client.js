const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

export async function apiRequest(endpoint, options = {}) {
  const isFormData = options.body instanceof FormData

  const headers = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(options.headers || {}),
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,
      headers,
    }
  )

  let data = null

  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      `Request failed with status ${response.status}`

    throw new Error(
      typeof message === "string"
        ? message
        : JSON.stringify(message)
    )
  }

  return data
}