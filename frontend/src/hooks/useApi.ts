import { useState, useCallback } from 'react'

interface UseApiOptions {
    onSuccess?: (data: any) => void
    onError?: (error: any) => void
}

export function useApi<T>() {
    const [data, setData] = useState<T | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const execute = useCallback(
        async (apiCall: () => Promise<T>, options: UseApiOptions = {}) => {
            setLoading(true)
            setError(null)

            try {
                const result = await apiCall()
                setData(result)
                options.onSuccess?.(result)
                return result
            } catch (err: any) {
                const errorMessage =
                    err.response?.data?.detail ||
                    err.message ||
                    'An error occurred'
                setError(errorMessage)
                options.onError?.(err)
                throw err
            } finally {
                setLoading(false)
            }
        },
        []
    )

    const reset = useCallback(() => {
        setData(null)
        setError(null)
        setLoading(false)
    }, [])

    return {
        data,
        error,
        loading,
        execute,
        reset,
    }
}
