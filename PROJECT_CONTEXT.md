# Intro

We are doing a hackathon that has the goal of creating products that maximize social utility. There are prompts that teams can choose from to guide their implimenation.

## Prompt that guides the implimentation of this product:

```
The 'ID Gap' & The Cycle of Invisibility
Problem Outline

In Victoria, government-issued identification (ID) is the 'master key' to survival. Without it, an individual cannot open a bank account, rent an apartment, access many provincial health services, or even pick up a registered parcel. For the estimated 1,749+ unhoused individuals in Greater Victoria (as of the 2025 count), maintaining this 'key' is nearly impossible.

Core Friction Points
The 'ID to get ID' Paradox

To replace a lost BC Services Card, you often need a Birth Certificate. To get a Birth Certificate, you often need photo ID. This circular logic creates a bureaucratic 'lock-out' that can take months of social worker intervention to resolve.

The 'Street Tax' on Paper

Vulnerable people face high rates of theft and weather damage. Carrying a social insurance card or a paper birth certificate in a backpack during a Victoria winter is a recipe for losing one's legal identity.

The Fixed Address Barrier

Many government applications still require a physical mailing address for delivery. While some local shelters offer mail-drop services, these systems are often overwhelmed and manual.

Digital Literacy vs. Digital Mandate

As BC moves toward 'Digital ID', those without reliable smartphones, data plans, or the ability to navigate complex 2FA are being further marginalized.

Solution Targets
WHAT THIS CHALLENGE WANTS TEAMS TO BUILD

Digital document recovery & vaulting systems
Shelter mail-drop management & notification tools
Low-bandwidth/Offline-first Digital ID accessibility layers
```

# Our project idea

```
Assumptions:
Homeless does not have phones
The system is not responsible for tracking the address of the user
kiosk/org gonna use the software
They have ID’s on them that they want to upload
Def web apps
Actors:
System administrators: homeless shelter administrators, clinic staff, community programs, etc.. (resources that the user are trying to access)
Homeless people
Use cases:
As a system administrator I want to be able to access the documents of a user by using their biometrics
As a user I want to be able to automatically create my profile by registering my biometrics and uploading my documents



Tech side
Functional requirements:
Administrator dashboard - clinic, government person
We should need a search functionality that works off biometric data given by the person that came in
** Only available if the person wanting the service authenticates
This will have all the info about the ids like passport number, sin number
Consumer side - Homeless person
A way to scan biometric - physical
Fingerprints
Then this is uploaded in with a upsert check
Any documents scanned will be then uploaded, linked to that biometric id somehow, and need to validate that it's actually a gov doc and not random stuff.
Need a way to validate that document, could be autonomous or we just trust the person, or we have a man at the clinic or whatever
```
