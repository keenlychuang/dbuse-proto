"""
Document Base Manager Module for RAG Chatbot
Handles management of persistent document bases.
"""

import os
import json
import shutil
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

class DocumentBaseManager:
    """
    A class for managing persistent document bases for the RAG chatbot.
    Handles creation, listing, updating, and deletion of document bases.
    """
    
    def __init__(self, base_directory: str = "./document_bases"):
        """
        Initialize the DocumentBaseManager.
        
        Args:
            base_directory: Directory to store all document bases
        """
        self.base_directory = base_directory
        os.makedirs(base_directory, exist_ok=True)
        
        self.metadata_file = os.path.join(base_directory, "metadata.json")
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata about available document bases."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save metadata about document bases."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def create_document_base(self, name: str, description: str = "") -> str:
        """
        Create a new document base.
        
        Args:
            name: Name of the document base
            description: Optional description
            
        Returns:
            Path to the document base directory
        
        Raises:
            ValueError: If a document base with the given name already exists
        """
        if name in self.metadata:
            raise ValueError(f"Document base '{name}' already exists")
        
        # Sanitize name for directory
        safe_name = "".join(c if c.isalnum() else "_" for c in name)
        timestamp = int(time.time())
        dir_name = f"{safe_name}_{timestamp}"
        
        # Create directory for the document base
        doc_base_dir = os.path.join(self.base_directory, dir_name)
        os.makedirs(doc_base_dir, exist_ok=True)
        
        # Record metadata
        self.metadata[name] = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "description": description,
            "directory": dir_name,
            "num_documents": 0,
            "num_chunks": 0,
            "documents": []
        }
        
        self._save_metadata()
        return doc_base_dir
    
    def list_document_bases(self) -> List[Dict[str, Any]]:
        """
        List all available document bases.
        
        Returns:
            List of document base information
        """
        result = []
        for name, info in self.metadata.items():
            result.append({
                "name": name,
                "description": info.get("description", ""),
                "created_at": info.get("created_at"),
                "updated_at": info.get("updated_at"),
                "num_documents": info.get("num_documents", 0),
                "num_chunks": info.get("num_chunks", 0)
            })
        return result
    
    def get_document_base(self, name: str) -> Dict[str, Any]:
        """
        Get information about a specific document base.
        
        Args:
            name: Name of the document base
            
        Returns:
            Document base information
            
        Raises:
            KeyError: If document base doesn't exist
        """
        if name not in self.metadata:
            raise KeyError(f"Document base '{name}' not found")
        
        return self.metadata[name]
    
    def get_document_base_path(self, name: str) -> str:
        """
        Get the file system path to a specific document base.
        
        Args:
            name: Name of the document base
            
        Returns:
            Path to document base directory
            
        Raises:
            KeyError: If document base doesn't exist
        """
        if name not in self.metadata:
            raise KeyError(f"Document base '{name}' not found")
        
        dir_name = self.metadata[name]["directory"]
        return os.path.join(self.base_directory, dir_name)
    
    def update_document_base(self, name: str, num_documents: int = 0, 
                             num_chunks: int = 0, documents: List[str] = None) -> None:
        """
        Update document base metadata after adding documents.
        
        Args:
            name: Name of the document base
            num_documents: Number of documents added
            num_chunks: Number of chunks added
            documents: List of document paths added
            
        Raises:
            KeyError: If document base doesn't exist
        """
        if name not in self.metadata:
            raise KeyError(f"Document base '{name}' not found")
        
        base_info = self.metadata[name]
        base_info["updated_at"] = datetime.now().isoformat()
        base_info["num_documents"] += num_documents
        base_info["num_chunks"] += num_chunks
        
        if documents:
            if "documents" not in base_info:
                base_info["documents"] = []
            
            # Add only filenames, not full paths
            base_info["documents"].extend([os.path.basename(doc) for doc in documents])
        
        self._save_metadata()
    
    def delete_document_base(self, name: str) -> None:
        """
        Delete a document base.
        
        Args:
            name: Name of the document base
            
        Raises:
            KeyError: If document base doesn't exist
        """
        if name not in self.metadata:
            raise KeyError(f"Document base '{name}' not found")
        
        # Get directory path
        dir_name = self.metadata[name]["directory"]
        dir_path = os.path.join(self.base_directory, dir_name)
        
        # Delete directory if it exists
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        
        # Remove from metadata
        del self.metadata[name]
        self._save_metadata()
    
    def rename_document_base(self, old_name: str, new_name: str) -> None:
        """
        Rename a document base.
        
        Args:
            old_name: Current name of the document base
            new_name: New name for the document base
            
        Raises:
            KeyError: If document base doesn't exist
            ValueError: If new name already exists
        """
        if old_name not in self.metadata:
            raise KeyError(f"Document base '{old_name}' not found")
        
        if new_name in self.metadata:
            raise ValueError(f"Document base '{new_name}' already exists")
        
        # Copy metadata
        self.metadata[new_name] = self.metadata[old_name].copy()
        self.metadata[new_name]["updated_at"] = datetime.now().isoformat()
        
        # Remove old entry
        del self.metadata[old_name]
        self._save_metadata()


# Example usage
if __name__ == "__main__":
    # Initialize document base manager
    manager = DocumentBaseManager()
    
    # Create a new document base
    manager.create_document_base("AI Documents", "Collection of documents about artificial intelligence")
    
    # List available document bases
    bases = manager.list_document_bases()
    for base in bases:
        print(f"Name: {base['name']}")
        print(f"Description: {base['description']}")
        print(f"Documents: {base['num_documents']}")
        print(f"Chunks: {base['num_chunks']}")
        print()
    
    # Update document base after adding documents
    manager.update_document_base("AI Documents", num_documents=2, num_chunks=15, 
                              documents=["ai_intro.pdf", "ml_basics.docx"])
    
    # Get path to a document base
    path = manager.get_document_base_path("AI Documents")
    print(f"Document base path: {path}")