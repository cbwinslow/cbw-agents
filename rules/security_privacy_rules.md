# Security & Privacy Rules

**Priority**: 🔒 Critical (Must Follow)

These rules are **mandatory** and violations may result in security breaches or system compromise.

## Overview

Security and privacy are paramount in AI agent operations. These rules protect sensitive data, prevent unauthorized access, and ensure compliance with security best practices.

## Core Principles

1. **Principle of Least Privilege**: Only access what is necessary
2. **Defense in Depth**: Multiple layers of security
3. **Fail Secure**: Default to secure state on error
4. **Audit Trail**: Log all security-relevant operations
5. **Zero Trust**: Verify everything, trust nothing

## Rules

### SEC-001: Never Expose Secrets or Credentials

**Description**: Never log, display, or transmit secrets, API keys, passwords, tokens, or other credentials.

**Requirements**:
- Never print credentials to stdout/stderr
- Never log credentials to files
- Never transmit credentials in plain text
- Redact credentials in error messages
- Use environment variables or secure vaults for credentials

**Example - Violation**:
```python
# ❌ NEVER DO THIS
print(f"API Key: {api_key}")
logger.info(f"Connecting with password: {password}")
```

**Example - Correct**:
```python
# ✅ CORRECT
logger.info("Connecting to API...")
# Use environment variable or secure vault
api_key = os.getenv('API_KEY')
if not api_key:
    logger.error("API key not found in environment")
```

### SEC-002: Never Modify SSH Configurations

**Description**: Never modify SSH configurations, keys, or connection parameters.

**Protected Files**:
- `~/.ssh/config`
- `~/.ssh/known_hosts`
- `~/.ssh/id_*` (all key files)
- `/etc/ssh/sshd_config`

**Requirements**:
- Never read SSH private keys
- Never modify SSH configuration files
- Never establish new SSH connections without explicit permission
- Never copy or move SSH keys

**Rationale**: SSH credentials are system-critical and modifications can break connectivity or create security vulnerabilities.

### SEC-003: Never Commit Sensitive Information

**Description**: Never commit secrets, credentials, or sensitive information to version control.

**Protected Information**:
- API keys and tokens
- Passwords and passphrases
- Private keys
- Database connection strings
- Personal identifiable information (PII)
- Internal IP addresses and hostnames

**Requirements**:
- Check for secrets before committing
- Use `.gitignore` for sensitive files
- Use environment variables for configuration
- Implement pre-commit hooks for secret detection

**Tools**:
```bash
# Use git-secrets or similar tools
git secrets --scan
```

### SEC-004: Never Disable Security Features

**Description**: Never disable authentication, authorization, encryption, or other security mechanisms.

**Prohibited Actions**:
- Disabling SSL/TLS verification
- Removing authentication checks
- Bypassing authorization
- Disabling firewall rules
- Removing security headers

**Example - Violation**:
```python
# ❌ NEVER DO THIS
requests.get(url, verify=False)  # Disables SSL verification
```

**Example - Correct**:
```python
# ✅ CORRECT
try:
    response = requests.get(url, verify=True, timeout=30)
except requests.exceptions.SSLError as e:
    logger.error(f"SSL verification failed: {e}")
    # Handle error appropriately
```

### SEC-005: Always Validate and Sanitize Inputs

**Description**: Validate and sanitize all user inputs to prevent injection attacks.

**Requirements**:
- Validate input types and formats
- Sanitize inputs before use in commands
- Use parameterized queries for databases
- Escape special characters in shell commands
- Limit input length and complexity

**Example - Correct**:
```python
# ✅ CORRECT
import re
from pathlib import Path

def validate_filename(filename: str) -> bool:
    """Validate filename to prevent path traversal."""
    # Only allow alphanumeric, dash, underscore, and dot
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        return False
    # Prevent path traversal
    if '..' in filename or filename.startswith('/'):
        return False
    return True

def safe_file_operation(filename: str):
    if not validate_filename(filename):
        raise ValueError("Invalid filename")
    # Proceed with operation
```

### SEC-006: Never Access Files Outside Authorized Scope

**Description**: Only access files within authorized directories and never traverse outside defined boundaries.

**Requirements**:
- Validate all file paths
- Prevent path traversal attacks
- Use absolute paths or resolve paths safely
- Check permissions before access
- Log all file access attempts

**Protected Paths**:
- `/etc/` (system configuration)
- `/root/` (root user home)
- `~/.ssh/` (SSH keys)
- `~/.gnupg/` (GPG keys)
- `/proc/` (system processes)
- `/sys/` (system information)

**Example - Correct**:
```python
# ✅ CORRECT
from pathlib import Path

def safe_read_file(filename: str, base_dir: str = "/workspace"):
    """Safely read file within authorized directory."""
    base_path = Path(base_dir).resolve()
    file_path = (base_path / filename).resolve()
    
    # Ensure file is within base directory
    if not str(file_path).startswith(str(base_path)):
        raise ValueError("Access denied: Path traversal detected")
    
    # Check if file exists and is readable
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File not found: {filename}")
    
    return file_path.read_text()
```

## Access Control

### File System Access

**Allowed**:
- Project workspace directories
- Designated output directories
- Temporary directories (`/tmp`)

**Requires Permission**:
- User home directory files
- System configuration files
- Log directories

**Forbidden**:
- SSH configuration and keys
- System binaries and libraries
- Other users' home directories
- Sensitive system files

### Network Access

**Allowed**:
- HTTP/HTTPS requests to public APIs
- Documented service endpoints

**Requires Permission**:
- Internal network resources
- Database connections
- Message queue connections

**Forbidden**:
- Port scanning
- Network reconnaissance
- Unauthorized protocol usage

## Data Protection

### Personal Information

**Requirements**:
- Minimize collection of PII
- Encrypt PII at rest and in transit
- Implement data retention policies
- Provide data deletion capabilities
- Comply with privacy regulations (GDPR, CCPA)

### Data Classification

1. **Public**: Can be freely shared
2. **Internal**: For organization use only
3. **Confidential**: Restricted access
4. **Secret**: Highly restricted, encrypted

**Handling Requirements**:
- Label data according to classification
- Apply appropriate access controls
- Encrypt confidential and secret data
- Log access to sensitive data

## Encryption

### Data in Transit

**Requirements**:
- Use TLS 1.2 or higher
- Verify SSL certificates
- Use strong cipher suites
- Implement certificate pinning where appropriate

### Data at Rest

**Requirements**:
- Encrypt sensitive data at rest
- Use strong encryption algorithms (AES-256)
- Secure key management
- Rotate encryption keys regularly

## Authentication & Authorization

### Authentication

**Requirements**:
- Use multi-factor authentication where available
- Never store passwords in plain text
- Use secure password hashing (bcrypt, Argon2)
- Implement session timeout
- Protect against brute force attacks

### Authorization

**Requirements**:
- Implement role-based access control (RBAC)
- Follow principle of least privilege
- Validate permissions for every action
- Log authorization failures
- Implement resource-level permissions

## Audit Logging

### What to Log

**Required**:
- Authentication attempts (success and failure)
- Authorization decisions
- Data access and modifications
- Configuration changes
- Security events

**Format**:
```json
{
    "timestamp": "2025-12-08T12:00:00Z",
    "event_type": "file_access",
    "agent_id": "agent-001",
    "resource": "/workspace/file.txt",
    "action": "read",
    "result": "success",
    "ip_address": "redacted"
}
```

### Log Protection

**Requirements**:
- Protect logs from tampering
- Implement log rotation
- Secure log storage
- Retain logs per compliance requirements
- Redact sensitive information in logs

## Incident Response

### Detection

**Monitor for**:
- Unusual access patterns
- Failed authentication attempts
- Authorization violations
- Data exfiltration attempts
- System anomalies

### Response

**Actions**:
1. Log the incident with full context
2. Alert security team if available
3. Isolate affected systems if necessary
4. Preserve evidence
5. Document incident timeline
6. Implement corrective measures

## Compliance Checks

### Pre-Operation Checklist

- [ ] No hardcoded credentials
- [ ] Input validation implemented
- [ ] Output sanitization applied
- [ ] Access controls verified
- [ ] Audit logging enabled
- [ ] Error handling doesn't leak sensitive info
- [ ] SSL/TLS verification enabled
- [ ] File paths validated and confined

### Regular Audits

**Frequency**: Weekly or after significant changes

**Areas to Audit**:
- Credential storage and usage
- File access patterns
- Network communication
- Error logs for information leakage
- Access control effectiveness

## Security Tools

### Recommended Tools

```bash
# Secret scanning
git secrets --scan

# Dependency vulnerability scanning
pip-audit

# Static security analysis
bandit -r .

# SSL/TLS testing
nmap --script ssl-enum-ciphers
```

## Violation Response

### Automatic Actions

When a security rule is violated:
1. **Block the operation** immediately
2. **Log the violation** with full context
3. **Alert** operators if configured
4. **Report** to user with guidance

### Example Alert

```
🚫 SECURITY VIOLATION DETECTED
Rule: SEC-002 (SSH Configuration Protection)
Action: Blocked attempt to modify ~/.ssh/config
Agent: agent-code-001
Timestamp: 2025-12-08T12:00:00Z
Recommendation: SSH configurations require explicit user authorization
```

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Version**: 2.0.0  
**Last Updated**: 2025-12-08  
**Priority**: 🔒 Critical  
**Compliance**: Mandatory
