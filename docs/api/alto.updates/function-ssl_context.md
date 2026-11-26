---
title: ssl_context
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-ssl_context/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def ssl_context() -> ssl.SSLContext
```

{% endraw %}{% include api-source.html name="ssl_context" line=915 %}{% raw %}

</div>

Make the settings for a secure connection, trusting the certificate
authorities that come with Alto.

A packaged copy cannot count on the system's: the Python inside it
may look for them where the computer it was built on keeps
them, and a connection would then fail on a distribution that keeps
them somewhere else.

**Returns**

| Type | Description |
| --- | --- |
| `ssl.SSLContext` | A context that checks the server's certificate and name against certifi's list. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     ssl_context().verify_mode
...     == ssl.CERT_REQUIRED,
...     len(ssl_context().get_ca_certs()) > 100,
... )
(True, True)
```
{% endraw %}
