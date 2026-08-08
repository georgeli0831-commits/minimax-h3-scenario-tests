# S1 Factory host introduction — 90-second edit plan

## Production lock

- **Presenter:** `assets/generated/china-host-front.png`; keep the same short black bob, sand overshirt, white T-shirt, dark-blue jeans, and unretouched natural skin texture.
- **Vehicle:** only `assets/vehicle/X18-black-red/` (black body, red side panels, twin mirrors, round headlamp, stepped two-person seat and backrest).
- **Location:** `assets/generated/factory-gate-reference.png`.
- **Light:** late-afternoon open shade / warm sun; no beauty lighting, no heavy fill, no dramatic colour shift.
- **Director constraint:** face stays medium/medium-close for speech; every action begins and ends in the same place in a 5-second H3 shot. Never ask H3 to complete the full 90 seconds in one generation.
- **Compliance:** row 38–41 of the supplied X18 sheet identifies different 2000W/3000W and battery variants. Keep power, top-speed and battery claims qualified as configuration-dependent; do not add on-screen numeric text.

## Chinese pre-record list

Record these as twelve separate **WAV** files, one sentence per file, target 7–8 seconds each. Do not synthesize them with H3. For every S1 case the prompt must say exactly: `use <Audio 1> exactly as it is`.

| ID | Time | Presenter speech (Chinese) | Picture / direction |
|---|---:|---|---|
| A01 | 00:00–00:08 | 大家好，我在工厂门口，今天带大家认识这台黑红配色的 X18 电动巡航车。 | Stand centre-left, bike parked three-quarter right; locked-off medium shot. |
| A02 | 00:08–00:15 | 它采用钢管车架，低座高的巡航姿态，让上车和双脚落地都更从容。 | Walk slowly toward the bike; backward gimbal, medium shot. |
| A03 | 00:15–00:23 | 这台车的座垫高度约七百毫米，轴距约一百二十八厘米，坐姿很舒展。 | Stop beside seat; point once, no hand occlusion of the face. |
| A04 | 00:23–00:30 | 十八乘十英寸宽胎和前油刹加碟刹，是日常城市骑行很重要的基础。 | Crouch near the front wheel; single slow push-in, no cutaway. |
| A05 | 00:30–00:38 | 圆形前灯、后视镜和清晰的仪表，保留了巡航车应有的辨识度。 | Return upright and point to the headlamp and handlebar once. |
| A06 | 00:38–00:45 | X18 可以按需求配置两千瓦或三千瓦动力，具体以最终版本和当地法规为准。 | Medium profile at the side panel; no visual numbers generated. |
| A07 | 00:45–00:53 | 对应配置的最高速度资料为五十五到七十公里每小时，选择前请先确认当地要求。 | Face camera near the bike; restrained hand gesture. |
| A08 | 00:53–01:00 | 资料标注的最大续航约六十到七十公里，充电时间约七小时，实际表现看使用条件。 | Sit lightly on the stationary bike; no riding yet. |
| A09 | 01:00–01:08 | 前后减震、双人座椅和后靠背，让通勤和周末短途出行都更有余量。 | Point to rear suspension and backrest, then face camera. |
| A10 | 01:08–01:15 | NFC 刷卡启动、转向灯和刹车灯等配置，也让日常使用更直接更安心。 | Handlebar-detail orientation, presenter stays in medium shot. |
| A11 | 01:15–01:23 | 最大载荷资料为两百公斤；出发前仍要检查轮胎、刹车和电量，安全永远排在第一位。 | Helmet on, mount the stationary bike; foot stays down. |
| A12 | 01:23–01:30 | 这就是 X18 的第一印象：有巡航风格，也有面向日常的实用细节。欢迎继续了解。 | Ride away slowly on a straight, empty factory forecourt; follow shot; no spoken turn-back. |

## H3 test mapping

Each test submission remains 0.4MP, 5s and 25 steps. The full 90-second film is an edit of PASS clips, not a single generation.

| Test case | Script source | Camera / action limit |
|---|---|---|
| S1-R1-01 | A01, crop to 5s | Static medium close-up: speech and lip-sync baseline. |
| S1-R1-02 | A02, crop to 5s | One slow walking move; presenter keeps eyes toward camera. |
| S1-R1-03 | A03 or A05, crop to 5s | Human and X18 in frame; one pointing action only. |
| S1-R1-04 | A04, crop to 5s | One controlled crouch; wheel stays recognisable. |
| S1-R1-05 | A11, crop to 5s | Mount and a short, low-speed start. |
| S1-R1-06 | A12, crop to 5s | Slow ride-away only; do not force a head-turn while speaking. |

## Prompt guardrail for every S1 submission

`<Picture 1> is the single Chinese female presenter; <Picture 2> is the exact black-and-red X18 vehicle; <Picture 3> is the factory exterior. Keep all three identities unchanged. use <Audio 1> exactly as it is. No new people, no vehicle substitution, no text overlays, no logo fabrication, no beauty smoothing.`
