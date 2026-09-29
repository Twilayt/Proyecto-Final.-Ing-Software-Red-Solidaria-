"""Registro y administración de perfiles de personas donantes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import DonorProfile, DonorStatus, Role, User
from app.schemas import DonorCreate, DonorOut, DonorStatusUpdate

router = APIRouter(prefix="/donors", tags=["Donantes"])


@router.post("", response_model=DonorOut, status_code=status.HTTP_201_CREATED)
def create_donor_profile(
    payload: DonorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DonorProfile:
    donor = DonorProfile(owner_id=current_user.id, **payload.model_dump())
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


@router.get("/me", response_model=list[DonorOut])
def list_my_profiles(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[DonorProfile]:
    return list(
        db.scalars(
            select(DonorProfile)
            .where(DonorProfile.owner_id == current_user.id)
            .order_by(DonorProfile.id.desc())
        )
    )


@router.get("", response_model=list[DonorOut])
def list_all_profiles(
    profile_status: DonorStatus | None = Query(default=None, alias="status"),
    _: User = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
) -> list[DonorProfile]:
    query = select(DonorProfile).order_by(DonorProfile.id.desc())
    if profile_status:
        query = query.where(DonorProfile.status == profile_status)
    return list(db.scalars(query))


def get_profile_or_404(profile_id: int, db: Session) -> DonorProfile:
    profile = db.get(DonorProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Perfil de donante no encontrado")
    return profile


@router.get("/{profile_id}", response_model=DonorOut)
def read_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DonorProfile:
    profile = get_profile_or_404(profile_id, db)
    if current_user.role != Role.ADMIN and profile.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes consultar este perfil")
    return profile


@router.patch("/{profile_id}/status", response_model=DonorOut)
def update_profile_status(
    profile_id: int,
    payload: DonorStatusUpdate,
    _: User = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
) -> DonorProfile:
    profile = get_profile_or_404(profile_id, db)
    profile.status = payload.status
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    profile = get_profile_or_404(profile_id, db)
    if current_user.role != Role.ADMIN and profile.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar este perfil")
    db.delete(profile)
    db.commit()

