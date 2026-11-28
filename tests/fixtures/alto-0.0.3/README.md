# Alto 0.0.3 learner profile

The shipped Linux x86-64 app wrote both files under `profile/`. The synthetic learner uses SM-2 and practices Note Identification on the treble staff from D3 to E7. On November 25, 2026, at 12:00 UTC, the learner answered C for E3. The card is due again at 12:01 UTC.

## Fixture creation

1. Download the Linux archive, `SHA256SUMS`, and `SHA256SUMS.sig` from the [Alto v0.0.3 release](https://github.com/altosaurus/alto/releases/tag/v0.0.3). The archive's SHA-256 is `75c652ce18ec589c394bc7982dd54ff146df15d77f5cddcd8ca38d6c035f3285`.
2. On Linux x86-64 with libfaketime installed, run the extracted executable with an empty learner directory and a fixed UTC clock.

   ```sh
   sha256sum --check --ignore-missing SHA256SUMS
   tar -xzf alto-0.0.3-linux-x86_64.tar.gz
   export ALTO_HOME="$(mktemp -d)"
   TZ=UTC FAKETIME='2026-11-25 12:00:00' FAKETIME_DONT_FAKE_MONOTONIC=1 \
     LD_PRELOAD=/usr/lib/x86_64-linux-gnu/faketime/libfaketime.so.1 \
     ./alto-0.0.3-linux-x86_64/alto/alto
   ```

3. Create the profile **Upgrade Learner**. In **Settings → Practice**, select **SM-2** and close the dialog.
4. Open **Note Identification → Exercise settings → Clefs** and clear **Bass**, leaving **Treble** selected. Go back, open **Range**, and click **Lower the highest note** once. The range reads **D3 – E7**.
5. Collapse exercise settings and answer **C** once. Quit Alto through the menu. Copy `data/alto.db` and `config/alto/alto.ini` from `ALTO_HOME`, preserving their directories. The response duration and window geometry can vary.

## Candidate check

The Linux package job gives the installed candidate a disposable copy of this directory at 12:02 UTC. It checks the original attempt and due date, opens Note Identification, checks the saved controls, and answers E. A second launch must find both attempts on the original card and a future due date.

When preparing the next release, refresh the fixture from the previous stable download and update the producing version, archive checksum, and expected review in the [packaged upgrade check](../../../packaging/linux/check_profile_upgrade.py).
