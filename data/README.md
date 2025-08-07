# Data Directory

This directory stores application data, exports, and user-generated content.

## Structure
- `exports/` - Exported conversations and reports
- `uploads/` - User uploaded files (if any)
- `backups/` - Backup data
- `temp/` - Temporary processing files

## Purpose
- **User Data**: Store conversation exports and user data
- **Backup**: Application data backups
- **Processing**: Temporary files during data processing
- **Import/Export**: Data transfer functionality

## Files Created by User Actions
- Conversation exports (JSON format)
- Configuration backups
- User uploaded documents (future feature)

## Security Note
- This directory may contain sensitive user data
- Ensure appropriate permissions and backup strategies
- Consider encryption for sensitive data

## Cleanup
- Temporary files should be cleaned up automatically
- Manual cleanup of old exports may be needed
- Check disk space usage periodically
