# Naturstatus Norge

Åpent norsk dashboard som viser utviklingen i vernet natur, datakilder og Norges mål mot 2030.

## Hva nettstedet måler

- Andel formelt vernet land på fastlandet: offentlig SSB-indikator for 2025 (17,8 %).
- Formelt vern i hele Norge inkludert Svalbard og Jan Mayen: regjeringens rapporterte indikator i mars 2026 (25,8 %). Dette er ikke samme geografiske avgrensning som fastlandstallet.
- SSB tabell 08936, km² vernet land: samlet, ikke-dobbeltellende total **fra 2018**, og separate vernekategorier fra **1975**. SSB begynte å inkludere Svalbard i nasjonale tall i 2010 og Jan Mayen i 2012. Skriptet trekker dem bare fra i år de inngår.

Målet om 30 % i 2030 inkluderer kvalifiserte OECM-tiltak og må ikke tolkes som likestilt med andel formelt vern. En økning i vern sier heller ikke alene noe sikkert om naturtilstand eller effektiv forvaltning.

## Gjeldende vernekart

Kartet viser **nåværende** vern og formelt foreslått vern fra Miljødirektoratets WMS (`naturvern_omrade` og `foreslatt_naturvern_omrade`). Klikk på kartet henter opplysninger med ArcGIS FeatureServer (lag 0 og 4). Kartverket leverer bakgrunnskart. Kartet er ikke en tidsmaskin eller en uttømmende beskrivelse av økologisk tilstand. Det viser ikke planlagt utbygging.

Kildenes ytelse og tilgjengelighet påvirker kartet. Importen av statistikk er uavhengig av GIS-tjenestene. Automatiske PR-tester kontrollerer WMS, CORS, FeatureServer og et kartbilde.

## Lokal utvikling

Ingen byggavhengigheter for nettsiden:

```bash
python -m http.server 8000
python -m unittest discover -s tests
```

Hent den fullstendige serien fra SSB (krever internett):

```bash
python scripts/update_ssb.py
```

Dette henter PxWeb API v2, validerer datastrukturen og kontrollerer at 2025-fastlandstallet blir 57 483,38 km². Ved ugyldig input stoppes importen med feil; eksisterende data beholdes.

## Kontinuerlige oppdateringer

- Pull requests: `.github/workflows/ci.yml` kjører offline tester og et live SSB-integrasjonstest.
- Ukentlig og ved endring av importkode: `.github/workflows/update-data.yml` henter og verifiserer SSB, committer kun reelle dataendringer.
- `.github/workflows/pages.yml` publiserer på main og etter vellykket dataoppdaterings-workflow.

GitHub Pages må aktiveres under **Settings → Pages → Source: GitHub Actions**.

## Kilder

[SSB tabell 08936](https://www.ssb.no/statbank/table/08936/), [SSB metode for vernede områder](https://www.ssb.no/natur-og-miljo/areal/statistikk/vernede-omrader), [Meld. St. 35 (2023–2024)](https://www.regjeringen.no/no/dokumenter/meld.-st.-35-20232024/id3054780/).

Historiske SSB-statistikker kan endres ved revisjon og ved endringer i kartgrunnlag og vernelovgivning. Før 2002 er noen arealer basert på verneforskrifter i stedet for digitale vernekart. Datapunkter som tilhører forskjellige kategorier skal ikke summeres uten kontroll av overlapp.

## 2030-mål: oppfølging av norsk landbevaring

`data/targets.json` dokumenterer Norges landmål for 2030 (30 % inkludert Svalbard og Jan Mayen), rapportert andel formelt vern (25,8 %, regjeringens rapport av 3. mars 2026) og **ukjent** kvalifisert OECM-andel. Seksjonen viser nominell differanse på 4,2 prosentpoeng, men fremsetter **ingen prognose for 2030** og påstår ikke at denne differansen er nødvendig nytt vern. Måloppnåelse kan ikke konkluderes fra disse tallene alene.

Endring av målgrunnlaget krever dokumentert kilde og oppdaterte metodetester. SSBs historikk for fastlandet brukes ikke til å ekstrapolere målet med annet geografisk omfang.
