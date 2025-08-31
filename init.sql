-- PostgreSQL initialization script for Luna Agent Preview
-- This script sets up the database schema with pgvector extension for vector similarity search

-- Enable the vector extension for similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the documents table for storing document content and embeddings
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient similarity search
-- IVFFlat index for cosine similarity (recommended for most use cases)
CREATE INDEX IF NOT EXISTS documents_embedding_cosine_idx 
ON documents USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Alternative L2 distance index (uncomment if needed)
-- CREATE INDEX IF NOT EXISTS documents_embedding_l2_idx 
-- ON documents USING ivfflat (embedding vector_l2_ops) 
-- WITH (lists = 100);

-- Create index on metadata for fast filtering
CREATE INDEX IF NOT EXISTS documents_metadata_idx ON documents USING GIN (metadata);

-- Create index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS documents_created_at_idx ON documents (created_at DESC);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create a function for similarity search
CREATE OR REPLACE FUNCTION similarity_search(
    query_embedding VECTOR(1024),
    similarity_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE(
    id INT,
    content TEXT,
    similarity FLOAT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.content,
        1 - (d.embedding <=> query_embedding) AS similarity,
        d.metadata,
        d.created_at
    FROM documents d
    WHERE 1 - (d.embedding <=> query_embedding) > similarity_threshold
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Insert some sample data for testing (optional)
-- INSERT INTO documents (content, embedding, metadata) VALUES 
-- ('Sample document content for testing vector similarity search.', 
--  array_fill(0.1, ARRAY[1024])::vector, 
--  '{"source": "test", "type": "sample"}');

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO executive;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO executive;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO executive;

-- Show table information
\d+ documents;

-- Display configuration
SHOW shared_preload_libraries;

-- Confirm extension installation
SELECT * FROM pg_extension WHERE extname = 'vector';