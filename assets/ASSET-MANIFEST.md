# MiniMax H3 scenario-test asset manifest

Verified 2026-08-08. All image dimensions and SHA-256 values below were checked locally before transfer to the test host.

## Identity-critical X18 source images

Use only this black-and-red X18 family in every prompt. Do not introduce a different body, wheel, seat, headlamp, handlebar, mirror, or colourway.

| File | Origin | Dimensions | SHA-256 |
|---|---|---:|---|
| `vehicle/X18-black-red/x18-front-left-45.png` | User-supplied X18 `black_red/1.png` | 1600×1200 | `72fbd5edc80ff416c3d19e23e2d05685cf6e380dce05cc9f9b44422e7cee9c66` |
| `vehicle/X18-black-red/x18-side-profile.png` | User-supplied X18 source | 1600×1200 | `b3a7630064cbb933d7c24ffba2faa273a714de801cf9d5b811427c6624ecd6f3` |
| `vehicle/X18-black-red/x18-front.png` | User-supplied X18 source | 1600×1200 | `efa81162cb49d2e257a7a92b62def8c3817a1087c198a20244e858f6e5cf11a1` |

## Generated reference assets

| File | Intended use | Dimensions | SHA-256 |
|---|---|---:|---|
| `generated/factory-gate-reference.png` | S1 factory exterior plate | 1672×941 | `960e7f414cdb977315ea847585f0e815a2e94a8e43034f2a9093f2f1d42d6cbd` |
| `generated/china-host-turnaround.png` | S1 presenter three-view identity record | 1536×1024 | `3e1456e4e4d700eaae4a307d9612c27992220b058a9333768e1b190d584c075c` |
| `generated/china-host-front.png` | S1 presenter input, derived from the left panel of the turnaround | 512×1024 | `963582f017435e2d6746f4bc9d7de97539530239274862a8b56acd8c67d381ea` |
| `generated/brazil-customer-a-turnaround.png` | S2 customer A three-view identity record | 1536×1024 | `2006bc6558303fb59955c2ec60838a2700cb23e3e9d3a6261ec1e184ae8c20a1` |
| `generated/brazil-customer-a-front.png` | S2 customer A input, derived from the left panel of the turnaround | 512×1024 | `56d7b268453cc23ec18c03b725edd660494f2fe0ce4842fdd2208d6aea5cce76` |
| `generated/brazil-customer-b-turnaround.png` | S2 customer B three-view identity record | 1536×1024 | `670fb49b5e0a3e164b0341d3dbe31ddac19a4254cb69029ae8eba475fd160752` |
| `generated/brazil-customer-b-front.png` | S2 customer B input, derived from the left panel of the turnaround | 512×1024 | `6de440909a544b6b73e1e3c1e2aabdb4cac57f486bb8d6807cf008d624bd3dcf` |
| `generated/brazil-street-scene.png` | S2 São Paulo street plate | 1672×941 | `0fec1ba89240a0eebb74f44243707e0ac98731ba751ad64a0149e6782637d361` |

Generated references are test assets, not production claims. The S1 audio requirement remains separate: supply real pre-recorded Chinese WAV segments before any S1 submission.
