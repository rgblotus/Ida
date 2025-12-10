from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
import shutil
import os
import logging

from app.infra.database import get_db
from app.core.config import settings
from app.infra import Document, Collection, User
from app.services.document_processor import DocumentProcessor
from app.api.v1.deps import get_current_user
from app.domain.schemas.documents import DocumentResponse, UploadResponse


router = APIRouter(tags=["documents"])

logger = logging.getLogger(__name__)

from app.services.service_manager import get_vector_store_service

# Initialize document processor
def get_document_processor(db: AsyncSession = Depends(get_db)) -> DocumentProcessor:
    vector_store_service = get_vector_store_service()
    return DocumentProcessor(settings, vector_store_service, db)

@router.post("/upload", response_model=UploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(...),
    collection_name: str = "default",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    doc_processor: DocumentProcessor = Depends(get_document_processor)
):
    """Upload and process documents"""
    # Get or create collection
    result = await db.execute(
        select(Collection).where(
            Collection.name == collection_name,
            Collection.user_id == current_user.id
        )
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        collection = Collection(
            name=collection_name,
            user_id=current_user.id,
            description=f"Collection for {collection_name}"
        )
        db.add(collection)
        await db.commit()
        await db.refresh(collection)
    
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR) / str(current_user.id) / str(collection.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    document_ids = []
    
    for file in files:
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} exceeds maximum size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Get file extension
        file_extension = Path(file.filename).suffix.lower()
        
        # Validate file type
        supported_extensions = doc_processor.get_supported_extensions()
        if file_extension not in supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Supported types: {supported_extensions}"
            )
        
        # Save file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create title from filename
        title = Path(file.filename).stem
        if len(title) > 100:
            title = title[:97] + "..."

        # Create document record
        doc = Document(
            filename=file.filename,
            title=title,
            file_path=str(file_path),
            file_type=file_extension,
            file_size=file_size,
            collection_id=collection.id,
            user_id=current_user.id,
            status="pending"
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        document_ids.append(doc.id)
        
        # Schedule background processing
        background_tasks.add_task(
            doc_processor.process_document,
            doc.id,
            str(file_path),
            collection_name
        )
    
    return UploadResponse(
        message=f"Uploaded {len(files)} documents",
        document_ids=document_ids,
        collection_name=collection_name
    )

@router.get("/list", response_model=List[DocumentResponse])
async def list_documents(
    collection_name: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents, optionally filtered by collection and status"""
    query = select(Document).where(Document.user_id == current_user.id)
    
    if collection_name:
        query = query.join(Collection).where(Collection.name == collection_name)
    
    if status:
        query = query.where(Document.status == status)
    
    query = query.order_by(Document.created_at.desc())
    result = await db.execute(query)
    documents = result.scalars().all()
    
    # Load collections for each document
    response = []
    for doc in documents:
        collection_result = await db.execute(
            select(Collection).where(Collection.id == doc.collection_id)
        )
        collection = collection_result.scalar_one()
        
        response.append(DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            title=doc.title,
            file_type=doc.file_type,
            file_size=doc.file_size,
            collection_id=doc.collection_id,
            collection_name=collection.name,
            status=doc.status,
            chunk_count=doc.chunk_count,
            error_message=doc.error_message,
            created_at=doc.created_at,
            processed_at=doc.processed_at
        ))
    
    return response

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document details"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    collection_result = await db.execute(
        select(Collection).where(Collection.id == doc.collection_id)
    )
    collection = collection_result.scalar_one()
    
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        title=doc.title,
        file_type=doc.file_type,
        file_size=doc.file_size,
        collection_id=doc.collection_id,
        collection_name=collection.name,
        status=doc.status,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
        created_at=doc.created_at,
        processed_at=doc.processed_at
    )

@router.get("/{document_id}/visualize", response_model=Dict)
async def get_document_visualization(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    vector_store = Depends(get_vector_store_service)
):
    """Get 3D visualization data for document vectors"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if document is completed
    if doc.status != "completed":
        raise HTTPException(status_code=400, detail="Document is not yet processed")

    # Get collection name
    collection_result = await db.execute(
        select(Collection).where(Collection.id == doc.collection_id)
    )
    collection = collection_result.scalar_one()

    # Get 3D visualization data for this document only
    viz_data = vector_store.get_3d_visualization_data(collection.name, document_id)

    if "error" in viz_data:
        raise HTTPException(status_code=500, detail=viz_data["error"])

    return viz_data

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    vector_store = Depends(get_vector_store_service)
):
    """Delete a document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get collection name
    collection_result = await db.execute(
        select(Collection).where(Collection.id == doc.collection_id)
    )
    collection = collection_result.scalar_one()

    # Delete vectors from Milvus
    try:
        vector_store.delete_documents_by_id(collection.name, document_id)
    except Exception as e:
        # Log error but don't fail the entire operation
        logger.error(f"Failed to delete vectors for document {document_id}: {e}")

    # Delete file from filesystem
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # Delete from database
    await db.delete(doc)
    await db.commit()

    return {"message": "Document deleted successfully"}

@router.post("/batch-process")
async def batch_process(
    document_ids: List[int],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    doc_processor: DocumentProcessor = Depends(get_document_processor)
):
    """Batch process multiple documents"""
    # Verify all documents belong to user
    result = await db.execute(
        select(Document).where(
            Document.id.in_(document_ids),
            Document.user_id == current_user.id
        )
    )
    documents = result.scalars().all()
    
    if len(documents) != len(document_ids):
        raise HTTPException(status_code=404, detail="Some documents not found")
    
    # Get collection name from first document
    collection_result = await db.execute(
        select(Collection).where(Collection.id == documents[0].collection_id)
    )
    collection = collection_result.scalar_one()
    
    # Schedule batch processing
    background_tasks.add_task(
        doc_processor.batch_process_documents,
        document_ids,
        collection.name
    )
    
    return {
        "message": f"Batch processing {len(document_ids)} documents",
        "document_ids": document_ids
    }
