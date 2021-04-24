#!/bin/bash
set -e
cd "$(dirname "$0")" || exit 1;
curl -s "https://www.linguee.com/portuguese-english/search?query=constibado&ajax=1&source=PT" > constibado.html
curl -s "https://www.linguee.com/portuguese-english/search?query=esgotar&ajax=1&source=PT" > esgotar.html
curl -s "https://www.linguee.com/portuguese-english/search?query=obrigado&ajax=1&source=PT" > obrigado.html
curl -s "https://www.linguee.com/portuguese-english/search?query=xxxxzzzz&ajax=1&source=PT" > xxxxzzzz.html
curl -s "https://www.linguee.com/portuguese-english/search?query=not%20bad&ajax=1" > not_bad.html
