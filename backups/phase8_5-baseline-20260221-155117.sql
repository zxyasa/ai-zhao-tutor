--
-- PostgreSQL database dump
--

\restrict HRAo7hci8l3vof8pGEzOZIewHhjz9qz9havrIvwegZvuES3NYjkhohgz4xrEJbi

-- Dumped from database version 15.16 (Debian 15.16-1.pgdg13+1)
-- Dumped by pg_dump version 15.16 (Debian 15.16-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: achievements; Type: TABLE; Schema: public; Owner: mathcoach
--

CREATE TABLE public.achievements (
    id character varying NOT NULL,
    student_id character varying NOT NULL,
    badge_key character varying NOT NULL,
    title character varying NOT NULL,
    description character varying NOT NULL,
    unlocked_at timestamp without time zone NOT NULL
);


ALTER TABLE public.achievements OWNER TO mathcoach;

--
-- Name: daily_sessions; Type: TABLE; Schema: public; Owner: mathcoach
--

CREATE TABLE public.daily_sessions (
    id character varying NOT NULL,
    student_id character varying NOT NULL,
    session_date date NOT NULL,
    started_at timestamp without time zone NOT NULL,
    completed_questions integer NOT NULL,
    target_questions integer NOT NULL,
    is_completed boolean NOT NULL,
    completed_at timestamp without time zone
);


ALTER TABLE public.daily_sessions OWNER TO mathcoach;

--
-- Name: events; Type: TABLE; Schema: public; Owner: mathcoach
--

CREATE TABLE public.events (
    id character varying NOT NULL,
    student_id character varying NOT NULL,
    item_id character varying NOT NULL,
    answer_given character varying NOT NULL,
    is_correct boolean NOT NULL,
    time_spent double precision NOT NULL,
    hint_requested boolean,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.events OWNER TO mathcoach;

--
-- Name: items; Type: TABLE; Schema: public; Owner: mathcoach
--

CREATE TABLE public.items (
    id character varying NOT NULL,
    skill_id character varying NOT NULL,
    question_text text NOT NULL,
    question_type character varying NOT NULL,
    difficulty integer NOT NULL,
    parameters json NOT NULL,
    correct_answer character varying NOT NULL,
    hint text,
    explanation text NOT NULL,
    validation_rule character varying NOT NULL
);


ALTER TABLE public.items OWNER TO mathcoach;

--
-- Name: mastery; Type: TABLE; Schema: public; Owner: mathcoach
--

CREATE TABLE public.mastery (
    student_id character varying NOT NULL,
    skill_id character varying NOT NULL,
    total_attempts integer NOT NULL,
    correct_attempts integer NOT NULL,
    mastery_score double precision NOT NULL,
    last_updated timestamp without time zone NOT NULL
);


ALTER TABLE public.mastery OWNER TO mathcoach;

--
-- Name: parents; Type: TABLE; Schema: public; Owner: mathcoach
--

CREATE TABLE public.parents (
    id character varying NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    display_name character varying,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.parents OWNER TO mathcoach;

--
-- Name: students; Type: TABLE; Schema: public; Owner: mathcoach
--

CREATE TABLE public.students (
    id character varying NOT NULL,
    name character varying NOT NULL,
    year_level integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    avatar character varying DEFAULT 'star'::character varying NOT NULL,
    target_daily_questions integer DEFAULT 10 NOT NULL,
    current_streak integer DEFAULT 0 NOT NULL,
    longest_streak integer DEFAULT 0 NOT NULL,
    last_practice_date date,
    total_sessions integer DEFAULT 0 NOT NULL,
    parent_id character varying,
    pin_hash character varying
);


ALTER TABLE public.students OWNER TO mathcoach;

--
-- Data for Name: achievements; Type: TABLE DATA; Schema: public; Owner: mathcoach
--

COPY public.achievements (id, student_id, badge_key, title, description, unlocked_at) FROM stdin;
16dc2ad4-a140-4217-82cf-9865851cc3ea	astrid_zhao	sessions_20	练习达人	累计完成 20 次答题	2026-02-20 20:07:34
563a662f-8cf6-439c-902f-ceb6c408ec28	astrid_zhao	daily_goal_1	今日达标	首次完成每日目标	2026-02-20 20:14:13
\.


--
-- Data for Name: daily_sessions; Type: TABLE DATA; Schema: public; Owner: mathcoach
--

COPY public.daily_sessions (id, student_id, session_date, started_at, completed_questions, target_questions, is_completed, completed_at) FROM stdin;
db6bdd1a-d2af-49fc-9921-eb473ab7b1dd	astrid_zhao	2026-02-20	2026-02-20 09:10:35.571671	42	40	t	2026-02-20 20:14:13
6e39f5d8-2d76-4331-986c-ed7e1615715e	jon_zhao	2026-02-20	2026-02-20 09:09:07.624848	14	40	f	\N
68c24609-7f72-4d41-a918-7474373a42af	astrid_zhao	2026-02-21	2026-02-21 04:26:58.123317	0	40	f	\N
\.


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: mathcoach
--

COPY public.events (id, student_id, item_id, answer_given, is_correct, time_spent, hint_requested, "timestamp") FROM stdin;
494027EC-A7B3-4001-8D30-AB42C361654B	test_001	yr3_frac_compare_001_d1_6070	4	f	3.8679169416427612	f	2026-02-13 08:50:16
5624D3C1-B644-4F44-A1D0-4D6F97ED68F2	test_001	yr3_frac_compare_001_d3_3675	fd	f	3.4858709573745728	f	2026-02-13 08:50:24
C98A97CD-FE05-4CC9-BFF4-489539DDC1B6	test_001	yr3_frac_compare_001_d2_4164	12/13	t	10.80291998386383	f	2026-02-13 08:50:38
255D775A-6D35-4BEA-BB42-36ED665E1AEE	test_001	yr3_frac_compare_001_d3_4516	7/9	t	13.841572999954224	f	2026-02-13 08:50:54
FA261D12-F677-4C54-BD4B-EFFB08B32778	test_001	yr3_frac_compare_001_d3_6083	4/6	t	7.359594941139221	f	2026-02-13 08:51:09
260FACF7-0F6F-4803-AB2A-33F4AE663759	test_001	yr3_frac_compare_001_d3_1432	6/9	t	4.761468052864075	f	2026-02-13 08:51:18
F4759DA1-4A01-445F-9F04-C1714E9E5996	test_001	yr3_frac_compare_001_d3_8425	4/12	t	7.580534934997559	f	2026-02-13 08:51:27
4BE1941A-14F9-416D-A78C-E71A854F4999	test_001	yr3_frac_compare_001_d3_4034	r	f	2.890120029449463	f	2026-02-13 08:51:31
2A469548-B482-45CC-92F2-A2BA6362EE8E	test_001	yr3_frac_compare_001_d2_2060	e	f	1.3866689205169678	f	2026-02-13 08:51:34
88C5DF69-A64E-4E3F-947F-9ECFE0D44FCD	test_001	yr3_frac_compare_001_d2_7100	g	f	1.7605220079421997	f	2026-02-13 08:51:36
73FAA341-55DA-4CED-8E0A-E3A89A72CCA0	test_001	yr3_frac_compare_001_d3_8063	s	f	1.2491170167922974	f	2026-02-13 08:51:39
499340B3-E9DC-4DCE-88CA-A462B62BAD65	test_001	yr3_frac_compare_001_d3_3164	w	f	1.7167179584503174	f	2026-02-13 08:51:41
2FC0C697-4026-4074-916D-876EEA5FA7A9	test_001	yr3_frac_compare_001_d3_1432	w2	f	2.2154829502105713	f	2026-02-13 08:51:44
A96CBA50-EF0B-470B-9112-CB3F7E89EBA9	test_001	yr3_frac_compare_001_d2_3611	6/16	t	7.922019004821777	f	2026-02-13 08:51:53
B67DE0F4-01C7-4C1B-87CE-7FE7AF57EE3F	test_001	yr3_frac_compare_001_d3_8425	f	f	4.832843899726868	f	2026-02-13 08:51:59
C7CBEC91-2C6D-4518-9CB6-C2DB4D4D81F7	test_001	yr3_frac_compare_001_d2_3345	gsg	f	2.446855068206787	f	2026-02-13 08:52:03
0821B52A-B9D8-43DB-87AA-B72892D5D7DE	test_001	yr3_frac_compare_001_d1_6070	sgs	f	1.140447974205017	f	2026-02-13 08:52:05
7A691BD8-4A07-4D0C-A265-B6A95775ADCF	test_001	yr3_frac_compare_001_d1_3704	tretw	f	1.2027969360351562	f	2026-02-13 08:52:08
2240088B-570F-48D5-B8B1-E4D17AE4EF91	test_001	yr3_frac_compare_001_d3_1432	444	f	2.3258529901504517	f	2026-02-13 08:52:15
evt_fix_check_001	jon_zhao	jon_add_0ef1430c-7caf-4319-8024-e329dbe81ed9	62	t	2.1	f	2026-02-20 09:24:00
202C1C59-10C7-4C63-9B3D-94E77ED636BF	jon_zhao	jon_add_b73840eb-c10c-4a9e-a573-f76388c28fe5	33	f	3.539808988571167	f	2026-02-20 09:23:14
74E750FF-85B5-4293-93F9-3BACB144E3E8	jon_zhao	jon_add_a663d770-44fc-4a74-9931-a2af92a02fef	67	t	5.231133937835693	f	2026-02-20 09:23:29
45DF5791-74D5-44AB-82EA-585A24EA04FA	jon_zhao	jon_add_afdf4733-aff0-4975-9c73-5862d52d7b67	Fa	f	2.8811709880828857	f	2026-02-20 09:23:36
0C5F7634-A1E9-46A2-B151-D43CBB26504A	jon_zhao	jon_add_e05bd8e2-c488-4e12-a6e3-eaa7cb3e0c1f	75	t	15.714542984962463	f	2026-02-20 09:27:40
B13EE342-F223-4B2B-AFD3-9A66546B2916	jon_zhao	jon_sub_4b4424d6-3e8e-474f-a21f-875bfa071f9e	26	f	61.282625913619995	f	2026-02-20 09:48:52
89E63FD9-0211-46AE-BD22-71FA2208CFC4	astrid_zhao	astrid_missing_sub_93ea54e5-a77c-455e-ac5d-916507f5c925	23	t	17.216217041015625	f	2026-02-20 10:05:57
4E79B4CB-7F68-4A2A-A3B5-3F2499F5DCBF	astrid_zhao	astrid_missing_add_d9d16ed5-50f4-417e-af96-f1d09799925c	18	f	6.324595928192139	f	2026-02-20 10:06:06
8E0A350B-7C3A-4078-8AAA-F2E561A22183	astrid_zhao	astrid_missing_add_da6bbd37-0c7c-4d2e-bddf-4b0aa394e8b7	17	t	47.82870709896088	f	2026-02-20 10:15:13
18BFF618-9416-47E9-9F10-250355CF30DC	astrid_zhao	astrid_compare_24b999b3-d3d7-42af-9287-ec830fb4fa80	64	t	11.961068034172058	f	2026-02-20 10:16:23
9E0A9234-01A9-4D5E-9C70-12F5F0126C44	astrid_zhao	astrid_word_sub_f572e4bf-3581-4443-b3a5-e9c1f0bf7b12	36	f	35189.030525922775	f	2026-02-20 20:02:55
8F538304-B056-4995-87F0-6C73F193CF26	astrid_zhao	astrid_place_tens_a02ffd5c-7cf9-4e0a-ab0c-574cc32978e1	3	t	5.9099379777908325	f	2026-02-20 20:03:19
11537E34-D40A-41BE-8A9E-156EE88961ED	astrid_zhao	astrid_sub_ed24d85d-ba21-41e4-9b53-94f145cd31a8	0	f	14.195575952529907	f	2026-02-20 20:03:35
2690C000-139F-4648-A739-755C7600A44E	astrid_zhao	astrid_word_sub_524e7d8d-87c6-4f3d-b079-c3abcd6bcf64	16	f	8.103668928146362	f	2026-02-20 20:03:46
B9A44DFA-C2F5-4A70-815C-0DFA97E902F8	astrid_zhao	astrid_compare_2eaa2af9-b510-492b-a3cf-5f1c8a819908	80	t	12.064457893371582	f	2026-02-20 20:04:01
3C95CE30-F16B-4F1B-B0E2-18CAE5AAF027	astrid_zhao	astrid_add_bf69a56e-510d-4739-817d-8e768c88578b	18	t	6.400341033935547	f	2026-02-20 20:04:13
17F47E20-6B79-4F9B-9CA9-61799BC1E1D4	astrid_zhao	astrid_sub_ba2e70bd-f9a2-4e23-81ed-f25afbecf88b	0	t	4.402809023857117	f	2026-02-20 20:04:19
6C290EA1-5262-4166-8991-C57C0ED24435	astrid_zhao	astrid_compare_b97b5638-aa88-41d9-86ee-09b06c6d687d	24	t	7.715034008026123	f	2026-02-20 20:04:30
CED1986F-4492-4BF0-905C-39F9B3768AAD	astrid_zhao	astrid_place_tens_6c7deb01-d9db-4aaa-bdc0-466554b47dde	1	t	4.8223429918289185	f	2026-02-20 20:04:36
EBC29B0D-33BF-4335-B52B-1B1199F7127E	astrid_zhao	astrid_missing_add_e54995b0-7c32-4141-a52a-1cc4316a5470	6	t	10.962604999542236	f	2026-02-20 20:04:49
7B4D0B30-A5E9-4BE7-B944-F7DDEEED5C18	astrid_zhao	astrid_missing_add_dc608988-1f89-4eae-820e-2b114d84336f	10	t	16.332388043403625	f	2026-02-20 20:05:11
754AE8C6-AE13-4FEB-AA28-F80416C272FA	astrid_zhao	astrid_missing_sub_1f5ce220-5477-4157-b267-80c69d3da741	16	f	28.716737985610962	f	2026-02-20 20:05:42
FDF2E0A1-6170-4BF4-B09B-5B5FAE30F654	astrid_zhao	astrid_place_ones_5f58c6d1-088f-41d4-8169-2bdc892c25af	5	t	6.823667049407959	f	2026-02-20 20:06:10
E978171D-6820-4743-9F70-4AEB75741BC5	astrid_zhao	astrid_compare_31990df8-54d3-4f0a-b76d-dda6bec965c1	52	t	14.556704044342041	f	2026-02-20 20:06:28
B4BCF368-AB87-4048-8C13-8368F839240F	astrid_zhao	astrid_place_ones_6dc34852-3ccf-4f1e-942c-1563441e001b	0	t	5.289849042892456	f	2026-02-20 20:07:13
96B05319-9843-495B-8C9D-9E642254C974	astrid_zhao	astrid_missing_add_fd3650e2-5a5b-4084-81b5-9e86d2845eb8	12	f	18.45530593395233	f	2026-02-20 20:07:34
E6661C6F-3607-4772-A062-027A8DCD68F4	astrid_zhao	astrid_word_sub_c2e6c0fa-791d-498a-9e7c-fbcb6961a97a	24	f	8.375014066696167	f	2026-02-20 20:07:46
D3680442-7CD1-4CCB-9151-16219BBFAE66	astrid_zhao	astrid_place_tens_d9bc080f-5211-4bbc-a959-91b52a66196f	4	t	8.934331059455872	f	2026-02-20 20:08:07
66BF7343-FD50-45E9-A18A-9CA00E595CEF	astrid_zhao	astrid_missing_sub_3f0543ae-1b86-47cb-85ad-11f6ec29f90c	5	t	10.603049039840698	f	2026-02-20 20:08:18
E015E00B-C8E5-44A9-AA78-BCAED5BD8AFC	astrid_zhao	astrid_missing_add_a17cb705-1fa2-4012-be30-5304be7fbbe4	22	f	56.32337808609009	f	2026-02-20 20:09:50
A1248866-10E0-4ED9-95F8-1C16041FDEA4	astrid_zhao	astrid_add_f55eeb02-9c0a-4725-98ac-77e6d1469187	78	t	13.71199107170105	f	2026-02-20 20:10:08
17244496-0F83-4146-AF09-98E749323BCC	astrid_zhao	astrid_add_2839f2e2-b829-4e16-94de-86173fd0965b	59	t	14.88206696510315	f	2026-02-20 20:10:27
8926F60B-FE59-45D9-951C-BD345B9513ED	astrid_zhao	astrid_add_ff980080-02f3-4f1c-a3f0-6f9be6ed9cac	76	t	9.129536986351013	f	2026-02-20 20:10:38
9637CADA-8927-4852-8EC5-E7F7D0D68F27	astrid_zhao	astrid_word_add_c6623b63-a103-40d1-a521-eaa8d102c08c	28	t	33.103991985321045	f	2026-02-20 20:11:14
E17EE3D3-271B-4C1C-A07B-C825D0372487	astrid_zhao	astrid_compare_2079f4d5-029b-42a5-b9a6-1404fd796dc3	28	t	6.904510974884033	f	2026-02-20 20:11:34
748C2F67-A734-4648-B327-E3690BDA978E	astrid_zhao	astrid_sub_7b5d15c4-6be7-4c11-a2ed-78c2e7932133	59	f	37.52941596508026	f	2026-02-20 20:12:15
F61CEBCE-DDD6-4346-8ED2-A0F450FBE0E5	astrid_zhao	astrid_compare_36b90010-659a-4699-95b4-d6dfd40c4439	84	t	10.013657093048096	f	2026-02-20 20:12:27
9B791E9F-C64E-4670-BD5A-0869107FB066	astrid_zhao	astrid_place_tens_943bfe44-4638-4297-a569-a877f9c37314	1	t	7.970414996147156	f	2026-02-20 20:12:39
2EB6486A-F794-49E3-881F-E17F23FFA1DA	astrid_zhao	astrid_add_519ea212-aece-4b83-b80f-107ff8d1369c	66	t	8.87361192703247	f	2026-02-20 20:12:49
C9A12E64-DB3D-4962-B201-1E54FB26EC59	astrid_zhao	astrid_word_add_22745105-c3b2-4bf8-97ed-6642b13d58fb	35	f	11.850026965141296	f	2026-02-20 20:13:02
7A1DAEB9-1F80-47A2-8830-3B31656F3377	astrid_zhao	astrid_compare_8887041c-c2a2-499f-bc34-637df82420ea	48	t	9.42935597896576	f	2026-02-20 20:13:14
80A8BE06-E6A0-4F7E-BFB0-935309C231F9	astrid_zhao	astrid_add_7e2fd2ad-1b52-4b6a-bb6d-2a45edb48b26	23	t	5.885579943656921	f	2026-02-20 20:13:22
0AB32208-C4BC-4D7D-BFAD-DF625A7C2701	astrid_zhao	astrid_compare_d64b1b82-9baf-465f-92e2-3b02729d7e75	85	t	10.683194041252136	f	2026-02-20 20:13:34
407C5B73-B1F0-4E0E-BDF0-26434065DCCF	astrid_zhao	astrid_word_add_07239fba-32ee-4f0b-b5b8-20ec745629d8	23	f	9.7479909658432	f	2026-02-20 20:13:45
2B84C4E9-AC00-4EB0-AC46-83F933EA5376	astrid_zhao	astrid_compare_556a8dae-38d1-466f-8b98-8919919e6b5b	80	t	5.849521040916443	f	2026-02-20 20:13:53
6EDC0411-92AE-4F27-ABFF-78A008E8EF79	astrid_zhao	astrid_missing_add_8580aeff-6c4d-43b6-ac2d-3d4de5b38cc6	22	f	18.988693952560425	f	2026-02-20 20:14:13
5D15A146-F847-4F47-BB82-6A2A53156EFC	astrid_zhao	astrid_missing_sub_96b45e07-9ba5-49b9-9799-71a8f8231733	23	f	37.34388196468353	f	2026-02-20 20:14:53
09A08FE1-5C94-4794-B4A6-3DF9E9886094	astrid_zhao	astrid_missing_sub_9d6660a1-a3b4-4c7a-ab06-e87ca326d632	15	f	23.352519989013672	f	2026-02-20 20:15:18
619DD3E8-EFBA-4F0F-A655-0C52FF524139	jon_zhao	jon_sub_e125cdb7-c119-422d-9db9-db345c190f90	 21	f	47920.209371089935	f	2026-02-20 23:08:02
6BDCCCF0-8847-4C2D-8945-8B599A19AD06	jon_zhao	jon_add_a18c1a26-91e4-47eb-ae0c-3b8822df8488	64	t	70.1857830286026	f	2026-02-20 23:09:15
3A7E3DBA-A81C-45F8-8586-A099F9DFD220	jon_zhao	jon_sub_0b97afc1-a7f9-48a0-b9cb-250cae31dbc3	27	f	30.153601050376892	f	2026-02-20 23:09:51
2D4B5DC7-14DE-4E3B-BF79-44B5B733AE9D	jon_zhao	jon_add_105ebb08-dc88-441c-8095-27a07ce3630b	61	t	297.29296803474426	f	2026-02-20 23:15:20
7711B5D0-F3F8-4F74-97C3-ABEE65F6D710	jon_zhao	jon_sub_d60c3fc5-1fd8-4262-863c-57fd5b317ec8	26	f	34.19698703289032	f	2026-02-20 23:15:58
9AECB2C4-C2FF-464B-A5A3-AC5DE93066A1	jon_zhao	jon_add_b09be1a3-3fcc-45ec-9efb-bd398ec42cf0	74	t	43.30355095863342	f	2026-02-20 23:16:46
F4090B1F-83D9-4336-BC9E-E79FB30DF988	jon_zhao	jon_add_cd314da1-0546-4d4f-a778-a04bb836aa9e	56	t	56.84078598022461	f	2026-02-20 23:17:45
A6859221-B524-4244-A057-4CC448C8CF41	jon_zhao	jon_add_9be9eb60-fa2b-45e8-bac6-fa275ddff87d	66	t	751.270406961441	f	2026-02-20 23:30:18
\.


--
-- Data for Name: items; Type: TABLE DATA; Schema: public; Owner: mathcoach
--

COPY public.items (id, skill_id, question_text, question_type, difficulty, parameters, correct_answer, hint, explanation, validation_rule) FROM stdin;
yr3_frac_compare_001_d1_5029	yr3_frac_compare_001	Which is larger: 2/3 or 1/3?	fraction	1	{"num1": 2, "num2": 1, "denom1": 3, "denom2": 3}	2/3	When denominators are the same, compare the numerators	Since both fractions have denominator 3, we compare numerators: 2 > 1, so 2/3 is larger	exact_match
yr3_frac_compare_001_d1_2099	yr3_frac_compare_001	Which is larger: 5/6 or 3/6?	fraction	1	{"num1": 5, "num2": 3, "denom1": 6, "denom2": 6}	5/6	When denominators are the same, compare the numerators	Since both fractions have denominator 6, we compare numerators: 5 > 3, so 5/6 is larger	exact_match
yr3_frac_compare_001_d1_5187	yr3_frac_compare_001	Which is larger: 5/8 or 7/8?	fraction	1	{"num1": 5, "num2": 7, "denom1": 8, "denom2": 8}	7/8	When denominators are the same, compare the numerators	Since both fractions have denominator 8, we compare numerators: 7 > 5, so 7/8 is larger	exact_match
yr3_frac_compare_001_d1_6070	yr3_frac_compare_001	Which is larger: 3/8 or 6/8?	fraction	1	{"num1": 3, "num2": 6, "denom1": 8, "denom2": 8}	6/8	When denominators are the same, compare the numerators	Since both fractions have denominator 8, we compare numerators: 6 > 3, so 6/8 is larger	exact_match
yr3_frac_compare_001_d1_1147	yr3_frac_compare_001	Which is larger: 1/10 or 3/10?	fraction	1	{"num1": 1, "num2": 3, "denom1": 10, "denom2": 10}	3/10	When denominators are the same, compare the numerators	Since both fractions have denominator 10, we compare numerators: 3 > 1, so 3/10 is larger	exact_match
yr3_frac_compare_001_d1_3704	yr3_frac_compare_001	Which is larger: 2/6 or 1/6?	fraction	1	{"num1": 2, "num2": 1, "denom1": 6, "denom2": 6}	2/6	When denominators are the same, compare the numerators	Since both fractions have denominator 6, we compare numerators: 2 > 1, so 2/6 is larger	exact_match
yr3_frac_compare_001_d1_8286	yr3_frac_compare_001	Which is larger: 3/7 or 4/7?	fraction	1	{"num1": 3, "num2": 4, "denom1": 7, "denom2": 7}	4/7	When denominators are the same, compare the numerators	Since both fractions have denominator 7, we compare numerators: 4 > 3, so 4/7 is larger	exact_match
yr3_frac_compare_001_d1_6374	yr3_frac_compare_001	Which is larger: 2/4 or 3/4?	fraction	1	{"num1": 2, "num2": 3, "denom1": 4, "denom2": 4}	3/4	When denominators are the same, compare the numerators	Since both fractions have denominator 4, we compare numerators: 3 > 2, so 3/4 is larger	exact_match
yr3_frac_compare_001_d1_2002	yr3_frac_compare_001	Which is larger: 4/5 or 1/5?	fraction	1	{"num1": 4, "num2": 1, "denom1": 5, "denom2": 5}	4/5	When denominators are the same, compare the numerators	Since both fractions have denominator 5, we compare numerators: 4 > 1, so 4/5 is larger	exact_match
yr3_frac_compare_001_d1_8507	yr3_frac_compare_001	Which is larger: 3/7 or 5/7?	fraction	1	{"num1": 3, "num2": 5, "denom1": 7, "denom2": 7}	5/7	When denominators are the same, compare the numerators	Since both fractions have denominator 7, we compare numerators: 5 > 3, so 5/7 is larger	exact_match
yr3_frac_compare_001_d2_3443	yr3_frac_compare_001	Which is larger: 9/11 or 8/11?	fraction	2	{"num1": 9, "num2": 8, "denom1": 11, "denom2": 11}	9/11	When denominators are the same, which numerator is larger?	Both fractions have denominator 11. Compare numerators: 9 > 8	exact_match
yr3_frac_compare_001_d2_3345	yr3_frac_compare_001	Which is larger: 1/3 or 2/3?	fraction	2	{"num1": 1, "num2": 2, "denom1": 3, "denom2": 3}	2/3	When denominators are the same, which numerator is larger?	Both fractions have denominator 3. Compare numerators: 2 > 1	exact_match
yr3_frac_compare_001_d2_3611	yr3_frac_compare_001	Which is larger: 6/16 or 2/16?	fraction	2	{"num1": 6, "num2": 2, "denom1": 16, "denom2": 16}	6/16	When denominators are the same, which numerator is larger?	Both fractions have denominator 16. Compare numerators: 6 > 2	exact_match
yr3_frac_compare_001_d2_2060	yr3_frac_compare_001	Which is larger: 2/3 or 1/3?	fraction	2	{"num1": 2, "num2": 1, "denom1": 3, "denom2": 3}	2/3	When denominators are the same, which numerator is larger?	Both fractions have denominator 3. Compare numerators: 2 > 1	exact_match
yr3_frac_compare_001_d2_7100	yr3_frac_compare_001	Which is larger: 11/17 or 14/17?	fraction	2	{"num1": 11, "num2": 14, "denom1": 17, "denom2": 17}	14/17	When denominators are the same, which numerator is larger?	Both fractions have denominator 17. Compare numerators: 14 > 11	exact_match
yr3_frac_compare_001_d2_2958	yr3_frac_compare_001	Which is larger: 1/4 or 3/4?	fraction	2	{"num1": 1, "num2": 3, "denom1": 4, "denom2": 4}	3/4	When denominators are the same, which numerator is larger?	Both fractions have denominator 4. Compare numerators: 3 > 1	exact_match
yr3_frac_compare_001_d2_1805	yr3_frac_compare_001	Which is larger: 6/12 or 5/12?	fraction	2	{"num1": 6, "num2": 5, "denom1": 12, "denom2": 12}	6/12	When denominators are the same, which numerator is larger?	Both fractions have denominator 12. Compare numerators: 6 > 5	exact_match
yr3_frac_compare_001_d2_2510	yr3_frac_compare_001	Which is larger: 5/14 or 12/14?	fraction	2	{"num1": 5, "num2": 12, "denom1": 14, "denom2": 14}	12/14	When denominators are the same, which numerator is larger?	Both fractions have denominator 14. Compare numerators: 12 > 5	exact_match
yr3_frac_compare_001_d2_9841	yr3_frac_compare_001	Which is larger: 10/16 or 7/16?	fraction	2	{"num1": 10, "num2": 7, "denom1": 16, "denom2": 16}	10/16	When denominators are the same, which numerator is larger?	Both fractions have denominator 16. Compare numerators: 10 > 7	exact_match
yr3_frac_compare_001_d2_4164	yr3_frac_compare_001	Which is larger: 12/13 or 1/13?	fraction	2	{"num1": 12, "num2": 1, "denom1": 13, "denom2": 13}	12/13	When denominators are the same, which numerator is larger?	Both fractions have denominator 13. Compare numerators: 12 > 1	exact_match
yr3_frac_compare_001_d3_3164	yr3_frac_compare_001	Which is larger: 4/5 or 10/15?	fraction	3	{"num1": 4, "num2": 10, "denom1": 5, "denom2": 15}	4/5	Find a common denominator to compare fractions with different denominators	Convert to common denominator 15: 4/5 = 12/15 and 10/15 = 10/15. Then compare numerators.	exact_match
yr3_frac_compare_001_d3_1432	yr3_frac_compare_001	Which is larger: 1/3 or 6/9?	fraction	3	{"num1": 1, "num2": 6, "denom1": 3, "denom2": 9}	6/9	Find a common denominator to compare fractions with different denominators	Convert to common denominator 9: 1/3 = 3/9 and 6/9 = 6/9. Then compare numerators.	exact_match
yr3_frac_compare_001_d3_8425	yr3_frac_compare_001	Which is larger: 1/4 or 4/12?	fraction	3	{"num1": 1, "num2": 4, "denom1": 4, "denom2": 12}	4/12	Find a common denominator to compare fractions with different denominators	Convert to common denominator 12: 1/4 = 3/12 and 4/12 = 4/12. Then compare numerators.	exact_match
yr3_frac_compare_001_d3_6338	yr3_frac_compare_001	Which is larger: 4/5 or 7/15?	fraction	3	{"num1": 4, "num2": 7, "denom1": 5, "denom2": 15}	4/5	Find a common denominator to compare fractions with different denominators	Convert to common denominator 15: 4/5 = 12/15 and 7/15 = 7/15. Then compare numerators.	exact_match
yr3_frac_compare_001_d3_6083	yr3_frac_compare_001	Which is larger: 1/2 or 4/6?	fraction	3	{"num1": 1, "num2": 4, "denom1": 2, "denom2": 6}	4/6	Find a common denominator to compare fractions with different denominators	Convert to common denominator 6: 1/2 = 3/6 and 4/6 = 4/6. Then compare numerators.	exact_match
yr3_frac_compare_001_d3_5570	yr3_frac_compare_001	Which is larger: 1/2 or 1/6?	fraction	3	{"num1": 1, "num2": 1, "denom1": 2, "denom2": 6}	1/2	Find a common denominator to compare fractions with different denominators	Convert to common denominator 6: 1/2 = 3/6 and 1/6 = 1/6. Then compare numerators.	exact_match
yr3_frac_compare_001_d3_8063	yr3_frac_compare_001	Which is larger: 3/5 or 9/10?	fraction	3	{"num1": 3, "num2": 9, "denom1": 5, "denom2": 10}	9/10	Find a common denominator to compare fractions with different denominators	Convert to common denominator 10: 3/5 = 6/10 and 9/10 = 9/10. Then compare numerators.	exact_match
yr3_frac_compare_001_d3_3675	yr3_frac_compare_001	Which is larger: 2/4 or 11/12?	fraction	3	{"num1": 2, "num2": 11, "denom1": 4, "denom2": 12}	11/12	Find a common denominator to compare fractions with different denominators	Convert to common denominator 12: 2/4 = 6/12 and 11/12 = 11/12. Then compare numerators.	exact_match
yr3_frac_compare_001_d3_4516	yr3_frac_compare_001	Which is larger: 2/3 or 7/9?	fraction	3	{"num1": 2, "num2": 7, "denom1": 3, "denom2": 9}	7/9	Find a common denominator to compare fractions with different denominators	Convert to common denominator 9: 2/3 = 6/9 and 7/9 = 7/9. Then compare numerators.	exact_match
yr3_frac_compare_001_d3_4034	yr3_frac_compare_001	Which is larger: 4/5 or 3/15?	fraction	3	{"num1": 4, "num2": 3, "denom1": 5, "denom2": 15}	4/5	Find a common denominator to compare fractions with different denominators	Convert to common denominator 15: 4/5 = 12/15 and 3/15 = 3/15. Then compare numerators.	exact_match
yr4_frac_equiv_001_d1_8564	yr4_frac_equiv_001	What is an equivalent fraction to 4/5? (Use denominator 10)	fraction	1	{"base_num": 4, "base_denom": 5, "multiplier": 2}	8/10	Multiply both numerator and denominator by the same number	To get denominator 10, multiply 5 by 2. Also multiply numerator: 4 × 2 = 8	equivalent_fraction
yr4_frac_equiv_001_d1_4030	yr4_frac_equiv_001	What is an equivalent fraction to 1/5? (Use denominator 10)	fraction	1	{"base_num": 1, "base_denom": 5, "multiplier": 2}	2/10	Multiply both numerator and denominator by the same number	To get denominator 10, multiply 5 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d1_8288	yr4_frac_equiv_001	What is an equivalent fraction to 2/6? (Use denominator 12)	fraction	1	{"base_num": 2, "base_denom": 6, "multiplier": 2}	4/12	Multiply both numerator and denominator by the same number	To get denominator 12, multiply 6 by 2. Also multiply numerator: 2 × 2 = 4	equivalent_fraction
yr4_frac_equiv_001_d1_3563	yr4_frac_equiv_001	What is an equivalent fraction to 2/7? (Use denominator 14)	fraction	1	{"base_num": 2, "base_denom": 7, "multiplier": 2}	4/14	Multiply both numerator and denominator by the same number	To get denominator 14, multiply 7 by 2. Also multiply numerator: 2 × 2 = 4	equivalent_fraction
yr4_frac_equiv_001_d1_3317	yr4_frac_equiv_001	What is an equivalent fraction to 1/4? (Use denominator 8)	fraction	1	{"base_num": 1, "base_denom": 4, "multiplier": 2}	2/8	Multiply both numerator and denominator by the same number	To get denominator 8, multiply 4 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d1_4398	yr4_frac_equiv_001	What is an equivalent fraction to 1/2? (Use denominator 4)	fraction	1	{"base_num": 1, "base_denom": 2, "multiplier": 2}	2/4	Multiply both numerator and denominator by the same number	To get denominator 4, multiply 2 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d1_4550	yr4_frac_equiv_001	What is an equivalent fraction to 3/4? (Use denominator 8)	fraction	1	{"base_num": 3, "base_denom": 4, "multiplier": 2}	6/8	Multiply both numerator and denominator by the same number	To get denominator 8, multiply 4 by 2. Also multiply numerator: 3 × 2 = 6	equivalent_fraction
yr4_frac_equiv_001_d1_2744	yr4_frac_equiv_001	What is an equivalent fraction to 1/2? (Use denominator 4)	fraction	1	{"base_num": 1, "base_denom": 2, "multiplier": 2}	2/4	Multiply both numerator and denominator by the same number	To get denominator 4, multiply 2 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d1_1031	yr4_frac_equiv_001	What is an equivalent fraction to 1/6? (Use denominator 12)	fraction	1	{"base_num": 1, "base_denom": 6, "multiplier": 2}	2/12	Multiply both numerator and denominator by the same number	To get denominator 12, multiply 6 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d1_9737	yr4_frac_equiv_001	What is an equivalent fraction to 1/5? (Use denominator 10)	fraction	1	{"base_num": 1, "base_denom": 5, "multiplier": 2}	2/10	Multiply both numerator and denominator by the same number	To get denominator 10, multiply 5 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d2_4253	yr4_frac_equiv_001	What is an equivalent fraction to 2/3? (Use denominator 9)	fraction	2	{"base_num": 2, "base_denom": 3, "multiplier": 3}	6/9	Multiply both numerator and denominator by the same number	To get denominator 9, multiply 3 by 3. Also multiply numerator: 2 × 3 = 6	equivalent_fraction
yr4_frac_equiv_001_d2_6098	yr4_frac_equiv_001	What is an equivalent fraction to 1/2? (Use denominator 4)	fraction	2	{"base_num": 1, "base_denom": 2, "multiplier": 2}	2/4	Multiply both numerator and denominator by the same number	To get denominator 4, multiply 2 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d2_9821	yr4_frac_equiv_001	What is an equivalent fraction to 2/3? (Use denominator 9)	fraction	2	{"base_num": 2, "base_denom": 3, "multiplier": 3}	6/9	Multiply both numerator and denominator by the same number	To get denominator 9, multiply 3 by 3. Also multiply numerator: 2 × 3 = 6	equivalent_fraction
yr4_frac_equiv_001_d2_5749	yr4_frac_equiv_001	What is an equivalent fraction to 4/8? (Use denominator 24)	fraction	2	{"base_num": 4, "base_denom": 8, "multiplier": 3}	12/24	Multiply both numerator and denominator by the same number	To get denominator 24, multiply 8 by 3. Also multiply numerator: 4 × 3 = 12	equivalent_fraction
yr4_frac_equiv_001_d2_8356	yr4_frac_equiv_001	What is an equivalent fraction to 3/8? (Use denominator 16)	fraction	2	{"base_num": 3, "base_denom": 8, "multiplier": 2}	6/16	Multiply both numerator and denominator by the same number	To get denominator 16, multiply 8 by 2. Also multiply numerator: 3 × 2 = 6	equivalent_fraction
yr4_frac_equiv_001_d2_9068	yr4_frac_equiv_001	What is an equivalent fraction to 1/2? (Use denominator 4)	fraction	2	{"base_num": 1, "base_denom": 2, "multiplier": 2}	2/4	Multiply both numerator and denominator by the same number	To get denominator 4, multiply 2 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d2_2896	yr4_frac_equiv_001	What is an equivalent fraction to 3/6? (Use denominator 12)	fraction	2	{"base_num": 3, "base_denom": 6, "multiplier": 2}	6/12	Multiply both numerator and denominator by the same number	To get denominator 12, multiply 6 by 2. Also multiply numerator: 3 × 2 = 6	equivalent_fraction
yr4_frac_equiv_001_d2_6299	yr4_frac_equiv_001	What is an equivalent fraction to 2/3? (Use denominator 9)	fraction	2	{"base_num": 2, "base_denom": 3, "multiplier": 3}	6/9	Multiply both numerator and denominator by the same number	To get denominator 9, multiply 3 by 3. Also multiply numerator: 2 × 3 = 6	equivalent_fraction
yr4_frac_equiv_001_d2_2050	yr4_frac_equiv_001	What is an equivalent fraction to 3/5? (Use denominator 15)	fraction	2	{"base_num": 3, "base_denom": 5, "multiplier": 3}	9/15	Multiply both numerator and denominator by the same number	To get denominator 15, multiply 5 by 3. Also multiply numerator: 3 × 3 = 9	equivalent_fraction
yr4_frac_equiv_001_d2_2230	yr4_frac_equiv_001	What is an equivalent fraction to 1/5? (Use denominator 10)	fraction	2	{"base_num": 1, "base_denom": 5, "multiplier": 2}	2/10	Multiply both numerator and denominator by the same number	To get denominator 10, multiply 5 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d3_9132	yr4_frac_equiv_001	What is an equivalent fraction to 1/2? (Use denominator 10)	fraction	3	{"base_num": 1, "base_denom": 2, "multiplier": 5}	5/10	Multiply both numerator and denominator by the same number	To get denominator 10, multiply 2 by 5. Also multiply numerator: 1 × 5 = 5	equivalent_fraction
yr4_frac_equiv_001_d3_1981	yr4_frac_equiv_001	What is an equivalent fraction to 1/2? (Use denominator 6)	fraction	3	{"base_num": 1, "base_denom": 2, "multiplier": 3}	3/6	Multiply both numerator and denominator by the same number	To get denominator 6, multiply 2 by 3. Also multiply numerator: 1 × 3 = 3	equivalent_fraction
yr4_frac_equiv_001_d3_4219	yr4_frac_equiv_001	What is an equivalent fraction to 1/2? (Use denominator 10)	fraction	3	{"base_num": 1, "base_denom": 2, "multiplier": 5}	5/10	Multiply both numerator and denominator by the same number	To get denominator 10, multiply 2 by 5. Also multiply numerator: 1 × 5 = 5	equivalent_fraction
yr4_frac_equiv_001_d3_9249	yr4_frac_equiv_001	What is an equivalent fraction to 3/4? (Use denominator 24)	fraction	3	{"base_num": 3, "base_denom": 4, "multiplier": 6}	18/24	Multiply both numerator and denominator by the same number	To get denominator 24, multiply 4 by 6. Also multiply numerator: 3 × 6 = 18	equivalent_fraction
yr4_frac_equiv_001_d3_8065	yr4_frac_equiv_001	What is an equivalent fraction to 1/2? (Use denominator 6)	fraction	3	{"base_num": 1, "base_denom": 2, "multiplier": 3}	3/6	Multiply both numerator and denominator by the same number	To get denominator 6, multiply 2 by 3. Also multiply numerator: 1 × 3 = 3	equivalent_fraction
yr4_frac_equiv_001_d3_8957	yr4_frac_equiv_001	What is an equivalent fraction to 1/4? (Use denominator 8)	fraction	3	{"base_num": 1, "base_denom": 4, "multiplier": 2}	2/8	Multiply both numerator and denominator by the same number	To get denominator 8, multiply 4 by 2. Also multiply numerator: 1 × 2 = 2	equivalent_fraction
yr4_frac_equiv_001_d3_3178	yr4_frac_equiv_001	What is an equivalent fraction to 4/7? (Use denominator 21)	fraction	3	{"base_num": 4, "base_denom": 7, "multiplier": 3}	12/21	Multiply both numerator and denominator by the same number	To get denominator 21, multiply 7 by 3. Also multiply numerator: 4 × 3 = 12	equivalent_fraction
yr4_frac_equiv_001_d3_6654	yr4_frac_equiv_001	What is an equivalent fraction to 2/3? (Use denominator 6)	fraction	3	{"base_num": 2, "base_denom": 3, "multiplier": 2}	4/6	Multiply both numerator and denominator by the same number	To get denominator 6, multiply 3 by 2. Also multiply numerator: 2 × 2 = 4	equivalent_fraction
yr4_frac_equiv_001_d3_1655	yr4_frac_equiv_001	What is an equivalent fraction to 1/2? (Use denominator 10)	fraction	3	{"base_num": 1, "base_denom": 2, "multiplier": 5}	5/10	Multiply both numerator and denominator by the same number	To get denominator 10, multiply 2 by 5. Also multiply numerator: 1 × 5 = 5	equivalent_fraction
yr4_frac_equiv_001_d3_4865	yr4_frac_equiv_001	What is an equivalent fraction to 4/6? (Use denominator 24)	fraction	3	{"base_num": 4, "base_denom": 6, "multiplier": 4}	16/24	Multiply both numerator and denominator by the same number	To get denominator 24, multiply 6 by 4. Also multiply numerator: 4 × 4 = 16	equivalent_fraction
yr4_frac_equiv_001_d4_3912	yr4_frac_equiv_001	Find the missing denominator: 1/6 = 5/?	fraction	4	{"base_num": 1, "base_denom": 6, "multiplier": 5}	30	What number do you multiply the known values by?	Multiply both parts by 5	exact_match
yr4_frac_equiv_001_d4_6188	yr4_frac_equiv_001	Find the missing numerator: 4/5 = ?/15	fraction	4	{"base_num": 4, "base_denom": 5, "multiplier": 3}	12	What number do you multiply the known values by?	Multiply both parts by 3	exact_match
yr4_frac_equiv_001_d4_9019	yr4_frac_equiv_001	Find the missing numerator: 1/2 = ?/6	fraction	4	{"base_num": 1, "base_denom": 2, "multiplier": 3}	3	What number do you multiply the known values by?	Multiply both parts by 3	exact_match
yr4_frac_equiv_001_d4_7200	yr4_frac_equiv_001	Find the missing denominator: 1/4 = 3/?	fraction	4	{"base_num": 1, "base_denom": 4, "multiplier": 3}	12	What number do you multiply the known values by?	Multiply both parts by 3	exact_match
yr4_frac_equiv_001_d4_1542	yr4_frac_equiv_001	Find the missing numerator: 5/8 = ?/32	fraction	4	{"base_num": 5, "base_denom": 8, "multiplier": 4}	20	What number do you multiply the known values by?	Multiply both parts by 4	exact_match
yr4_frac_equiv_001_d4_3057	yr4_frac_equiv_001	Find the missing denominator: 4/7 = 12/?	fraction	4	{"base_num": 4, "base_denom": 7, "multiplier": 3}	21	What number do you multiply the known values by?	Multiply both parts by 3	exact_match
yr4_frac_equiv_001_d4_9127	yr4_frac_equiv_001	Find the missing numerator: 2/3 = ?/9	fraction	4	{"base_num": 2, "base_denom": 3, "multiplier": 3}	6	What number do you multiply the known values by?	Multiply both parts by 3	exact_match
yr4_frac_equiv_001_d4_3256	yr4_frac_equiv_001	Find the missing denominator: 2/7 = 6/?	fraction	4	{"base_num": 2, "base_denom": 7, "multiplier": 3}	21	What number do you multiply the known values by?	Multiply both parts by 3	exact_match
yr4_frac_equiv_001_d4_6585	yr4_frac_equiv_001	Find the missing denominator: 4/6 = 12/?	fraction	4	{"base_num": 4, "base_denom": 6, "multiplier": 3}	18	What number do you multiply the known values by?	Multiply both parts by 3	exact_match
yr4_frac_equiv_001_d4_3622	yr4_frac_equiv_001	Find the missing numerator: 2/3 = ?/15	fraction	4	{"base_num": 2, "base_denom": 3, "multiplier": 5}	10	What number do you multiply the known values by?	Multiply both parts by 5	exact_match
yr5_frac_add_001_d1_5691	yr5_frac_add_001	What is 1/10 + 3/10?	fraction	1	{"num1": 1, "num2": 3, "denom1": 10, "denom2": 10, "result_num": 4, "result_denom": 10}	4/10	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 10, add numerators: 1 + 3 = 4. Answer: 4/10	equivalent_fraction
yr5_frac_add_001_d1_2646	yr5_frac_add_001	What is 1/5 + 1/5?	fraction	1	{"num1": 1, "num2": 1, "denom1": 5, "denom2": 5, "result_num": 2, "result_denom": 5}	2/5	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 5, add numerators: 1 + 1 = 2. Answer: 2/5	equivalent_fraction
yr5_frac_add_001_d1_5165	yr5_frac_add_001	What is 4/8 + 2/8?	fraction	1	{"num1": 4, "num2": 2, "denom1": 8, "denom2": 8, "result_num": 6, "result_denom": 8}	6/8	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 8, add numerators: 4 + 2 = 6. Answer: 6/8	equivalent_fraction
yr5_frac_add_001_d1_6562	yr5_frac_add_001	What is 1/9 + 5/9?	fraction	1	{"num1": 1, "num2": 5, "denom1": 9, "denom2": 9, "result_num": 6, "result_denom": 9}	6/9	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 9, add numerators: 1 + 5 = 6. Answer: 6/9	equivalent_fraction
yr5_frac_add_001_d1_1059	yr5_frac_add_001	What is 3/8 + 4/8?	fraction	1	{"num1": 3, "num2": 4, "denom1": 8, "denom2": 8, "result_num": 7, "result_denom": 8}	7/8	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 8, add numerators: 3 + 4 = 7. Answer: 7/8	equivalent_fraction
yr5_frac_add_001_d1_9880	yr5_frac_add_001	What is 1/7 + 2/7?	fraction	1	{"num1": 1, "num2": 2, "denom1": 7, "denom2": 7, "result_num": 3, "result_denom": 7}	3/7	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 7, add numerators: 1 + 2 = 3. Answer: 3/7	equivalent_fraction
yr5_frac_add_001_d1_3103	yr5_frac_add_001	What is 5/8 + 2/8?	fraction	1	{"num1": 5, "num2": 2, "denom1": 8, "denom2": 8, "result_num": 7, "result_denom": 8}	7/8	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 8, add numerators: 5 + 2 = 7. Answer: 7/8	equivalent_fraction
yr5_frac_add_001_d1_2143	yr5_frac_add_001	What is 2/7 + 3/7?	fraction	1	{"num1": 2, "num2": 3, "denom1": 7, "denom2": 7, "result_num": 5, "result_denom": 7}	5/7	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 7, add numerators: 2 + 3 = 5. Answer: 5/7	equivalent_fraction
yr5_frac_add_001_d1_3230	yr5_frac_add_001	What is 1/9 + 2/9?	fraction	1	{"num1": 1, "num2": 2, "denom1": 9, "denom2": 9, "result_num": 3, "result_denom": 9}	3/9	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 9, add numerators: 1 + 2 = 3. Answer: 3/9	equivalent_fraction
yr5_frac_add_001_d1_9933	yr5_frac_add_001	What is 4/6 + 1/6?	fraction	1	{"num1": 4, "num2": 1, "denom1": 6, "denom2": 6, "result_num": 5, "result_denom": 6}	5/6	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 6, add numerators: 4 + 1 = 5. Answer: 5/6	equivalent_fraction
yr5_frac_add_001_d2_4772	yr5_frac_add_001	What is 4/9 + 2/9?	fraction	2	{"num1": 4, "num2": 2, "denom1": 9, "denom2": 9, "result_num": 6, "result_denom": 9}	6/9	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 9, add numerators: 4 + 2 = 6. Answer: 6/9	equivalent_fraction
yr5_frac_add_001_d2_1727	yr5_frac_add_001	What is 4/8 + 3/8?	fraction	2	{"num1": 4, "num2": 3, "denom1": 8, "denom2": 8, "result_num": 7, "result_denom": 8}	7/8	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 8, add numerators: 4 + 3 = 7. Answer: 7/8	equivalent_fraction
yr5_frac_add_001_d2_1684	yr5_frac_add_001	What is 1/5 + 4/5?	fraction	2	{"num1": 1, "num2": 4, "denom1": 5, "denom2": 5, "result_num": 5, "result_denom": 5}	5/5	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 5, add numerators: 1 + 4 = 5. Answer: 5/5	equivalent_fraction
yr5_frac_add_001_d2_6146	yr5_frac_add_001	What is 5/8 + 7/8?	fraction	2	{"num1": 5, "num2": 7, "denom1": 8, "denom2": 8, "result_num": 12, "result_denom": 8}	12/8	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 8, add numerators: 5 + 7 = 12. Answer: 12/8	equivalent_fraction
yr5_frac_add_001_d2_7380	yr5_frac_add_001	What is 7/9 + 8/9?	fraction	2	{"num1": 7, "num2": 8, "denom1": 9, "denom2": 9, "result_num": 15, "result_denom": 9}	15/9	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 9, add numerators: 7 + 8 = 15. Answer: 15/9	equivalent_fraction
yr5_frac_add_001_d2_3075	yr5_frac_add_001	What is 2/5 + 4/5?	fraction	2	{"num1": 2, "num2": 4, "denom1": 5, "denom2": 5, "result_num": 6, "result_denom": 5}	6/5	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 5, add numerators: 2 + 4 = 6. Answer: 6/5	equivalent_fraction
yr5_frac_add_001_d2_8415	yr5_frac_add_001	What is 1/2 + 1/2?	fraction	2	{"num1": 1, "num2": 1, "denom1": 2, "denom2": 2, "result_num": 2, "result_denom": 2}	2/2	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 2, add numerators: 1 + 1 = 2. Answer: 2/2	equivalent_fraction
yr5_frac_add_001_d2_5626	yr5_frac_add_001	What is 1/4 + 3/4?	fraction	2	{"num1": 1, "num2": 3, "denom1": 4, "denom2": 4, "result_num": 4, "result_denom": 4}	4/4	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 4, add numerators: 1 + 3 = 4. Answer: 4/4	equivalent_fraction
yr5_frac_add_001_d2_4762	yr5_frac_add_001	What is 2/8 + 4/8?	fraction	2	{"num1": 2, "num2": 4, "denom1": 8, "denom2": 8, "result_num": 6, "result_denom": 8}	6/8	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 8, add numerators: 2 + 4 = 6. Answer: 6/8	equivalent_fraction
yr5_frac_add_001_d2_6820	yr5_frac_add_001	What is 2/6 + 5/6?	fraction	2	{"num1": 2, "num2": 5, "denom1": 6, "denom2": 6, "result_num": 7, "result_denom": 6}	7/6	When denominators are the same, add the numerators and keep the denominator	Since both fractions have denominator 6, add numerators: 2 + 5 = 7. Answer: 7/6	equivalent_fraction
yr5_frac_add_001_d3_4020	yr5_frac_add_001	What is 3/5 + 9/10?	fraction	3	{"num1": 3, "num2": 9, "denom1": 5, "denom2": 10, "result_num": 15, "result_denom": 10}	15/10	Find a common denominator, then add the numerators	Common denominator is 10. Convert and add: (6 + 9) / 10 = 15/10	equivalent_fraction
yr5_frac_add_001_d3_1508	yr5_frac_add_001	What is 2/3 + 2/6?	fraction	3	{"num1": 2, "num2": 2, "denom1": 3, "denom2": 6, "result_num": 6, "result_denom": 6}	6/6	Find a common denominator, then add the numerators	Common denominator is 6. Convert and add: (4 + 2) / 6 = 6/6	equivalent_fraction
yr5_frac_add_001_d3_8943	yr5_frac_add_001	What is 1/2 + 1/6?	fraction	3	{"num1": 1, "num2": 1, "denom1": 2, "denom2": 6, "result_num": 4, "result_denom": 6}	4/6	Find a common denominator, then add the numerators	Common denominator is 6. Convert and add: (3 + 1) / 6 = 4/6	equivalent_fraction
yr5_frac_add_001_d3_7839	yr5_frac_add_001	What is 3/5 + 8/10?	fraction	3	{"num1": 3, "num2": 8, "denom1": 5, "denom2": 10, "result_num": 14, "result_denom": 10}	14/10	Find a common denominator, then add the numerators	Common denominator is 10. Convert and add: (6 + 8) / 10 = 14/10	equivalent_fraction
yr5_frac_add_001_d3_5590	yr5_frac_add_001	What is 2/4 + 4/8?	fraction	3	{"num1": 2, "num2": 4, "denom1": 4, "denom2": 8, "result_num": 8, "result_denom": 8}	8/8	Find a common denominator, then add the numerators	Common denominator is 8. Convert and add: (4 + 4) / 8 = 8/8	equivalent_fraction
yr5_frac_add_001_d3_5330	yr5_frac_add_001	What is 2/5 + 2/10?	fraction	3	{"num1": 2, "num2": 2, "denom1": 5, "denom2": 10, "result_num": 6, "result_denom": 10}	6/10	Find a common denominator, then add the numerators	Common denominator is 10. Convert and add: (4 + 2) / 10 = 6/10	equivalent_fraction
yr5_frac_add_001_d3_6996	yr5_frac_add_001	What is 2/4 + 5/12?	fraction	3	{"num1": 2, "num2": 5, "denom1": 4, "denom2": 12, "result_num": 11, "result_denom": 12}	11/12	Find a common denominator, then add the numerators	Common denominator is 12. Convert and add: (6 + 5) / 12 = 11/12	equivalent_fraction
yr5_frac_add_001_d3_6657	yr5_frac_add_001	What is 2/3 + 4/9?	fraction	3	{"num1": 2, "num2": 4, "denom1": 3, "denom2": 9, "result_num": 10, "result_denom": 9}	10/9	Find a common denominator, then add the numerators	Common denominator is 9. Convert and add: (6 + 4) / 9 = 10/9	equivalent_fraction
yr5_frac_add_001_d3_2620	yr5_frac_add_001	What is 4/5 + 7/10?	fraction	3	{"num1": 4, "num2": 7, "denom1": 5, "denom2": 10, "result_num": 15, "result_denom": 10}	15/10	Find a common denominator, then add the numerators	Common denominator is 10. Convert and add: (8 + 7) / 10 = 15/10	equivalent_fraction
yr5_frac_add_001_d3_4576	yr5_frac_add_001	What is 2/3 + 2/6?	fraction	3	{"num1": 2, "num2": 2, "denom1": 3, "denom2": 6, "result_num": 6, "result_denom": 6}	6/6	Find a common denominator, then add the numerators	Common denominator is 6. Convert and add: (4 + 2) / 6 = 6/6	equivalent_fraction
yr5_frac_add_001_d4_8740	yr5_frac_add_001	What is 2/3 + 5/11?	fraction	4	{"num1": 2, "num2": 5, "denom1": 3, "denom2": 11, "result_num": 37, "result_denom": 33}	37/33	Find a common denominator, then add the numerators	Common denominator is 33. Convert and add: (22 + 15) / 33 = 37/33	equivalent_fraction
yr5_frac_add_001_d4_8954	yr5_frac_add_001	What is 1/11 + 6/7?	fraction	4	{"num1": 1, "num2": 6, "denom1": 11, "denom2": 7, "result_num": 73, "result_denom": 77}	73/77	Find a common denominator, then add the numerators	Common denominator is 77. Convert and add: (7 + 66) / 77 = 73/77	equivalent_fraction
yr5_frac_add_001_d4_6054	yr5_frac_add_001	What is 4/6 + 1/5?	fraction	4	{"num1": 4, "num2": 1, "denom1": 6, "denom2": 5, "result_num": 26, "result_denom": 30}	26/30	Find a common denominator, then add the numerators	Common denominator is 30. Convert and add: (20 + 6) / 30 = 26/30	equivalent_fraction
yr5_frac_add_001_d4_6669	yr5_frac_add_001	What is 6/12 + 1/9?	fraction	4	{"num1": 6, "num2": 1, "denom1": 12, "denom2": 9, "result_num": 22, "result_denom": 36}	22/36	Find a common denominator, then add the numerators	Common denominator is 36. Convert and add: (18 + 4) / 36 = 22/36	equivalent_fraction
yr5_frac_add_001_d4_9367	yr5_frac_add_001	What is 2/5 + 8/9?	fraction	4	{"num1": 2, "num2": 8, "denom1": 5, "denom2": 9, "result_num": 58, "result_denom": 45}	58/45	Find a common denominator, then add the numerators	Common denominator is 45. Convert and add: (18 + 40) / 45 = 58/45	equivalent_fraction
yr5_frac_add_001_d4_4414	yr5_frac_add_001	What is 3/6 + 1/2?	fraction	4	{"num1": 3, "num2": 1, "denom1": 6, "denom2": 2, "result_num": 6, "result_denom": 6}	6/6	Find a common denominator, then add the numerators	Common denominator is 6. Convert and add: (3 + 3) / 6 = 6/6	equivalent_fraction
yr5_frac_add_001_d4_9685	yr5_frac_add_001	What is 1/2 + 4/9?	fraction	4	{"num1": 1, "num2": 4, "denom1": 2, "denom2": 9, "result_num": 17, "result_denom": 18}	17/18	Find a common denominator, then add the numerators	Common denominator is 18. Convert and add: (9 + 8) / 18 = 17/18	equivalent_fraction
yr5_frac_add_001_d4_2518	yr5_frac_add_001	What is 2/12 + 2/3?	fraction	4	{"num1": 2, "num2": 2, "denom1": 12, "denom2": 3, "result_num": 10, "result_denom": 12}	10/12	Find a common denominator, then add the numerators	Common denominator is 12. Convert and add: (2 + 8) / 12 = 10/12	equivalent_fraction
yr5_frac_add_001_d4_7613	yr5_frac_add_001	What is 3/10 + 2/4?	fraction	4	{"num1": 3, "num2": 2, "denom1": 10, "denom2": 4, "result_num": 16, "result_denom": 20}	16/20	Find a common denominator, then add the numerators	Common denominator is 20. Convert and add: (6 + 10) / 20 = 16/20	equivalent_fraction
yr5_frac_add_001_d4_1000	yr5_frac_add_001	What is 1/4 + 2/6?	fraction	4	{"num1": 1, "num2": 2, "denom1": 4, "denom2": 6, "result_num": 7, "result_denom": 12}	7/12	Find a common denominator, then add the numerators	Common denominator is 12. Convert and add: (3 + 4) / 12 = 7/12	equivalent_fraction
jon_add_b8ddadce-1c92-4eb8-85ac-bc67eec15ef8	jon_carry_add_sub_100	39 + 29 = ?	arithmetic	2	{"a": 39, "b": 29, "operation": "add"}	68	先算个位，个位超过 10 需要进位。	个位 9+9 进位，再加十位，答案是 68。	numeric
jon_add_0ef1430c-7caf-4319-8024-e329dbe81ed9	jon_carry_add_sub_100	36 + 26 = ?	arithmetic	2	{"a": 36, "b": 26, "operation": "add"}	62	先算个位，个位超过 10 需要进位。	个位 6+6 进位，再加十位，答案是 62。	numeric
jon_add_b73840eb-c10c-4a9e-a573-f76388c28fe5	jon_carry_add_sub_100	26 + 45 = ?	arithmetic	2	{"a": 26, "b": 45, "operation": "add"}	71	先算个位，个位超过 10 需要进位。	个位 6+5 进位，再加十位，答案是 71。	numeric
jon_add_a663d770-44fc-4a74-9931-a2af92a02fef	jon_carry_add_sub_100	38 + 29 = ?	arithmetic	2	{"a": 38, "b": 29, "operation": "add"}	67	先算个位，个位超过 10 需要进位。	个位 8+9 进位，再加十位，答案是 67。	numeric
jon_add_afdf4733-aff0-4975-9c73-5862d52d7b67	jon_carry_add_sub_100	39 + 37 = ?	arithmetic	2	{"a": 39, "b": 37, "operation": "add"}	76	先算个位，个位超过 10 需要进位。	个位 9+7 进位，再加十位，答案是 76。	numeric
jon_add_e05bd8e2-c488-4e12-a6e3-eaa7cb3e0c1f	jon_carry_add_sub_100	29 + 46 = ?	arithmetic	2	{"a": 29, "b": 46, "operation": "add"}	75	先算个位，个位超过 10 需要进位。	个位 9+6 进位，再加十位，答案是 75。	numeric
jon_sub_46aaa610-9e3e-46c4-b9f5-be52beec89c4	jon_carry_add_sub_100	81 - 33 = ?	arithmetic	2	{"a": 81, "b": 33, "operation": "sub"}	48	个位不够减时，向十位借 1。	81 的个位不够减 33 的个位，借位后计算，答案是 48。	numeric
jon_sub_4b4424d6-3e8e-474f-a21f-875bfa071f9e	jon_carry_add_sub_100	61 - 36 = ?	arithmetic	2	{"a": 61, "b": 36, "operation": "sub"}	25	个位不够减时，向十位借 1。	61 的个位不够减 36 的个位，借位后计算，答案是 25。	numeric
jon_sub_e125cdb7-c119-422d-9db9-db345c190f90	jon_carry_add_sub_100	44 - 25 = ?	arithmetic	1	{"a": 44, "b": 25, "operation": "sub"}	19	个位不够减时，向十位借 1。	44 的个位不够减 25 的个位，借位后计算，答案是 19。	numeric
astrid_missing_sub_e970d145-9c7d-42b4-bdf2-d60d467366e5	yr2_sem1_missing_number	56 - □ = 27，□ = ?	arithmetic	1	{"a": 56, "b": 29, "c": 27, "type": "missing_sub_middle"}	29	被减数减去几会得到 27？	因为 56 - 29 = 27，所以 □ = 29。	numeric
astrid_add_a4e9b099-47f9-4a44-9646-f4d28293add2	yr2_sem1_add_sub_100	23 + 11 = ?	arithmetic	1	{"a": 23, "b": 11, "operation": "add", "carry": false}	34	先算个位，再算十位。	23 + 11 = 34。	numeric
jon_add_a473a8c2-fd05-4442-801f-871312e604ab	jon_carry_add_sub_100	27 + 18 = ?	arithmetic	1	{"a": 27, "b": 18, "operation": "add"}	45	先算个位，个位超过 10 需要进位。	个位 7+8 进位，再加十位，答案是 45。	numeric
astrid_word_sub_4fb1b9bf-8fe1-4fbe-94b9-b429a9aeff0c	yr2_sem1_word_problem	盒子里有 48 颗糖，吃掉 28 颗，还剩多少颗？	arithmetic	1	{"a": 48, "b": 28, "operation": "sub"}	20	“还剩”通常用减法。	48 - 28 = 20。	numeric
jon_sub_d6b080a8-788c-427b-afae-a77de670e230	jon_carry_add_sub_100	60 - 16 = ?	arithmetic	1	{"a": 60, "b": 16, "operation": "sub"}	44	If the ones digit is not enough, borrow 1 ten.	The ones digit in 60 is smaller than in 16, so borrow and subtract. The answer is 44.	numeric
astrid_sub_26464da2-c14e-4abb-b080-ef1c0c3e7c9e	yr2_sem1_add_sub_100	98 - 33 = ?	arithmetic	1	{"a": 98, "b": 33, "operation": "sub", "borrow": false}	65	When ones are enough, subtract ones first.	98 - 33 = 65.	numeric
astrid_missing_sub_93ea54e5-a77c-455e-ac5d-916507f5c925	yr2_sem1_missing_number	49 - □ = 26, so □ = ?	arithmetic	1	{"a": 49, "b": 23, "c": 26, "type": "missing_sub_middle"}	23	What number should be subtracted from 49 to get 26?	Since 49 - 23 = 26, □ = 23.	numeric
astrid_missing_add_d9d16ed5-50f4-417e-af96-f1d09799925c	yr2_sem1_missing_number	□ + 9 = 28, so □ = ?	arithmetic	1	{"a": 19, "b": 9, "c": 28, "type": "missing_add_left"}	19	Think: how much should be added to 9 to make 28?	Since 19 + 9 = 28, □ = 19.	numeric
astrid_missing_add_da6bbd37-0c7c-4d2e-bddf-4b0aa394e8b7	yr2_sem1_missing_number	□ + 25 = 42, so □ = ?	arithmetic	1	{"a": 17, "b": 25, "c": 42, "type": "missing_add_left"}	17	Think: how much should be added to 25 to make 42?	Since 17 + 25 = 42, □ = 17.	numeric
astrid_sub_29ccd281-d2fc-4312-83d1-34f7f8a1c98a	yr2_sem1_add_sub_100	86 - 16 = ?	arithmetic	1	{"a": 86, "b": 16, "operation": "sub", "borrow": false}	70	When ones are enough, subtract ones first.	86 - 16 = 70.	numeric
astrid_compare_24b999b3-d3d7-42af-9287-ec830fb4fa80	yr2_sem1_compare_100	Which number is larger, 49 or 64? Enter the number only.	arithmetic	1	{"a": 49, "b": 64}	64	Compare tens first. If tens are equal, compare ones.	The larger number between 49 and 64 is 64.	numeric
astrid_word_sub_f572e4bf-3581-4443-b3a5-e9c1f0bf7b12	yr2_sem1_word_problem	There are 55 candies in a box. After eating 29, how many are left?	arithmetic	1	{"a": 55, "b": 29, "operation": "sub"}	26	The phrase 'left' usually means subtraction.	55 - 29 = 26.	numeric
astrid_place_tens_a02ffd5c-7cf9-4e0a-ab0c-574cc32978e1	yr2_sem1_place_value	How many tens are in 34?	arithmetic	1	{"number": 34, "ask": "tens"}	3	The tens digit shows how many tens.	34 has 3 tens.	numeric
astrid_sub_ed24d85d-ba21-41e4-9b53-94f145cd31a8	yr2_sem1_add_sub_100	29 - 26 = ?	arithmetic	1	{"a": 29, "b": 26, "operation": "sub", "borrow": false}	3	When ones are enough, subtract ones first.	29 - 26 = 3.	numeric
astrid_word_sub_524e7d8d-87c6-4f3d-b079-c3abcd6bcf64	yr2_sem1_word_problem	There are 34 candies in a box. After eating 21, how many are left?	arithmetic	1	{"a": 34, "b": 21, "operation": "sub"}	13	The phrase 'left' usually means subtraction.	34 - 21 = 13.	numeric
astrid_compare_2eaa2af9-b510-492b-a3cf-5f1c8a819908	yr2_sem1_compare_100	Which number is larger, 32 or 80? Enter the number only.	arithmetic	1	{"a": 32, "b": 80}	80	Compare tens first. If tens are equal, compare ones.	The larger number between 32 and 80 is 80.	numeric
astrid_add_bf69a56e-510d-4739-817d-8e768c88578b	yr2_sem1_add_sub_100	16 + 2 = ?	arithmetic	1	{"a": 16, "b": 2, "operation": "add", "carry": false}	18	Add the ones first, then the tens.	16 + 2 = 18.	numeric
astrid_sub_ba2e70bd-f9a2-4e23-81ed-f25afbecf88b	yr2_sem1_add_sub_100	27 - 27 = ?	arithmetic	1	{"a": 27, "b": 27, "operation": "sub", "borrow": false}	0	When ones are enough, subtract ones first.	27 - 27 = 0.	numeric
astrid_compare_b97b5638-aa88-41d9-86ee-09b06c6d687d	yr2_sem1_compare_100	Which number is larger, 19 or 24? Enter the number only.	arithmetic	1	{"a": 19, "b": 24}	24	Compare tens first. If tens are equal, compare ones.	The larger number between 19 and 24 is 24.	numeric
astrid_place_tens_6c7deb01-d9db-4aaa-bdc0-466554b47dde	yr2_sem1_place_value	How many tens are in 14?	arithmetic	1	{"number": 14, "ask": "tens"}	1	The tens digit shows how many tens.	14 has 1 tens.	numeric
astrid_missing_add_e54995b0-7c32-4141-a52a-1cc4316a5470	yr2_sem1_missing_number	□ + 21 = 27, so □ = ?	arithmetic	1	{"a": 6, "b": 21, "c": 27, "type": "missing_add_left"}	6	Think: how much should be added to 21 to make 27?	Since 6 + 21 = 27, □ = 6.	numeric
astrid_missing_add_dc608988-1f89-4eae-820e-2b114d84336f	yr2_sem1_missing_number	□ + 14 = 24, so □ = ?	arithmetic	1	{"a": 10, "b": 14, "c": 24, "type": "missing_add_left"}	10	Think: how much should be added to 14 to make 24?	Since 10 + 14 = 24, □ = 10.	numeric
astrid_missing_sub_1f5ce220-5477-4157-b267-80c69d3da741	yr2_sem1_missing_number	46 - □ = 28, so □ = ?	arithmetic	1	{"a": 46, "b": 18, "c": 28, "type": "missing_sub_middle"}	18	What number should be subtracted from 46 to get 28?	Since 46 - 18 = 28, □ = 18.	numeric
astrid_place_ones_5f58c6d1-088f-41d4-8169-2bdc892c25af	yr2_sem1_place_value	What is the ones digit in 45?	arithmetic	1	{"number": 45, "ask": "ones"}	5	The ones digit is the rightmost digit.	The ones digit in 45 is 5.	numeric
astrid_compare_31990df8-54d3-4f0a-b76d-dda6bec965c1	yr2_sem1_compare_100	Which number is larger, 52 or 27? Enter the number only.	arithmetic	1	{"a": 52, "b": 27}	52	Compare tens first. If tens are equal, compare ones.	The larger number between 52 and 27 is 52.	numeric
astrid_place_ones_6dc34852-3ccf-4f1e-942c-1563441e001b	yr2_sem1_place_value	What is the ones digit in 30?	arithmetic	1	{"number": 30, "ask": "ones"}	0	The ones digit is the rightmost digit.	The ones digit in 30 is 0.	numeric
astrid_missing_add_fd3650e2-5a5b-4084-81b5-9e86d2845eb8	yr2_sem1_missing_number	□ + 23 = 38, so □ = ?	arithmetic	1	{"a": 15, "b": 23, "c": 38, "type": "missing_add_left"}	15	Think: how much should be added to 23 to make 38?	Since 15 + 23 = 38, □ = 15.	numeric
astrid_word_sub_c2e6c0fa-791d-498a-9e7c-fbcb6961a97a	yr2_sem1_word_problem	There are 75 candies in a box. After eating 26, how many are left?	arithmetic	1	{"a": 75, "b": 26, "operation": "sub"}	49	The phrase 'left' usually means subtraction.	75 - 26 = 49.	numeric
astrid_place_tens_d9bc080f-5211-4bbc-a959-91b52a66196f	yr2_sem1_place_value	How many tens are in 43?	arithmetic	1	{"number": 43, "ask": "tens"}	4	The tens digit shows how many tens.	43 has 4 tens.	numeric
astrid_missing_sub_3f0543ae-1b86-47cb-85ad-11f6ec29f90c	yr2_sem1_missing_number	25 - □ = 20, so □ = ?	arithmetic	1	{"a": 25, "b": 5, "c": 20, "type": "missing_sub_middle"}	5	What number should be subtracted from 25 to get 20?	Since 25 - 5 = 20, □ = 5.	numeric
astrid_missing_add_a17cb705-1fa2-4012-be30-5304be7fbbe4	yr2_sem1_missing_number	□ + 18 = 25, so □ = ?	arithmetic	1	{"a": 7, "b": 18, "c": 25, "type": "missing_add_left"}	7	Think: how much should be added to 18 to make 25?	Since 7 + 18 = 25, □ = 7.	numeric
astrid_add_f55eeb02-9c0a-4725-98ac-77e6d1469187	yr2_sem1_add_sub_100	61 + 17 = ?	arithmetic	1	{"a": 61, "b": 17, "operation": "add", "carry": false}	78	Add the ones first, then the tens.	61 + 17 = 78.	numeric
astrid_add_2839f2e2-b829-4e16-94de-86173fd0965b	yr2_sem1_add_sub_100	46 + 13 = ?	arithmetic	1	{"a": 46, "b": 13, "operation": "add", "carry": false}	59	Add the ones first, then the tens.	46 + 13 = 59.	numeric
astrid_add_ff980080-02f3-4f1c-a3f0-6f9be6ed9cac	yr2_sem1_add_sub_100	71 + 5 = ?	arithmetic	1	{"a": 71, "b": 5, "operation": "add", "carry": false}	76	Add the ones first, then the tens.	71 + 5 = 76.	numeric
astrid_word_add_c6623b63-a103-40d1-a521-eaa8d102c08c	yr2_sem1_word_problem	Xiaoming has 14 pencils and buys 14 more. How many pencils does he have in total?	arithmetic	1	{"a": 14, "b": 14, "operation": "add"}	28	The phrase 'buys more' usually means addition.	14 + 14 = 28.	numeric
astrid_compare_2079f4d5-029b-42a5-b9a6-1404fd796dc3	yr2_sem1_compare_100	Which number is larger, 20 or 28? Enter the number only.	arithmetic	1	{"a": 20, "b": 28}	28	Compare tens first. If tens are equal, compare ones.	The larger number between 20 and 28 is 28.	numeric
astrid_sub_7b5d15c4-6be7-4c11-a2ed-78c2e7932133	yr2_sem1_add_sub_100	67 - 12 = ?	arithmetic	1	{"a": 67, "b": 12, "operation": "sub", "borrow": false}	55	When ones are enough, subtract ones first.	67 - 12 = 55.	numeric
astrid_compare_36b90010-659a-4699-95b4-d6dfd40c4439	yr2_sem1_compare_100	Which number is larger, 84 or 13? Enter the number only.	arithmetic	1	{"a": 84, "b": 13}	84	Compare tens first. If tens are equal, compare ones.	The larger number between 84 and 13 is 84.	numeric
astrid_place_tens_943bfe44-4638-4297-a569-a877f9c37314	yr2_sem1_place_value	How many tens are in 11?	arithmetic	1	{"number": 11, "ask": "tens"}	1	The tens digit shows how many tens.	11 has 1 tens.	numeric
astrid_add_519ea212-aece-4b83-b80f-107ff8d1369c	yr2_sem1_add_sub_100	64 + 2 = ?	arithmetic	1	{"a": 64, "b": 2, "operation": "add", "carry": false}	66	Add the ones first, then the tens.	64 + 2 = 66.	numeric
astrid_word_add_22745105-c3b2-4bf8-97ed-6642b13d58fb	yr2_sem1_word_problem	Xiaoming has 18 pencils and buys 22 more. How many pencils does he have in total?	arithmetic	1	{"a": 18, "b": 22, "operation": "add"}	40	The phrase 'buys more' usually means addition.	18 + 22 = 40.	numeric
astrid_compare_8887041c-c2a2-499f-bc34-637df82420ea	yr2_sem1_compare_100	Which number is larger, 42 or 48? Enter the number only.	arithmetic	1	{"a": 42, "b": 48}	48	Compare tens first. If tens are equal, compare ones.	The larger number between 42 and 48 is 48.	numeric
astrid_add_7e2fd2ad-1b52-4b6a-bb6d-2a45edb48b26	yr2_sem1_add_sub_100	21 + 2 = ?	arithmetic	1	{"a": 21, "b": 2, "operation": "add", "carry": false}	23	Add the ones first, then the tens.	21 + 2 = 23.	numeric
astrid_compare_d64b1b82-9baf-465f-92e2-3b02729d7e75	yr2_sem1_compare_100	Which number is larger, 15 or 85? Enter the number only.	arithmetic	1	{"a": 15, "b": 85}	85	Compare tens first. If tens are equal, compare ones.	The larger number between 15 and 85 is 85.	numeric
astrid_word_add_07239fba-32ee-4f0b-b5b8-20ec745629d8	yr2_sem1_word_problem	Xiaoming has 18 pencils and buys 13 more. How many pencils does he have in total?	arithmetic	1	{"a": 18, "b": 13, "operation": "add"}	31	The phrase 'buys more' usually means addition.	18 + 13 = 31.	numeric
astrid_compare_556a8dae-38d1-466f-8b98-8919919e6b5b	yr2_sem1_compare_100	Which number is larger, 80 or 34? Enter the number only.	arithmetic	1	{"a": 80, "b": 34}	80	Compare tens first. If tens are equal, compare ones.	The larger number between 80 and 34 is 80.	numeric
astrid_missing_add_8580aeff-6c4d-43b6-ac2d-3d4de5b38cc6	yr2_sem1_missing_number	□ + 40 = 66, so □ = ?	arithmetic	1	{"a": 26, "b": 40, "c": 66, "type": "missing_add_left"}	26	Think: how much should be added to 40 to make 66?	Since 26 + 40 = 66, □ = 26.	numeric
astrid_missing_sub_96b45e07-9ba5-49b9-9799-71a8f8231733	yr2_sem1_missing_number	75 - □ = 39, so □ = ?	arithmetic	1	{"a": 75, "b": 36, "c": 39, "type": "missing_sub_middle"}	36	What number should be subtracted from 75 to get 39?	Since 75 - 36 = 39, □ = 36.	numeric
astrid_missing_sub_9d6660a1-a3b4-4c7a-ab06-e87ca326d632	yr2_sem1_missing_number	45 - □ = 25, so □ = ?	arithmetic	1	{"a": 45, "b": 20, "c": 25, "type": "missing_sub_middle"}	20	What number should be subtracted from 45 to get 25?	Since 45 - 20 = 25, □ = 20.	numeric
astrid_sub_40bbcde9-6c7b-4e46-81f2-ad44f1da4fff	yr2_sem1_add_sub_100	79 - 19 = ?	arithmetic	1	{"a": 79, "b": 19, "operation": "sub", "borrow": false}	60	When ones are enough, subtract ones first.	79 - 19 = 60.	numeric
astrid_missing_sub_04935961-d7ac-4776-ae17-4dcbe90640be	yr2_sem1_missing_number	61 - □ = 21, so □ = ?	arithmetic	1	{"a": 61, "b": 40, "c": 21, "type": "missing_sub_middle"}	40	What number should be subtracted from 61 to get 21?	Since 61 - 40 = 21, □ = 40.	numeric
jon_add_a18c1a26-91e4-47eb-ae0c-3b8822df8488	jon_carry_add_sub_100	39 + 25 = ?	arithmetic	2	{"a": 39, "b": 25, "operation": "add"}	64	Add ones first. If ones are 10 or more, carry to the tens place.	In ones: 9+5 requires carrying, then add tens. The answer is 64.	numeric
jon_sub_0b97afc1-a7f9-48a0-b9cb-250cae31dbc3	jon_carry_add_sub_100	32 - 19 = ?	arithmetic	1	{"a": 32, "b": 19, "operation": "sub"}	13	If the ones digit is not enough, borrow 1 ten.	The ones digit in 32 is smaller than in 19, so borrow and subtract. The answer is 13.	numeric
jon_add_105ebb08-dc88-441c-8095-27a07ce3630b	jon_carry_add_sub_100	36 + 25 = ?	arithmetic	2	{"a": 36, "b": 25, "operation": "add"}	61	Add ones first. If ones are 10 or more, carry to the tens place.	In ones: 6+5 requires carrying, then add tens. The answer is 61.	numeric
jon_sub_d60c3fc5-1fd8-4262-863c-57fd5b317ec8	jon_carry_add_sub_100	52 - 38 = ?	arithmetic	1	{"a": 52, "b": 38, "operation": "sub"}	14	If the ones digit is not enough, borrow 1 ten.	The ones digit in 52 is smaller than in 38, so borrow and subtract. The answer is 14.	numeric
jon_add_b09be1a3-3fcc-45ec-9efb-bd398ec42cf0	jon_carry_add_sub_100	45 + 29 = ?	arithmetic	2	{"a": 45, "b": 29, "operation": "add"}	74	Add ones first. If ones are 10 or more, carry to the tens place.	In ones: 5+9 requires carrying, then add tens. The answer is 74.	numeric
jon_add_cd314da1-0546-4d4f-a778-a04bb836aa9e	jon_carry_add_sub_100	17 + 39 = ?	arithmetic	2	{"a": 17, "b": 39, "operation": "add"}	56	Add ones first. If ones are 10 or more, carry to the tens place.	In ones: 7+9 requires carrying, then add tens. The answer is 56.	numeric
jon_add_9be9eb60-fa2b-45e8-bac6-fa275ddff87d	jon_carry_add_sub_100	17 + 49 = ?	arithmetic	2	{"a": 17, "b": 49, "operation": "add"}	66	Add ones first. If ones are 10 or more, carry to the tens place.	In ones: 7+9 requires carrying, then add tens. The answer is 66.	numeric
astrid_word_add_3e0fe72d-06e8-46ef-9fa3-69d05c88c8e0	yr2_sem1_word_problem	Xiaoming has 29 pencils and buys 11 more. How many pencils does he have in total?	arithmetic	1	{"a": 29, "b": 11, "operation": "add"}	40	The phrase 'buys more' usually means addition.	29 + 11 = 40.	numeric
astrid_missing_add_41ce48c6-70ef-4449-b6b6-36db7fb1e967	yr2_sem1_missing_number	□ + 26 = 64, so □ = ?	arithmetic	1	{"a": 38, "b": 26, "c": 64, "type": "missing_add_left"}	38	Think: how much should be added to 26 to make 64?	Since 38 + 26 = 64, □ = 38.	numeric
astrid_sub_0e3d5cc5-0b7d-42a4-a963-9a9f361116fe	yr2_sem1_add_sub_100	63 - 23 = ?	arithmetic	1	{"a": 63, "b": 23, "operation": "sub", "borrow": false}	40	When ones are enough, subtract ones first.	63 - 23 = 40.	numeric
astrid_add_4aa2c946-ee4f-4ab2-8e63-ed2fe0acdbe0	yr2_sem1_add_sub_100	40 + 5 = ?	arithmetic	1	{"a": 40, "b": 5, "operation": "add", "carry": false}	45	Add the ones first, then the tens.	40 + 5 = 45.	numeric
astrid_add_6c8567b9-68b8-4029-b5ea-8bbbeb7e9059	yr2_sem1_add_sub_100	71 + 16 = ?	arithmetic	1	{"a": 71, "b": 16, "operation": "add", "carry": false}	87	Add the ones first, then the tens.	71 + 16 = 87.	numeric
astrid_sub_5935da6d-d9de-4670-aa16-1c4d271d0afe	yr2_sem1_add_sub_100	68 - 20 = ?	arithmetic	1	{"a": 68, "b": 20, "operation": "sub", "borrow": false}	48	When ones are enough, subtract ones first.	68 - 20 = 48.	numeric
astrid_compare_1a7e549b-fa58-4d02-bc84-092b73154988	yr2_sem1_compare_100	Which number is larger, 56 or 17? Enter the number only.	arithmetic	1	{"a": 56, "b": 17}	56	Compare tens first. If tens are equal, compare ones.	The larger number between 56 and 17 is 56.	numeric
astrid_add_bbe79232-b003-4485-8a9d-a4afddb298c1	yr2_sem1_add_sub_100	58 + 11 = ?	arithmetic	1	{"a": 58, "b": 11, "operation": "add", "carry": false}	69	Add the ones first, then the tens.	58 + 11 = 69.	numeric
\.


--
-- Data for Name: mastery; Type: TABLE DATA; Schema: public; Owner: mathcoach
--

COPY public.mastery (student_id, skill_id, total_attempts, correct_attempts, mastery_score, last_updated) FROM stdin;
jon_zhao	jon_carry_add_sub_100	14	8	0.5714285714285714	2026-02-20 23:30:18.653716
test_001	yr3_frac_compare_001	19	6	0.3157894736842105	2026-02-13 08:52:15.493137
astrid_zhao	yr2_sem1_place_value	6	6	1	2026-02-20 20:12:39.062455
astrid_zhao	yr2_sem1_add_sub_100	9	7	0.7777777777777778	2026-02-20 20:13:22.671084
astrid_zhao	yr2_sem1_word_problem	6	1	0.16666666666666666	2026-02-20 20:13:45.450723
astrid_zhao	yr2_sem1_compare_100	9	9	1	2026-02-20 20:13:53.277263
astrid_zhao	yr2_sem1_missing_number	12	5	0.4166666666666667	2026-02-20 20:15:18.560969
\.


--
-- Data for Name: parents; Type: TABLE DATA; Schema: public; Owner: mathcoach
--

COPY public.parents (id, email, password_hash, display_name, is_active, created_at) FROM stdin;
7e14f5cf-c04e-4fde-a321-f4762831933c	phase8.smoke.parent@example.com	pbkdf2_sha256$1xqX2A-J1OatfXFNY7pT2g==$3GrEzeuv1W9BQUCgv-6Xt4DUijWORoRJY50cv0tNISc=	Phase8 Smoke Parent	t	2026-02-21 03:04:57.109494
6dc1371f-95e8-474d-b6f0-e7037359be26	phase8-smoke@example.com	pbkdf2_sha256$tA8d82WSsqzn4_KyXyU_Ew==$WP0x6xb1boKer3hq0BNKJ4vv-IhUGoUKl92MJW6pjak=	Phase8 Smoke Parent	t	2026-02-21 04:09:24.485581
75b19891-fdb9-4aa9-8c98-8ddbf38b7163	michael@micleah.com	pbkdf2_sha256$8EZ5rb323djSIRNXCxNlfA==$Qg1rpWCmKJ16jV1gsAoDD4uWxiI_YqLqSJ-RVewBWpY=	Michael	t	2026-02-21 04:15:38.261261
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: mathcoach
--

COPY public.students (id, name, year_level, created_at, avatar, target_daily_questions, current_streak, longest_streak, last_practice_date, total_sessions, parent_id, pin_hash) FROM stdin;
test_001	测试学生	3	2026-02-13 08:49:46.295854	star	10	0	0	\N	0	\N	\N
jon_zhao	Jon	4	2026-02-20 09:08:45.848468	lion	40	1	1	2026-02-20	14	75b19891-fdb9-4aa9-8c98-8ddbf38b7163	pbkdf2_sha256$hfN5rTFTtS-r3nJp_vmXsg==$kVjvQ123UMfd8sLvPAhED6yYMrg2jW8lAxhb4rT2NjE=
astrid_zhao	Astrid	3	2026-02-20 09:08:45.848468	unicorn	40	1	1	2026-02-20	42	75b19891-fdb9-4aa9-8c98-8ddbf38b7163	pbkdf2_sha256$AjYbwEoeSRTx71NpcXC6UA==$SPHT5r6YEVIXraY87vKy8mmYt_X87PJEJsOMMzvXyyY=
\.


--
-- Name: achievements achievements_pkey; Type: CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.achievements
    ADD CONSTRAINT achievements_pkey PRIMARY KEY (id);


--
-- Name: daily_sessions daily_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.daily_sessions
    ADD CONSTRAINT daily_sessions_pkey PRIMARY KEY (id);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- Name: mastery mastery_pkey; Type: CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.mastery
    ADD CONSTRAINT mastery_pkey PRIMARY KEY (student_id, skill_id);


--
-- Name: parents parents_email_key; Type: CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.parents
    ADD CONSTRAINT parents_email_key UNIQUE (email);


--
-- Name: parents parents_pkey; Type: CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.parents
    ADD CONSTRAINT parents_pkey PRIMARY KEY (id);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: ix_achievements_badge_key; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_achievements_badge_key ON public.achievements USING btree (badge_key);


--
-- Name: ix_achievements_student_id; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_achievements_student_id ON public.achievements USING btree (student_id);


--
-- Name: ix_daily_sessions_session_date; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_daily_sessions_session_date ON public.daily_sessions USING btree (session_date);


--
-- Name: ix_daily_sessions_student_id; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_daily_sessions_student_id ON public.daily_sessions USING btree (student_id);


--
-- Name: ix_events_item_id; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_events_item_id ON public.events USING btree (item_id);


--
-- Name: ix_events_student_id; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_events_student_id ON public.events USING btree (student_id);


--
-- Name: ix_events_timestamp; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_events_timestamp ON public.events USING btree ("timestamp");


--
-- Name: ix_items_difficulty; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_items_difficulty ON public.items USING btree (difficulty);


--
-- Name: ix_items_skill_id; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_items_skill_id ON public.items USING btree (skill_id);


--
-- Name: ix_mastery_skill_id; Type: INDEX; Schema: public; Owner: mathcoach
--

CREATE INDEX ix_mastery_skill_id ON public.mastery USING btree (skill_id);


--
-- Name: achievements achievements_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.achievements
    ADD CONSTRAINT achievements_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- Name: daily_sessions daily_sessions_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.daily_sessions
    ADD CONSTRAINT daily_sessions_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- Name: events events_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: events events_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- Name: mastery mastery_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mathcoach
--

ALTER TABLE ONLY public.mastery
    ADD CONSTRAINT mastery_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- PostgreSQL database dump complete
--

\unrestrict HRAo7hci8l3vof8pGEzOZIewHhjz9qz9havrIvwegZvuES3NYjkhohgz4xrEJbi

