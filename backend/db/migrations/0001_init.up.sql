-- Contact-form submissions.
CREATE TABLE contact_messages (
    id         BIGSERIAL PRIMARY KEY,
    name       TEXT        NOT NULL,
    email      TEXT        NOT NULL,
    subject    TEXT        NOT NULL DEFAULT '',
    body       TEXT        NOT NULL,
    source_ip  TEXT        NOT NULL DEFAULT '',
    user_agent TEXT        NOT NULL DEFAULT '',
    handled    BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- CMS content blocks consumed by the frontend (body is arbitrary JSON).
CREATE TABLE content_blocks (
    id         BIGSERIAL PRIMARY KEY,
    slug       TEXT        NOT NULL UNIQUE,
    title      TEXT        NOT NULL DEFAULT '',
    body       JSONB       NOT NULL DEFAULT '{}'::jsonb,
    published  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Lightweight analytics events (pageviews, cv downloads, etc.).
CREATE TABLE analytics_events (
    id         BIGSERIAL PRIMARY KEY,
    kind       TEXT        NOT NULL,
    path       TEXT        NOT NULL DEFAULT '',
    referrer   TEXT        NOT NULL DEFAULT '',
    subhost    TEXT        NOT NULL DEFAULT '',  -- '' = main site, else sub-app slug
    session_id TEXT        NOT NULL DEFAULT '',
    user_agent TEXT        NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_analytics_events_created_at ON analytics_events (created_at);
CREATE INDEX idx_analytics_events_kind ON analytics_events (kind);

-- Registry of subhosted mini-apps (mirrors the Nginx subdomain reverse proxies).
CREATE TABLE subhosts (
    id         BIGSERIAL PRIMARY KEY,
    slug       TEXT        NOT NULL UNIQUE,  -- 'brewery', 'queue'
    name       TEXT        NOT NULL,
    subdomain  TEXT        NOT NULL UNIQUE,  -- 'brewery.tomsherlock.space'
    upstream   TEXT        NOT NULL,         -- '127.0.0.1:9001'
    enabled    BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
