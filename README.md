# PCIM

DEV.PCIM is the repository for all artifacts related to the development of the IHE DEV PCIM Profile.

## Overview

The Point-of-Care Identity Management (PCIM) Profile defines transactions for reporting, managing and consuming device-patient association status. Accurate device-patient association status has numerous benefits, but key to the profile is ensuring that device data being transmitted can be stamped with accurate patient information. This not only increases patient safety, but also provides value to the caregiver as the alarm or other data has the patient and optional location attached to it. 

## Status

A foundational change proposal (CP), Revision 2.0, that refines the [Point-of-Care Identity Management (PCIM) Revsion 1.1 - Trial implementation specification](https://www.ihe.net/uploadedFiles/Documents/PCD/IHE_PCD_Suppl_PCIM.pdf), has been balloted, approved and posted for [public review](https://profiles.ihe.net/DEV/PCIM/index.html). 

A work list is in place for review of additional CPs.

[CP Work List](https://github.com/IHE/DEV.PCIM/blob/master/asciidoc/index.adoc)

## Process

We are using AsciiDoc to author our CP documents and use a GitHub flow process. Create a PR branch and make your changes and then push and assign Eldon Metz and Tom Kowalczyk as approvers for review. 

To generate the HTML format for the docs, use the gen-html.sh or gen-html.bat scripts. The output is found in the output directory in your local workspace at the root of the repo. Note, they are ignored and not saved in the repository.

### Linux

```./gen-html.sh```

### Windows

Double click gen-html.bat or run ```gen-html.bat``` in the command prompt or in PowerShell.

## Contributing

Please contact [Eldon Metz](mailto:emetz@innovisionmedical.com)  or [Tom Kowalczyk](mailto:Tom.Kowalczyk@BBraunUSA.com) if you wish to contribute to this profile.

Working Group meetings are held weekly on Friday's at 10am Central Time.
