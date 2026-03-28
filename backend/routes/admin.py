from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from utils.dependencies import get_current_admin
from schemas.booth import (
    BoothCreate,
    BoothUpdate,
    BoothResponse,
    BoothAssignDevice,
    BoothConfigUpdate,
)
from schemas.auth import TokenVerifyResponse
from schemas.transaction import TransactionResponse
from services.booth_service import BoothService
from services.auth_service import AuthService
from services.transaction_service import TransactionService

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/booths", response_model=List[BoothResponse])
async def get_all_booths(
    admin: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)
):
    """Get all booths (admin only)."""
    booths = await BoothService.get_all_booths(db)
    return [
        {
            "id": str(booth.id),
            "name": booth.name,
            "location": booth.location,
            "device_id": booth.device_id,
            "is_active": booth.is_active,
            "config": booth.config,
            "created_at": booth.created_at,
            "last_active_at": booth.last_active_at,
            "current_session_id": str(booth.current_session_id)
            if booth.current_session_id
            else None,
        }
        for booth in booths
    ]


@router.post(
    "/booths", response_model=BoothResponse, status_code=status.HTTP_201_CREATED
)
async def create_booth(
    booth_data: BoothCreate,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new booth (admin only)."""
    booth = await BoothService.create_booth(db, booth_data)
    return {
        "id": str(booth.id),
        "name": booth.name,
        "location": booth.location,
        "device_id": booth.device_id,
        "is_active": booth.is_active,
        "config": booth.config,
        "created_at": booth.created_at,
        "last_active_at": booth.last_active_at,
        "current_session_id": str(booth.current_session_id)
        if booth.current_session_id
        else None,
    }


@router.get("/booths/{booth_id}", response_model=BoothResponse)
async def get_booth(
    booth_id: str,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get booth by ID (admin only)."""
    booth = await BoothService.get_booth_by_id(db, booth_id)

    if not booth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booth not found"
        )

    return {
        "id": str(booth.id),
        "name": booth.name,
        "location": booth.location,
        "device_id": booth.device_id,
        "is_active": booth.is_active,
        "config": booth.config,
        "created_at": booth.created_at,
        "last_active_at": booth.last_active_at,
        "current_session_id": str(booth.current_session_id)
        if booth.current_session_id
        else None,
    }


@router.put("/booths/{booth_id}", response_model=BoothResponse)
async def update_booth(
    booth_id: str,
    booth_data: BoothUpdate,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update booth (admin only)."""
    booth = await BoothService.update_booth(db, booth_id, booth_data)

    if not booth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booth not found"
        )

    return {
        "id": str(booth.id),
        "name": booth.name,
        "location": booth.location,
        "device_id": booth.device_id,
        "is_active": booth.is_active,
        "config": booth.config,
        "created_at": booth.created_at,
        "last_active_at": booth.last_active_at,
        "current_session_id": str(booth.current_session_id)
        if booth.current_session_id
        else None,
    }


@router.put("/booths/{booth_id}/config", response_model=BoothResponse)
async def update_booth_config(
    booth_id: str,
    config_data: BoothConfigUpdate,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update booth configuration (admin only)."""
    booth = await BoothService.update_booth_config(db, booth_id, config_data)

    if not booth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booth not found"
        )

    return {
        "id": str(booth.id),
        "name": booth.name,
        "location": booth.location,
        "device_id": booth.device_id,
        "is_active": booth.is_active,
        "config": booth.config,
        "created_at": booth.created_at,
        "last_active_at": booth.last_active_at,
        "current_session_id": str(booth.current_session_id)
        if booth.current_session_id
        else None,
    }


@router.post("/booths/{booth_id}/assign", response_model=BoothResponse)
async def assign_device_to_booth(
    booth_id: str,
    assign_data: BoothAssignDevice,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Assign a device to a booth (admin only)."""
    booth = await BoothService.assign_device_to_booth(
        db, booth_id, assign_data.device_id
    )

    if not booth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booth or device not found"
        )

    return {
        "id": str(booth.id),
        "name": booth.name,
        "location": booth.location,
        "device_id": booth.device_id,
        "is_active": booth.is_active,
        "config": booth.config,
        "created_at": booth.created_at,
        "last_active_at": booth.last_active_at,
        "current_session_id": str(booth.current_session_id)
        if booth.current_session_id
        else None,
    }


@router.post("/booths/{booth_id}/unassign", response_model=BoothResponse)
async def unassign_device(
    booth_id: str,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Unassign device from booth (admin only)."""
    booth = await BoothService.unassign_device(db, booth_id)

    if not booth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booth not found"
        )

    return {
        "id": str(booth.id),
        "name": booth.name,
        "location": booth.location,
        "device_id": booth.device_id,
        "is_active": booth.is_active,
        "config": booth.config,
        "created_at": booth.created_at,
        "last_active_at": booth.last_active_at,
        "current_session_id": str(booth.current_session_id)
        if booth.current_session_id
        else None,
    }


@router.delete("/booths/{booth_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booth(
    booth_id: str,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete booth (admin only)."""
    success = await BoothService.delete_booth(db, booth_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booth not found"
        )


@router.post("/devices/{device_id}/kick")
async def kick_device(
    device_id: str,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Kick a device from its session (admin only)."""
    success = await AuthService.kick_device(db, device_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Device not found"
        )

    return {"message": "Device kicked successfully", "device_id": device_id}


@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_token(admin: dict = Depends(get_current_admin)):
    """Verify admin token validity."""
    return {
        "valid": True,
        "admin_id": admin.get("admin_id"),
        "username": admin.get("username"),
        "role": admin.get("role"),
    }


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    booth_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all transactions with optional filters (admin only)."""
    transactions = await TransactionService.get_transactions(
        db, booth_id=booth_id, status=status, start_date=start_date, end_date=end_date
    )
    return transactions
