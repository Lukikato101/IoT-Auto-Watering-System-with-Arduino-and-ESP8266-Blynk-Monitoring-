import {
  useEffect,
  useState,
  useCallback,
} from 'react';

import {
  getLatestData,
  getHistory,
  getSensorStats,
} from "../services/api";

/**
 * Custom hook for fetching and managing sensor data
 * 
 * @returns {Object} Sensor data state and status
 *   - moisture: Current moisture reading (0-1023)
 *   - history: Array of historical readings
 *   - stats: Statistics object with min/max/avg
 *   - loading: Boolean indicating fetch in progress
 *   - error: Error message if fetch failed
 *   - lastUpdated: Timestamp of last successful update
 */
function useSensorData() {
  const [moisture, setMoisture] = useState(0);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch all sensor data
  const fetchData = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);

      // Parallel requests for better performance
      const [latestResponse, historyResponse, statsResponse] = await Promise.all([
        getLatestData(),
        getHistory(50),  // Limit to last 50 for performance
        getSensorStats(24),  // Last 24 hours stats
      ]);

      // Update state only if we have valid data
      if (latestResponse?.moisture !== undefined) {
        setMoisture(latestResponse.moisture);
      }

      if (Array.isArray(historyResponse) && historyResponse.length > 0) {
        setHistory(historyResponse);
      }

      if (statsResponse) {
        setStats(statsResponse);
      }

      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      const errorMessage = err?.message || "Failed to fetch sensor data";
      setError(errorMessage);
      console.error("Sensor data fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch and polling setup
  useEffect(() => {
    // Fetch immediately on mount
    fetchData();

    // Set up polling interval (5 seconds)
    const intervalId = setInterval(fetchData, 5000);

    // Cleanup
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [fetchData]);

  return {
    moisture,
    history,
    stats,
    loading,
    error,
    lastUpdated,
    refetch: fetchData,  // Manual refresh function
  };
}

export default useSensorData;
export default useSensorData

