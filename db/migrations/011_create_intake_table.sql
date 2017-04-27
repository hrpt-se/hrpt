--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: pollster_results_intake; Type: TABLE; Schema: public; Owner: admin; Tablespace: 
--

CREATE TABLE pollster_results_intake (
    id integer NOT NULL,
    "user" integer,
    global_id character varying(36),
    channel character varying(36),
    "timestamp" timestamp with time zone,
    "Q1" integer,
    "Q3" character varying(30),
    "Q2" character varying(7),
    "Q6f" text,
    "Q6ff" text,
    "Q6g" text,
    "Q6gg" text,
    "Q0" integer,
    "Q3hh" text,
    "Q4d" integer,
    "Q4d1" integer,
    "Q4" integer,
    "Q4e1" integer,
    "Q4c" integer,
    "Q4c1" integer,
    "Q13" integer,
    "Q13e1" integer,
    "Q7gg" text,
    "Q4gg" text,
    "Q4d2" integer,
    "Q4e2" integer,
    "Q4c2" integer,
    "Q13e2" integer,
    "Q14b" text,
    "Q14c" text,
    "Q14d" text,
    "Q18a" integer,
    "Q18b" integer,
    "Q18c_0" boolean NOT NULL,
    "Q18c_1" boolean NOT NULL,
    "Q18c_2" boolean NOT NULL,
    "Q18c_3" boolean NOT NULL,
    "Q18c_4" boolean NOT NULL,
    "Q18c_5" boolean NOT NULL,
    "Q18d_0" boolean NOT NULL,
    "Q18d_1" boolean NOT NULL,
    "Q18d_2" boolean NOT NULL,
    "Q18d_3" boolean NOT NULL,
    "Q18d_4" boolean NOT NULL,
    "Q18d_5" boolean NOT NULL,
    CONSTRAINT "pollster_results_intake_Q0_check1" CHECK (("Q0" >= 0)),
    CONSTRAINT "pollster_results_intake_Q13_check1" CHECK (("Q13" >= 0)),
    CONSTRAINT "pollster_results_intake_Q13e1_check1" CHECK (("Q13e1" >= 0)),
    CONSTRAINT "pollster_results_intake_Q13e2_check1" CHECK (("Q13e2" >= 0)),
    CONSTRAINT "pollster_results_intake_Q18a_check1" CHECK (("Q18a" >= 0)),
    CONSTRAINT "pollster_results_intake_Q18b_check1" CHECK (("Q18b" >= 0)),
    CONSTRAINT "pollster_results_intake_Q1_check1" CHECK (("Q1" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4_check1" CHECK (("Q4" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4c1_check1" CHECK (("Q4c1" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4c2_check1" CHECK (("Q4c2" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4c_check1" CHECK (("Q4c" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4d1_check1" CHECK (("Q4d1" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4d2_check1" CHECK (("Q4d2" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4d_check1" CHECK (("Q4d" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4e1_check1" CHECK (("Q4e1" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4e2_check1" CHECK (("Q4e2" >= 0))
);


ALTER TABLE public.pollster_results_intake OWNER TO admin;

--
-- Name: pollster_results_intake_id_seq1; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE pollster_results_intake_id_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pollster_results_intake_id_seq1 OWNER TO admin;

--
-- Name: pollster_results_intake_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE pollster_results_intake_id_seq1 OWNED BY pollster_results_intake.id;


--
-- Name: pollster_results_weekly; Type: TABLE; Schema: public; Owner: admin; Tablespace: 
--

CREATE TABLE pollster_results_weekly (
    id integer NOT NULL,
    "user" integer,
    global_id character varying(36),
    channel character varying(36),
    "timestamp" timestamp with time zone,
    "Q0" character varying(7),
    "Q6k" text,
    "Q1a" integer,
    "Q1aa" integer,
    "Q1b" integer,
    "Q1bb" integer,
    "Q1c" text,
    "Q1_0" boolean NOT NULL,
    "Q1_1" boolean NOT NULL,
    "Q1_2" boolean NOT NULL,
    "Q1_4" boolean NOT NULL,
    "Q1_5" boolean NOT NULL,
    "Q1_3" boolean NOT NULL,
    "Q1_6" boolean NOT NULL,
    "Q1_13" boolean NOT NULL,
    "Q1_7" boolean NOT NULL,
    "Q1_10" boolean NOT NULL,
    "Q1_11" boolean NOT NULL,
    "Q1_9" boolean NOT NULL,
    "Q1_8" boolean NOT NULL,
    "Q1_12" boolean NOT NULL,
    "Q1_14" boolean NOT NULL,
    "Q1_18" boolean NOT NULL,
    "Q1_22" boolean NOT NULL,
    "Q1_15" boolean NOT NULL,
    "Q1_16" boolean NOT NULL,
    "Q1_17" boolean NOT NULL,
    "Q1_20" boolean NOT NULL,
    "Q1_21" boolean NOT NULL,
    "Q1_19" boolean NOT NULL,
    "Q111_0" boolean NOT NULL,
    "Q111_1" boolean NOT NULL,
    "Q111_2" boolean NOT NULL,
    "Q111_4" boolean NOT NULL,
    "Q111_5" boolean NOT NULL,
    "Q111_3" boolean NOT NULL,
    "Q111_6" boolean NOT NULL,
    "Q111_13" boolean NOT NULL,
    "Q111_7" boolean NOT NULL,
    "Q111_10" boolean NOT NULL,
    "Q111_11" boolean NOT NULL,
    "Q111_9" boolean NOT NULL,
    "Q111_8" boolean NOT NULL,
    "Q111_12" boolean NOT NULL,
    "Q111_14" boolean NOT NULL,
    "Q111_18" boolean NOT NULL,
    "Q111_22" boolean NOT NULL,
    "Q111_15" boolean NOT NULL,
    "Q111_16" boolean NOT NULL,
    "Q111_17" boolean NOT NULL,
    "Q111_20" boolean NOT NULL,
    "Q111_21" boolean NOT NULL,
    "Q111_19" boolean NOT NULL,
    "Q5" integer,
    "Q6d" integer,
    "Q6b" integer,
    "Q6e" integer,
    "Q6ee" integer,
    "Q6f" integer,
    "Q6ff" integer,
    "Q3" integer,
    "Q3_0_open" date,
    "Q11" integer,
    "Q6g" text,
    "Q6h" text,
    "Q6i" text,
    "Q6j" text,
    "Q1d" integer,
    "Q1e" integer,
    "Q14c_0" boolean NOT NULL,
    "Q14c_1" boolean NOT NULL,
    "Q14c_2" boolean NOT NULL,
    "Q14c_3" boolean NOT NULL,
    "Q14c_4" boolean NOT NULL,
    "Q14c_5" boolean NOT NULL,
    "Q14d_0" boolean NOT NULL,
    "Q14d_1" boolean NOT NULL,
    "Q14d_2" boolean NOT NULL,
    "Q14d_3" boolean NOT NULL,
    "Q14d_4" boolean NOT NULL,
    "Q14d_5" boolean NOT NULL,
    CONSTRAINT "pollster_results_weekly_Q11_check" CHECK (("Q11" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q1a_check" CHECK (("Q1a" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q1aa_check" CHECK (("Q1aa" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q1b_check" CHECK (("Q1b" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q1bb_check" CHECK (("Q1bb" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q1d_check" CHECK (("Q1d" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q1e_check" CHECK (("Q1e" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q3_check" CHECK (("Q3" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q5_check" CHECK (("Q5" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6b_check" CHECK (("Q6b" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6d_check" CHECK (("Q6d" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6e_check" CHECK (("Q6e" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6ee_check" CHECK (("Q6ee" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6f_check" CHECK (("Q6f" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6ff_check" CHECK (("Q6ff" >= 0))
);


ALTER TABLE public.pollster_results_weekly OWNER TO admin;

--
-- Name: pollster_results_weekly_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE pollster_results_weekly_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pollster_results_weekly_id_seq OWNER TO admin;

--
-- Name: pollster_results_weekly_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE pollster_results_weekly_id_seq OWNED BY pollster_results_weekly.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY pollster_results_intake ALTER COLUMN id SET DEFAULT nextval('pollster_results_intake_id_seq1'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY pollster_results_weekly ALTER COLUMN id SET DEFAULT nextval('pollster_results_weekly_id_seq'::regclass);


--
-- Data for Name: pollster_results_intake; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY pollster_results_intake (id, "user", global_id, channel, "timestamp", "Q1", "Q3", "Q2", "Q6f", "Q6ff", "Q6g", "Q6gg", "Q0", "Q3hh", "Q4d", "Q4d1", "Q4", "Q4e1", "Q4c", "Q4c1", "Q13", "Q13e1", "Q7gg", "Q4gg", "Q4d2", "Q4e2", "Q4c2", "Q13e2", "Q14b", "Q14c", "Q14d", "Q18a", "Q18b", "Q18c_0", "Q18c_1", "Q18c_2", "Q18c_3", "Q18c_4", "Q18c_5", "Q18d_0", "Q18d_1", "Q18d_2", "Q18d_3", "Q18d_4", "Q18d_5") FROM stdin;
\.


--
-- Name: pollster_results_intake_id_seq1; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('pollster_results_intake_id_seq1', 1, false);


--
-- Data for Name: pollster_results_weekly; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY pollster_results_weekly (id, "user", global_id, channel, "timestamp", "Q0", "Q6k", "Q1a", "Q1aa", "Q1b", "Q1bb", "Q1c", "Q1_0", "Q1_1", "Q1_2", "Q1_4", "Q1_5", "Q1_3", "Q1_6", "Q1_13", "Q1_7", "Q1_10", "Q1_11", "Q1_9", "Q1_8", "Q1_12", "Q1_14", "Q1_18", "Q1_22", "Q1_15", "Q1_16", "Q1_17", "Q1_20", "Q1_21", "Q1_19", "Q111_0", "Q111_1", "Q111_2", "Q111_4", "Q111_5", "Q111_3", "Q111_6", "Q111_13", "Q111_7", "Q111_10", "Q111_11", "Q111_9", "Q111_8", "Q111_12", "Q111_14", "Q111_18", "Q111_22", "Q111_15", "Q111_16", "Q111_17", "Q111_20", "Q111_21", "Q111_19", "Q5", "Q6d", "Q6b", "Q6e", "Q6ee", "Q6f", "Q6ff", "Q3", "Q3_0_open", "Q11", "Q6g", "Q6h", "Q6i", "Q6j", "Q1d", "Q1e", "Q14c_0", "Q14c_1", "Q14c_2", "Q14c_3", "Q14c_4", "Q14c_5", "Q14d_0", "Q14d_1", "Q14d_2", "Q14d_3", "Q14d_4", "Q14d_5") FROM stdin;
\.


--
-- Name: pollster_results_weekly_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('pollster_results_weekly_id_seq', 1, false);


--
-- Name: pollster_results_intake_pkey1; Type: CONSTRAINT; Schema: public; Owner: admin; Tablespace: 
--

ALTER TABLE ONLY pollster_results_intake
    ADD CONSTRAINT pollster_results_intake_pkey1 PRIMARY KEY (id);


--
-- Name: pollster_results_weekly_pkey; Type: CONSTRAINT; Schema: public; Owner: admin; Tablespace: 
--

ALTER TABLE ONLY pollster_results_weekly
    ADD CONSTRAINT pollster_results_weekly_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

