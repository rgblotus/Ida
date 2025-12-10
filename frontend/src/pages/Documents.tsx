import React, { useState, useEffect } from 'react'
import { DocumentUpload } from '../components/documents/DocumentUpload'
import { PageLayout } from '../components/layout/PageLayout'
import { Modal } from '../components/ui/Modal'
import { documentsAPI, collectionsAPI } from '../services/api'
import type { Document, Collection } from '../types/api'
import VectorVisualization from '../components/visualization/VectorVisualization'
import {
    FileText,
    Filter,
    RefreshCw,
    Upload,
    Database,
    Layers,
    Clock,
    CheckCircle,
    XCircle,
    Loader,
    Trash2,
    Eye,
    BarChart3,
    Zap,
} from 'lucide-react'

export const Documents: React.FC = () => {
    const [documents, setDocuments] = useState<Document[]>([])
    const [collections, setCollections] = useState<Collection[]>([])
    const [selectedCollection, setSelectedCollection] = useState<string>('all')
    const [selectedStatus, setSelectedStatus] = useState<string>('all')
    const [isLoading, setIsLoading] = useState(false)
    const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
    const [vizData, setVizData] = useState<{
        points: number[][]
        labels: string[]
        metadata?: Record<string, unknown>[]
        total_points: number
    } | null>(null)
    const [isLoadingViz, setIsLoadingViz] = useState(false)
    const [showVizModal, setShowVizModal] = useState(false)

    useEffect(() => {
        loadCollections()
        loadDocuments()
    }, [])

    useEffect(() => {
        loadDocuments()
    }, [selectedCollection, selectedStatus])

    const loadCollections = async () => {
        try {
            const data = await collectionsAPI.list()
            setCollections(data)
        } catch (error) {
            console.error('Failed to load collections:', error)
        }
    }

    const loadDocuments = async () => {
        setIsLoading(true)
        try {
            const collectionFilter =
                selectedCollection === 'all' ? undefined : selectedCollection
            const statusFilter =
                selectedStatus === 'all' ? undefined : selectedStatus

            const data = await documentsAPI.list(collectionFilter, statusFilter)
            setDocuments(data)
        } catch (error) {
            console.error('Failed to load documents:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const handleUploadComplete = () => {
        loadDocuments()
        loadCollections()
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this document?')) return
        try {
            await documentsAPI.delete(id)
            setDocuments((docs) => docs.filter((d) => d.id !== id))
            if (selectedDoc?.id === id) setSelectedDoc(null)
        } catch (error) {
            console.error('Failed to delete document:', error)
            alert('Failed to delete document')
        }
    }

    const handleVisualize = async (documentId: number) => {
        setIsLoadingViz(true)
        try {
            const data = await documentsAPI.visualize(documentId)
            setVizData(data)
            setShowVizModal(true)
        } catch (error) {
            console.error('Failed to load visualization:', error)
            alert('Failed to load vector visualization')
        } finally {
            setIsLoadingViz(false)
        }
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="w-5 h-5 text-green-400" />
            case 'failed':
                return <XCircle className="w-5 h-5 text-red-400" />
            case 'processing':
                return <Loader className="w-5 h-5 text-blue-400 animate-spin" />
            default:
                return <Clock className="w-5 h-5 text-yellow-400" />
        }
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'from-green-500/20 to-emerald-500/20 border-green-500/30'
            case 'failed':
                return 'from-red-500/20 to-rose-500/20 border-red-500/30'
            case 'processing':
                return 'from-blue-500/20 to-cyan-500/20 border-blue-500/30'
            default:
                return 'from-yellow-500/20 to-orange-500/20 border-yellow-500/30'
        }
    }

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        })
    }

    // Calculate stats
    const stats = {
        total: documents.length,
        completed: documents.filter((d) => d.status === 'completed').length,
        processing: documents.filter((d) => d.status === 'processing').length,
        failed: documents.filter((d) => d.status === 'failed').length,
        totalChunks: documents.reduce(
            (sum, d) => sum + (d.chunk_count || 0),
            0
        ),
        totalSize: documents.reduce((sum, d) => sum + (d.file_size || 0), 0),
    }

    return (
        <PageLayout
            theme="indigo"
            title="Document Management"
            subtitle="Upload, vectorize, and manage your documents"
            icon={<FileText className="w-6 h-6 text-white" />}
            actions={
                <button
                    onClick={loadDocuments}
                    disabled={isLoading}
                    className="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-white transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                    <RefreshCw
                        className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}
                    />
                    <span>Refresh</span>
                </button>
            }
            sidePanel={
                selectedDoc && (
                    <div className="w-96 bg-gradient-to-b from-indigo-900/30 to-purple-900/30 backdrop-blur-xl border-l border-white/20 overflow-y-auto">
                        <div className="p-6 sticky top-0 bg-gradient-to-b from-indigo-900/50 to-transparent backdrop-blur-xl border-b border-white/20 z-10">
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                    <Eye className="w-5 h-5 text-indigo-400" />
                                    Document Details
                                </h3>
                                <button
                                    onClick={() => setSelectedDoc(null)}
                                    className="p-1 hover:bg-white/10 rounded transition-colors"
                                >
                                    <XCircle className="w-5 h-5 text-white/60" />
                                </button>
                            </div>
                        </div>

                        <div className="p-6 space-y-4">
                            {/* File Info */}
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                    <FileText className="w-4 h-4 text-purple-400" />
                                    File Information
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div>
                                        <p className="text-white/60 text-xs">
                                            Filename
                                        </p>
                                        <p className="text-white font-mono break-all">
                                            {selectedDoc.filename}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-white/60 text-xs">
                                            File Size
                                        </p>
                                        <p className="text-white font-mono">
                                            {formatFileSize(
                                                selectedDoc.file_size || 0
                                            )}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-white/60 text-xs">
                                            Status
                                        </p>
                                        <div className="flex items-center gap-2 mt-1">
                                            {getStatusIcon(selectedDoc.status)}
                                            <span className="text-white font-semibold capitalize">
                                                {selectedDoc.status}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Vectorization Info */}
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                    <Zap className="w-4 h-4 text-yellow-400" />
                                    Vectorization
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex items-center justify-between">
                                        <span className="text-white/60">
                                            Total Chunks
                                        </span>
                                        <span className="text-white font-bold">
                                            {selectedDoc.chunk_count || 0}
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-white/60">
                                            Collection
                                        </span>
                                        <span className="text-white font-mono text-xs">
                                            {selectedDoc.collection_name}
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-white/60">
                                            Embedding Model
                                        </span>
                                        <span className="text-white font-mono text-xs">
                                            text-emb-3-small
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-white/60">
                                            Vector Dim
                                        </span>
                                        <span className="text-white font-mono">
                                            1536
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Chunk Details */}
                            {selectedDoc.chunk_count > 0 && (
                                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                        <Layers className="w-4 h-4 text-cyan-400" />
                                        Chunk Analysis
                                    </h4>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex items-center justify-between">
                                            <span className="text-white/60">
                                                Avg Chunk Size
                                            </span>
                                            <span className="text-white font-mono">
                                                {Math.round(
                                                    (selectedDoc.file_size ||
                                                        0) /
                                                        (selectedDoc.chunk_count ||
                                                            1)
                                                )}{' '}
                                                bytes
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-white/60">
                                                Chunk Overlap
                                            </span>
                                            <span className="text-white font-mono">
                                                200 chars
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-white/60">
                                                Stored Vectors
                                            </span>
                                            <span className="text-white font-bold">
                                                {selectedDoc.chunk_count}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Vector Visualization */}
                            {selectedDoc.chunk_count > 0 && (
                                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                        <BarChart3 className="w-4 h-4 text-purple-400" />
                                        Vector Visualization
                                    </h4>
                                    <button
                                        onClick={() =>
                                            handleVisualize(selectedDoc.id)
                                        }
                                        disabled={isLoadingViz}
                                        className="w-full px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded-lg text-purple-200 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                                    >
                                        {isLoadingViz ? (
                                            <Loader className="w-4 h-4 animate-spin" />
                                        ) : (
                                            <BarChart3 className="w-4 h-4" />
                                        )}
                                        <span>
                                            {isLoadingViz
                                                ? 'Loading...'
                                                : 'Open 3D Visualization'}
                                        </span>
                                    </button>
                                </div>
                            )}

                            {/* Timestamps */}
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                    <Clock className="w-4 h-4 text-blue-400" />
                                    Timeline
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div>
                                        <p className="text-white/60 text-xs">
                                            Uploaded
                                        </p>
                                        <p className="text-white font-mono text-xs">
                                            {formatDate(selectedDoc.created_at)}
                                        </p>
                                    </div>
                                    {selectedDoc.processed_at && (
                                        <div>
                                            <p className="text-white/60 text-xs">
                                                Processed
                                            </p>
                                            <p className="text-white font-mono text-xs">
                                                {formatDate(
                                                    selectedDoc.processed_at
                                                )}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Error Message */}
                            {selectedDoc.error_message && (
                                <div className="bg-red-500/20 backdrop-blur-sm rounded-xl p-4 border border-red-500/30">
                                    <h4 className="text-sm font-semibold text-red-300 mb-2 flex items-center gap-2">
                                        <XCircle className="w-4 h-4" />
                                        Error Details
                                    </h4>
                                    <p className="text-xs text-red-200">
                                        {selectedDoc.error_message}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                )
            }
        >
            <div className="space-y-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                    <div className="bg-white/10 backdrop-blur-xl rounded-xl p-4 border border-white/20">
                        <div className="flex items-center gap-2 mb-2">
                            <FileText className="w-4 h-4 text-purple-400" />
                            <span className="text-xs text-white/60">
                                Total Docs
                            </span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                            {stats.total}
                        </p>
                    </div>

                    <div className="bg-white/10 backdrop-blur-xl rounded-xl p-4 border border-white/20">
                        <div className="flex items-center gap-2 mb-2">
                            <CheckCircle className="w-4 h-4 text-green-400" />
                            <span className="text-xs text-white/60">
                                Completed
                            </span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                            {stats.completed}
                        </p>
                    </div>

                    <div className="bg-white/10 backdrop-blur-xl rounded-xl p-4 border border-white/20">
                        <div className="flex items-center gap-2 mb-2">
                            <Loader className="w-4 h-4 text-blue-400" />
                            <span className="text-xs text-white/60">
                                Processing
                            </span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                            {stats.processing}
                        </p>
                    </div>

                    <div className="bg-white/10 backdrop-blur-xl rounded-xl p-4 border border-white/20">
                        <div className="flex items-center gap-2 mb-2">
                            <XCircle className="w-4 h-4 text-red-400" />
                            <span className="text-xs text-white/60">
                                Failed
                            </span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                            {stats.failed}
                        </p>
                    </div>

                    <div className="bg-white/10 backdrop-blur-xl rounded-xl p-4 border border-white/20">
                        <div className="flex items-center gap-2 mb-2">
                            <Layers className="w-4 h-4 text-cyan-400" />
                            <span className="text-xs text-white/60">
                                Total Chunks
                            </span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                            {stats.totalChunks}
                        </p>
                    </div>

                    <div className="bg-white/10 backdrop-blur-xl rounded-xl p-4 border border-white/20">
                        <div className="flex items-center gap-2 mb-2">
                            <Database className="w-4 h-4 text-pink-400" />
                            <span className="text-xs text-white/60">
                                Total Size
                            </span>
                        </div>
                        <p className="text-lg font-bold text-white">
                            {formatFileSize(stats.totalSize)}
                        </p>
                    </div>
                </div>

                {/* Upload Section */}
                <DocumentUpload
                    onUploadComplete={handleUploadComplete}
                    selectedCollection={
                        selectedCollection !== 'all'
                            ? selectedCollection
                            : 'default'
                    }
                />

                {/* Filters */}
                <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 border border-white/20">
                    <div className="flex items-center gap-4 flex-wrap">
                        <div className="flex items-center gap-2">
                            <Filter className="w-5 h-5 text-white/60" />
                            <span className="text-white/80 font-medium">
                                Filters:
                            </span>
                        </div>

                        <select
                            value={selectedCollection}
                            onChange={(e) =>
                                setSelectedCollection(e.target.value)
                            }
                            className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                            <option value="all" className="bg-slate-900">
                                All Collections
                            </option>
                            {collections.map((col) => (
                                <option
                                    key={col.id}
                                    value={col.name}
                                    className="bg-slate-900"
                                >
                                    {col.name} ({col.document_count})
                                </option>
                            ))}
                        </select>

                        <select
                            value={selectedStatus}
                            onChange={(e) => setSelectedStatus(e.target.value)}
                            className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                            <option value="all" className="bg-slate-900">
                                All Status
                            </option>
                            <option value="pending" className="bg-slate-900">
                                Pending
                            </option>
                            <option value="processing" className="bg-slate-900">
                                Processing
                            </option>
                            <option value="completed" className="bg-slate-900">
                                Completed
                            </option>
                            <option value="failed" className="bg-slate-900">
                                Failed
                            </option>
                        </select>
                    </div>
                </div>

                {/* Documents Grid */}
                <div>
                    <h2 className="text-xl font-bold text-white mb-4">
                        Documents ({documents.length})
                    </h2>

                    {isLoading ? (
                        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-12 border border-white/20 text-center">
                            <RefreshCw className="w-12 h-12 mx-auto mb-4 text-purple-400 animate-spin" />
                            <p className="text-white/60">
                                Loading documents...
                            </p>
                        </div>
                    ) : documents.length === 0 ? (
                        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-12 border border-white/20 text-center">
                            <Upload className="w-16 h-16 mx-auto mb-4 text-white/40" />
                            <p className="text-white/60 text-lg">
                                No documents yet
                            </p>
                            <p className="text-white/40 text-sm mt-2">
                                Upload your first document to get started
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {documents.map((doc) => (
                                <div
                                    key={doc.id}
                                    className={`bg-gradient-to-br ${getStatusColor(
                                        doc.status
                                    )} backdrop-blur-xl rounded-xl p-4 border cursor-pointer hover:scale-105 transition-transform`}
                                    onClick={() => setSelectedDoc(doc)}
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center gap-2">
                                            {getStatusIcon(doc.status)}
                                            <span className="text-xs font-semibold text-white/80 uppercase">
                                                {doc.status}
                                            </span>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                handleDelete(doc.id)
                                            }}
                                            className="p-1 hover:bg-red-500/20 rounded transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4 text-red-400" />
                                        </button>
                                    </div>

                                    <h3
                                        className="text-white font-semibold mb-2 truncate"
                                        title={doc.filename}
                                    >
                                        {doc.filename}
                                    </h3>

                                    <div className="space-y-1 text-xs text-white/70">
                                        <div className="flex items-center justify-between">
                                            <span>Collection:</span>
                                            <span className="font-mono text-white/90">
                                                {doc.collection_name}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span>Chunks:</span>
                                            <span className="font-mono text-white/90">
                                                {doc.chunk_count || 0}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span>Size:</span>
                                            <span className="font-mono text-white/90">
                                                {formatFileSize(
                                                    doc.file_size || 0
                                                )}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span>Uploaded:</span>
                                            <span className="font-mono text-white/90">
                                                {new Date(
                                                    doc.created_at
                                                ).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Visualization Modal */}
            <Modal
                isOpen={showVizModal}
                onClose={() => setShowVizModal(false)}
                title={`3D Vector Visualization - ${
                    selectedDoc?.filename || 'Document'
                }`}
                size="lg"
                fullContent={true}
            >
                <div className="flex-1 min-h-0 p-0" style={{ height: '50vh' }}>
                    {vizData ? (
                        <VectorVisualization
                            data={vizData}
                            className="w-full h-full"
                        />
                    ) : (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <Loader className="w-12 h-12 mx-auto mb-4 text-purple-400 animate-spin" />
                                <p className="text-white">
                                    Loading visualization...
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </Modal>
        </PageLayout>
    )
}
