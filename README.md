# Naturstatus Norge

Åpen, kildebasert oversikt over Norges naturmål og historisk arealvern.

## Status

Første versjon av nettsiden har dokumenterte sammenligningspunkter for fastlandet (2020 og 2025) og et særskilt nasjonalt tall rapportert mars 2026. Dette er **ikke** en full historisk tidsserie. Vi skal kun publisere en full år-for-år-serie når vi har verifisert måleenhet, geografisk avgrensning og offisiell kilde fra SSB.

## Kjør lokalt

Ingen byggavhengigheter: `python -m http.server 8000` og åpne localhost:8000.

Kjør tester: `python -m unittest discover -s tests`.

## GitHub Pages

Settings → Pages → Build and deployment → **GitHub Actions**. Etter at denne grenen er merget til main vil publisering trigges på hver push. Forventet URL: https://mikkel-bs.github.io/naturstatus/.

## Dataprinsipper

Arealvern på fastlandet skal ikke presenteres som oppnåelse av et mål som også omfatter Svalbard og Jan Mayen. Formelt vern er ikke identisk med samlet måloppnåelse, siden kvalifiserte OECM-tiltak også kan telle. Vernet areal sier ikke i seg selv noe endelig om naturtilstand.

Kilder: [SSB 08936](https://www.ssb.no/statbank/table/08936/), [Meld. St. 35 (2023–2024)](https://www.regjeringen.no/no/dokumenter/meld.-st.-35-20232024/id3054780/).

## Neste oppgaver

- Verifiser og importer årlig SSB-serie fra 1975 og fremover.
- Vis dagens vern og foreslått vern på kart fra Naturbase.
- Dokumenter metode, kildeversjoner og datakvalitet.
