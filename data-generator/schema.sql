CREATE TABLE IF NOT EXISTS users (
    user_id  bigserial PRIMARY KEY,
    tier text,
    country text,
    signup_date date,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT chk_tier CHECK (tier IN ('standard', 'premium'))
);

CREATE TABLE IF NOT EXISTS corridors (
    corridor_code text PRIMARY KEY,
    source_currency Varchar(3),
    target_currency Varchar(3),
    corridor_name text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


CREATE TABLE IF NOT EXISTS transactions (
    transaction_id bigserial PRIMARY KEY, 
    user_id bigint REFERENCES users(user_id),
    corridor_code text REFERENCES corridors(corridor_code),
    amount_ngn numeric(18, 2),
    amount_target_currency numeric(18, 2),
    fx_rate_applied numeric(18, 6),
    fee_amount_ngn numeric(18, 2),
    status text CHECK (status IN ('initiated', 'processing', 'completed', 'failed')),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

CREATE INDEX idx_transactions_updated_at ON transactions (updated_at);
