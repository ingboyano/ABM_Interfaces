from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, SelectField
from wtforms import SubmitField, SelectMultipleField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class VMRequestForm(FlaskForm):
    """Form for creating a new VM request."""
    # VM identification
    name = StringField('VM Name', validators=[DataRequired(), Length(min=3, max=100)])
    
    # Requestor information
    requestor_name = StringField('Requestor Name', validators=[DataRequired(), Length(max=100)])
    requestor_email = EmailField('Requestor Email', validators=[DataRequired(), Email(), Length(max=120)])
    
    # Admin information
    primary_admin_name = StringField('Primary Admin Name', validators=[DataRequired(), Length(max=100)])
    primary_admin_email = EmailField('Primary Admin Email', validators=[DataRequired(), Email(), Length(max=120)])
    secondary_admin_name = StringField('Secondary Admin Name', validators=[Optional(), Length(max=100)])
    secondary_admin_email = EmailField('Secondary Admin Email', validators=[Optional(), Email(), Length(max=120)])
    
    # VM specs
    cpu_count = IntegerField('CPUs', validators=[DataRequired(), NumberRange(min=1)])
    ram_gb = IntegerField('RAM (GB)', validators=[DataRequired(), NumberRange(min=1)])
    disk_gb = IntegerField('Disk (GB)', validators=[DataRequired(), NumberRange(min=10)])
    
    # Location information
    physical_location = StringField('Physical Location', validators=[Optional(), Length(max=100)])
    virtual_host = StringField('Virtual Host', validators=[Optional(), Length(max=100)])
    
    # OS information
    operating_system = StringField('Operating System', validators=[DataRequired(), Length(max=100)])
    
    # Backup information
    backup_required = BooleanField('Backup Required')
    backup_frequency = SelectField('Backup Frequency', 
                                  choices=[
                                      ('', 'Select frequency'),
                                      ('daily', 'Daily'),
                                      ('weekly', 'Weekly'),
                                      ('monthly', 'Monthly'),
                                      ('none', 'No Backup')
                                  ])
    
    # VLANs - will be populated dynamically
    vlans = SelectMultipleField('VLANs', coerce=int)
    
    # Additional information
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    
    # Submit button
    submit = SubmitField('Submit VM Request')

class VMUpdateForm(VMRequestForm):
    """Form for updating an existing VM, inherits from VMRequestForm."""
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'), 
        ('Approved', 'Approved'), 
        ('Rejected', 'Rejected'), 
        ('Active', 'Active')
    ])
    submit = SubmitField('Update VM')

class VMApprovalForm(FlaskForm):
    """Form for approving or rejecting VM requests."""
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'), 
        ('Approved', 'Approved'), 
        ('Rejected', 'Rejected'), 
        ('Active', 'Active')
    ])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Update Status')

class VLANForm(FlaskForm):
    """Form for managing VLANs."""
    name = StringField('VLAN Name', validators=[DataRequired(), Length(max=50)])
    description = StringField('Description', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Add VLAN')
