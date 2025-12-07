"""
OpenSearch Client for Local Installation
Simple connection to local OpenSearch without AWS dependencies
"""

from opensearchpy import OpenSearch
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global client instance
_opensearch_client: Optional[OpenSearch] = None

def get_opensearch_client() -> OpenSearch:
    """
    Returns a singleton OpenSearch client for local installation
    
    Returns:
        OpenSearch: Configured OpenSearch client
    """
    global _opensearch_client
    
    if _opensearch_client is not None:
        return _opensearch_client
    
    try:
        # Get OpenSearch connection details from environment
        host = os.getenv('OPENSEARCH_HOST', 'localhost')
        port = int(os.getenv('OPENSEARCH_PORT', '9200'))
        username = os.getenv('OPENSEARCH_USERNAME', 'admin')
        password = os.getenv('OPENSEARCH_PASSWORD', 'admin')
        use_ssl = os.getenv('OPENSEARCH_USE_SSL', 'false').lower() == 'true'
        
        # Create simple OpenSearch client for local installation
        if username and password and username != 'none':
            # With basic authentication
            _opensearch_client = OpenSearch(
                hosts=[{'host': host, 'port': port}],
                http_auth=(username, password),
                use_ssl=use_ssl,
                verify_certs=False,
                ssl_show_warn=False,
                timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
        else:
            # Without authentication (security plugin disabled)
            _opensearch_client = OpenSearch(
                hosts=[{'host': host, 'port': port}],
                use_ssl=use_ssl,
                verify_certs=False,
                ssl_show_warn=False,
                timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
        
        # Test connection
        info = _opensearch_client.info()
        logger.info(f"Connected to OpenSearch: {info['version']['number']} at {host}:{port}")
        
        return _opensearch_client
        
    except Exception as e:
        logger.error(f"Failed to create OpenSearch client: {str(e)}")
        raise

def create_index_if_not_exists(index_name: str, mapping: dict = None):
    """
    Creates an index if it doesn't exist
    
    Args:
        index_name: Name of the index
        mapping: Optional index mapping
    """
    client = get_opensearch_client()
    
    try:
        if not client.indices.exists(index=index_name):
            body = {}
            if mapping:
                body['mappings'] = mapping
            
            client.indices.create(index=index_name, body=body)
            logger.info(f"Created index: {index_name}")
        else:
            logger.debug(f"Index already exists: {index_name}")
    except Exception as e:
        logger.error(f"Error creating index {index_name}: {str(e)}")
        raise

def bulk_index(index_name: str, documents: list) -> dict:
    """
    Bulk indexes documents to OpenSearch
    
    Args:
        index_name: Target index name
        documents: List of documents to index
        
    Returns:
        dict: Bulk operation response
    """
    client = get_opensearch_client()
    
    # Prepare bulk request body
    bulk_body = []
    for doc in documents:
        bulk_body.append({"index": {"_index": index_name}})
        bulk_body.append(doc)
    
    try:
        response = client.bulk(body=bulk_body, refresh=True)
        
        if response.get('errors'):
            logger.warning(f"Bulk indexing had errors: {response}")
        else:
            logger.info(f"Successfully indexed {len(documents)} documents to {index_name}")
        
        return response
    except Exception as e:
        logger.error(f"Bulk indexing failed: {str(e)}")
        raise

def test_connection() -> dict:
    """
    Tests the OpenSearch connection
    
    Returns:
        dict: Cluster information
    """
    try:
        client = get_opensearch_client()
        info = client.info()
        cluster_health = client.cluster.health()
        
        return {
            "status": "connected",
            "version": info['version']['number'],
            "cluster_name": info['cluster_name'],
            "cluster_health": cluster_health['status']
        }
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
