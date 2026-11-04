# PCIM

DEV.PCIM is the repository for all artifacts related to the development of the IHE DEV PCIM Profile.

## Overview

The Point-of-Care Identity Management (PCIM) Profile defines transactions for reporting, managing and consuming device-patient association status. Accurate device-patient association status has numerous benefits, but key to the profile is ensuring that device data being transmitted can be stamped with accurate patient information. This not only increases patient safety, but also provides value to the caregiver as the alarm or other data has the patient and optional location attached to it. 

## Status

A handful of change proposals have been incorporated into the Trial Implementation based on feedback identified from the working group meetings, IHE Connectathon testing and HIMSS interoperability showcase demonstrations over the past few years.
The latest [PCIM specification](https://profiles.ihe.net/DEV/PCIM/index.html) is published and available online.

A work list is in place for review of additional CPs.

[CP Work List](https://github.com/IHE/DEV.PCIM/blob/master/asciidoc/index.adoc)

## Process

We are using AsciiDoc to author our CP documents and use a GitHub flow process. Create a PR branch and make your changes and then push and assign Eldon Metz and Tom Kowalczyk as approvers for review. 

To generate the HTML format for the docs, use the gen-html.sh or gen-html.bat scripts. The output is found in the output directory in your local workspace at the root of the repo. Note, they are ignored and not saved in the repository.

### Linux

```./gen-html.sh```

### Windows

Double click gen-html.bat or run ```gen-html.bat``` in the command prompt or in PowerShell.

## Reviewing the proposed OID edition

Build from the repository root with JDK 17:

```sh
./.ci/asciidoc-converter/gradlew -p .ci/asciidoc-converter check asciidoctor
```

Open `output/html/IHE_DEV_Suppl_PCIM.html`. Appendix A.7 contains governance;
Appendix B contains the entity registry, generated requirement OIDs, and the
historical transaction/message-profile crosswalk. The WG walkthrough is
`output/html/pcim_oid_wg_review.html`.

The build generates OID attributes and the catalogue before rendering. Edit
`asciidoc/pcim_oid_entities.adoc` for entity identities and the supplement's
semantic requirement blocks for requirements; do not edit generated files.
Keep the entity table's six-column format, explicit anchors and full numeric
OIDs. The parser deliberately rejects unsupported cell syntax.

Review JSON is in `output/referenced-artifacts`: requirements, requirement trace,
and OID registry. These artifacts are marked draft and new allocations remain
proposed. They are not approved assignments or a complete normative inventory.
After intentional source edits, refresh the committed review fixture with
`pcimRequirementsFixture`. JSON generation refreshes commit provenance on each
run. A standalone AsciiDoc render requires its generated includes first.

## Contributing

Please contact [Eldon Metz](mailto:emetz@innovisionmedical.com)  or [Tom Kowalczyk](mailto:Tom.Kowalczyk@BBraunUSA.com) if you wish to contribute to this profile.

Working Group meetings are held weekly on Thursday's at 11am Central Time.
