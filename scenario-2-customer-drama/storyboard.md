# S2 Brazilian customer drama — 120-second edit plan

## Production lock

- **Customer A:** `assets/generated/brazil-customer-a-front.png`, olive overshirt / charcoal T-shirt / khaki chinos.
- **Customer B:** `assets/generated/brazil-customer-b-front.png`, rust overshirt / cream T-shirt / black jeans.
- **Vehicle:** only `assets/vehicle/X18-black-red/`.
- **Scene:** `assets/generated/brazil-street-scene.png`; practical early-morning São Paulo light, warm but not orange, no invented storefront text.
- **Coverage:** 20 clips × 6 seconds = 120 seconds. Generate only 5-second H3 tests; editorial can use selective 4–5-second excerpts and repeated cutaways after identity passes.
- **Dialogue rule:** Brazilian Portuguese spoken by the roles in the table. Keep each line short and put the speaking face medium/medium-close. For actual two-voice production, prefer separate role audio references when available; do not claim a price absent an approved price list.

## Script and shot list

| # | Time | Portuguese dialogue / action | Camera, lighting and director note |
|---:|---:|---|---|
| 01 | 00:00–00:06 | **B:** “Ei, essa é a X18 que você comentou?” | A arrives slowly and stops; B waits by the café; wide establishing shot. |
| 02 | 00:06–00:12 | **A:** “É sim. Vim mostrar por que ela funciona bem no dia a dia.” | Medium two-shot; keep bike side profile visible. |
| 03 | 00:12–00:18 | **B:** “O desenho é bem diferente. Posso olhar de perto?” | Medium on B then rack focus to headlamp; no cut. |
| 04 | 00:18–00:24 | **A:** “Claro. Repara no farol redondo e nos retrovisores.” | A points once at headlamp; strong vehicle-match test. |
| 05 | 00:24–00:30 | **B:** “E esse banco parece confortável para duas pessoas.” | Side two-shot; backrest remains identical to reference. |
| 06 | 00:30–00:36 | **A:** “Tem dois assentos e encosto; é uma posição bem relaxada.” | A seated, B beside vehicle; calm natural daylight. |
| 07 | 00:36–00:42 | **B:** “Qual é a autonomia que a ficha informa?” | Medium close-up B; background soft but recognisable. |
| 08 | 00:42–00:48 | **A:** “A referência é de sessenta a setenta quilômetros, conforme uso e versão.” | Medium close-up A; avoid numbers as generated on-screen text. |
| 09 | 00:48–00:54 | **B:** “E para carregar, quanto tempo eu preciso?” | Two-shot from handlebar side; preserve faces. |
| 10 | 00:54–01:00 | **A:** “A ficha fala em cerca de sete horas. O ideal é planejar a recarga.” | A gestures to charge-area conceptually; no invented connector close-up. |
| 11 | 01:00–01:06 | **B:** “Vi que existem versões de potência diferente, certo?” | B faces A; medium shoulder-level view. |
| 12 | 01:06–01:12 | **A:** “Sim, há opções de dois ou três quilowatts; confirme a versão local.” | A faces camera slightly; no false badges or text. |
| 13 | 01:12–01:18 | **B:** “A largura dos pneus passa uma sensação de estabilidade.” | Low side angle, stationary bike, B points at tire once. |
| 14 | 01:18–01:24 | **A:** “São pneus largos, com freio a disco dianteiro e suspensão.” | A crouches briefly; no body or wheel deformation. |
| 15 | 01:24–01:30 | **B:** “Posso dar uma volta curta aqui na rua?” | A hands B a helmet; centre both faces. |
| 16 | 01:30–01:36 | **A:** “Pode. Sai devagar e fica sempre atento ao trânsito.” | Close two-shot; natural conversation pace. |
| 17 | 01:36–01:42 | **B:** “A saída é suave. A posição de pilotagem é bem confortável.” | B moves 3–4 metres only; tracking shot, no fast turn. |
| 18 | 01:42–01:48 | **A:** “Ela foi pensada para deslocamentos curtos e rotina urbana.” | A watches from curb; bike returns into same frame. |
| 19 | 01:48–01:54 | **B:** “Gostei. Parece prática sem perder o estilo.” | Bike stopped, B dismounts; one movement only. |
| 20 | 01:54–02:00 | **A:** “Essa é a ideia: experimentar, escolher a configuração certa e rodar com segurança.” | Final two-shot with X18 in profile; fade in edit, not in H3. |

## H3 case mapping

| Test case | Reference allocation / prompt intent |
|---|---|
| S2-R1-01 | `<Picture 1>` A, `<Picture 2>` B; the X18 must be explicitly described and used only in a simple arrival-and-stop shot. |
| S2-R1-02 | A and B side-by-side with the X18; one short alternated line each, medium two-shot. |
| S2-R2-01 | `<Picture 1>` A, `<Picture 2>` X18, `<Picture 3>` São Paulo street; A speaks alone. |
| S2-R2-02 | A, B, X18 references; four dialogue fragments split across multiple 5-second clips, not one 20-second request. |
| S2-R2-03 | Low-memory workflow: introduce the street scene only after A/B/X18 identity is proven. |
| S2-R2-04 | Re-run the best 02 setup only if an approved A voice reference is supplied. |

## Prompt guardrail

`The two Brazilian men and the black-and-red X18 must remain exactly the people and vehicle shown in the reference images. Speak only the specified Brazilian Portuguese line for the visible speaker. No third person, no face swap, no costume change, no vehicle change, no invented price or signage, no subtitles or text overlay.`
