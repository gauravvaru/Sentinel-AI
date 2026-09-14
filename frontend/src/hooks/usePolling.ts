import { useState, useEffect, useCallback } from 'react';

interface UsePollingOptions<T> {
  fetcher: () => Promise<T>;
  intervalMs?: number;
  enabled?: boolean;
}

export function usePolling<T>({ fetcher, intervalMs = 30000, enabled = true }: UsePollingOptions<T>) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const executeFetch = useCallback(async () => {
    if (!enabled) return;
    try {
      const result = await fetcher();
      setData(result);
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, [fetcher, enabled]);

  useEffect(() => {
    setIsLoading(true);
    executeFetch();

    if (enabled && intervalMs > 0) {
      const intervalId = setInterval(executeFetch, intervalMs);
      return () => clearInterval(intervalId);
    }
  }, [executeFetch, intervalMs, enabled]);

  return { data, error, isLoading, lastUpdated, refetch: executeFetch };
}
