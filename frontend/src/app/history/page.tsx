"use client"

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { ExtractionJob } from '@/types/extraction'
import { Button } from '@/components/ui/button'
import { ArrowLeft, ExternalLink, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react'

export default function HistoryPage() {
  const router = useRouter()
  const [jobs, setJobs] = useState<ExtractionJob[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const result = await api.getHistory(50, 0)
      setJobs(result.items)
    } catch (err: any) {
      setError(err.message || 'Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'processing':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (date: string) => {
    return new Date(date).toLocaleString()
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button variant="ghost" onClick={() => router.push('/')} className="mb-4">
            <ArrowLeft className="mr-2 w-4 h-4" />
            Back to Home
          </Button>
          <h1 className="text-3xl font-bold">Extraction History</h1>
          <p className="text-gray-600 mt-2">
            View and manage your past extractions
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-700">
            {error}
          </div>
        )}

        {/* Jobs List */}
        <div className="space-y-4">
          {jobs.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <p className="text-gray-500 mb-4">No extraction history yet</p>
              <Button onClick={() => router.push('/')}>
                Create Your First Extraction
              </Button>
            </div>
          ) : (
            jobs.map((job) => (
              <div
                key={job.job_id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon(job.status)}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                        {job.status.toUpperCase()}
                      </span>
                    </div>

                    <h3 className="font-semibold text-lg mb-2 break-all">
                      {job.url}
                    </h3>

                    <p className="text-gray-600 text-sm mb-3">
                      {job.prompt}
                    </p>

                    <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                      <span>
                        Created: {formatDate(job.created_at)}
                      </span>
                      {job.records_count !== null && (
                        <span>
                          <strong>{job.records_count}</strong> records
                        </span>
                      )}
                      {job.llm_provider_used && (
                        <span>
                          Provider: <strong>{job.llm_provider_used}</strong>
                        </span>
                      )}
                    </div>

                    {job.error_message && (
                      <div className="mt-3 p-2 bg-red-50 rounded text-sm text-red-700">
                        Error: {job.error_message}
                      </div>
                    )}
                  </div>

                  <div className="ml-4">
                    {job.status === 'completed' && (
                      <Button
                        onClick={() => router.push(`/results/${job.job_id}`)}
                        size="sm"
                      >
                        View Results
                        <ExternalLink className="ml-2 w-4 h-4" />
                      </Button>
                    )}
                    {job.status === 'processing' && (
                      <Button
                        onClick={() => router.push(`/results/${job.job_id}`)}
                        size="sm"
                        variant="outline"
                      >
                        Check Status
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
