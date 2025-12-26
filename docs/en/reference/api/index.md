# API Reference

{% for category in [
	"Application components",
	"Widgets",
	"Container widgets",
	"Style",
	"Resources",
	"Data sources",
	"Constants and types",
	"Hardware",
] %}
## {{ category }} { .api-reference }

{{ api_table(category) }}

{% endfor %}
