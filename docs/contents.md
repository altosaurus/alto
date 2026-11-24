---
title: Contents
permalink: /contents/
---
{% assign ordered = site.pages | where_exp: "p", "p.nav_order" | sort: "nav_order" %}
{% assign groups = ordered | group_by: "nav_group" %}
{% for group in groups %}
{% if group.name == empty or group.name == nil %}
{% for item in group.items %}- [{{ item.title }}]({{ item.url | relative_url }})
{% endfor %}
{% else %}
{% assign overview = group.items | where: "title", group.name | first %}
<h2>{% if overview %}<a href="{{ overview.url | relative_url }}">{{ group.name }}</a>{% else %}{{ group.name }}{% endif %}</h2>
{% include category-pages.html group=group.name %}
{% endif %}
{% endfor %}
