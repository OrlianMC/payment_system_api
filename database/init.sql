-- ------------------------------------------------------------
-- Init SQL - Estructura de la base de datos
-- ------------------------------------------------------------

-- Tipos ENUM
CREATE TYPE public.cardbrand AS ENUM ('visa','mastercard','amex','discover');
CREATE TYPE public.paymentstatus AS ENUM ('approved','rejected','pending');
CREATE TYPE public.userrole AS ENUM ('admin','user');

-- Tablas
CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    role public.userrole NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone
);

CREATE TABLE public.profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying,
    last_name character varying,
    ci character varying,
    phone character varying,
    address character varying,
    age integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone
);

CREATE TABLE public.cards (
    id integer NOT NULL,
    user_id integer NOT NULL,
    card_holder_name character varying NOT NULL,
    brand public.cardbrand NOT NULL,
    last_four character varying NOT NULL,
    masked_number character varying NOT NULL,
    expiration_month integer NOT NULL,
    expiration_year integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone
);

CREATE TABLE public.payments (
    id integer NOT NULL,
    user_id integer NOT NULL,
    card_id integer NOT NULL,
    amount double precision NOT NULL,
    currency character varying NOT NULL,
    status public.paymentstatus NOT NULL,
    status_reason character varying,
    processor_reference character varying,
    idempotency_key character varying,
    processed_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone
);

-- Secuencias para IDs
CREATE SEQUENCE public.users_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE public.profiles_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE public.cards_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE public.payments_id_seq START WITH 1 INCREMENT BY 1;

-- Asociar secuencias a columnas
ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
ALTER TABLE ONLY public.profiles ALTER COLUMN id SET DEFAULT nextval('public.profiles_id_seq'::regclass);
ALTER TABLE ONLY public.cards ALTER COLUMN id SET DEFAULT nextval('public.cards_id_seq'::regclass);
ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);

-- Constraints: PK
ALTER TABLE ONLY public.users ADD CONSTRAINT users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.profiles ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.cards ADD CONSTRAINT cards_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.payments ADD CONSTRAINT payments_pkey PRIMARY KEY (id);

-- Constraints: UNIQUE
ALTER TABLE ONLY public.profiles ADD CONSTRAINT profiles_user_id_key UNIQUE (user_id);
CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);
CREATE INDEX ix_payments_idempotency_key ON public.payments USING btree (idempotency_key);

-- Constraints: Foreign Keys
ALTER TABLE ONLY public.profiles ADD CONSTRAINT profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.cards ADD CONSTRAINT cards_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.payments ADD CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
ALTER TABLE ONLY public.payments ADD CONSTRAINT payments_card_id_fkey FOREIGN KEY (card_id) REFERENCES public.cards(id);
