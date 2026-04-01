import { useState, useRef } from "react";
import {
  Upload,
  FileText,
  Briefcase,
  Building2,
  Clock,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { useImportJob, useImportCsv, useJobs } from "@/api/hooks";

export default function ImportPage() {
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [description, setDescription] = useState("");

  const fileRef = useRef<HTMLInputElement>(null);
  const importJob = useImportJob();
  const importCsv = useImportCsv();
  const { data: jobs } = useJobs(20);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;
    importJob.mutate(
      { title, company, description },
      {
        onSuccess: () => {
          setTitle("");
          setCompany("");
          setDescription("");
        },
      },
    );
  }

  function handleCsvUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    importCsv.mutate(file);
    if (fileRef.current) fileRef.current.value = "";
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Import Jobs</h1>
        <p className="mt-1 text-gray-400">
          Paste job descriptions or upload CSV files to extract skills
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Manual entry */}
        <form
          onSubmit={handleSubmit}
          className="rounded-xl border border-gray-800 bg-gray-900 p-6"
        >
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
            <FileText className="h-5 w-5 text-indigo-400" />
            Paste Job Description
          </h2>

          <div className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm text-gray-400">
                Job Title
              </label>
              <div className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-800 px-3">
                <Briefcase className="h-4 w-4 text-gray-500" />
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Senior Software Engineer"
                  className="w-full bg-transparent py-2.5 text-sm text-gray-200 outline-none placeholder:text-gray-600"
                />
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-sm text-gray-400">
                Company
              </label>
              <div className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-800 px-3">
                <Building2 className="h-4 w-4 text-gray-500" />
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Acme Corp"
                  className="w-full bg-transparent py-2.5 text-sm text-gray-200 outline-none placeholder:text-gray-600"
                />
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-sm text-gray-400">
                Job Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={8}
                placeholder="Paste the full job description here..."
                className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 text-sm text-gray-200 outline-none placeholder:text-gray-600 focus:border-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={importJob.isPending || !title.trim() || !description.trim()}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-50"
            >
              {importJob.isPending ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <Upload className="h-4 w-4" />
              )}
              Import Job
            </button>

            {importJob.isSuccess && (
              <p className="flex items-center gap-1.5 text-sm text-green-400">
                <CheckCircle2 className="h-4 w-4" />
                Job imported successfully!
              </p>
            )}
            {importJob.isError && (
              <p className="flex items-center gap-1.5 text-sm text-red-400">
                <AlertCircle className="h-4 w-4" />
                Failed to import job. Please try again.
              </p>
            )}
          </div>
        </form>

        {/* CSV upload */}
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
            <Upload className="h-5 w-5 text-purple-400" />
            CSV Upload
          </h2>

          <div
            onClick={() => fileRef.current?.click()}
            className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-700 bg-gray-800/50 p-12 transition-colors hover:border-indigo-500/50 hover:bg-gray-800"
          >
            <Upload className="mb-3 h-10 w-10 text-gray-500" />
            <p className="text-sm font-medium text-gray-300">
              Click to upload CSV
            </p>
            <p className="mt-1 text-xs text-gray-500">
              Expected columns: title, company, description
            </p>
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              onChange={handleCsvUpload}
              className="hidden"
            />
          </div>

          {importCsv.isPending && (
            <div className="mt-4 flex items-center gap-2 text-sm text-gray-400">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
              Importing CSV...
            </div>
          )}
          {importCsv.isSuccess && importCsv.data && (
            <p className="mt-4 flex items-center gap-1.5 text-sm text-green-400">
              <CheckCircle2 className="h-4 w-4" />
              Imported {importCsv.data.imported} jobs from CSV
            </p>
          )}
          {importCsv.isError && (
            <p className="mt-4 flex items-center gap-1.5 text-sm text-red-400">
              <AlertCircle className="h-4 w-4" />
              Failed to import CSV. Check the file format.
            </p>
          )}
        </div>
      </div>

      {/* Recent imports */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-white">
          Recently Imported Jobs
        </h2>
        <div className="space-y-3">
          {jobs?.map((job) => (
            <div
              key={job.id}
              className="flex items-start gap-4 rounded-lg border border-gray-800 bg-gray-800/40 p-4"
            >
              <Briefcase className="mt-0.5 h-5 w-5 shrink-0 text-indigo-400" />
              <div className="flex-1">
                <p className="font-medium text-white">{job.title}</p>
                <p className="text-sm text-gray-400">{job.company}</p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {job.skills.slice(0, 8).map((skill) => (
                    <span
                      key={skill}
                      className="rounded bg-gray-700 px-2 py-0.5 text-xs text-gray-300"
                    >
                      {skill}
                    </span>
                  ))}
                  {job.skills.length > 8 && (
                    <span className="rounded bg-gray-700 px-2 py-0.5 text-xs text-gray-500">
                      +{job.skills.length - 8} more
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="h-3.5 w-3.5" />
                {new Date(job.imported_at).toLocaleDateString()}
              </div>
            </div>
          ))}
          {(!jobs || jobs.length === 0) && (
            <p className="text-center text-gray-500">
              No jobs imported yet. Paste a job description or upload a CSV.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
