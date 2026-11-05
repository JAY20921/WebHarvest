"use client"

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { ExtractionJob } from '@/types/extraction'
import { Button } from '@/components/ui/button'
import { Loader2, Download, ArrowLeft, CheckCircle, XCircle, Clock } from 'lucide-react'

export default function ResultsPage() {
  const params = useParams()
  const router = useRouter()
  const jobId = params.jobId as string
  
  const [job, setJob] = useState<ExtractionJob | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<'table' | 'json'>('table')

  useEffect(() => {
    if (!jobId) return

    const pollJob = async () => {
      try {
        const result = await api.getExtractionStatus(jobId)
        setJob(result)
        
        // Stop polling if job is complete or failed
        if (result.status === 'completed' || result.status === 'failed') {
          setLoading(false)
        } else {
          // Poll every 2 seconds
          setTimeout(pollJob, 2000)
        }
      } catch (err: any) {
        setError(err.message || 'Failed to fetch job status')
        setLoading(false)
      }
    }

    pollJob()
  }, [jobId])

  const handleDownload = async (format: 'json' | 'csv' | 'xlsx') => {
    try {
      const blob = await api.exportExtraction(jobId, format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `extraction_${jobId}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err: any) {
      alert(err.message || 'Download failed')
    }
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-center mb-2">Error</h2>
          <p className="text-gray-600 text-center mb-4">{error}</p>
          <Button onClick={() => router.push('/')} className="w-full">
            <ArrowLeft className="mr-2 w-4 h-4" />
            Back to Home
          </Button>
        </div>
      </div>
    )
  }

  if (!job || (loading && job.status !== 'completed')) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Processing Your Request</h2>
          <p className="text-gray-600 mb-4">
            {job?.status === 'pending' && 'Queued for processing...'}
            {job?.status === 'processing' && 'Extracting data from webpage...'}
          </p>
          <div className="space-y-2 text-sm text-left">
            <div className="flex items-center">
              <Clock className="w-4 h-4 mr-2 text-gray-400" />
              <span className="text-gray-600">This usually takes 10-30 seconds</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (job.status === 'failed') {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-center mb-2">Extraction Failed</h2>
          <p className="text-gray-600 text-center mb-4">{job.error_message}</p>
          <Button onClick={() => router.push('/')} className="w-full">
            <ArrowLeft className="mr-2 w-4 h-4" />
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <Button variant="ghost" onClick={() => router.push('/')}>
              <ArrowLeft className="mr-2 w-4 h-4" />
              Back
            </Button>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-sm font-medium text-green-700">Extraction Complete</span>
            </div>
          </div>

          <h1 className="text-2xl font-bold mb-2">Extraction Results</h1>
          <p className="text-gray-600 text-sm mb-4">{job.url}</p>
          
          <div className="flex items-center gap-4 text-sm">
            <span className="text-gray-600">
              <strong>{job.records_count || 0}</strong> records extracted
            </span>
            <span className="text-gray-400">•</span>
            <span className="text-gray-600">
              Provider: <strong>{job.llm_provider_used || 'N/A'}</strong>
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => handleDownload('json')}>
              <Download className="mr-2 w-4 h-4" />
              Download JSON
            </Button>
            <Button onClick={() => handleDownload('csv')} variant="outline">
              <Download className="mr-2 w-4 h-4" />
              Download CSV
            </Button>
            <Button onClick={() => handleDownload('xlsx')} variant="outline">
              <Download className="mr-2 w-4 h-4" />
              Download Excel
            </Button>
          </div>
        </div>

        {/* View Toggle */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
          <div className="flex gap-2">
            <Button
              variant={view === 'table' ? 'default' : 'outline'}
              onClick={() => setView('table')}
            >
              Table View
            </Button>
            <Button
              variant={view === 'json' ? 'default' : 'outline'}
              onClick={() => setView('json')}
            >
              JSON View
            </Button>
          </div>
        </div>

        {/* Data Display */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          {view === 'table' && job.data && job.data.length > 0 && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {Object.keys(job.data[0]).map((key) => (
                      <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {job.data.map((record, idx) => (
                    <tr key={idx}>
                      {Object.values(record).map((value: any, vidx) => (
                        <td key={vidx} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {String(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {view === 'json' && (
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
              {JSON.stringify(job.data, null, 2)}
            </pre>
          )}

          {(!job.data || job.data.length === 0) && (
            <p className="text-center text-gray-500 py-8">No data extracted</p>
          )}
        </div>
      </div>
    </div>
  )
}
