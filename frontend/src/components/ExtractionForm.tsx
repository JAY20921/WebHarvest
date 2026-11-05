"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-react'

interface ExtractionFormProps {
  onSubmit: (url: string, prompt: string, format: string) => Promise<void>
}

export default function ExtractionForm({ onSubmit }: ExtractionFormProps) {
  const [url, setUrl] = useState('')
  const [prompt, setPrompt] = useState('')
  const [format, setFormat] = useState('json')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await onSubmit(url, prompt, format)
    } finally {
      setLoading(false)
    }
  }

  const examplePrompts = [
    "Extract all product names and prices",
    "Get article titles, authors, and publication dates",
    "Extract job titles, companies, and locations",
    "Get all links and their descriptions",
  ]

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* URL Input */}
      <div>
        <label htmlFor="url" className="block text-sm font-medium mb-2">
          Website URL
        </label>
        <input
          id="url"
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/products"
          required
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Prompt Input */}
      <div>
        <label htmlFor="prompt" className="block text-sm font-medium mb-2">
          What do you want to extract?
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe what data you want to extract in plain English..."
          required
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        
        {/* Example Prompts */}
        <div className="mt-2">
          <p className="text-xs text-gray-500 mb-2">Example prompts:</p>
          <div className="flex flex-wrap gap-2">
            {examplePrompts.map((example, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setPrompt(example)}
                className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Format Selector */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Output Format
        </label>
        <div className="flex gap-4">
          {['json', 'csv', 'xlsx'].map((fmt) => (
            <label key={fmt} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="format"
                value={fmt}
                checked={format === fmt}
                onChange={(e) => setFormat(e.target.value)}
                className="mr-2"
              />
              <span className="text-sm uppercase">{fmt}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        disabled={loading}
        className="w-full h-12 text-lg"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Processing...
          </>
        ) : (
          'Extract Data'
        )}
      </Button>
    </form>
  )
}
