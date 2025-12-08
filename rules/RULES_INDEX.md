# Rules Index - Quick Reference

Complete index of all AI agent rules organized by category and priority.

## 🔒 Critical Priority Rules

### Security & Privacy Rules
| Rule ID | Description | File |
|---------|-------------|------|
| SEC-001 | Never expose secrets, API keys, or credentials | [security_privacy_rules.md](security_privacy_rules.md) |
| SEC-002 | Never modify SSH configurations or keys | [security_privacy_rules.md](security_privacy_rules.md) |
| SEC-003 | Never commit sensitive information to version control | [security_privacy_rules.md](security_privacy_rules.md) |
| SEC-004 | Never disable security features or authentication | [security_privacy_rules.md](security_privacy_rules.md) |
| SEC-005 | Always validate and sanitize user inputs | [security_privacy_rules.md](security_privacy_rules.md) |
| SEC-006 | Never access files outside authorized scope | [security_privacy_rules.md](security_privacy_rules.md) |

### Memory Management Rules
| Rule ID | Description | File |
|---------|-------------|------|
| MEM-001 | Always release allocated resources | [memory_management_rules.md](memory_management_rules.md) |
| MEM-002 | Monitor memory usage continuously | [memory_management_rules.md](memory_management_rules.md) |
| MEM-003 | Implement cleanup in error paths | [memory_management_rules.md](memory_management_rules.md) |
| MEM-004 | Use context managers for resource handling | [memory_management_rules.md](memory_management_rules.md) |
| MEM-005 | Limit long-term memory storage | [memory_management_rules.md](memory_management_rules.md) |
| MEM-006 | Implement memory archival strategies | [memory_management_rules.md](memory_management_rules.md) |

## ⚡ High Priority Rules

### Code Quality Rules
| Rule ID | Description | File |
|---------|-------------|------|
| CODE-001 | Write comprehensive tests for all code | [code_quality_rules.md](code_quality_rules.md) |
| CODE-002 | Follow consistent code style standards | [code_quality_rules.md](code_quality_rules.md) |
| CODE-003 | Document all public APIs and functions | [code_quality_rules.md](code_quality_rules.md) |
| CODE-004 | Never bypass code review processes | [code_quality_rules.md](code_quality_rules.md) |
| CODE-005 | Run linters and tests before committing | [code_quality_rules.md](code_quality_rules.md) |
| CODE-006 | Keep functions small and focused | [code_quality_rules.md](code_quality_rules.md) |

### Communication Rules
| Rule ID | Description | File |
|---------|-------------|------|
| COMM-001 | Provide clear, concise responses | [communication_rules.md](communication_rules.md) |
| COMM-002 | Always acknowledge user requests | [communication_rules.md](communication_rules.md) |
| COMM-003 | Clarify ambiguous instructions | [communication_rules.md](communication_rules.md) |
| COMM-004 | Report progress on long-running tasks | [communication_rules.md](communication_rules.md) |
| COMM-005 | Use structured formatting for readability | [communication_rules.md](communication_rules.md) |
| COMM-006 | Maintain professional tone | [communication_rules.md](communication_rules.md) |

### Error Handling Rules
| Rule ID | Description | File |
|---------|-------------|------|
| ERR-001 | Never silently ignore errors | [error_handling_rules.md](error_handling_rules.md) |
| ERR-002 | Provide meaningful error messages | [error_handling_rules.md](error_handling_rules.md) |
| ERR-003 | Log all errors with context | [error_handling_rules.md](error_handling_rules.md) |
| ERR-004 | Implement retry logic with backoff | [error_handling_rules.md](error_handling_rules.md) |
| ERR-005 | Validate inputs before processing | [error_handling_rules.md](error_handling_rules.md) |
| ERR-006 | Implement graceful degradation | [error_handling_rules.md](error_handling_rules.md) |

### Testing & Quality Rules
| Rule ID | Description | File |
|---------|-------------|------|
| TEST-001 | Achieve minimum 80% code coverage | [testing_quality_rules.md](testing_quality_rules.md) |
| TEST-002 | Write unit tests for all functions | [testing_quality_rules.md](testing_quality_rules.md) |
| TEST-003 | Include integration tests for workflows | [testing_quality_rules.md](testing_quality_rules.md) |
| TEST-004 | Test error conditions and edge cases | [testing_quality_rules.md](testing_quality_rules.md) |
| TEST-005 | Automate test execution in CI/CD | [testing_quality_rules.md](testing_quality_rules.md) |
| TEST-006 | Keep tests independent and deterministic | [testing_quality_rules.md](testing_quality_rules.md) |

## 🚀 Medium Priority Rules

### Performance Rules
| Rule ID | Description | File |
|---------|-------------|------|
| PERF-001 | Optimize response time for user operations | [performance_rules.md](performance_rules.md) |
| PERF-002 | Implement caching for repeated operations | [performance_rules.md](performance_rules.md) |
| PERF-003 | Use async operations for I/O-bound tasks | [performance_rules.md](performance_rules.md) |
| PERF-004 | Monitor and limit resource consumption | [performance_rules.md](performance_rules.md) |
| PERF-005 | Implement pagination for large datasets | [performance_rules.md](performance_rules.md) |
| PERF-006 | Profile and optimize hot paths | [performance_rules.md](performance_rules.md) |

### Documentation Rules
| Rule ID | Description | File |
|---------|-------------|------|
| DOC-001 | Document all public APIs with examples | [documentation_rules.md](documentation_rules.md) |
| DOC-002 | Keep documentation synchronized with code | [documentation_rules.md](documentation_rules.md) |
| DOC-003 | Include architecture diagrams | [documentation_rules.md](documentation_rules.md) |
| DOC-004 | Provide quick start guides | [documentation_rules.md](documentation_rules.md) |
| DOC-005 | Document configuration options | [documentation_rules.md](documentation_rules.md) |
| DOC-006 | Maintain changelog for all releases | [documentation_rules.md](documentation_rules.md) |

## 🤝 Collaboration Rules (Multi-Agent Systems)

### Democratic Voting Rules
| Rule ID | Description | File |
|---------|-------------|------|
| VOTE-001 | All decisions must reach quorum | [democratic_voting_rules.md](democratic_voting_rules.md) |
| VOTE-002 | Implement weighted voting mechanisms | [democratic_voting_rules.md](democratic_voting_rules.md) |
| VOTE-003 | Record all votes and rationale | [democratic_voting_rules.md](democratic_voting_rules.md) |
| VOTE-004 | Support multiple voting strategies | [democratic_voting_rules.md](democratic_voting_rules.md) |
| VOTE-005 | Handle tie-breaking scenarios | [democratic_voting_rules.md](democratic_voting_rules.md) |
| VOTE-006 | Respect minority opinions | [democratic_voting_rules.md](democratic_voting_rules.md) |

### Delegation Rules
| Rule ID | Description | File |
|---------|-------------|------|
| DEL-001 | Clearly define task scope before delegation | [delegation_rules.md](delegation_rules.md) |
| DEL-002 | Match tasks to agent capabilities | [delegation_rules.md](delegation_rules.md) |
| DEL-003 | Track delegation chain and accountability | [delegation_rules.md](delegation_rules.md) |
| DEL-004 | Set clear deadlines and expectations | [delegation_rules.md](delegation_rules.md) |
| DEL-005 | Monitor delegated task progress | [delegation_rules.md](delegation_rules.md) |
| DEL-006 | Provide feedback on completed delegations | [delegation_rules.md](delegation_rules.md) |

### Communication Protocol Rules
| Rule ID | Description | File |
|---------|-------------|------|
| PROT-001 | Use standardized message formats | [communication_protocol_rules.md](communication_protocol_rules.md) |
| PROT-002 | Implement heartbeat mechanisms | [communication_protocol_rules.md](communication_protocol_rules.md) |
| PROT-003 | Handle message ordering and delivery | [communication_protocol_rules.md](communication_protocol_rules.md) |
| PROT-004 | Implement message acknowledgment | [communication_protocol_rules.md](communication_protocol_rules.md) |
| PROT-005 | Use RabbitMQ for async communication | [communication_protocol_rules.md](communication_protocol_rules.md) |
| PROT-006 | Encrypt sensitive inter-agent messages | [communication_protocol_rules.md](communication_protocol_rules.md) |

## Rule Priority Legend

- 🔒 **Critical**: Must follow - violations may cause security issues or system failure
- ⚡ **High**: Should follow - strongly recommended for reliability and quality
- 🚀 **Medium**: Recommended - improves performance and maintainability
- 🤝 **Collaboration**: Essential for multi-agent democratic systems

## Quick Lookup by Topic

### Security
- SEC-001 to SEC-006

### Memory & Resources
- MEM-001 to MEM-006
- PERF-004, PERF-006

### Code Quality
- CODE-001 to CODE-006
- TEST-001 to TEST-006

### Communication
- COMM-001 to COMM-006
- PROT-001 to PROT-006

### Multi-Agent Collaboration
- VOTE-001 to VOTE-006
- DEL-001 to DEL-006

### Error Handling
- ERR-001 to ERR-006

### Performance
- PERF-001 to PERF-006

### Documentation
- DOC-001 to DOC-006

---

**Version**: 2.0.0  
**Last Updated**: 2025-12-08  
**Total Rules**: 60+

For detailed descriptions and examples, see individual rule files.
