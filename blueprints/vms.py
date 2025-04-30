"""
VMs blueprint for managing virtual machine requests.
Includes routes for listing, creating, editing, and viewing VM details.
"""
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from models import VM, VMHistory, User, VLAN
from forms import VMRequestForm, VMUpdateForm, VMApprovalForm, VLANForm

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
vms = Blueprint('vms', __name__, url_prefix='/vms')

@vms.route('/')
@login_required
def list_vms():
    """Display a list of VM requests with search functionality."""
    search_term = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    # Build query based on user role and search term
    query = VM.query
    
    # Filter by role (admin sees all, users see only their own)
    if current_user.role != 'admin':
        query = query.filter_by(requestor_id=current_user.id)
    
    # Apply search filter if provided
    if search_term:
        search = f"%{search_term}%"
        query = query.filter(or_(
            VM.name.ilike(search),
            VM.requestor_name.ilike(search),
            VM.operating_system.ilike(search),
            VM.status.ilike(search)
        ))
    
    # Execute query with pagination
    vms = query.order_by(VM.created_at.desc()).paginate(page=page, per_page=10)
    
    logger.debug(f"Listing VMs for user {current_user.username} with search term: '{search_term}'")
    return render_template('vms/list.html', vms=vms, search_term=search_term)

@vms.route('/new', methods=['GET', 'POST'])
@login_required
def new_vm():
    """Create a new VM request."""
    form = VMRequestForm()
    
    # Populate the VLANs field with choices from the database
    form.vlans.choices = [(vlan.id, vlan.name) for vlan in VLAN.query.all()]
    
    if form.validate_on_submit():
        # Create new VM object
        vm = VM(
            name=form.name.data,
            requestor_name=form.requestor_name.data,
            requestor_email=form.requestor_email.data,
            primary_admin_name=form.primary_admin_name.data,
            primary_admin_email=form.primary_admin_email.data,
            secondary_admin_name=form.secondary_admin_name.data,
            secondary_admin_email=form.secondary_admin_email.data,
            cpu_count=form.cpu_count.data,
            ram_gb=form.ram_gb.data,
            disk_gb=form.disk_gb.data,
            physical_location=form.physical_location.data,
            virtual_host=form.virtual_host.data,
            operating_system=form.operating_system.data,
            backup_required=form.backup_required.data,
            backup_frequency=form.backup_frequency.data,
            notes=form.notes.data,
            status='Pending',
            requestor_id=current_user.id
        )
        
        # Add selected VLANs
        if form.vlans.data:
            selected_vlans = VLAN.query.filter(VLAN.id.in_(form.vlans.data)).all()
            vm.vlans = selected_vlans
        
        # Save to database
        db.session.add(vm)
        db.session.commit()
        
        logger.info(f"New VM request created: {vm.name} by {current_user.username}")
        flash(f'VM request "{vm.name}" has been submitted successfully!', 'success')
        return redirect(url_for('vms.list_vms'))
    
    return render_template('vms/new.html', form=form)

@vms.route('/<int:vm_id>')
@login_required
def view_vm(vm_id):
    """Display detailed information about a VM."""
    vm = VM.query.get_or_404(vm_id)
    
    # Check if user has permission to view this VM
    if current_user.role != 'admin' and vm.requestor_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to access unauthorized VM: {vm.id}")
        abort(403)
    
    # Get the history of changes
    history = VMHistory.query.filter_by(vm_id=vm.id).order_by(VMHistory.timestamp.desc()).all()
    
    logger.debug(f"Viewing VM details for VM ID: {vm_id}")
    return render_template('vms/detail.html', vm=vm, history=history)

@vms.route('/<int:vm_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vm(vm_id):
    """Edit an existing VM request."""
    vm = VM.query.get_or_404(vm_id)
    
    # Check if user has permission to edit this VM
    if current_user.role != 'admin' and vm.requestor_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to edit unauthorized VM: {vm.id}")
        abort(403)
    
    # Create form and populate with VM data
    form = VMUpdateForm(obj=vm)
    
    # Populate the VLANs field with choices and selected values
    form.vlans.choices = [(vlan.id, vlan.name) for vlan in VLAN.query.all()]
    
    # Only admins can change status
    if current_user.role != 'admin':
        del form.status
    
    if form.validate_on_submit():
        # Track changes for history
        changes = []
        
        # Check for changes in each field
        for field in form:
            if field.name in ['submit', 'csrf_token']:
                continue
            
            # Handle special case for VLANs
            if field.name == 'vlans':
                old_vlans = set(vlan.id for vlan in vm.vlans)
                new_vlans = set(form.vlans.data) if form.vlans.data else set()
                
                if old_vlans != new_vlans:
                    # Safe retrieval of VLAN names
                    old_vlan_names = []
                    for vlan_id in old_vlans:
                        vlan = VLAN.query.get(vlan_id)
                        if vlan:
                            old_vlan_names.append(vlan.name)
                    
                    new_vlan_names = []
                    for vlan_id in new_vlans:
                        vlan = VLAN.query.get(vlan_id)
                        if vlan:
                            new_vlan_names.append(vlan.name)
                    
                    changes.append({
                        'field': 'vlans',
                        'old_value': ', '.join(old_vlan_names),
                        'new_value': ', '.join(new_vlan_names)
                    })
            else:
                old_value = getattr(vm, field.name)
                if old_value != field.data:
                    changes.append({
                        'field': field.name,
                        'old_value': str(old_value),
                        'new_value': str(field.data)
                    })
        
        # Save original VLANs data to update separately
        vlans_data = form.vlans.data
        
        # Remove vlans from form to prevent populate_obj from trying to set them directly
        form.vlans.data = []
        
        # Update VM object from form data (except VLANs)
        form.populate_obj(vm)
        
        # Update VLANs relationship separately
        if vlans_data:
            selected_vlans = VLAN.query.filter(VLAN.id.in_(vlans_data)).all()
            vm.vlans = selected_vlans
        else:
            vm.vlans = []
        
        # Update timestamp
        vm.updated_at = datetime.utcnow()
        
        # If status changed to Approved or Rejected, update approver
        if current_user.role == 'admin' and form.status.data in ['Approved', 'Rejected']:
            vm.approver_id = current_user.id
        
        # Save history records
        for change in changes:
            history = VMHistory(
                vm_id=vm.id,
                changed_field=change['field'],
                old_value=change['old_value'],
                new_value=change['new_value'],
                user_id=current_user.id
            )
            db.session.add(history)
        
        # Save changes
        db.session.commit()
        
        logger.info(f"VM {vm.name} updated by {current_user.username} with {len(changes)} changes")
        flash(f'VM "{vm.name}" has been updated successfully!', 'success')
        return redirect(url_for('vms.view_vm', vm_id=vm.id))
    
    # For GET request, populate VLANs with current values
    if request.method == 'GET':
        form.vlans.data = [vlan.id for vlan in vm.vlans]
    
    return render_template('vms/edit.html', form=form, vm=vm)

@vms.route('/<int:vm_id>/approval', methods=['GET', 'POST'])
@login_required
def approve_vm(vm_id):
    """Approve or reject a VM request (admin only)."""
    if current_user.role != 'admin':
        logger.warning(f"Non-admin user {current_user.username} attempted to access approval page")
        abort(403)
    
    vm = VM.query.get_or_404(vm_id)
    form = VMApprovalForm(obj=vm)
    
    if form.validate_on_submit():
        old_status = vm.status
        vm.status = form.status.data
        
        # If notes were provided, update them
        if form.notes.data:
            if vm.notes:
                vm.notes = vm.notes + "\n\n" + f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] {current_user.username}: " + form.notes.data
            else:
                vm.notes = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] {current_user.username}: " + form.notes.data
        
        # Update approver information
        vm.approver_id = current_user.id
        vm.updated_at = datetime.utcnow()
        
        # Create history record for status change
        if old_status != vm.status:
            history = VMHistory(
                vm_id=vm.id,
                changed_field='status',
                old_value=old_status,
                new_value=vm.status,
                user_id=current_user.id
            )
            db.session.add(history)
        
        db.session.commit()
        
        logger.info(f"VM {vm.name} status changed from {old_status} to {vm.status} by admin {current_user.username}")
        flash(f'VM "{vm.name}" status updated to {vm.status}!', 'success')
        return redirect(url_for('vms.list_vms'))
    
    return render_template('vms/approval.html', form=form, vm=vm)

@vms.route('/<int:vm_id>/delete', methods=['POST'])
@login_required
def delete_vm(vm_id):
    """Delete a VM request (admin only)."""
    if current_user.role != 'admin':
        logger.warning(f"Non-admin user {current_user.username} attempted to delete VM")
        abort(403)
    
    vm = VM.query.get_or_404(vm_id)
    vm_name = vm.name
    
    db.session.delete(vm)
    db.session.commit()
    
    logger.info(f"VM {vm_name} deleted by admin {current_user.username}")
    flash(f'VM "{vm_name}" has been deleted!', 'warning')
    return redirect(url_for('vms.list_vms'))

@vms.route('/vlan/add', methods=['POST'])
@login_required
def add_vlan():
    """Add a new VLAN from the VM form."""
    # This is a special AJAX endpoint, we don't need CSRF protection here
    # as it's being called from our form which already has CSRF protection
    
    # Get form data
    name = request.form.get('name')
    description = request.form.get('description', '')
    
    if not name:
        return jsonify({'error': 'VLAN name is required'}), 400
    
    # Check if VLAN with this name already exists
    existing_vlan = VLAN.query.filter_by(name=name).first()
    if existing_vlan:
        return jsonify({'error': 'VLAN with this name already exists'}), 400
    
    try:
        # Create new VLAN
        vlan = VLAN(name=name, description=description)
        db.session.add(vlan)
        db.session.commit()
        
        logger.info(f"New VLAN {name} added by {current_user.username}")
        
        # Return the new VLAN info
        return jsonify({
            'id': vlan.id, 
            'name': vlan.name,
            'message': f'VLAN "{name}" added successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding VLAN: {str(e)}")
        return jsonify({'error': 'An error occurred while adding the VLAN'}), 500
