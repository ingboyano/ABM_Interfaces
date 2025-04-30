-- Drop tables if they exist
DROP TABLE IF EXISTS vm_history;
DROP TABLE IF EXISTS vm_vlan;
DROP TABLE IF EXISTS vms;
DROP TABLE IF EXISTS vlans;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create VLANs table
CREATE TABLE vlans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(200)
);

-- Create VMs table
CREATE TABLE vms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    requestor_name VARCHAR(100) NOT NULL,
    requestor_email VARCHAR(120) NOT NULL,
    primary_admin_name VARCHAR(100) NOT NULL,
    primary_admin_email VARCHAR(120) NOT NULL,
    secondary_admin_name VARCHAR(100),
    secondary_admin_email VARCHAR(120),
    cpu_count INTEGER NOT NULL,
    ram_gb INTEGER NOT NULL,
    disk_gb INTEGER NOT NULL,
    physical_location VARCHAR(100),
    virtual_host VARCHAR(100),
    operating_system VARCHAR(100) NOT NULL,
    backup_required BOOLEAN DEFAULT FALSE,
    backup_frequency VARCHAR(50),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    requestor_id INTEGER REFERENCES users(id),
    approver_id INTEGER REFERENCES users(id)
);

-- Create junction table for VM-VLAN many-to-many relationship
CREATE TABLE vm_vlan (
    vm_id INTEGER REFERENCES vms(id) ON DELETE CASCADE,
    vlan_id INTEGER REFERENCES vlans(id) ON DELETE CASCADE,
    PRIMARY KEY (vm_id, vlan_id)
);

-- Create VM history table for versioning
CREATE TABLE vm_history (
    id SERIAL PRIMARY KEY,
    vm_id INTEGER NOT NULL REFERENCES vms(id) ON DELETE CASCADE,
    changed_field VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create admin user
INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@example.com', 
        -- This is a bcrypt hash for 'SvaTecnica1'
        '$2b$12$CJEhWLnPjQC3OpBPUeCAReG5soxTvwhKAgQ54AQFfIm2JMtx8gRx6',
        'admin');

-- Insert some default VLANs
INSERT INTO vlans (name, description) VALUES 
    ('VLAN10', 'Development network'),
    ('VLAN20', 'Testing network'),
    ('VLAN30', 'Production network'),
    ('VLAN40', 'Management network'),
    ('VLAN50', 'Backup network');
