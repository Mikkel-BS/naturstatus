# Naturstatus Norge

Åpent norsk dashboard som viser utviklingen i vernet natur, datakilder og Norges mål mot 2030.

## Hva nettstedet måler

- Andel formelt vernet land på fastlandet: offentlig SSB-indikator for 2025 (17,8 %).
- Formelt vern i hele Norge inkludert Svalbard og Jan Mayen: regjeringens rapporterte indikator i mars 2026 (25,8 %). Dette er ikke samme geografiske avgrensning som fastlandstallet.
- SSB tabell 08936, km² vernet land: samlet, ikke-dobbeltellende total **fra 2018**, og separate vernekategorier fra **1975**. SSBs nasjonale 2009-tall inkluderer allerede Svalbard, mens Jan Mayen trekkes fra fra og med 2012. Vi validerer 2009-fastlandstall mot SSBs arkiverte publisering. Skriptet trekker dem bare fra i år de inngår.

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

## Økosystemenes representasjon og tilstand

`data/ecosystems.json` er en kildefestet, manuelt vedlikeholdt indikatoroversikt:

- **Vern:** NIBIOs skogstatistikk pr. 1. januar 2025. Av totalt skogareal ligger 7,6 % i nasjonalparker, naturreservater eller landskapsvernområder (5,6 % i bare de to sistnevnte strengere verneformene). Produktiv skog: 5,9 % for tre former og 4,4 % for de to strengere formene.
- **Naturindeks 2025:** Miljødirektoratets indikatorverdier mellom 0 og 1 for skog, våtmark, fjell, åpent lavland og ferskvann. Dette er biologisk mangfold relativt til et referansenivå, **ikke** prosent vernet areal.
- **Vern for andre økosystemer:** Regjeringens naturmelding fra 2024 rapporterer om lag 16 % vernet våtmark, 34 % fjell, 12 % kulturlandskap og åpent lavland samlet, og 14 % elver og innsjøer. Tallene er avrundet og har annet referansetidspunkt og arealgrunnlag enn NIBIOs skogtall. «Åpent lavland» i naturindeksen er ikke identisk med det samlede vernetallet for kulturlandskap og åpent lavland. Landmålets geografiske omfang (inkl. Svalbard og Jan Mayen) skiller seg fra fastlandsindikatorene.

Kilder: [Regjeringens naturmelding 2024, kap. 6.3.2](https://www.regjeringen.no/no/dokumenter/meld.-st.-35-20232024/id3054780/?ch=6), [NIBIO – verneområder](https://www.skogbruk.nibio.no/verneomrader), [Miljødirektoratet – Naturindeks 2025](https://www.miljodirektoratet.no/aktuelt/nyheter/2025/november-2025/ny-naturindeks-norsk-natur-betydelig-redusert/), [Miljødirektoratet – Norges verneområder](https://www.miljodirektoratet.no/ansvarsomrader/vernet-natur/norges-verneomrader/).

Disse indikatorene er ikke inkludert i den ukentlige SSB-oppdateringen. Ved ny publisering må `data/ecosystems.json` revideres mot kildene og kontrolleres i en pull request.

## Historikk etter økosystem: hva er faktisk dokumentert?

### Skog: offisiell verneutvikling over tre takstperioder

Fra SSB tabell [14591](https://www.ssb.no/statbank/table/14591/) henter `scripts/update_forest.py` **vernet produktivt skogareal (km²)** og **produktivt skogareal totalt (km²)** for landet i overlappende femårsperioder. Andel i prosent beregnes som (vernet areal / produktivt areal) × 100 for samme periode.

Kildens aktuelle perioder er 2019–2023, 2020–2024 og 2021–2025. De gir **ikke** årlige uavhengige observasjoner, og skal ikke behandles som det. Vekst i området kan ikke direkte tolkes som økologisk forbedring eller som kausalt resultat av én bestemt policy. Serien er heller ikke identisk med NIBIOs verneandel for produktiv skog (5,9 % i tre verneformer, 4,4 % i nasjonalparker og naturreservater i 2025): definisjoner, utvalg og verneformer er ikke harmonisert.

Filer:
- `data/forest_history.json`: kilde og dokumenterte måledata.
- `data/forest_history.csv`: transparent, eksporterbart observasjonsgrunnlag.
- `scripts/update_forest.py`: deterministisk PxWeb v2-importør med schema- og tallvalidering.

Både importøren for naturvern (SSB 08936) og for skog (SSB 14591) inngår i den ukentlige validerte datasykroniseringen og i PR-tester.

### Andre økosystemer: status, ikke oppdiktet utvikling

Naturmeldingen [Meld. St. 35 (2023–2024)](https://www.regjeringen.no/no/dokumenter/meld.-st.-35-20232024/id3054780/?ch=6) oppgir omtrentlige verneandeler for våtmark, fjell, elver/innsjøer og kulturlandskap/åpent lavland. Dette er **ett publisert tverrsnitt**, ikke en trendserie. Vi presenterer dem ikke som historiske vernekurver.

[Naturindeks for Norge 2025](https://www.naturindeks.no/DownloadData) inneholder sammenlignbare beregnede vurderinger for biologisk mangfold i 2000, 2010, 2014, 2019 og 2024. Dette gjelder *naturtilstand*, ikke *verneandel*. Naturstatus importerer og validerer den offisielle historiske Nature Index-serien fra samme versjon for fem økosystemer. Etter 2025 er det ikke planlagt samme femårige oppdatering av den samlede naturindeksen.

Det er fremdeles **ikke mulig å fastslå fra Naturstatus** om andelen vernet våtmark, fjell, elver/innsjøer eller kulturlandskap har økt med et bestemt antall prosentpoeng over tid. Dette vil kreve sammenlignbare tidsserieuttrekk eller historiske romlige analyser.


## Historisk naturtilstand per økosystem (Naturindeks 2025)

Naturstatus viser den nasjonale og regionale **naturindeksen** for skog, fjell, våtmark, åpent lavland og ferskvann i fem **referanseår: 2000, 2010, 2014, 2019 og 2024**. Den offisielle 2025-utgaven bruker 2024 som siste referanseår. For hver verdi vises 95 % konfidensintervall fra publiserte data. Fem geografiske landsdeler og «Hele Norge» kan velges.

Dette er **tilstand til biologisk mangfold**, ikke hvor stor andel av hvert økosystem som er vernet. Referanseårene er ikke årlig registrering; vi viser punkter uten å tegne interpolerte linjer. Store eller små forskjeller må tolkes i lys av statistisk usikkerhet, endret økologi og metode. Skogvernets utvikling 1990–2022 er foreløpig presentert av NIBIO som figurer, og tallene er ikke digitalisert i denne tjenesten; vi har ikke tolket grafiske kurver som kontrollerte rådata. De økosystemspesifikke verneandelene i 2024/2025 er **øyeblikksbilder**, ikke historiske serier.

Data: [Miljødirektoratet (2025), NI2025: Nature Index Values, CC BY 4.0](https://doi.org/10.21345/gfbt-pr39). Uttrekk via de samme offisielle visnings-API-ene som nettstedet [naturindeks.no](https://www.naturindeks.no/DownloadData) bruker. Alle 150 observasjoner ligger i `data/nature_index_history.json` og `data/nature_index_history.csv`. Attributtene `median`, `lower95`, `upper95` kommer uendret fra `chartSeries` (etter nøkkelnavnendring). `scripts/update_nature_index.py` validerer økosystem-ID, år, region, intervaller og siste referanseår mot eksisterende indeks.

Ved ønske om oppdatering brukes **Actions → Refresh Nature Index history (manual) → Run workflow**. Datasettene oppdateres ikke ukentlig fordi 2025-utgaven er et frosset forskningsprodukt. En senere ny versjon vil kreve metodisk versjonering i stedet for å overskrive historiske tall lydløst.

Valider mot offentlig API med `python scripts/update_nature_index.py --check`. `python -m unittest discover -s tests` verifiserer fullstendighet og matematisk korrekthet uten nettverk.

### Sammenlign utviklingen i naturindeks mellom fem økosystemer

På siden for historisk naturtilstand vises en sammenligning av beregnede naturindeksmedianer mellom referanseårene **2000 og 2024** for skog, fjell, våtmark, åpent lavland og ferskvann. Velg region i den eksisterende nedtrekksmenyen for å oppdatere alle fem rader. Et felles nullsentrert søylediagram viser positive og negative medianendringer på samme skala **innen regionen**. Bruk «Detaljer» for å åpne det enkelte økosystemets fem referanseår og 95 % konfidensintervaller.

Denne sammenligningen bruker kun `data/nature_index_history.json`; den genererer ingen nye naturindeksobservasjoner eller historiske verneandeler. Differansen mellom to medianestimater har ikke et eget beregnet konfidensintervall, og er **ikke en automatisk signifikanskonklusjon**. Det må fremdeles skilles klart mellom økologisk tilstand (naturindeks) og areal vernet i prosent.

## Datakvalitet: feilaktig 2009-topp (rettet)

En tidligere utgave trakk Svalbard fra først fra 2010, selv om SSBs landsaggregat allerede inkluderte øygruppen i **2009**. Det skapte en kunstig topp i både nasjonalparker og naturreservater, etterfulgt av en falsk nedgang i 2010. De korrigerte fastlandstallene for 2009 er **29 581,68 km² nasjonalparker** og **4 774,27 km² naturreservater** i tabell 08936. [SSBs arkiverte 2009-statistikk](https://www.ssb.no/natur-og-miljo/statistikker/arealvern/arkiv/2010-07-08) oppgir avrundet 29 582 og 4 774 km². Importen kontrollerer disse nøkkeltallene og stopper ved avvik. Kartets offisielle symboler er rødt diagonalt mønster for vedtatt vern og lilla horisontalt mønster for foreslått vern.

I figurene betyr «største registrerte endring» utelukkende den numeriske forskjellen mellom to påfølgende rapporterte år. Det dokumenterer ikke hvorfor arealet endret seg, og sier ikke hvorvidt naturtilstanden er blitt bedre.
