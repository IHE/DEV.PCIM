# PCIM

DEV.PCIM is the repository for all artifacts related to the development of the IHE DEV PCIM Profile.

## Overview

The Point-of-Care Identity Management (PCIM) Profile defines transactions for reporting, managing and consuming device-patient association status. Accurate device-patient association status has numerous benefits, but key to the profile is ensuring that device data being transmitted can be stamped with accurate patient information. This not only increases patient safety, but also provides value to the caregiver as the alarm or other data has the patient and optional location attached to it. 

## Status

We are currently working on change proposals (CP) to refine the [Point-of-Care Identity Management (PCIM) Revsion 1.1 - Trial implementation specification](https://www.ihe.net/uploadedFiles/Documents/PCD/IHE_PCD_Suppl_PCIM.pdf).

Version 1.2 has been submitted for approval along with the corresponding Foundational CP. The links below take you directly to the HTML version of these documents. 

* [Foundational CP](https://htmlpreview.github.io/?https://github.com/IHE/DEV.PCIM/blob/master/CPs/for_approval/cp_nn1.html)
* [PCIM Trial Spec with Foundational Changes Applied – Version 1.2](https://htmlpreview.github.io/?https://github.com/IHE/DEV.PCIM/blob/master/CPs/for_approval/IHE_DEV_Suppl_PCIM_Foundational%20CP%20applied.html)

A work list is in place for review of potential upcoming CPs.

[CP Work List](https://github.com/IHE/DEV.PCIM/blob/master/CPs/index.adoc)

## Process

We are using AsciiDoc to author our CP documents and use a GitHub flow process. Create a PR branch and make your changes and then push and assign Eldon Metz and Tom Kowalczyk as approvers for review. 

To generate the HTML format for the docs, use the gradle wrapper with the asciidoctor task. The output is found in the CPs/html directory in your local workspace, they are not stored in the repository.

```./gradlew asciidoctor```

## Contributing

Please contact [Eldon Metz](mailto:emetz@innovisionmedical.com)  or [Tom Kowalczyk](mailto:Tom.Kowalczyk@BBraunUSA.com) if you wish to contribute to this profile.

Working Group meetings are held weekly on Friday's at 10am Central Time.
