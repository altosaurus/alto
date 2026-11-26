---
title: verify_signature
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-verify_signature/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def verify_signature(
    data: bytes,
    *,
    signature: str,
    keys: tuple[str, ...],
) -> bool
```

{% endraw %}{% include api-source.html name="verify_signature" line=1097 %}{% raw %}

</div>

Say whether an Ed25519 signature of some data was made with one of
the keys.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `data` | `bytes` | What was signed. |
| `signature` | `str` | The signature, base64. Keyword-only. |
| `keys` | `tuple of str` | The public keys (base64) that are trusted. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True only if the signature is well formed and one of the keys made it. No key, a key that is not a key, and a signature that is not one all give False. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from nacl.signing import SigningKey
>>> pair = SigningKey.generate()
>>> public = base64.b64encode(
...     bytes(pair.verify_key)
... ).decode()
>>> signed = base64.b64encode(
...     pair.sign(b"the list").signature
... ).decode()
>>> verify_signature(
...     b"the list",
...     signature=signed,
...     keys=(public,),
... )
True
>>> verify_signature(
...     b"another list",
...     signature=signed,
...     keys=(public,),
... )
False
>>> verify_signature(
...     b"the list", signature=signed, keys=()
... )
False
```
{% endraw %}
