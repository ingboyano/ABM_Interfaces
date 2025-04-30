from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app import db

# User model for authentication
class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False, default='user')  # 'admin' or 'user'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to VM requests created by this user
    vm_requests = relationship('VM', foreign_keys='VM.requestor_id', backref='requestor_user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Many-to-many relationship table for VMs and VLANs
vm_vlan = Table(
    'vm_vlan',
    db.Model.metadata,
    Column('vm_id', Integer, ForeignKey('vms.id')),
    Column('vlan_id', Integer, ForeignKey('vlans.id'))
)

# VLAN model
class VLAN(db.Model):
    """VLAN model to store network information."""
    __tablename__ = 'vlans'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    
    def __repr__(self):
        return f'<VLAN {self.name}>'

# VM model for VM requests
class VM(db.Model):
    """Virtual Machine model to store VM request information."""
    __tablename__ = 'vms'
    
    id = Column(Integer, primary_key=True)
    
    # VM details
    name = Column(String(100), nullable=False)
    requestor_name = Column(String(100), nullable=False)
    requestor_email = Column(String(120), nullable=False)
    primary_admin_name = Column(String(100), nullable=False)
    primary_admin_email = Column(String(120), nullable=False)
    secondary_admin_name = Column(String(100))
    secondary_admin_email = Column(String(120))
    
    # VM specifications
    cpu_count = Column(Integer, nullable=False)
    ram_gb = Column(Integer, nullable=False)
    disk_gb = Column(Integer, nullable=False)
    physical_location = Column(String(100))
    virtual_host = Column(String(100))
    operating_system = Column(String(100), nullable=False)
    
    # Backup information
    backup_required = Column(Boolean, default=False)
    backup_frequency = Column(String(50))
    
    # Notes and status
    notes = Column(Text)
    status = Column(String(20), default='Pending')  # Pending, Approved, Rejected, Active
    
    # Timestamps and user relations
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    requestor_id = Column(Integer, ForeignKey('users.id'))
    approver_id = Column(Integer, ForeignKey('users.id'))
    
    # Relations
    approver = relationship('User', foreign_keys=[approver_id], backref='approved_vms')
    vlans = relationship('VLAN', secondary=vm_vlan, backref='vms')
    history = relationship('VMHistory', backref='vm', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<VM {self.name} ({self.status})>'

# VM History model for versioning
class VMHistory(db.Model):
    """VM History model to track changes to VM requests."""
    __tablename__ = 'vm_history'
    
    id = Column(Integer, primary_key=True)
    vm_id = Column(Integer, ForeignKey('vms.id'), nullable=False)
    
    # What changed
    changed_field = Column(String(100), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    
    # Who made the change
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', foreign_keys=[user_id])
    
    # When the change was made
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VMHistory {self.vm_id} {self.changed_field}>'
