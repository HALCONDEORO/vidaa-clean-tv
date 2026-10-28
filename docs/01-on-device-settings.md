# Route 1: on-device settings (reversible)

Time: about 5 minutes with the remote. Every step is a normal setting and
can be switched back at any time.

Menu names vary between VIDAA versions and brands. If a name does not match,
open the privacy section and read down it: you are looking for anything about
viewing information, usage data, content recognition or advertising.

## 1. Turn off content recognition (ACR) and usage data

The tracking on VIDAA is called **Enhanced Viewing Service**: it is opt-in
at setup and recognises what is on screen from its audio. Where the official
Hisense VIDAA manuals (U5, U6 and U9) put it:

- **Settings → Advanced settings → Enhanced viewing settings → Enable
  Automatic Content Recognition → Off**. Confirm the two pop-ups ("No, thank
  you" and "Yes, Decline"). On VIDAA U5 the same setting sits under
  **Settings → System → Advanced settings**.
- Other guides describe it under **Settings → System → Advanced settings →
  Privacy**. Menu names vary by VIDAA version, brand and country; if you
  cannot find Enhanced Viewing at all, your model may not offer it.

In the same area, turn off:

- Device usage data
- App usage data collection

On VIDAA U9 the Enhanced Viewing menu also lists **Enable Personalized Ads**,
**Enable Content Recommendation** and **Enable Automatic Picture and Audio
Quality**; the manuals show them switching off there as well. On U5 they go
off together with Automatic Content Recognition.

What this does: turns off the documented content-recognition and usage-data
settings. The vendor documents the recognition setting as covering viewing
over apps, HDMI and broadcast; its exact scope and effect on the target TV
remain unverified until logged in [../TESTING.md](../TESTING.md).

Sources: the [VIDAA OS privacy policy](https://www.vidaa.com/os-privacy-policy/)
describes the Enhanced Viewing Service / ACR opt-out in the device Settings
menu; the [justatv.eu VIDAA guide](https://justatv.eu/en/guides/cleaning-up-a-hisense-television-with-vidaa)
and [velmo.one ACR guide](https://velmo.one/guides/turn-off-acr-hisense-tv/)
give menu paths; and the [Clean Your TV non-Android guide](https://cleanyour.tv/not-android)
compiles the exact paths and toggle names from the official Hisense VIDAA
U5/U6/U9 manuals (guide last checked 26 Oct 2026). European models may use
different names than US manuals.

## 2. Turn off personalized advertising and reset the ad ID

Per the VIDAA U9 manual: **Settings → System → Advanced settings →
Personalised Ads → Off**, and **Reset Ads ID** in the same place. Older menus
may not have it. Ads can still appear; the documented personalization toggle
controls whether they are chosen from a profile of you, not how many there
are. Its effect has not been verified on the target TV.

## 3. Withdraw the data-sharing consents you do not want

The manuals put these under **Settings → Support → Disclaimer and Privacy**,
then **Data Sharing, Privacy and EULA** (VIDAA U9), **EULA and Other Policy
and Services** (U6), or the same menu without a submenu (U5). Deny the
consents you do not want; you can agree to them again in the same menu.

Two things to know there:

- Unticking the **VIDAA Account** consent signs you out of the account.
- **Remove User Data**, in the same menu, deletes your stored usage data from
  the TV and the cloud. That deletion cannot be undone, so read what it says
  before confirming.

## 4. Hands-free voice (optional)

If your set listens for "Hey VIDAA" or "Alexa": **Settings → System → Voice
Service → VIDAA Voice or Amazon Alexa → Hands-Free Off** (U9), or
**Amazon Alexa → Built-in Microphone Off** on U5. TVs with far-field voice
also have a physical microphone switch on the set; the printed manual shows
where. The remote's mic button keeps working either way.

## 5. VIDAA account

The TV works without a VIDAA account. You only need one to install apps from
the VIDAA store. If you never use the store, sign out: one identifier fewer
tied to what you watch.

## 6. Home screen apps

Select an app on the home screen. If the system offers a bin icon, that app can
be removed. System apps and commercially bundled apps cannot be removed - by
design, with no way around it. Everything can be reordered: push what you do
not use to the end.

## 7. After every update

Some VIDAA updates reset privacy options, or re-ask for consent in a way that
re-enables them if you accept quickly with the remote. When the TV updates,
spend 30 seconds re-checking the privacy section.

## Status on Toshiba 50UV1553DB

Exact menu names are unverified on this model until the first hardware session
is logged in [../TESTING.md](../TESTING.md).
