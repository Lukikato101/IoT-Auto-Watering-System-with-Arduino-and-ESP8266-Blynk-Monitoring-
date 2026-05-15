/**
 * API client for IoT Watering System backend
 * 
 * Handles all HTTP requests to the FastAPI backend with error handling and timeouts
 */

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
const REQUEST_TIMEOUT = 10000; // 10 seconds

/**
 * Fetch wrapper with timeout and error handling
 */
const fetchWithTimeout = async (url, options = {}) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.name === "AbortError") {
      throw new Error(`Request timeout (${REQUEST_TIMEOUT / 1000}s)`);
    }
    throw error;
  }
};

/**
 * Get the latest sensor reading
 * @returns {Promise<{id: number, moisture: number, timestamp: string}>}
 */
export async function getLatestData() {
  try {
    const data = await fetchWithTimeout(`${BASE_URL}/sensor/latest`);
    return data;
  } catch (error) {
    console.error("Failed to fetch latest data:", error);
    throw error;
  }
}

/**
 * Get historical sensor data with pagination
 * @param {number} limit - Max records to return (default: 100)
 * @param {number} offset - Pagination offset (default: 0)
 * @param {number} hours - Optional filter for last N hours
 * @returns {Promise<Array>}
 */
export async function getHistory(limit = 100, offset = 0, hours = null) {
  try {
    const params = new URLSearchParams();
    params.append("limit", Math.min(limit, 10000));
    params.append("offset", offset);
    if (hours) {
      params.append("hours", hours);
    }

    const data = await fetchWithTimeout(
      `${BASE_URL}/sensor/history?${params.toString()}`
    );
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error("Failed to fetch history:", error);
    throw error;
  }
}

/**
 * Get sensor statistics over a time period
 * @param {number} hours - Time window in hours (default: 24)
 * @returns {Promise<{min_moisture, max_moisture, avg_moisture, sample_count}>}
 */
export async function getSensorStats(hours = 24) {
  try {
    const data = await fetchWithTimeout(
      `${BASE_URL}/sensor/stats?hours=${Math.min(hours, 730)}`
    );
    return data;
  } catch (error) {
    console.error("Failed to fetch statistics:", error);
    throw error;
  }
}

/**
 * Health check endpoint
 * @returns {Promise<{status, timestamp}>}
 */
export async function healthCheck() {
  try {
    const data = await fetchWithTimeout(`${BASE_URL}/`);
    return data;
  } catch (error) {
    console.error("API health check failed:", error);
    throw error;
  }
}

export default {
  getLatestData,
  getHistory,
  getSensorStats,
  healthCheck,
};