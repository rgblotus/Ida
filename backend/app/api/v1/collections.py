from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from typing import List, Optional, Dict
from datetime import datetime

from app.infra.database import get_db
from app.core.config import settings
from app.infra import Collection, User, Document
from app.api.v1.deps import get_current_user
from app.domain.schemas.collections import CollectionCreate, CollectionResponse, CollectionStatsResponse

router = APIRouter(tags=["collections"])

from app.services.vector_store_service import VectorStoreService
from app.services.service_manager import get_vector_store_service

@router.post("/", response_model=CollectionResponse)
async def create_collection(
    request: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new collection"""
    # Check if collection already exists
    result = await db.execute(
        select(Collection).where(
            Collection.name == request.name,
            Collection.user_id == current_user.id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Collection '{request.name}' already exists"
        )
    
    # Create collection
    collection = Collection(
        name=request.name,
        description=request.description,
        user_id=current_user.id
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    
    # Get document count
    doc_count_result = await db.execute(
        select(sql_func.count(Document.id)).where(
            Document.collection_id == collection.id
        )
    )
    doc_count = doc_count_result.scalar() or 0
    
    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        document_count=doc_count,
        created_at=collection.created_at,
        updated_at=collection.updated_at
    )

@router.get("/", response_model=List[CollectionResponse])
async def list_collections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all collections for current user"""
    result = await db.execute(
        select(Collection)
        .where(Collection.user_id == current_user.id)
        .order_by(Collection.created_at.desc())
    )
    collections = result.scalars().all()
    
    response = []
    for collection in collections:
        doc_count_result = await db.execute(
            select(sql_func.count(Document.id)).where(
                Document.collection_id == collection.id
            )
        )
        doc_count = doc_count_result.scalar() or 0
        
        response.append(CollectionResponse(
            id=collection.id,
            name=collection.name,
            description=collection.description,
            document_count=doc_count,
            created_at=collection.created_at,
            updated_at=collection.updated_at
        ))
    
    return response

@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get collection details"""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id
        )
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    doc_count_result = await db.execute(
        select(sql_func.count(Document.id)).where(
            Document.collection_id == collection.id
        )
    )
    doc_count = doc_count_result.scalar() or 0
    
    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        document_count=doc_count,
        created_at=collection.created_at,
        updated_at=collection.updated_at
    )

@router.get("/{collection_id}/stats", response_model=CollectionStatsResponse)
async def get_collection_stats(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    vector_store: VectorStoreService = Depends(get_vector_store_service)
):
    """Get detailed collection statistics"""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id
        )
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Get document count
    doc_count_result = await db.execute(
        select(sql_func.count(Document.id)).where(
            Document.collection_id == collection.id
        )
    )
    doc_count = doc_count_result.scalar() or 0
    
    # Get total chunks
    total_chunks_result = await db.execute(
        select(sql_func.sum(Document.chunk_count)).where(
            Document.collection_id == collection.id
        )
    )
    total_chunks = total_chunks_result.scalar() or 0
    
    # Get Milvus stats
    milvus_stats = vector_store.get_collection_stats(collection.name)
    milvus_entities = milvus_stats.get("num_entities", 0) if milvus_stats.get("exists") else 0
    
    return CollectionStatsResponse(
        id=collection.id,
        name=collection.name,
        document_count=doc_count,
        total_chunks=int(total_chunks),
        milvus_entities=milvus_entities,
        status="active" if milvus_stats.get("exists") else "not_initialized"
    )

@router.get("/{collection_id}/visualize", response_model=Dict)
async def get_collection_visualization(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    vector_store: VectorStoreService = Depends(get_vector_store_service)
):
    """Get 3D visualization data for collection vectors"""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id
        )
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Get 3D visualization data
    viz_data = vector_store.get_3d_visualization_data(collection.name)

    if "error" in viz_data:
        raise HTTPException(status_code=500, detail=viz_data["error"])

    return viz_data

@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: int,
    delete_vectors: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    vector_store: VectorStoreService = Depends(get_vector_store_service)
):
    """Delete a collection"""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id
        )
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Delete from Milvus if requested
    if delete_vectors:
        try:
            vector_store.delete_collection(collection.name)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Error deleting Milvus collection: {e}")
    
    # Delete from database (cascade will delete documents)
    await db.delete(collection)
    await db.commit()
    
    return {"message": "Collection deleted successfully"}

@router.patch("/{collection_id}")
async def update_collection(
    collection_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update collection details"""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id
        )
    )
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    if name:
        # Check if new name already exists
        existing_result = await db.execute(
            select(Collection).where(
                Collection.name == name,
                Collection.user_id == current_user.id,
                Collection.id != collection_id
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Collection '{name}' already exists"
            )
        
        collection.name = name
    
    if description is not None:
        collection.description = description
    
    collection.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Collection updated successfully"}
