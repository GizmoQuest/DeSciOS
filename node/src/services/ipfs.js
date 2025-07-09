const fs = require('fs');
const path = require('path');
const axios = require('axios');

// IPFS HTTP API configuration
const IPFS_API_BASE = 'http://localhost:5001/api/v0';
const IPFS_GATEWAY = 'http://localhost:8080/ipfs';

class IPFSService {
  constructor() {
    this.apiBase = IPFS_API_BASE;
    this.gateway = IPFS_GATEWAY;
    this.isConnected = false;
  }

  // Initialize IPFS connection
  async initialize() {
    try {
      const response = await axios.get(`${this.apiBase}/id`);
      if (response.data && response.data.ID) {
        this.isConnected = true;
        console.log('✅ IPFS connection established:', response.data.ID);
        return true;
      }
    } catch (error) {
      console.error('❌ Failed to connect to IPFS:', error.message);
      this.isConnected = false;
      return false;
    }
  }

  // Check if IPFS is connected
  isConnectedToIPFS() {
    return this.isConnected;
  }

  // Add data to IPFS
  async addData(data, options = {}) {
    try {
      if (!this.isConnected) {
        throw new Error('IPFS not connected');
      }

      let content;
      if (typeof data === 'string') {
        content = data;
      } else if (Buffer.isBuffer(data)) {
        content = data;
      } else if (data.path && data.content) {
        // File object
        content = data.content;
      } else {
        // JSON object
        content = JSON.stringify(data);
      }

      const FormData = require('form-data');
      const formData = new FormData();
      formData.append('file', Buffer.from(content));

      const response = await axios.post(`${this.apiBase}/add`, formData, {
        headers: {
          ...formData.getHeaders(),
        },
      });

      return response.data.Hash;
    } catch (error) {
      console.error('❌ Failed to add data to IPFS:', error);
      throw error;
    }
  }

  // Get data from IPFS
  async getData(hash) {
    try {
      if (!this.isConnected) {
        throw new Error('IPFS not connected');
      }

      const response = await axios.get(`${this.apiBase}/cat?arg=${hash}`, {
        responseType: 'arraybuffer'
      });

      return Buffer.from(response.data);
    } catch (error) {
      console.error('❌ Failed to get data from IPFS:', error);
      throw error;
    }
  }

  // Get data as string
  async getDataAsString(hash) {
    try {
      const data = await this.getData(hash);
      return data.toString();
    } catch (error) {
      console.error('❌ Failed to get data as string from IPFS:', error);
      throw error;
    }
  }

  // Get data as JSON
  async getDataAsJSON(hash) {
    try {
      const data = await this.getDataAsString(hash);
      return JSON.parse(data);
    } catch (error) {
      console.error('❌ Failed to get data as JSON from IPFS:', error);
      throw error;
    }
  }

  // Add file to IPFS
  async addFile(filePath, options = {}) {
    try {
      if (!this.isConnected) {
        throw new Error('IPFS not connected');
      }

      const file = fs.readFileSync(filePath);
      const result = await this.client.add({
        path: path.basename(filePath),
        content: file
      }, options);

      return result.cid.toString();
    } catch (error) {
      console.error('❌ Failed to add file to IPFS:', error);
      throw error;
    }
  }

  // Add multiple files/directory to IPFS
  async addDirectory(dirPath, options = {}) {
    try {
      if (!this.isConnected) {
        throw new Error('IPFS not connected');
      }

      const files = [];
      const addFilesRecursively = (currentPath, basePath = '') => {
        const items = fs.readdirSync(currentPath);
        
        for (const item of items) {
          const itemPath = path.join(currentPath, item);
          const relativePath = path.join(basePath, item);
          
          if (fs.statSync(itemPath).isDirectory()) {
            addFilesRecursively(itemPath, relativePath);
          } else {
            files.push({
              path: relativePath,
              content: fs.readFileSync(itemPath)
            });
          }
        }
      };

      addFilesRecursively(dirPath);
      
      const results = [];
      for await (const result of this.client.addAll(files, options)) {
        results.push({
          path: result.path,
          hash: result.cid.toString()
        });
      }

      return results;
    } catch (error) {
      console.error('❌ Failed to add directory to IPFS:', error);
      throw error;
    }
  }

  // Pin content to ensure it stays in IPFS
  async pinContent(hash) {
    try {
      if (!this.isConnected) {
        throw new Error('IPFS not connected');
      }

      await axios.post(`${this.apiBase}/pin/add?arg=${hash}`);
      console.log(`📌 Content pinned: ${hash}`);
      return true;
    } catch (error) {
      console.error('❌ Failed to pin content:', error);
      throw error;
    }
  }

  // Unpin content
  async unpinContent(hash) {
    try {
      if (!this.isConnected) {
        throw new Error('IPFS not connected');
      }

      await axios.post(`${this.apiBase}/pin/rm?arg=${hash}`);
      console.log(`📌 Content unpinned: ${hash}`);
      return true;
    } catch (error) {
      console.error('❌ Failed to unpin content:', error);
      throw error;
    }
  }

  // List pinned content
  async listPinnedContent() {
    try {
      if (!this.isConnected) {
        throw new Error('IPFS not connected');
      }

      const response = await axios.get(`${this.apiBase}/pin/ls`);
      const pins = [];
      
      if (response.data && response.data.Keys) {
        for (const hash in response.data.Keys) {
          pins.push({
            hash: hash,
            type: response.data.Keys[hash].Type
          });
        }
      }

      return pins;
    } catch (error) {
      console.error('❌ Failed to list pinned content:', error);
      throw error;
    }
  }

  // Get IPFS node stats
  async getStats() {
    try {
      if (!this.isConnected) {
        throw new Error('IPFS not connected');
      }

      const [id, version, stats] = await Promise.all([
        axios.get(`${this.apiBase}/id`),
        axios.get(`${this.apiBase}/version`),
        axios.get(`${this.apiBase}/stats/repo`)
      ]);

      return {
        id: id.data.ID,
        version: version.data.Version,
        repoSize: stats.data.RepoSize,
        storageMax: stats.data.StorageMax,
        addresses: id.data.Addresses
      };
    } catch (error) {
      console.error('❌ Failed to get IPFS stats:', error);
      throw error;
    }
  }

  // Create a content-addressed storage for academic data
  async storeAcademicData(data, metadata = {}) {
    try {
      const academicRecord = {
        timestamp: new Date().toISOString(),
        type: metadata.type || 'academic_data',
        author: metadata.author || 'unknown',
        version: metadata.version || 1,
        data: data,
        metadata: metadata
      };

      const hash = await this.addData(academicRecord);
      
      // Pin important academic data
      if (metadata.pin !== false) {
        await this.pinContent(hash);
      }

      return {
        hash,
        timestamp: academicRecord.timestamp,
        gateway_url: this.getGatewayURL(hash)
      };
    } catch (error) {
      console.error('❌ Failed to store academic data:', error);
      throw error;
    }
  }

  // Retrieve academic data with metadata
  async retrieveAcademicData(hash) {
    try {
      const data = await this.getDataAsJSON(hash);
      return {
        ...data,
        hash,
        gateway_url: this.getGatewayURL(hash)
      };
    } catch (error) {
      console.error('❌ Failed to retrieve academic data:', error);
      throw error;
    }
  }

  // Create a versioned document system
  async createVersionedDocument(filename, content, metadata = {}) {
    try {
      const document = {
        filename,
        content,
        version: metadata.version || 1,
        timestamp: new Date().toISOString(),
        author: metadata.author || 'unknown',
        metadata: metadata
      };

      const hash = await this.addData(document);
      await this.pinContent(hash);

      return {
        hash,
        version: document.version,
        timestamp: document.timestamp,
        gateway_url: this.getGatewayURL(hash)
      };
    } catch (error) {
      console.error('❌ Failed to create versioned document:', error);
      throw error;
    }
  }

  // Get gateway URL for hash
  getGatewayURL(hash) {
    return `${this.gateway}/${hash}`;
  }

  // Get API URL for hash
  getAPIURL(hash) {
    return `${this.apiBase}/cat?arg=${hash}`;
  }
}

// Initialize IPFS service
const ipfsService = new IPFSService();

async function initializeIPFS() {
  try {
    const success = await ipfsService.initialize();
    if (success) {
      return ipfsService;
    } else {
      console.log('⚠️  IPFS service initialization failed gracefully');
      return null;
    }
  } catch (error) {
    console.error('❌ Failed to initialize IPFS service:', error);
    return null;
  }
}

module.exports = {
  IPFSService,
  ipfsService,
  initializeIPFS
}; 