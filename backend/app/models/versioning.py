from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.models.base import BaseModel

class ConfigurationVersion(BaseModel):
    __tablename__ = "configuration_versions"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    version_tag = Column(String(50), nullable=False)
    snapshot_json = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)

    workspace = relationship("Workspace", back_populates="configuration_versions")
