/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable react/no-unescaped-entities */
/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  FileText,
  Boxes,
  Cpu,
  Search,
  Database,
  GitBranch,
  BarChart3,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  UploadCloud,
  Plus,
  Trash2,
  ExternalLink,
} from "lucide-react";

const BACKEND_URL =
  typeof window === "undefined"
    ? "http://backend:8000/api/v1"
    : "/api/v1";

interface DocumentItem {
  id: string;
  filename: string;
  file_path: string;
  file_hash: string;
  mime_type: string;
  size_bytes: number;
  status: string;
  category: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

interface ExtractionSchemaItem {
  id: string;
  name: string;
  description: string | null;
  schema_definition: Record<string, any>;
  created_at: string;
}

interface ExtractionResult {
  id: string;
  document_id: string;
  schema_id: string | null;
  structured_data: Record<string, any> | null;
  status: string;
  error_message: string | null;
  provenance: {
    citations: Array<{
      document_id: string;
      chunk_id: string;
      snippet: string;
      page_number: number | null;
      confidence_score: number;
      retrieval_strategy: string;
    }>;
    overall_confidence: number;
  } | null;
  created_at: string;
}

type TabType = "documents" | "schemas" | "extract" | "search";

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>("documents");

  // Ingestion states
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Schema states
  const [schemas, setSchemas] = useState<ExtractionSchemaItem[]>([]);
  const [schemaName, setSchemaName] = useState("");
  const [schemaDesc, setSchemaDesc] = useState("");
  const [schemaFields, setSchemaFields] = useState<Array<{ name: string; type: string }>>([
    { name: "invoice_number", type: "string" },
    { name: "vendor", type: "string" },
    { name: "total_amount", type: "number" },
  ]);
  const [isCreatingSchema, setIsCreatingSchema] = useState(false);

  // Extraction Workspace states
  const [selectedDocId, setSelectedDocId] = useState("");
  const [selectedSchemaId, setSelectedSchemaId] = useState("");
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionError, setExtractionError] = useState<string | null>(null);

  // Search Engine states
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchLimit, setSearchLimit] = useState(5);

  // Modal State for Scaffolded modules
  const [comingSoonModal, setComingSoonModal] = useState<{
    isOpen: boolean;
    title: string;
  } | null>(null);

  // Fetch document directory list
  const fetchDocuments = useCallback(async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/documents/?limit=50`);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents);
      }
    } catch (e) {
      console.error("Failed fetching documents directory:", e);
    }
  }, []);

  // Fetch extraction schemas
  const fetchSchemas = useCallback(async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/schemas/`);
      if (response.ok) {
        const data = await response.json();
        setSchemas(data);
      }
    } catch (e) {
      console.error("Failed fetching schemas templates:", e);
    }
  }, []);

  // Refresh catalogs
  useEffect(() => {
    fetchDocuments();
    fetchSchemas();
  }, [fetchDocuments, fetchSchemas]);

  // Document Ingestion Polling: Poll if any document is still parsing
  useEffect(() => {
    const activePolling = documents.some(
      (doc) => doc.status === "PENDING" || doc.status === "PARSING"
    );
    if (!activePolling) return;

    const timer = setInterval(() => {
      fetchDocuments();
    }, 2000);

    return () => clearInterval(timer);
  }, [documents, fetchDocuments]);

  // Upload handler
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(false);

    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      const response = await fetch(`${BACKEND_URL}/documents/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      setUploadFile(null);
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 3000);

      // Reset input element
      const fileInput = document.getElementById("file-input") as HTMLInputElement;
      if (fileInput) fileInput.value = "";

      await fetchDocuments();
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload document file.");
    } finally {
      setIsUploading(false);
    }
  };

  // Field change events inside schema declarations builder
  const handleFieldChange = (index: number, key: "name" | "type", val: string) => {
    const updated = [...schemaFields];
    updated[index][key] = val;
    setSchemaFields(updated);
  };

  // Add field row helper inside schema declarations builder
  const addFieldRow = () => {
    setSchemaFields([...schemaFields, { name: "", type: "string" }]);
  };

  // Remove field row helper inside schema declarations builder
  const removeFieldRow = (index: number) => {
    const updated = schemaFields.filter((_, idx) => idx !== index);
    setSchemaFields(updated);
  };

  // Schema creation triggers
  const handleCreateSchema = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!schemaName) return;

    setIsCreatingSchema(true);
    const schemaDefinition: Record<string, string> = {};
    schemaFields.forEach((f) => {
      if (f.name.trim()) {
        schemaDefinition[f.name.trim()] = f.type;
      }
    });

    try {
      const response = await fetch(`${BACKEND_URL}/schemas/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: schemaName,
          description: schemaDesc || null,
          schema_definition: schemaDefinition,
        }),
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      setSchemaName("");
      setSchemaDesc("");
      setSchemaFields([
        { name: "invoice_number", type: "string" },
        { name: "vendor", type: "string" },
        { name: "total_amount", type: "number" },
      ]);
      await fetchSchemas();
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsCreatingSchema(false);
    }
  };

  // Structured extraction trigger execution
  const handleRunExtraction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDocId || !selectedSchemaId) return;

    setIsExtracting(true);
    setExtractionError(null);
    setExtractionResult(null);

    try {
      const response = await fetch(`${BACKEND_URL}/extractions/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: selectedDocId,
          schema_id: selectedSchemaId,
        }),
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      setExtractionResult(data);
    } catch (err: any) {
      setExtractionError(err.message || "Failed to trigger structured extraction.");
    } finally {
      setIsExtracting(false);
    }
  };

  // Cross-document semantic retrievals query handler
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;

    setIsSearching(true);
    try {
      const response = await fetch(`${BACKEND_URL}/search/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          limit: searchLimit,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  // Open Coming Soon Modal
  const openComingSoon = (title: string) => {
    setComingSoonModal({ isOpen: true, title });
  };

  return (
    <div className="min-h-screen bg-[#FAFBFC] text-[#111827] font-sans flex flex-col antialiased">
      {/* Header navbar */}
      <header className="h-[72px] border-b border-[#ECEFF3] bg-white sticky top-0 z-50 px-8 flex items-center justify-between shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
        <div className="flex items-center gap-3.5">
          <div className="bg-[#2563EB] w-9 h-9 rounded-lg flex items-center justify-center font-bold text-white shadow-sm shadow-[#2563EB]/10">
            DF
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-[#111827]">
              DocuFlow AI
            </h1>
            <p className="text-[11px] text-[#6B7280] font-medium tracking-wide">
              PLATFORM WORKSPACE
            </p>
          </div>
        </div>

        {/* Global Connection Health Badge */}
        <div className="flex items-center gap-2 bg-[#F0FDF4] border border-[#DCFCE7] px-3.5 py-1.5 rounded-full text-xs font-semibold text-[#16A34A] shadow-sm">
          <span className="w-2.5 h-2.5 rounded-full bg-[#16A34A] shadow-sm shadow-[#16A34A]/25"></span>
          <span>API Connected</span>
        </div>
      </header>

      {/* Main Workspace Frame */}
      <div className="flex-1 max-w-[1440px] w-full mx-auto p-8 flex flex-col lg:flex-row gap-8">
        
        {/* Sidebar Nav (Linear SaaS aesthetic) */}
        <aside className="w-full lg:w-[260px] shrink-0 flex flex-col gap-6 bg-[#FCFCFD] border border-[#E5E7EB] rounded-2xl p-5 shadow-[0_2px_4px_rgba(0,0,0,0.015)]">
          <div className="flex flex-col gap-1.5">
            <span className="text-[11px] tracking-wider uppercase font-bold text-[#6B7280] px-3 mb-2">
              Workspace
            </span>
            <button
              onClick={() => setActiveTab("documents")}
              className={`w-full text-left px-3 py-2.5 rounded-xl flex items-center gap-3 font-semibold text-[14px] transition-all border cursor-pointer ${
                activeTab === "documents"
                  ? "bg-[#DBEAFE]/80 text-[#2563EB] border-[#DBEAFE]"
                  : "text-[#4B5563] border-transparent hover:bg-[#F3F4F6] hover:text-[#111827]"
              }`}
            >
              <FileText className="w-4.5 h-4.5" />
              Documents Directory
            </button>

            <button
              onClick={() => setActiveTab("schemas")}
              className={`w-full text-left px-3 py-2.5 rounded-xl flex items-center gap-3 font-semibold text-[14px] transition-all border cursor-pointer ${
                activeTab === "schemas"
                  ? "bg-[#DBEAFE]/80 text-[#2563EB] border-[#DBEAFE]"
                  : "text-[#4B5563] border-transparent hover:bg-[#F3F4F6] hover:text-[#111827]"
              }`}
            >
              <Boxes className="w-4.5 h-4.5" />
              Extraction Templates
            </button>

            <button
              onClick={() => setActiveTab("extract")}
              className={`w-full text-left px-3 py-2.5 rounded-xl flex items-center gap-3 font-semibold text-[14px] transition-all border cursor-pointer ${
                activeTab === "extract"
                  ? "bg-[#DBEAFE]/80 text-[#2563EB] border-[#DBEAFE]"
                  : "text-[#4B5563] border-transparent hover:bg-[#F3F4F6] hover:text-[#111827]"
              }`}
            >
              <Cpu className="w-4.5 h-4.5" />
              Run Extraction
            </button>

            <button
              onClick={() => setActiveTab("search")}
              className={`w-full text-left px-3 py-2.5 rounded-xl flex items-center gap-3 font-semibold text-[14px] transition-all border cursor-pointer ${
                activeTab === "search"
                  ? "bg-[#DBEAFE]/80 text-[#2563EB] border-[#DBEAFE]"
                  : "text-[#4B5563] border-transparent hover:bg-[#F3F4F6] hover:text-[#111827]"
              }`}
            >
              <Search className="w-4.5 h-4.5" />
              Semantic Search
            </button>
          </div>

          {/* Visually Separated Scaffolded Modules */}
          <div className="border-t border-[#ECEFF3] pt-5">
            <div className="flex items-center justify-between px-3 mb-3">
              <span className="text-[11px] tracking-wider uppercase font-bold text-[#6B7280]">
                Extended Modules
              </span>
              <span className="px-2 py-0.5 rounded-full bg-[#ECEFF3] text-[#6B7280] font-bold text-[8px] tracking-wide uppercase">
                Soon
              </span>
            </div>
            
            <div className="flex flex-col gap-1">
              <button
                onClick={() => openComingSoon("Vision Layout RAG")}
                className="w-full text-left px-3 py-2 rounded-xl flex items-center gap-3 text-[#6B7280] hover:bg-[#F3F4F6] hover:text-[#111827] text-[13px] font-medium transition-all group cursor-pointer"
              >
                <Database className="w-4 h-4 text-[#9CA3AF] group-hover:text-[#4B5563]" />
                <span>Vision Layout RAG</span>
              </button>
              
              <button
                onClick={() => openComingSoon("Knowledge Graph")}
                className="w-full text-left px-3 py-2 rounded-xl flex items-center gap-3 text-[#6B7280] hover:bg-[#F3F4F6] hover:text-[#111827] text-[13px] font-medium transition-all group cursor-pointer"
              >
                <GitBranch className="w-4 h-4 text-[#9CA3AF] group-hover:text-[#4B5563]" />
                <span>Knowledge Graph</span>
              </button>
              
              <button
                onClick={() => openComingSoon("Benchmark Dashboard")}
                className="w-full text-left px-3 py-2 rounded-xl flex items-center gap-3 text-[#6B7280] hover:bg-[#F3F4F6] hover:text-[#111827] text-[13px] font-medium transition-all group cursor-pointer"
              >
                <BarChart3 className="w-4 h-4 text-[#9CA3AF] group-hover:text-[#4B5563]" />
                <span>Benchmark Dashboard</span>
              </button>
            </div>
          </div>
        </aside>

        {/* Tab view panel sections */}
        <main className="flex-1 bg-white border border-[#E5E7EB] rounded-[18px] p-8 shadow-[0_4px_12px_rgba(0,0,0,0.02)] flex flex-col min-h-[600px] transition-all">
          
          {/* TAB 1: DOCUMENTS DIRECTORY */}
          {activeTab === "documents" && (
            <div className="flex-grow flex flex-col gap-8">
              <div>
                <h2 className="text-[26px] font-bold tracking-tight text-[#111827] leading-[1.2]">
                  Document Ingestion
                </h2>
                <p className="text-[14px] text-[#4B5563] mt-2 leading-[1.65]">
                  Index new files. Documents are parsed via PyMuPDF, chunked recursively, and indexed dynamically into the PostgreSQL vector store.
                </p>
              </div>

              {/* Redesigned spacious upload drop-zone */}
              <form
                onSubmit={handleUpload}
                className="border border-dashed border-[#ECEFF3] bg-[#FCFCFD] rounded-2xl p-8 flex flex-col items-center justify-center gap-5 hover:border-[#2563EB]/40 hover:bg-[#F3F4F6]/20 transition-all shadow-[inset_0_1px_2px_rgba(0,0,0,0.01)] group"
              >
                <div className="w-14 h-14 rounded-full bg-white border border-[#E5E7EB] shadow-sm flex items-center justify-center text-[#4B5563] group-hover:scale-105 transition-all">
                  <UploadCloud className="w-6.5 h-6.5 text-[#4B5563]" />
                </div>
                <div className="text-center">
                  <p className="text-[15px] font-bold text-[#111827]">
                    {uploadFile ? uploadFile.name : "Drag and drop or select files"}
                  </p>
                  <p className="text-[13px] text-[#6B7280] mt-1.5 font-medium">
                    Supports PDF, TXT up to 50MB
                  </p>
                </div>
                
                <input
                  id="file-input"
                  type="file"
                  accept=".pdf,.txt"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setUploadFile(e.target.files[0]);
                    }
                  }}
                  className="hidden"
                />
                
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => document.getElementById("file-input")?.click()}
                    className="h-11 px-5 border border-[#E5E7EB] hover:bg-[#F3F4F6] rounded-xl text-xs font-bold transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                  >
                    Choose File
                  </button>
                  <button
                    type="submit"
                    disabled={!uploadFile || isUploading}
                    className="h-11 px-5 bg-[#2563EB] hover:bg-[#1D4ED8] disabled:bg-[#9CA3AF] disabled:cursor-not-allowed text-white font-bold rounded-xl text-xs transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer shadow-sm shadow-[#2563EB]/10"
                  >
                    {isUploading ? "Uploading..." : "Trigger Ingestion"}
                  </button>
                </div>

                {uploadSuccess && (
                  <div className="flex items-center gap-2 text-[#16A34A] bg-[#F0FDF4] border border-[#DCFCE7] px-4 py-2 rounded-xl text-xs font-semibold transition-all">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Upload index triggered successfully!</span>
                  </div>
                )}

                {uploadError && (
                  <div className="flex items-center gap-2 text-[#DC2626] bg-[#FEF2F2] border border-[#FEE2E2] px-4 py-2 rounded-xl text-xs font-semibold transition-all animate-shake">
                    <XCircle className="w-4 h-4" />
                    <span>{uploadError}</span>
                  </div>
                )}
              </form>

              {/* Uploads Directory table */}
              <div className="flex-1 flex flex-col gap-4">
                <h3 className="text-[13px] font-bold tracking-wider text-[#6B7280] uppercase">
                  Document Index Directory ({documents.length})
                </h3>
                {documents.length === 0 ? (
                  <div className="flex-1 border border-[#E5E7EB] border-dashed rounded-2xl flex flex-col items-center justify-center py-12 text-[#6B7280] text-[14px]">
                    No documents indexed yet. Upload a file above.
                  </div>
                ) : (
                  <div className="border border-[#E5E7EB] rounded-2xl overflow-hidden shadow-sm">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-[#E5E7EB] bg-[#FCFCFD] h-12">
                          <th className="p-4 font-bold text-[#4B5563] uppercase tracking-wider">Filename</th>
                          <th className="p-4 font-bold text-[#4B5563] uppercase tracking-wider">Size</th>
                          <th className="p-4 font-bold text-[#4B5563] uppercase tracking-wider">Category</th>
                          <th className="p-4 font-bold text-[#4B5563] uppercase tracking-wider">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {documents.map((doc) => (
                          <tr
                            key={doc.id}
                            className="border-b border-[#ECEFF3] last:border-0 hover:bg-[#F3F4F6]/50 h-14 transition-all"
                          >
                            <td className="p-4 font-bold text-[#111827] text-[13px]">
                              {doc.filename}
                            </td>
                            <td className="p-4 text-[#4B5563] font-medium text-[13px]">
                              {(doc.size_bytes / 1024).toFixed(1)} KB
                            </td>
                            <td className="p-4">
                              <span className="px-2.5 py-1 rounded-full bg-[#DBEAFE]/80 text-[10px] font-bold text-[#2563EB]">
                                {doc.category}
                              </span>
                            </td>
                            <td className="p-4">
                              <span
                                className={`px-2.5 py-1 rounded-full text-[10px] font-bold inline-flex items-center gap-1.5 ${
                                  doc.status === "PARSED"
                                    ? "bg-[#F0FDF4] text-[#16A34A] border border-[#DCFCE7]"
                                    : doc.status === "FAILED"
                                    ? "bg-[#FEF2F2] text-[#DC2626] border border-[#FEE2E2]"
                                    : "bg-[#FFFBEB] text-[#D97706] border border-[#FEF3C7] animate-pulse"
                                }`}
                              >
                                {doc.status === "PARSING" && (
                                  <Loader2 className="w-3 h-3 animate-spin" />
                                )}
                                {doc.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: EXTRACTION SCHEMAS */}
          {activeTab === "schemas" && (
            <div className="flex-grow flex flex-col gap-8">
              <div>
                <h2 className="text-[26px] font-bold tracking-tight text-[#111827] leading-[1.2]">
                  Extraction Templates
                </h2>
                <p className="text-[14px] text-[#4B5563] mt-2 leading-[1.65]">
                  Configure validation schema templates to guide structural mapping algorithms.
                </p>
              </div>

              {/* Create Schema Card */}
              <form
                onSubmit={handleCreateSchema}
                className="border border-[#E5E7EB] bg-[#FCFCFD] p-8 rounded-[18px] flex flex-col gap-6 shadow-sm"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] text-[#4B5563] font-bold">
                      Schema Title
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Purchase Order Schema"
                      value={schemaName}
                      onChange={(e) => setSchemaName(e.target.value)}
                      className="h-11 px-4 bg-white border border-[#E5E7EB] focus:border-[#2563EB] rounded-xl text-sm transition-all text-[#111827] outline-none shadow-sm"
                      required
                    />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] text-[#4B5563] font-bold">
                      Brief Description
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Extracts date, PO, vendor totals"
                      value={schemaDesc}
                      onChange={(e) => setSchemaDesc(e.target.value)}
                      className="h-11 px-4 bg-white border border-[#E5E7EB] focus:border-[#2563EB] rounded-xl text-sm transition-all text-[#111827] outline-none shadow-sm"
                    />
                  </div>
                </div>

                {/* Fields builder mapping */}
                <div className="flex flex-col gap-4">
                  <div className="flex items-center justify-between border-b border-[#ECEFF3] pb-3">
                    <span className="text-[13px] font-bold text-[#4B5563] uppercase tracking-wider">
                      Schema Variables Definition
                    </span>
                    <button
                      type="button"
                      onClick={addFieldRow}
                      className="px-3.5 py-2 border border-[#E5E7EB] hover:bg-[#F3F4F6] text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      Add Variable
                    </button>
                  </div>

                  <div className="flex flex-col gap-3">
                    {schemaFields.map((field, idx) => (
                      <div key={idx} className="flex items-center gap-3 animate-fade-in">
                        <input
                          type="text"
                          placeholder="Variable identifier (e.g. invoice_no)"
                          value={field.name}
                          onChange={(e) =>
                            handleFieldChange(idx, "name", e.target.value)
                          }
                          className="flex-1 h-10 px-3.5 bg-white border border-[#E5E7EB] focus:border-[#2563EB] rounded-xl text-xs text-[#111827] outline-none shadow-sm"
                          required
                        />
                        <select
                          value={field.type}
                          onChange={(e) =>
                            handleFieldChange(idx, "type", e.target.value)
                          }
                          className="h-10 px-3.5 bg-white border border-[#E5E7EB] focus:border-[#2563EB] rounded-xl text-xs text-[#111827] outline-none shadow-sm"
                        >
                          <option value="string">String (Text)</option>
                          <option value="number">Number (Float)</option>
                          <option value="integer">Integer (Whole)</option>
                          <option value="boolean">Boolean (True/False)</option>
                        </select>
                        <button
                          type="button"
                          onClick={() => removeFieldRow(idx)}
                          className="p-2.5 border border-[#E5E7EB] hover:bg-[#FEF2F2] hover:text-[#DC2626] rounded-xl text-[#9CA3AF] transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end pt-4 border-t border-[#ECEFF3]">
                  <button
                    type="submit"
                    disabled={isCreatingSchema || !schemaName}
                    className="h-11 px-6 bg-[#2563EB] hover:bg-[#1D4ED8] disabled:bg-[#9CA3AF] disabled:cursor-not-allowed text-white font-bold rounded-xl text-xs transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer shadow-sm shadow-[#2563EB]/10"
                  >
                    {isCreatingSchema ? "Saving..." : "Save Template"}
                  </button>
                </div>
              </form>

              {/* Schemas List catalog */}
              <div className="flex-1 flex flex-col gap-4">
                <h3 className="text-[13px] font-bold tracking-wider text-[#6B7280] uppercase">
                  Available Templates ({schemas.length})
                </h3>
                {schemas.length === 0 ? (
                  <div className="flex-grow border border-[#E5E7EB] border-dashed rounded-2xl flex flex-col items-center justify-center py-12 text-[#6B7280] text-[14px]">
                    No schemas templates registered yet. Define one above.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {schemas.map((sch) => (
                      <div
                        key={sch.id}
                        className="border border-[#E5E7EB] bg-white p-6 rounded-[18px] flex flex-col justify-between hover:shadow-md hover:border-[#2563EB]/20 transition-all"
                      >
                        <div>
                          <h4 className="font-bold text-[#111827] text-[15px]">{sch.name}</h4>
                          <p className="text-[12px] text-[#6B7280] mt-1">
                            {sch.description || "No description provided."}
                          </p>
                        </div>
                        <div className="mt-5 border-t border-[#ECEFF3] pt-4 flex flex-wrap gap-2">
                          {Object.entries(sch.schema_definition).map(
                            ([fname, ftype]) => (
                              <span
                                key={fname}
                                className="px-2.5 py-1 rounded-lg bg-[#FAFBFC] border border-[#E5E7EB] text-[10px] font-bold text-[#4B5563]"
                              >
                                {fname}: <span className="text-[#2563EB]">{ftype}</span>
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: RUN EXTRACTION WORKSPACE */}
          {activeTab === "extract" && (
            <div className="flex-grow flex flex-col gap-8">
              <div>
                <h2 className="text-[26px] font-bold tracking-tight text-[#111827] leading-[1.2]">
                  Extraction Workspace
                </h2>
                <p className="text-[14px] text-[#4B5563] mt-2 leading-[1.65]">
                  Select an ingested document source and a schema template to map structured variables values with provenance trails.
                </p>
              </div>

              {/* Document select forms card */}
              <form
                onSubmit={handleRunExtraction}
                className="border border-[#E5E7EB] bg-[#FCFCFD] p-6 rounded-2xl flex flex-col gap-5 shadow-sm"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] text-[#4B5563] font-bold">
                      Source Document
                    </label>
                    <select
                      value={selectedDocId}
                      onChange={(e) => setSelectedDocId(e.target.value)}
                      className="h-11 px-4 bg-white border border-[#E5E7EB] focus:border-[#2563EB] rounded-xl text-sm text-[#111827] outline-none shadow-sm"
                      required
                    >
                      <option value="">-- Choose ingested document --</option>
                      {documents
                        .filter((d) => d.status === "PARSED")
                        .map((d) => (
                          <option key={d.id} value={d.id}>
                            {d.filename} ({d.category})
                          </option>
                        ))}
                    </select>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] text-[#4B5563] font-bold">
                      Target Schema Template
                    </label>
                    <select
                      value={selectedSchemaId}
                      onChange={(e) => setSelectedSchemaId(e.target.value)}
                      className="h-11 px-4 bg-white border border-[#E5E7EB] focus:border-[#2563EB] rounded-xl text-sm text-[#111827] outline-none shadow-sm"
                      required
                    >
                      <option value="">-- Choose template --</option>
                      {schemas.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={isExtracting || !selectedDocId || !selectedSchemaId}
                    className="h-11 px-6 bg-[#2563EB] hover:bg-[#1D4ED8] disabled:bg-[#9CA3AF] disabled:cursor-not-allowed text-white font-bold rounded-xl text-xs transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer shadow-sm shadow-[#2563EB]/10 flex items-center gap-2"
                  >
                    {isExtracting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                    {isExtracting ? "Extracting Structured JSON..." : "Run Structured Extraction"}
                  </button>
                </div>

                {extractionError && (
                  <div className="flex items-center gap-2 text-[#DC2626] bg-[#FEF2F2] border border-[#FEE2E2] px-4 py-2.5 rounded-xl text-xs font-semibold transition-all">
                    <XCircle className="w-4 h-4" />
                    <span>{extractionError}</span>
                  </div>
                )}
              </form>

              {/* Extraction output (Structured side-by-side pane) */}
              <div className="flex-1 flex flex-col gap-4">
                <h3 className="text-[13px] font-bold tracking-wider text-[#6B7280] uppercase">
                  Extraction Results & Provenance
                </h3>

                {extractionResult ? (
                  <div className="flex-grow grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in">
                    {/* JSON viewer block */}
                    <div className="border border-[#E5E7EB] rounded-[18px] bg-white p-6 flex flex-col gap-4 shadow-sm">
                      <div className="flex items-center justify-between border-b border-[#ECEFF3] pb-3">
                        <div className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-full bg-[#16A34A]"></span>
                          <span className="text-[13px] font-bold text-[#111827]">
                            Structured Output JSON
                          </span>
                        </div>
                        <span className="px-2 py-0.5 rounded-md bg-[#F0FDF4] text-[#16A34A] border border-[#DCFCE7] text-[10px] font-bold tracking-wide uppercase">
                          Success
                        </span>
                      </div>
                      
                      <pre className="flex-1 text-xs text-[#2563EB] overflow-auto bg-[#FAFBFC] border border-[#E5E7EB] p-5 rounded-2xl font-mono leading-[1.6]">
                        {JSON.stringify(extractionResult.structured_data, null, 2)}
                      </pre>
                    </div>

                    {/* Citations panel card */}
                    <div className="border border-[#E5E7EB] rounded-[18px] bg-white p-6 flex flex-col gap-4 shadow-sm">
                      <div className="flex items-center justify-between border-b border-[#ECEFF3] pb-3">
                        <span className="text-[13px] font-bold text-[#111827]">
                          Citations Audit Trail
                        </span>
                        {extractionResult.provenance && (
                          <span className="text-xs font-bold text-[#4B5563]">
                            Aggregated Match:{" "}
                            <span className="text-[#2563EB]">
                              {(extractionResult.provenance.overall_confidence * 100).toFixed(0)}%
                            </span>
                          </span>
                        )}
                      </div>
                      
                      <div className="flex-1 overflow-auto flex flex-col gap-3.5 max-h-[360px] pr-1">
                        {extractionResult.provenance &&
                        extractionResult.provenance.citations.length > 0 ? (
                          extractionResult.provenance.citations.map((cite, i) => (
                            <div
                              key={i}
                              className="border border-[#E5E7EB] bg-[#FCFCFD] p-4.5 rounded-2xl flex flex-col gap-3 hover:shadow-sm hover:border-[#2563EB]/25 transition-all text-xs"
                            >
                              <div className="flex items-center justify-between">
                                <span className="px-2 py-0.5 rounded-md bg-[#E5E7EB]/50 text-[10px] font-bold text-[#4B5563]">
                                  Page {cite.page_number || 1} • {cite.retrieval_strategy}
                                </span>
                                <span className="text-[10px] text-[#16A34A] font-bold bg-[#F0FDF4] px-2 py-0.5 rounded border border-[#DCFCE7]">
                                  {(cite.confidence_score * 100).toFixed(0)}% Match
                                </span>
                              </div>
                              <p className="text-[#4B5563] leading-[1.6] italic bg-white border-l-3 border-[#2563EB] p-3 rounded-xl shadow-[inset_0_1px_2px_rgba(0,0,0,0.005)]">
                                &quot;{cite.snippet}...&quot;
                              </p>
                            </div>
                          ))
                        ) : (
                          <div className="flex-1 flex flex-col items-center justify-center text-[#9CA3AF] text-xs py-8">
                            No citations generated. Fallback rules applied.
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex-grow border border-[#E5E7EB] border-dashed rounded-2xl flex flex-col items-center justify-center py-16 text-[#6B7280] text-[14px]">
                    Configure extraction parameters and click run to map results.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 4: SEMANTIC SEARCH ENGINE */}
          {activeTab === "search" && (
            <div className="flex-grow flex flex-col gap-8">
              <div>
                <h2 className="text-[26px] font-bold tracking-tight text-[#111827] leading-[1.2]">
                  Semantic Search Engine
                </h2>
                <p className="text-[14px] text-[#4B5563] mt-2 leading-[1.65]">
                  Search across database chunk indices. Platform generates search query vectors and computes cosine similarity ranking.
                </p>
              </div>

              {/* Semantic search fields */}
              <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
                <input
                  type="text"
                  placeholder="Enter a conceptual search query (e.g., Acme billing details...)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 h-12 px-4 bg-white border border-[#E5E7EB] focus:border-[#2563EB] rounded-xl text-sm text-[#111827] outline-none shadow-sm"
                  required
                />
                
                <div className="flex gap-3">
                  <select
                    value={searchLimit}
                    onChange={(e) => setSearchLimit(Number(e.target.value))}
                    className="h-12 px-3.5 bg-white border border-[#E5E7EB] focus:border-[#2563EB] rounded-xl text-xs text-[#111827] outline-none shadow-sm cursor-pointer"
                  >
                    <option value="3">3 Chunks</option>
                    <option value="5">5 Chunks</option>
                    <option value="10">10 Chunks</option>
                  </select>
                  
                  <button
                    type="submit"
                    disabled={isSearching || !searchQuery}
                    className="h-12 px-6 bg-[#2563EB] hover:bg-[#1D4ED8] disabled:bg-[#9CA3AF] disabled:cursor-not-allowed text-white font-bold rounded-xl text-xs transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer shadow-sm shadow-[#2563EB]/10 flex items-center gap-2 shrink-0"
                  >
                    {isSearching && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                    {isSearching ? "Searching Index..." : "Search"}
                  </button>
                </div>
              </form>

              {/* Search Matches Cards */}
              <div className="flex-grow flex flex-col gap-4">
                <h3 className="text-[13px] font-bold tracking-wider text-[#6B7280] uppercase">
                  Similarity Matches ({searchResults.length})
                </h3>

                {searchResults.length > 0 ? (
                  <div className="overflow-auto flex flex-col gap-4 max-h-[420px] pr-1">
                    {searchResults.map((match, idx) => (
                      <div
                        key={idx}
                        className="border border-[#E5E7EB] bg-white p-6 rounded-[18px] flex flex-col gap-3.5 hover:shadow-md hover:border-[#2563EB]/25 transition-all text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="w-5 h-5 rounded-full bg-[#DBEAFE] text-[#2563EB] flex items-center justify-center font-bold text-[10px]">
                              {idx + 1}
                            </span>
                            <span className="font-bold text-[#4B5563] text-[11px] tracking-wide uppercase">
                              Chunk Index {match.chunk_index}
                            </span>
                          </div>
                          <span className="px-2.5 py-1 rounded-full bg-[#F0FDF4] border border-[#DCFCE7] text-[10px] font-bold text-[#16A34A]">
                            Similarity: {(match.score * 100).toFixed(1)}%
                          </span>
                        </div>
                        
                        <p className="text-[#111827] leading-[1.65] font-medium bg-[#FAFBFC] border border-[#ECEFF3] p-4.5 rounded-2xl shadow-[inset_0_1px_2px_rgba(0,0,0,0.005)]">
                          {match.content}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex-grow border border-[#E5E7EB] border-dashed rounded-2xl flex flex-col items-center justify-center py-16 text-[#6B7280] text-[14px]">
                    Input query terms above to fetch semantic vector matches.
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Modern SaaS Coming Soon Modal Popups */}
      {comingSoonModal?.isOpen && (
        <div className="fixed inset-0 z-100 flex items-center justify-center p-6 bg-slate-900/30 backdrop-blur-xs transition-opacity duration-300">
          <div className="bg-white border border-[#E5E7EB] rounded-3xl p-8 max-w-md w-full shadow-2xl flex flex-col gap-5 transform scale-100 transition-all duration-300">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-[#FEF3C7] flex items-center justify-center text-[#D97706] shrink-0 shadow-inner">
                <AlertTriangle className="w-6 h-6 animate-pulse" />
              </div>
              <div className="flex flex-col gap-1.5">
                <h3 className="text-[20px] font-bold text-[#111827] leading-tight">
                  Coming Soon
                </h3>
                <p className="text-[14px] font-bold text-[#4B5563] leading-snug">
                  The "{comingSoonModal.title}" module is currently under active development.
                </p>
              </div>
            </div>
            
            <p className="text-xs text-[#6B7280] leading-[1.65]">
              We are building this feature with production-grade architecture, layout-aware vector structures, and multi-agent workflow orchestration templates. Stay tuned for future releases.
            </p>

            <div className="flex justify-end gap-3 pt-3 border-t border-[#ECEFF3]">
              <button
                onClick={() => window.open("https://github.com/TarequeSyed/DocFlow-Ai", "_blank")}
                className="h-10 px-4 border border-[#E5E7EB] hover:bg-[#F3F4F6] text-[#4B5563] hover:text-[#111827] font-bold rounded-xl text-xs transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer flex items-center gap-1.5"
              >
                View Roadmap
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setComingSoonModal(null)}
                className="h-10 px-5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold rounded-xl text-xs transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer shadow-sm shadow-[#2563EB]/10"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
