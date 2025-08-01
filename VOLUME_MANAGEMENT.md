# DeSciOS Volume Management

This document explains how DeSciOS handles volumes and how to ensure proper deployment regardless of whether volumes exist or are fresh.

## Volume Structure

DeSciOS uses three main volume directories:

- `./data/academic` - Academic platform database and uploads
- `./data/ipfs` - IPFS node data and configuration
- `./data/user` - User data and workspace files

## Automatic Volume Initialization

The DeSciOS container automatically handles volume initialization:

1. **Directory Creation**: All necessary directories are created with proper permissions
2. **Ownership**: Directories are owned by the `deScier` user (UID 1000)
3. **IPFS Initialization**: IPFS is automatically initialized if not already present
4. **Database Setup**: Academic platform database is automatically created and seeded

## Fresh Deployment

To test a fresh deployment (useful for testing or resetting data):

```bash
# Use the provided test script
./test-fresh-deployment.sh

# Or manually:
docker-compose down
sudo rm -rf ./data/academic ./data/ipfs ./data/user
docker-compose up -d
```

## Volume Permissions

The container automatically sets proper permissions:

- Directories: `755` (rwxr-xr-x)
- Ownership: `deScier:deScier` (UID 1000:GID 1000)

## Troubleshooting

### Permission Issues

If you encounter permission issues:

```bash
# Fix ownership
sudo chown -R 1000:1000 ./data/

# Fix permissions
sudo chmod -R 755 ./data/
```

### IPFS Issues

If IPFS fails to start:

```bash
# Check IPFS status
docker exec descios-academic su - deScier -c 'ipfs id'

# Reinitialize IPFS
docker exec descios-academic su - deScier -c 'rm -rf ~/.ipfs && ipfs init --profile=server'
```

### Academic Platform Issues

If the academic platform fails to start:

```bash
# Check logs
docker logs descios-academic

# Reinitialize database
docker exec descios-academic su - deScier -c 'cd /home/deScier/DeSciOS/node && node ensure-admin.js'
```

## Data Persistence

- **Academic Platform**: Database and uploads persist across container restarts
- **IPFS**: Node data and configuration persist across container restarts
- **User Data**: Workspace files persist across container restarts

## Backup and Restore

To backup your data:

```bash
# Create backup
tar -czf descios-backup-$(date +%Y%m%d).tar.gz ./data/

# Restore from backup
tar -xzf descios-backup-YYYYMMDD.tar.gz
```

## Health Checks

The container includes health checks to ensure services are running:

- noVNC accessibility check
- Automatic restart on failure
- Service monitoring via supervisord

## Environment Variables

Key environment variables for volume management:

- `PUID=1000` - User ID for volume ownership
- `PGID=1000` - Group ID for volume ownership
- `DATABASE_PATH=/home/deScier/.academic/database.sqlite` - Database location
- `UPLOADS_PATH=/home/deScier/.academic/uploads` - Uploads directory 