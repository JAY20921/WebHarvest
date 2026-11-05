"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import ExtractionForm from '@/components/ExtractionForm'
import { api } from '@/lib/api'
import { ExternalLink, Zap, Shield, Download } from 'lucide-react'

export default function Home() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (url: string, prompt: string, format: string) => {
    setError(null)
    try {
      const result = await api.createExtraction(url, prompt, format as any)
      router.push(`/results/${result.job_id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to create extraction job')
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <div className="inline-block px-4 py-2 bg-blue-100 rounded-full text-blue-700 text-sm font-medium mb-6">
            ✨ AI-Powered Web Scraping
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Turn Any Website Into Structured Data
          </h1>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Just describe what you need in plain English. Our AI figures out how to extract it and delivers clean, structured data in JSON, CSV, or Excel.
          </p>
        </div>

        {/* Main Extraction Form */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8 mb-12">
          <ExtractionForm onSubmit={handleSubmit} />
          
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Natural Language</h3>
            <p className="text-gray-600 text-sm">
              No CSS selectors or XPath needed. Just describe what you want in plain English.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Intelligent & Reliable</h3>
            <p className="text-gray-600 text-sm">
              AI understands page structure and adapts to changes. Automatic failover ensures reliability.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <Download className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Multiple Formats</h3>
            <p className="text-gray-600 text-sm">
              Export your data as JSON, CSV, or Excel. Perfect for analysis, imports, and automation.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold mb-6 text-center">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { step: 1, title: 'Enter URL', desc: 'Provide the website URL you want to extract data from' },
              { step: 2, title: 'Describe Data', desc: 'Tell us what information you need in plain English' },
              { step: 3, title: 'AI Extracts', desc: 'Our AI analyzes the page and extracts your data' },
              { step: 4, title: 'Download', desc: 'Get your structured data in JSON, CSV, or Excel' },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-lg mx-auto mb-3">
                  {item.step}
                </div>
                <h4 className="font-semibold mb-2">{item.title}</h4>
                <p className="text-sm text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-12 text-center">
          <a href="/history" className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center">
            View Extraction History
            <ExternalLink className="ml-1 w-4 h-4" />
          </a>
        </div>
      </div>
    </main>
  )
}
