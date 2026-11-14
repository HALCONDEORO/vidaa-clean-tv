# Check compatibility by feature, not brand

A Hisense or Toshiba badge is not enough to choose a cleanup method. Even
when two sets run VIDAA, a DNS result on one model does not verify its
settings menus, local remote control or any software modification on another.

## Identify the set before changing anything

1. Read the exact model, region and full firmware/build string from the
   normal information menu. Menu names vary; do not enter a service menu.
2. Check the model's manual or manufacturer support page for the operating
   system. Do not treat a VIDAA-branded app or a package name as proof of the
   OS. The [Clean Your TV Hisense directory](https://cleanyourtv.wiki/tv/hisense/)
   distinguishes non-Android VIDAA from Android-based Hisense models,
   including China-market models with VIDAA branding.
3. Choose the feature below. If identification is still uncertain, keep the
   set unchanged and collect the missing information first. VIDAA's
   [official support page](https://www.vidaa.com/support/) directs hardware
   support questions to the TV manufacturer.

## What the current evidence covers

| Feature | Evidence available | What it does not establish |
|---|---|---|
| On-device privacy settings | Sourced menu paths in [route 1](01-on-device-settings.md) | No completed settings session is logged here. Similar firmware names do not verify the menu path or its effect. |
| DNS filtering | [OliverS45's contribution](https://github.com/HALCONDEORO/vidaa-clean-tv/pull/31), logged in [TESTING.md](../TESTING.md): owner-reported Hisense 65A67H, V0000.09.09G.P0930, 2026-11-08 | Region was not recorded. No raw query-log export was analysed. This is not a Toshiba result, a settings test or a promise about every streaming app. |
| Upstream DNS rules | [ipanalytics' blocklist](https://github.com/ipanalytics/Hisense-VIDAA-DNS-Clean-TV-Blocklist): Hisense observations and explicitly labeled inferred candidates | A hostname's presence or name alone does not prove its purpose. New firmware and regions may use different hosts; blocking a shared host can break required features. |
| Local MQTT remote control | [warrenrees/ha_vidaatv](https://github.com/warrenrees/ha_vidaatv) describes PIN pairing and support for MQTT-capable Hisense/VIDAA sets and some Toshiba sets | Not tested here on the Toshiba 50UV1553DB. Remote key control is not evidence of package management or permission to change software. See the [exploration note](04-local-control-mqtt.md). |
| ADB/package cleanup | Clean Your TV documents Android-based models separately from non-Android VIDAA | An Android model's package list must not be applied to a non-Android VIDAA TV. This project supplies no ADB workflow. |

These are different kinds of evidence, not a list of certified devices.
The per-model pages are in [tv/](tv/README.md). A firmware update is a reason
to recheck affected steps, not a reason to copy another model's results.

## What about native Home or launcher projects?

[nineodernein/hisense-vidaa-clean-home](https://github.com/nineodernein/hisense-vidaa-clean-home)
reports a native Home integration on one MTK9602 / VIDAA U9 / P0930 device.
Its README distinguishes that original trial from its generalized public
package, which it says has not been installed as a new build on the reference
TV. Those are the author's reports, not tests by this project.

That work is a separate software-modification route. It is not imported,
installed, recommended as a cleanup step or covered by this project's
rollback instructions. Sharing the VIDAA name, U9 label or P0930 suffix is
not enough to establish compatibility. This project stays with normal
settings and DNS filtering; no firmware, native Home or service-menu changes.

## Report one feature at a time

Use the [model report guidance](../CONTRIBUTING.md#reporting-a-new-model) and
[first-session protocol](05-first-hardware-session.md). Include the model,
region, complete firmware string, exact step, expected and observed result,
and what was reverted. State which features were not tested. An owner report
is useful without pretending to be an independent hardware test.

Sources reviewed 2026-11-14. No new hardware testing was performed for this
page. Original wording; no third-party code, blocklist or device files copied.
