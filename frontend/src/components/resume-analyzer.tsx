"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent } from "@/components/ui/card"
import { CircularProgress } from "@/components/circular-progress"
import { useToast } from "@/hooks/use-toast"
import { Loader2, Upload, FileText, CheckCircle, Download } from "lucide-react"

const getColorForSimilarity = (score: number) => {
  if (score >= 80) return "#22c55e" // green-500
  if (score >= 50) return "#f59e0b" // amber-500
  return "#ef4444" // red-500
}

export function ResumeAnalyzer() {
  const [jobDescription, setJobDescription] = useState("")
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [similarity, setSimilarity] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [analyzed, setAnalyzed] = useState(false)
  const [resumeText, setResumeText] = useState<string>("")
  const [jobDescriptionText, setJobDescriptionText] = useState<string>("")
  const [aiFeedback, setAiFeedback] = useState<string>("")
  const [loadingFeedback, setLoadingFeedback] = useState(false)
  const [generatingPDF, setGeneratingPDF] = useState(false)
  const { toast } = useToast()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type === "application/pdf") {
      setResumeFile(file)
    } else if (file) {
      toast({
        title: "Invalid file format",
        description: "Please upload a PDF file",
        variant: "destructive",
      })
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

    if (!resumeFile) {
      toast({
        title: "Resume required",
        description: "Please upload your resume",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append("pdf_file", resumeFile)
      formData.append("job_description", jobDescription)

      const response = await fetch("http://127.0.0.1:8000/analyze/pinecone", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to analyze resume")
      }

      const data = await response.json()
      setSimilarity(data.similarity)
      setResumeText(data.resume_text)
      setJobDescriptionText(data.job_description)
      setAnalyzed(true)
      setAiFeedback("Generating AI feedback...")

      // Get AI feedback
      try {
        setLoadingFeedback(true)
        const feedbackFormData = new FormData()
        feedbackFormData.append("pdf_file", resumeFile)
        feedbackFormData.append("job_description", jobDescription)

        const feedbackResponse = await fetch("http://127.0.0.1:8000/feedback", {
          method: "POST",
          body: feedbackFormData,
        })

        if (feedbackResponse.ok) {
          const feedbackData = await feedbackResponse.json()
          setAiFeedback(feedbackData.feedback || "No feedback available")
        } else {
          setAiFeedback("Failed to generate AI feedback")
        }
      } catch (feedbackError) {
        console.error("Error getting feedback:", feedbackError)
        setAiFeedback("Error generating AI feedback")
      } finally {
        setLoadingFeedback(false)
      }
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

  const generatePDFReport = async () => {
    if (!analyzed || similarity === null || !resumeFile) {
      toast({
        title: "No analysis available",
        description: "Please analyze a resume first before generating a report",
        variant: "destructive",
      })
      return
    }

    setGeneratingPDF(true)

    try {
      const formData = new FormData()
      formData.append("pdf_file", resumeFile)
      formData.append("job_description", jobDescription)
      formData.append("similarity", similarity.toString())
      formData.append("feedback", aiFeedback)

      const response = await fetch("http://127.0.0.1:8000/download", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to generate PDF report")
      }

      // Download the PDF
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')
      a.download = `resume-analysis-${timestamp}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        title: "Report generated",
        description: "PDF report has been downloaded successfully",
      })

    } catch (error) {
      console.error("Error generating PDF:", error)
      toast({
        title: "PDF generation failed",
        description: error instanceof Error ? error.message : "There was an error generating the PDF report",
        variant: "destructive",
      })
    } finally {
      setGeneratingPDF(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full w-full max-w-screen-2xl mx-auto">
      {/* Left Panel - Input */}
      <Card className="bg-gray-800 border-gray-700 shadow-lg">
        <CardContent className="pt-6 h-full flex flex-col">
          <h2 className="text-xl font-semibold mb-6 text-gray-200">Resume Analysis</h2>
          <div className="space-y-4 flex-1 flex flex-col">
            <div className="flex-1 space-y-4">
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
            </div>

            <div className="space-y-3 mt-auto">
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

              {analyzed && similarity !== null && (
                <Button
                  onClick={generatePDFReport}
                  disabled={generatingPDF}
                  variant="outline"
                  className="w-full border-gray-300 bg-gray-100 text-gray-900 hover:bg-gray-900 hover:text-white hover:border-gray-600"
                >
                  {generatingPDF ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating PDF...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 h-4 w-4" />
                      Download PDF Report
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Right Panel - Results */}
      <Card className="bg-gray-800 border-gray-700 shadow-lg">
        <CardContent className="pt-6 h-full flex flex-col">
          {analyzed && similarity !== null ? (
            <div className="h-full flex flex-col space-y-6">
              {/* Similarity Percentage */}
              <div>
                <h2 className="text-xl font-semibold mb-4 text-gray-200 text-center">Similarity Score</h2>
                <div className="flex flex-col items-center">
                  <div className="flex items-center justify-center mb-4">
                    <CircularProgress
                      value={similarity}
                      circleColor="#4b5563"
                      progressColor={getColorForSimilarity(similarity)}
                    />
                  </div>

                  <div className="text-center">
                    <p className="text-lg font-medium text-gray-300 mb-2">
                      <span style={{ color: getColorForSimilarity(similarity) }}>{Math.round(similarity)}%</span> Match
                    </p>
                    {similarity >= 80 ? (
                      <div className="flex items-center justify-center" style={{ color: getColorForSimilarity(similarity) }}>
                        <CheckCircle className="h-5 w-5 mr-2" />
                        <span>Great match!</span>
                      </div>
                    ) : similarity >= 50 ? (
                      <p className="text-sm" style={{ color: getColorForSimilarity(similarity) }}>
                        Good match
                      </p>
                    ) : (
                      <p className="text-sm" style={{ color: getColorForSimilarity(similarity) }}>
                        Low match
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* AI Feedback */}
              <div className="flex-1 flex flex-col">
                <h2 className="text-xl font-semibold mb-4 text-gray-200">AI Feedback</h2>
                <div className="bg-gray-700 rounded-md p-4 flex-1 relative">
                  {loadingFeedback ? (
                    <div className="flex items-center justify-center h-32">
                      <Loader2 className="h-6 w-6 animate-spin text-blue-400" />
                    </div>
                  ) : (
                    <pre className="text-sm text-gray-200 whitespace-pre-wrap">{aiFeedback}</pre>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400 text-center">
              <div>
                <Upload className="mx-auto h-12 w-12 text-gray-500 mb-4" />
                <p>Upload your resume and job description to see analysis results</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}