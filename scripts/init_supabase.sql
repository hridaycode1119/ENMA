-- ==============================================================================
-- AIRA Enterprise AI Agent: Supabase PostgreSQL Schema Initialization
-- Paste this script into your Supabase Dashboard -> SQL Editor and click "Run".
-- ==============================================================================

-- Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tasks Table (Autonomous AI Task Plans & Status)
CREATE TABLE IF NOT EXISTS public.aira_tasks (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    user_instruction TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'IDLE',
    plan_json JSONB,
    tool_name TEXT,
    execution_time_ms DOUBLE PRECISION DEFAULT 0.0,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aira_tasks_created_at ON public.aira_tasks (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_aira_tasks_state ON public.aira_tasks (state);

-- 2. Calendar & Meetings Table
CREATE TABLE IF NOT EXISTS public.aira_calendar_events (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    title TEXT NOT NULL,
    event_time TEXT NOT NULL,
    duration TEXT DEFAULT '30 mins',
    meet_url TEXT,
    attendees JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aira_cal_created_at ON public.aira_calendar_events (created_at DESC);

-- 3. Document Records Table
CREATE TABLE IF NOT EXISTS public.aira_documents (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    page_count INTEGER DEFAULT 1,
    raw_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aira_docs_created_at ON public.aira_documents (created_at DESC);

-- 4. Notes, Journals & Bookmarks Table
CREATE TABLE IF NOT EXISTS public.aira_notes (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    category TEXT NOT NULL DEFAULT 'note', -- 'note', 'journal', 'bookmark'
    title TEXT NOT NULL,
    content TEXT,
    date_str TEXT,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aira_notes_cat_created ON public.aira_notes (category, created_at DESC);

-- 5. Audit & Human-in-the-Loop Security Logs Table
CREATE TABLE IF NOT EXISTS public.aira_audit_logs (
    id TEXT PRIMARY KEY DEFAULT uuid_generate_v4()::TEXT,
    task_id TEXT REFERENCES public.aira_tasks(id) ON DELETE SET NULL,
    tool_name TEXT NOT NULL,
    action TEXT NOT NULL,
    user_confirmed BOOLEAN DEFAULT FALSE,
    details JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aira_audit_created_at ON public.aira_audit_logs (created_at DESC);

-- Enable Row Level Security (RLS) & Allow public anon access for MVP / Service role
ALTER TABLE public.aira_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.aira_calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.aira_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.aira_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.aira_audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read-write for aira_tasks" ON public.aira_tasks FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for aira_calendar_events" ON public.aira_calendar_events FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for aira_documents" ON public.aira_documents FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for aira_notes" ON public.aira_notes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for aira_audit_logs" ON public.aira_audit_logs FOR ALL USING (true) WITH CHECK (true);
