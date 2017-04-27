COPY cms_page (rght, level, navigation_extenders, parent_id, reverse_id, login_required, soft_root, creation_date, lft, publication_end_date, template, tree_id, publication_date, in_navigation, id, moderator_state, published, site_id, changed_by, created_by, publisher_is_draft, publisher_state, publisher_public_id, limit_visibility_in_menu) FROM stdin;
2	0		\N	\N	f	f	2017-04-27 09:12:11.652229+00	1	\N	base/twocol.html	47	2017-04-27 09:12:29.017001+00	f	93	0	t	1	root	root	t	1	\N	\N
\.

COPY cms_placeholder (slot, id, default_width) FROM stdin;
Right bar	350	\N
Main content	351	\N
\.

COPY cms_page_placeholders (id, page_id, placeholder_id) FROM stdin;
153	93	350
154	93	351
\.

COPY cms_cmsplugin (language, "position", creation_date, id, plugin_type, parent_id, tree_id, lft, rght, level, placeholder_id) FROM stdin;
sv	0	2017-04-27 09:12:16.889122+00	1386	ListUserSurveysPlugin	\N	512	1	2	0	351
\.


COPY cms_title (language, title, page_id, id, path, creation_date, slug, has_url_overwrite) FROM stdin;
sv	Välkommen	93	116	valkommen	2017-04-27 09:12:11.693488+00	valkommen	f
\.

COPY cmsplugin_surveylistplugin (cmsplugin_ptr_id) FROM stdin;
1386
\.
