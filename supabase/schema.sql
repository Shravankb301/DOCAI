-- Create the risks table for storing compliance analysis results
CREATE TABLE IF NOT EXISTS risks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_path TEXT,
    status TEXT NOT NULL,
    details JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index on the status column for faster queries
CREATE INDEX IF NOT EXISTS idx_risks_status ON risks (status);

-- Create an index on the created_at column for chronological queries
CREATE INDEX IF NOT EXISTS idx_risks_created_at ON risks (created_at);

-- Add RLS (Row Level Security) policies
ALTER TABLE risks ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all authenticated users to select from the risks table
CREATE POLICY "Allow select for authenticated users" 
    ON risks FOR SELECT 
    USING (auth.role() = 'authenticated');

-- Create a policy that allows all authenticated users to insert into the risks table
CREATE POLICY "Allow insert for authenticated users" 
    ON risks FOR INSERT 
    WITH CHECK (auth.role() = 'authenticated');

-- Create a policy that allows all authenticated users to update their own records
CREATE POLICY "Allow update for authenticated users" 
    ON risks FOR UPDATE 
    USING (auth.role() = 'authenticated');

-- Create a policy that allows all authenticated users to delete their own records
CREATE POLICY "Allow delete for authenticated users" 
    ON risks FOR DELETE 
    USING (auth.role() = 'authenticated'); 