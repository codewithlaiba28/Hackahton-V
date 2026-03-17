-- Phase 2 Initial Schema
-- Created: 2026-03-17
-- Description: Complete PostgreSQL schema for Customer Success FTE CRM

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. CUSTOMERS TABLE
-- =============================================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_created ON customers(created_at);

-- =============================================================================
-- 2. CUSTOMER IDENTIFIERS TABLE
-- =============================================================================
CREATE TABLE customer_identifiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type VARCHAR(50) NOT NULL,
    identifier_value VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

CREATE INDEX idx_customer_identifiers_value ON customer_identifiers(identifier_value);
CREATE INDEX idx_customer_identifiers_customer ON customer_identifiers(customer_id);

-- =============================================================================
-- 3. CONVERSATIONS TABLE
-- =============================================================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    initial_channel VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active',
    sentiment_score DECIMAL(3,2),
    resolution_type VARCHAR(50),
    escalated_to VARCHAR(255),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_channel ON conversations(initial_channel);
CREATE INDEX idx_conversations_started ON conversations(started_at);

-- =============================================================================
-- 4. MESSAGES TABLE
-- =============================================================================
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,
    direction VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER,
    latency_ms INTEGER,
    tool_calls JSONB DEFAULT '[]',
    channel_message_id VARCHAR(255),
    delivery_status VARCHAR(50) DEFAULT 'pending',
    sentiment_score DECIMAL(3,2),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_channel ON messages(channel);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_messages_direction ON messages(direction);

-- =============================================================================
-- 5. TICKETS TABLE
-- =============================================================================
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    source_channel VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    assigned_to VARCHAR(255),
    sla_deadline TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_channel ON tickets(source_channel);
CREATE INDEX idx_tickets_customer ON tickets(customer_id);
CREATE INDEX idx_tickets_created ON tickets(created_at);
CREATE INDEX idx_tickets_priority ON tickets(priority);

-- =============================================================================
-- 6. KNOWLEDGE BASE TABLE (with pgvector)
-- =============================================================================
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    embedding VECTOR(1536),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0
);

-- IVFFlat index for semantic search
CREATE INDEX idx_knowledge_embedding 
ON knowledge_base USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_tags ON knowledge_base USING GIN (tags);
CREATE INDEX idx_knowledge_active ON knowledge_base(is_active);

-- =============================================================================
-- 7. CHANNEL CONFIGS TABLE
-- =============================================================================
CREATE TABLE channel_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel VARCHAR(50) UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB NOT NULL,
    response_template TEXT,
    max_response_length INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- 8. AGENT METRICS TABLE
-- =============================================================================
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    channel VARCHAR(50),
    dimensions JSONB DEFAULT '{}',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_metrics_name ON agent_metrics(metric_name);
CREATE INDEX idx_metrics_recorded ON agent_metrics(recorded_at);
CREATE INDEX idx_metrics_channel ON agent_metrics(channel);

-- =============================================================================
-- SEED DATA
-- =============================================================================

-- Insert default channel configurations
INSERT INTO channel_configs (channel, enabled, config, max_response_length) VALUES
('email', TRUE, '{"smtp_host": "smtp.gmail.com", "smtp_port": 587}'::jsonb, 500),
('whatsapp', TRUE, '{"twilio_enabled": true}'::jsonb, 300),
('web_form', TRUE, '{"confirmation_email": true}'::jsonb, 300)
ON CONFLICT (channel) DO NOTHING;

-- =============================================================================
-- VERIFICATION QUERY
-- =============================================================================
-- Run this to verify all tables created:
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' AND table_type = 'BASE TABLE' 
-- ORDER BY table_name;
-- Should return: 8 tables
