# API Reference

{% for category in [
	"Application components",
	"General widgets",
	"Layout widgets",
	"Resources",
	"Data sources",
	"Hardware",
	"Other"
] %}
## {{ category }} { .api-reference }

{{ api_table(category) }}

{% endfor %}
