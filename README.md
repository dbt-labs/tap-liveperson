# This repo is no longer actively maintained

This repository is no longer actively maintained. The dbt Labs team will no longer be accepting pull requests or responding to issues on this repo. If you would like to take over maintenance of this repo, please open an issue indicating so. The previous maintainers of the repo will be happy to help transfer over ownership to a good home :) 

# tap-liveperson

Author: Drew Banin (drew@fishtownanalytics.com)

This is a [Singer](http://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

It:

- Generates a catalog of available data in LivePerson
- Extracts the following resources:
  - [Engagement History](https://developers.liveperson.com/data-engagement-history-overview.html)
  - [Messaging Interactions](https://developers.liveperson.com/data-messaging-interactions-overview.html)
  - [Agent Groups](https://developers.liveperson.com/agent-groups-api-methods-get-all-agent-groups.html)
  - [Skills](https://developers.liveperson.com/skills-api-methods-get-all-skills.html)
  - [Users](https://developers.liveperson.com/users-api-methods-get-all-users.html)
  - [Agent Activity](https://developers.liveperson.com/data-access-api-methods-agent-activity.html)
  - [Queue Health](https://developers.liveperson.com/operational-realtime-api-methods-queue-health.html)

### Quick Start

1. Install

```bash
git clone git@github.com:fishtown-analytics/tap-liveperson.git
cd tap-liveperson
pip install .
```

2. Get credentials from Liveperson. You'll need to:

- create an OAuth app
- get the app key, app secret, client ID, and client secret. Save these -- you'll need them in the next step.

3. Create the config file.

There is a template you can use at `config.json.example`, just copy it to `config.json` in the repo root and insert your client ID and secret.

4. Run the application to generate a catalog.

```bash
tap-liveperson -c config.json --discover > catalog.json
```

5. Select the tables you'd like to replicate

Step 4 a file called `catalog.json` that specifies all the available endpoints and fields. You'll need to open the file and select the ones you'd like to replicate. See the [Singer guide on Catalog Format](https://github.com/singer-io/getting-started/blob/c3de2a10e10164689ddd6f24fee7289184682c1f/BEST_PRACTICES.md#catalog-format) for more information on how tables are selected.

6. Run it!

```bash
tap-liveperson -c config.json --catalog catalog.json
```

Copyright &copy; 2019 Fishtown Analytics
