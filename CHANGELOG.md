
# CHANGELOG

## alpha-v0.0.2

### Added
- Proper UUID support throughout the Chain Processor system
- Node_name field to NodeExecutionResult to preserve original node names
- Get_node_uuid helper methods in Registry and ChainExecutor
- Deterministic UUID generation for nodes based on names
- Configurable logging via environment variables
- Configurable API URL for demo script
- Comprehensive error sanitization with sensitive data redaction
- Database locking to prevent race conditions during chain execution
- Proper handling for node result count mismatches
- Detailed error logging throughout chain execution process

### Changed
- **Breaking**: Updated to require Python 3.13 in all packages and Dockerfiles
- **Breaking**: Changed NodeExecutionResult.node_id to use UUID objects instead of strings
- Improved NodeExecutionResult to properly track success state
- Enhanced type safety in chain executor with explicit type checking
- Improved transaction management in API error handling
- Fixed node name uniqueness issues in registry with namespacing

### Fixed
- Success flag bug in NodeExecutionResult
- Node ID handling inconsistency in chain execution
- Redundant conditional code in chain executor
- Removed unused imports
- Inconsistent Docker commands for API service

### Security
- Improved transaction handling to ensure data consistency in error scenarios
- Added regex-based sanitization for sensitive information in error messages

### Documentation
- Updated API documentation to reflect UUID changes
- Added deprecation warnings for string-based node IDs
