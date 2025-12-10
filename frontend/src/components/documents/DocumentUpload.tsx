import React, { useState, useCallback } from 'react';
import { Upload, X, FileText, Loader2 } from 'lucide-react';
import { documentsAPI } from '../../services/api';

interface DocumentUploadProps {
  onUploadComplete?: () => void;
  selectedCollection?: string;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadComplete,
  selectedCollection = 'default'
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [collectionName, setCollectionName] = useState(selectedCollection);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(prev => [...prev, ...droppedFiles]);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles(prev => [...prev, ...selectedFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    try {
      await documentsAPI.upload(files, collectionName);
      setFiles([]);
      onUploadComplete?.();
      alert(`Successfully uploaded ${files.length} file(s)`);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
      <h2 className="text-2xl font-bold text-white mb-4">Upload Documents</h2>

      {/* Collection Name Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-white/80 mb-2">
          Collection Name
        </label>
        <input
          type="text"
          value={collectionName}
          onChange={(e) => setCollectionName(e.target.value)}
          placeholder="default"
          className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
          isDragging
            ? 'border-purple-400 bg-purple-500/20'
            : 'border-white/30 bg-white/5'
        }`}
      >
        <Upload className={`w-12 h-12 mx-auto mb-4 ${isDragging ? 'text-purple-400' : 'text-white/60'}`} />
        <p className="text-white/80 mb-2">
          Drag and drop files here, or click to select
        </p>
        <p className="text-sm text-white/50 mb-4">
          Supported: PDF, DOCX, TXT, MD, HTML, JSON
        </p>
        <input
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
          accept=".pdf,.docx,.doc,.txt,.md,.html,.json"
        />
        <label
          htmlFor="file-upload"
          className="inline-block px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg cursor-pointer hover:from-purple-700 hover:to-blue-700 transition-all duration-200"
        >
          Select Files
        </label>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          <h3 className="text-sm font-semibold text-white/80">
            Selected Files ({files.length})
          </h3>
          <div className="max-h-48 overflow-y-auto space-y-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-white/5 rounded-lg p-3 border border-white/10"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <FileText className="w-5 h-5 text-purple-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate">{file.name}</p>
                    <p className="text-xs text-white/50">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 hover:bg-white/10 rounded transition-colors"
                >
                  <X className="w-4 h-4 text-white/60" />
                </button>
              </div>
            ))}
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className="w-full mt-4 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                <span>Upload {files.length} File{files.length > 1 ? 's' : ''}</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};
