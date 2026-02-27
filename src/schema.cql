
CREATE KEYSPACE IF NOT EXISTS hackernews
WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': 3};

CREATE TABLE IF NOT EXISTS hackernews.comments (
    id bigint PRIMARY KEY,
    title text,
    url text,
    text text,
    text_embedding VECTOR<FLOAT, 384>,
    dead boolean,
    "by" text,
    score int,
    time bigint,
    timestamp timestamp,
    type text,
    parent bigint,
    descendants int,
    ranking int,
    deleted boolean
);

CREATE INDEX IF NOT EXISTS ann_index ON hackernews.comments(text_embedding) 
USING 'vector_index'
WITH OPTIONS = { 'similarity_function': 'DOT_PRODUCT' };
