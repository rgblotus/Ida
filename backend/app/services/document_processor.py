from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredFileLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
from pathlib import Path
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class LaTeXAwareTextSplitter:
    """Text splitter that preserves LaTeX math expressions"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # LaTeX patterns to preserve
        self.latex_patterns = [
            (r'\$\$[\s\S]*?\$\$', 'DISPLAY_MATH'),  # $$...$$
            (r'\\\[[\s\S]*?\\\]', 'DISPLAY_MATH_ALT'),  # \[...\]
            (r'\\begin\{equation\}[\s\S]*?\\end\{equation\}', 'EQUATION_ENV'),  # \begin{equation}...\end{equation}
            (r'\\begin\{align\}[\s\S]*?\\end\{align\}', 'ALIGN_ENV'),  # \begin{align}...\end{align}
            (r'\\begin\{gather\}[\s\S]*?\\end\{gather\}', 'GATHER_ENV'),  # \begin{gather}...\end{gather}
            (r'\$[^$\n]+\$', 'INLINE_MATH'),  # $...$
            (r'\\\([\s\S]*?\\\)', 'INLINE_MATH_ALT'),  # \(...\)
        ]

    def split_text(self, text: str) -> List[str]:
        """Split text while preserving LaTeX expressions"""
        # Replace LaTeX expressions with placeholders
        placeholders = {}
        placeholder_counter = 0
        modified_text = text

        for pattern, placeholder_type in self.latex_patterns:
            def replace_func(match):
                nonlocal placeholder_counter
                placeholder = f"__LATEX_{placeholder_type}_{placeholder_counter}__"
                placeholders[placeholder] = match.group(0)
                placeholder_counter += 1
                return placeholder

            modified_text = re.sub(pattern, replace_func, modified_text, flags=re.MULTILINE)

        # Split the modified text
        chunks = []
        start = 0
        text_len = len(modified_text)

        while start < text_len:
            end = start + self.chunk_size

            if end >= text_len:
                chunks.append(modified_text[start:])
                break

            # Find a good split point (prefer sentence endings)
            split_point = end
            for i in range(max(start, end - 100), min(end + 100, text_len)):
                if modified_text[i] in '.!?\n' and not modified_text[i-1:i+1] == '..':
                    # Check if we're inside a placeholder
                    before_char = modified_text[max(0, i-50):i]
                    after_char = modified_text[i:min(text_len, i+50)]

                    # Make sure we're not splitting inside a placeholder
                    if not ('__LATEX_' in before_char and '__' in after_char):
                        split_point = i + 1
                        break

            chunk = modified_text[start:split_point]

            # Restore LaTeX expressions in chunk
            for placeholder, latex in placeholders.items():
                chunk = chunk.replace(placeholder, latex)

            chunks.append(chunk)

            # Move start position with overlap
            start = max(start + 1, split_point - self.chunk_overlap)

        return chunks

    def split_documents(self, documents):
        """Split documents using LaTeX-aware splitting"""
        from langchain_core.documents import Document

        split_docs = []
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            for chunk in chunks:
                split_docs.append(Document(
                    page_content=chunk,
                    metadata=doc.metadata
                ))

        return split_docs

class DocumentProcessor:
    """Service for processing documents and adding them to vector store"""
    
    def __init__(self, settings, vector_store_service, db_session):
        self.settings = settings
        self.vector_store_service = vector_store_service
        self.db = db_session

        # Initialize LaTeX-aware text splitter
        self.text_splitter = LaTeXAwareTextSplitter(
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP
        )
    
    def load_document(self, file_path: str) -> List:
        """
        Load document based on file type
        
        Args:
            file_path: Path to the document
        
        Returns:
            List of loaded documents
        """
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension == '.txt':
                loader = TextLoader(file_path)
            elif file_extension in ['.docx', '.doc']:
                loader = Docx2txtLoader(file_path)
            else:
                # Fallback to unstructured loader
                loader = UnstructuredFileLoader(file_path)
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            raise
    
    def split_documents(self, documents: List) -> List:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents
        
        Returns:
            List of text chunks
        """
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Failed to split documents: {e}")
            raise
    
    async def process_document(
        self,
        document_id: int,
        file_path: str,
        collection_name: str
    ):
        """
        Process a document: load, split, and add to vector store
        
        Args:
            document_id: Database ID of the document
            file_path: Path to the document file
            collection_name: Name of the collection to add to
        """
        from app.infra import Document
        from sqlalchemy import select
        
        try:
            # Update status to processing
            result = await self.db.execute(select(Document).where(Document.id == document_id))
            document = result.scalar_one_or_none()
            if not document:
                logger.error(f"Document {document_id} not found")
                return
            
            document.status = "processing"
            await self.db.commit()
            
            # Load document
            loaded_docs = self.load_document(file_path)
            
            # Split into chunks
            chunks = self.split_documents(loaded_docs)
            
            # Prepare texts and metadatas
            texts = [chunk.page_content for chunk in chunks]
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                # Create title from filename (remove extension and clean up)
                title = Path(document.filename).stem
                if len(title) > 100:  # Truncate long titles
                    title = title[:97] + "..."

                # Create comprehensive metadata for different collection schemas
                metadata = {
                    # Core document fields
                    "document_id": document_id,
                    "filename": document.filename,
                    "title": title,  # Required field for Milvus schema
                    "subject": title,  # Alternative field name for compatibility
                    "name": title,  # Another common field name

                    # Chunk information
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_id": f"{document_id}_{i}",

                    # Collection info
                    "collection": collection_name,
                    "collection_name": collection_name,

                    # Content info
                    "content_length": len(chunk.page_content),
                    "has_content": len(chunk.page_content.strip()) > 0,

                    # Document metadata
                    "file_size": document.file_size,
                    "file_type": document.file_type,

                    # Author information (required by some collection schemas)
                    "author": chunk.metadata.get('author', 'Unknown'),

                    # Processing info
                    "processed_at": document.created_at.isoformat() if document.created_at else None,

                    # Include any additional metadata from the chunk
                    **chunk.metadata
                }

                # Remove None values to avoid schema issues
                metadata = {k: v for k, v in metadata.items() if v is not None}
                metadatas.append(metadata)
            
            # Add to vector store in batches to avoid GPU memory issues
            batch_size = 10  # Process in small batches
            doc_ids = []

            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size]

                logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size} ({len(batch_texts)} chunks)")

                batch_ids = self.vector_store_service.add_documents(
                    collection_name=collection_name,
                    texts=batch_texts,
                    metadatas=batch_metadatas
                )
                doc_ids.extend(batch_ids)
            
            # Update document status
            document.status = "completed"
            document.chunk_count = len(chunks)
            document.processed_at = datetime.utcnow()
            document.doc_metadata = {
                "vector_ids": doc_ids,
                "total_chunks": len(chunks)
            }
            await self.db.commit()
            
            logger.info(f"Successfully processed document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            
            # Update status to failed
            result = await self.db.execute(select(Document).where(Document.id == document_id))
            document = result.scalar_one_or_none()
            if document:
                document.status = "failed"
                document.error_message = str(e)
                await self.db.commit()
    
    async def batch_process_documents(
        self,
        document_ids: List[int],
        collection_name: str
    ):
        """
        Process multiple documents in batch
        
        Args:
            document_ids: List of document IDs
            collection_name: Name of the collection
        """
        from app.infra import Document
        from sqlalchemy import select
        
        for doc_id in document_ids:
            result = await self.db.execute(select(Document).where(Document.id == doc_id))
            document = result.scalar_one_or_none()
            if document:
                await self.process_document(doc_id, document.file_path, collection_name)
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return ['.pdf', '.txt', '.docx', '.doc', '.md', '.html', '.json']
