import uuid
from typing import List
from fastapi import APIRouter, HTTPException

from shared.schemas import Profile
from db.store import save_profile, load_profile, list_profiles, write_audit

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("", response_model=Profile, status_code=201)
@router.post("/", response_model=Profile, status_code=201, include_in_schema=False)
def create_profile(profile: Profile):
    """
    Create a new profile.
    Validates input using the Profile model and writes an audit log entry.
    """
    profile_data = profile.model_dump()
    if not profile_data.get("profile_id"):
        profile_data["profile_id"] = str(uuid.uuid4())

    saved = save_profile(profile_data)

    write_audit(
        action="create_profile",
        details={
            "name": profile.name,
            "email": profile.email,
            "skills_count": len(profile.skills),
        },
        entity_id=saved["profile_id"],
        entity_type="profile",
    )

    return saved


@router.get("", response_model=List[Profile])
@router.get("/", response_model=List[Profile], include_in_schema=False)
def get_all_profiles():
    """List all stored profiles."""
    return list_profiles()


@router.get("/{profile_id}", response_model=Profile)
def get_profile(profile_id: str):
    """
    Retrieve a profile by profile_id.
    Returns 404 if not found.
    """
    profile = load_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Profile with id '{profile_id}' not found",
        )
    return profile


@router.put("/{profile_id}", response_model=Profile)
def update_profile(profile_id: str, profile_update: Profile):
    """
    Update an existing profile by profile_id.
    Validates input using the Profile model and writes an audit log entry.
    """
    existing = load_profile(profile_id)
    if not existing:
        raise HTTPException(
            status_code=404,
            detail=f"Profile with id '{profile_id}' not found",
        )

    update_data = profile_update.model_dump()
    update_data["profile_id"] = profile_id

    saved = save_profile(update_data)

    write_audit(
        action="update_profile",
        details={
            "name": profile_update.name,
            "email": profile_update.email,
            "skills_count": len(profile_update.skills),
        },
        entity_id=profile_id,
        entity_type="profile",
    )

    return saved
