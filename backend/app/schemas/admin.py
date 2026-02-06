"""
Schemas para administración.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class UserListItem(BaseModel):
    """Item en lista de usuarios."""
    id: int
    email: str
    is_admin: bool
    is_blocked: bool
    email_verified: bool
    created_at: datetime
    plan: str
    device_count: int
    abuse_events: int


class UserListResponse(BaseModel):
    """Respuesta de lista de usuarios."""
    users: List[UserListItem]
    total: int
    skip: int
    limit: int


class DeviceInfo(BaseModel):
    """Información de dispositivo."""
    id: int
    fingerprint_hash: str
    platform: Optional[str]
    first_seen: datetime
    last_seen: datetime
    login_count: int


class AbuseEventInfo(BaseModel):
    """Información de evento de abuso."""
    id: int
    event_type: str
    severity: str
    description: Optional[str]
    created_at: datetime


class OAuthIdentityInfo(BaseModel):
    """Información de identidad OAuth."""
    provider: str
    provider_email: Optional[str]
    created_at: datetime
    last_login: datetime


class PlanInfo(BaseModel):
    """Información del plan."""
    id: int
    name: str
    display_name: str
    price_usd: float
    started_at: datetime


class AbuseScoreInfo(BaseModel):
    """Información de score de abuso."""
    score: int
    flags: List[str]
    risk_level: str


class UserDetailResponse(BaseModel):
    """Respuesta detallada de usuario."""
    id: int
    email: str
    is_admin: bool
    is_blocked: bool
    blocked_reason: Optional[str]
    blocked_at: Optional[datetime]
    email_verified: bool
    created_at: datetime
    plan: Optional[PlanInfo]
    devices: List[DeviceInfo]
    abuse_events: List[AbuseEventInfo]
    abuse_score: AbuseScoreInfo
    oauth_identities: List[OAuthIdentityInfo]


class BlockUserRequest(BaseModel):
    """Request para bloquear usuario."""
    reason: str


class ChangePlanRequest(BaseModel):
    """Request para cambiar plan."""
    plan_name: str


class SystemMetricsResponse(BaseModel):
    """Respuesta de métricas del sistema."""
    total_users: int
    active_users_7d: int
    blocked_users: int
    new_users_30d: int
    plan_distribution: dict
    conversion_rate: float
    abuse_events_30d: int
    abuse_by_severity: dict