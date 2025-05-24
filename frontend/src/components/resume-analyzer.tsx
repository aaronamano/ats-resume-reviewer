"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent } from "@/components/ui/card"
import { CircularProgress } from "@/components/circular-progress"
import { useToast } from "@/hooks/use-toast"
import { Loader2, Upload, FileText, CheckCircle } from "lucide-react"

export function ResumeAnalyzer() {
  const [jobDescription, setJobDescription] = useState("")
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [resumeText, setResumeText] = useState("")
  const [similarity, setSimilarity] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [analyzed, setAnalyzed] = useState(false)
  const { toast } = useToast()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type === "application/pdf") {
      setResumeFile(file)
      extractTextFromPDF(file)
    } else if (file) {
      toast({
        title: "Invalid file format",
        description: "Please upload a PDF file",
        variant: "destructive",
      })
    }
  }

  const extractTextFromPDF = async (file: File) => {
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append("file", file)

      const response = await fetch("/api/extract-pdf", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Failed to extract text from PDF")
      }

      const data = await response.json()
      setResumeText(data.text)

      toast({
        title: "Resume uploaded successfully",
        description: "Your resume has been processed and is ready for analysis",
      })
    } catch (error) {
      console.error("Error extracting text from PDF:", error)
      toast({
        title: "Error processing PDF",
        description: "There was an error extracting text from your resume",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const analyzeResume = async () => {
    if (!jobDescription.trim()) {
      toast({
        title: "Job description required",
        description: "Please enter the job description",
        variant: "destructive",
      })
      return
    }

    if (!resumeText) {
      toast({
        title: "Resume required",
        description: "Please upload your resume",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          jobDescription,
          resumeText,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to analyze resume")
      }

      const data = await response.json()
      setSimilarity(data.similarity)
      setAnalyzed(true)

      toast({
        title: "Analysis complete",
        description: `Your resume has a ${data.similarity}% match with the job description`,
      })
    } catch (error) {
      console.error("Error analyzing resume:", error)
      toast({
        title: "Analysis failed",
        description: error instanceof Error ? error.message : "There was an error analyzing your resume",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <Card className="bg-gray-800 border-gray-700 shadow-lg">
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="job-description" className="block text-sm font-medium text-gray-300 mb-1">
                Job Description / Requirements
              </label>
              <Textarea
                id="job-description"
                placeholder="Copy and paste the job description or requirements here..."
                className="min-h-[200px] bg-gray-700 border-gray-600 text-gray-200 placeholder:text-gray-500"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
            </div>

            <div>
              <label htmlFor="resume-upload" className="block text-sm font-medium text-gray-300 mb-1">
                Upload Resume (PDF)
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-600 border-dashed rounded-md bg-gray-700">
                <div className="space-y-1 text-center">
                  <div className="flex flex-col items-center">
                    {resumeFile ? (
                      <div className="flex items-center space-x-2">
                        <FileText className="h-8 w-8 text-green-400" />
                        <span className="text-sm text-gray-300">{resumeFile.name}</span>
                      </div>
                    ) : (
                      <Upload className="mx-auto h-12 w-12 text-gray-500" />
                    )}
                  </div>
                  <div className="flex text-sm text-gray-400">
                    <label
                      htmlFor="resume-upload"
                      className="relative cursor-pointer bg-transparent rounded-md font-medium text-blue-400 hover:text-blue-300 focus-within:outline-none"
                    >
                      <span>{resumeFile ? "Change file" : "Upload a file"}</span>
                      <input
                        id="resume-upload"
                        name="resume-upload"
                        type="file"
                        className="sr-only"
                        accept="application/pdf"
                        onChange={handleFileChange}
                      />
                    </label>
                  </div>
                  <p className="text-xs text-gray-500">PDF up to 10MB</p>
                </div>
              </div>
            </div>

            <Button
              onClick={analyzeResume}
              disabled={loading || !resumeFile || !jobDescription.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                "Analyze Resume"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {analyzed && similarity !== null && (
        <Card className="bg-gray-800 border-gray-700 shadow-lg">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-4 text-gray-200">Analysis Results</h2>
              <div className="flex items-center justify-center mb-4">
                <CircularProgress value={similarity} circleColor="#4b5563" progressColor="#3b82f6" />
              </div>
              <div className="text-center">
                <p className="text-lg font-medium text-gray-300">
                  Your resume has a <span className="font-bold text-blue-400">{similarity}%</span> match with the job
                  requirements
                </p>
                {similarity >= 80 ? (
                  <div className="mt-4 flex items-center text-green-400">
                    <CheckCircle className="h-5 w-5 mr-2" />
                    <span>Great match! Your resume aligns well with this job.</span>
                  </div>
                ) : similarity >= 50 ? (
                  <p className="mt-4 text-amber-400">
                    Good match. Consider highlighting more relevant skills and experiences.
                  </p>
                ) : (
                  <p className="mt-4 text-red-400">
                    Low match. You may want to tailor your resume more specifically to this job.
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
