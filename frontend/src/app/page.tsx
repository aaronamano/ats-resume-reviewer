import { ResumeAnalyzer } from "@/components/resume-analyzer"

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-100 sm:text-4xl">AI Resume Reviewer</h1>
        <p className="mt-3 text-xl text-gray-400">
          Compare your resume against job requirements to see how well they match
        </p>
      </div>

      <ResumeAnalyzer />
    </main>
  )
}
