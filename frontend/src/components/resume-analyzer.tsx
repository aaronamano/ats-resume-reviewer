"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent } from "@/components/ui/card"
import { CircularProgress } from "@/components/circular-progress"
import { useToast } from "@/hooks/use-toast"
import { Loader2, Upload, FileText, CheckCircle } from "lucide-react"

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
                <CircularProgress
                  value={similarity}
                  circleColor="#4b5563"
                  progressColor={getColorForSimilarity(similarity)}
                />
              </div>

              {/* Add new results display */}
              <div className="w-full mt-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium text-gray-300">Job Description</h3>
                    <div className="p-3 bg-gray-700 rounded-md">
                      <pre className="text-sm text-gray-200 whitespace-pre-wrap">{jobDescriptionText}</pre>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium text-gray-300">Your Resume</h3>
                    <div className="p-3 bg-gray-700 rounded-md">
                      <pre className="text-sm text-gray-200 whitespace-pre-wrap">{resumeText}</pre>
                    </div>
                  </div>
                </div>
              </div>

              <div className="text-center mt-6">
                <p className="text-lg font-medium text-gray-300">
                  Your resume has a{" "}
                  <span style={{ color: getColorForSimilarity(similarity) }}>{Math.round(similarity)}%</span> match with the job
                  requirements
                </p>
                {similarity >= 80 ? (
                  <div className="mt-4 flex items-center" style={{ color: getColorForSimilarity(similarity) }}>
                    <CheckCircle className="h-5 w-5 mr-2" />
                    <span>Great match! Your resume aligns well with this job.</span>
                  </div>
                ) : similarity >= 50 ? (
                  <p className="mt-4" style={{ color: getColorForSimilarity(similarity) }}>
                    Good match. Consider highlighting more relevant skills and experiences.
                  </p>
                ) : (
                  <p className="mt-4" style={{ color: getColorForSimilarity(similarity) }}>
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
