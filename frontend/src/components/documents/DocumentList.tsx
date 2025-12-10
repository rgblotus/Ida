import React from 'react';
import { FileText, CheckCircle, AlertCircle, Loader2, Trash2 } from 'lucide-react';
import type { Document } from '../../types/api';
import { documentsAPI } from '../../services/api';

interface DocumentListProps {
  documents: Document[];
  onDelete?: (id: number) => void;
  onRefresh?: () => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onDelete,
  onRefresh
}) => {
  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await documentsAPI.delete(id);
      onDelete?.(id);
      onRefresh?.();
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('Failed to delete document');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Loader2 className="w-5 h-5 text-yellow-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'processing':
        return 'Processing';
      case 'failed':
        return 'Failed';
      default:
        return 'Pending';
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (documents.length === 0) {
    return (
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-12 border border-white/20 text-center">
        <FileText className="w-16 h-16 mx-auto mb-4 text-white/40" />
        <p className="text-white/60 text-lg">No documents found</p>
        <p className="text-white/40 text-sm mt-2">Upload some documents to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 hover:bg-white/15 transition-all duration-200"
        >
          <div className="flex items-start justify-between gap-4">
            {/* Document Info */}
            <div className="flex items-start gap-3 flex-1 min-w-0">
              <FileText className="w-6 h-6 text-purple-400 flex-shrink-0 mt-1" />
              <div className="flex-1 min-w-0">
                <h3 className="text-white font-medium truncate">{doc.filename}</h3>
                <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-white/60">
                  <span className="flex items-center gap-1">
                    {getStatusIcon(doc.status)}
                    {getStatusText(doc.status)}
                  </span>
                  <span>•</span>
                  <span>{doc.collection_name}</span>
                  <span>•</span>
                  <span>{formatFileSize(doc.file_size)}</span>
                  {doc.chunk_count > 0 && (
                    <>
                      <span>•</span>
                      <span>{doc.chunk_count} chunks</span>
                    </>
                  )}
                </div>
                <p className="text-xs text-white/40 mt-1">
                  Uploaded: {formatDate(doc.created_at)}
                </p>
                {doc.error_message && (
                  <p className="text-xs text-red-400 mt-2 bg-red-500/10 rounded px-2 py-1">
                    Error: {doc.error_message}
                  </p>
                )}
              </div>
            </div>

            {/* Actions */}
            <button
              onClick={() => handleDelete(doc.id)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/60 hover:text-red-400"
              title="Delete document"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
