"""
Announcement endpoints for the High School Management System API
"""

from datetime import datetime
from uuid import uuid4
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementPayload(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    expires_on: str
    starts_on: Optional[str] = None


def _validate_date(date_value: str, field_name: str) -> None:
    try:
        datetime.strptime(date_value, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must use YYYY-MM-DD format"
        ) from exc


def _validate_teacher(teacher_username: Optional[str]) -> Dict[str, Any]:
    if not teacher_username:
        raise HTTPException(
            status_code=401,
            detail="Authentication required for this action"
        )

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    return teacher


def _serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": announcement["_id"],
        "message": announcement["message"],
        "starts_on": announcement.get("starts_on"),
        "expires_on": announcement["expires_on"]
    }


@router.get("", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get currently active announcements for public display"""
    today = datetime.utcnow().strftime("%Y-%m-%d")

    query = {
        "expires_on": {"$gte": today},
        "$or": [
            {"starts_on": None},
            {"starts_on": {"$exists": False}},
            {"starts_on": {"$lte": today}}
        ]
    }

    announcements = [
        _serialize_announcement(item)
        for item in announcements_collection.find(query).sort("expires_on", 1)
    ]

    return announcements


@router.get("/all", response_model=List[Dict[str, Any]])
def get_all_announcements(teacher_username: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """Get all announcements for management UI (authenticated users only)"""
    _validate_teacher(teacher_username)

    announcements = [
        _serialize_announcement(item)
        for item in announcements_collection.find({}).sort("expires_on", 1)
    ]

    return announcements


@router.post("", response_model=Dict[str, Any])
def create_announcement(payload: AnnouncementPayload, teacher_username: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Create a new announcement (authenticated users only)"""
    teacher = _validate_teacher(teacher_username)

    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Announcement message is required")

    _validate_date(payload.expires_on, "expires_on")

    if payload.starts_on:
        _validate_date(payload.starts_on, "starts_on")
        if payload.starts_on > payload.expires_on:
            raise HTTPException(
                status_code=400,
                detail="starts_on cannot be after expires_on"
            )

    announcement_id = uuid4().hex
    doc = {
        "_id": announcement_id,
        "message": message,
        "starts_on": payload.starts_on,
        "expires_on": payload.expires_on,
        "created_by": teacher["username"]
    }

    announcements_collection.insert_one(doc)
    return _serialize_announcement(doc)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    payload: AnnouncementPayload,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Update an announcement (authenticated users only)"""
    _validate_teacher(teacher_username)

    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Announcement message is required")

    _validate_date(payload.expires_on, "expires_on")

    if payload.starts_on:
        _validate_date(payload.starts_on, "starts_on")
        if payload.starts_on > payload.expires_on:
            raise HTTPException(
                status_code=400,
                detail="starts_on cannot be after expires_on"
            )

    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {
            "$set": {
                "message": message,
                "starts_on": payload.starts_on,
                "expires_on": payload.expires_on
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    announcement = announcements_collection.find_one({"_id": announcement_id})
    return _serialize_announcement(announcement)


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, teacher_username: Optional[str] = Query(None)) -> Dict[str, str]:
    """Delete an announcement (authenticated users only)"""
    _validate_teacher(teacher_username)

    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}