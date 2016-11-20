Linguee API
===========

[Linguee](https://linguee.com) provides excellent dictionary and
translation memory service. Unfortunately, there is no way you can get automated
access to it. Linguee API fixes the problem. It acts as a proxy and converts
their HTML responses to easy to use JSON API.

API endpoint
------------

Proxy provides a single API endpoint at `GET /api`. Accepted arguments:

- `q`: query string, word or text to translate
- `src`: source language (as a two-letter code)
- `dst`: target language (as a two-letter code)

Sample installation
-------------------

Sample installation is available at https://linguee-api.herokuapp.com.
That's how you translate word "bacalhau" from Portuguese to English:
https://linguee-api.herokuapp.com/api?q=bacalhau&src=pt&dst=en

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


Supported languages
-------------------

API supports all languages, supported by Linguee. As in Linguee, not all
language pairs are valid though. Supported languages:
`bg` (Bulgarian),  `cs` (Czech),  `da` (Danish),  `de` (German),  `el` (Greek),
`en` (English),  `es` (Spanish),  `et` (Estonian),  `fi` (Finnish),
`fr` (French),  `hu` (Hungarian),  `it` (Italian),  `ja` (Japan),
`lt` (Lithuanian),  `lv` (Latvian),  `mt` (Maltese),  `nl` (Dutch),
`pl` (Polish),  `pt` (Portuguese),  `ro` (Romanian),  `ru` (Russian),
`sk` (Slovak),  `sl` (Solvene),  `sv` (Swedish),  `zh` (Chinese).

Terms and Conditions
--------------------

If you use the API, make sure you comply with
[Linguee Terms and Conditions](http://www.linguee.com/page/termsAndConditions.php),
and in particular with that clause:

> Both private and business usage of linguee.com services is free of charge.
> It is however strictly prohibited to forward on our services to third
> parties against payment
