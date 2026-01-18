'use client'

import { useState } from 'react'
import { uploadImage } from '@/lib/api'

interface ImageUploadProps {
  onSuccess: (sessionId: string, topics: string[]) => void
}

export default function ImageUpload({ onSuccess }: ImageUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (selectedFile.type.startsWith('image/')) {
        setFile(selectedFile)
        setError(null)
        
        // Create preview
        const reader = new FileReader()
        reader.onloadend = () => {
          setPreview(reader.result as string)
        }
        reader.readAsDataURL(selectedFile)
      } else {
        setError('Please upload an image file')
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const result = await uploadImage(file)
      onSuccess(result.session_id, result.topics)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">
          Upload Syllabus Image
        </h2>
        <p className="text-gray-600">
          Upload an image of your syllabus or topic list
        </p>
      </div>

      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-500 transition-colors">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer flex flex-col items-center"
        >
          <svg
            className="w-12 h-12 text-gray-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <span className="text-gray-600 font-medium">
            {file ? file.name : 'Click to upload or drag and drop'}
          </span>
          <span className="text-sm text-gray-500 mt-2">
            PNG, JPG, JPEG up to 10MB
          </span>
        </label>
      </div>

      {preview && (
        <div className="mt-4">
          <img
            src={preview}
            alt="Preview"
            className="max-w-full h-auto rounded-lg shadow-md mx-auto max-h-96"
          />
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? 'Processing...' : 'Upload & Extract Topics'}
        </button>
      )}
    </div>
  )
}
