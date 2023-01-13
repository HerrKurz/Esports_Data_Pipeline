# Esports data pipeline

- This project aims to perform Extract, Transform, and Load professional League of Legends e-sport matches data and prepares it for further analysis.


- The primary data source comes from Oracle`s Elixir ([Downloads](https://oracleselixir.com/tools/downloads)), which provides professional League of Legends e-sport matches data from 2014 to today. It's updated daily, and each calendar year has a separate .csv file.


- Additional e-sport players' data is extracted from [Leaguepedia API](https://lol.fandom.com/wiki/Help:Leaguepedia_API). This step allows us to easily enrich the data by fetching other external resources. For example, geographic data enrichment involves adding country code or latitude and longitude to an existing dataset, enabling [Kibana's Maps](https://www.elastic.co/guide/en/kibana/current/maps.html) to visualize and explore the data.

## Architecture diagram

![Architecture diagram](images/architecture_diagram_v2.png) 

1. Extract the match data from [Oracle's Elixir](https://oracleselixir.com/tools/downloads).
2. Transform and enrich the data with player info using [Leaguepedia API](https://lol.fandom.com/wiki/Help:Leaguepedia_API), country geographic coordinates [GeoData MediaWiki](https://www.mediawiki.org/wiki/Extension:GeoData), and ISO 3166-1 numeric country code [Rest Countries](https://gitlab.com/amatos/rest-countries).
3. Load the data to [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html).
4. Create a dashboard using [Kibana](https://www.elastic.co/guide/en/kibana/master/index.html). 
5. Deploy the application and database on [AWS EC2](https://aws.amazon.com/ec2/).

## Dashboard
![General dashboard](images/general_info_dashboard.png) 

### Database access
In order to gain the access to the database and other dashboards (Viewer role), please contact me directly. EC2 t2.medium with Elasticsearch + Kibana is hosted at http://3.121.139.77:5601/.
## Project structure
```
📦Esports_data_pipeline
 ┣ 📂Elasticsearch
 ┃ ┣ 📜dashboards.txt # - Backup for dashboards created in Kibana.
 ┃ ┣ 📜index_template.txt # - Template settings and mappings for indexes.
 ┃ ┣ 📜mapping.txt
 ┃ ┗ 📜visualizations.txt
 ┣ 📂images
 ┃ ┣ 📜architecture_diagram_v2.png
 ┃ ┣ 📜diagram_architecture.jpg
 ┃ ┗ 📜general_info_dashboard.png
 ┣ 📂src
 ┃ ┣ 📜data_enricher.py # - Handles additional extractions and data transformations.
 ┃ ┣ 📜data_extractor.py # - Handles the main extraction part.
 ┃ ┣ 📜elasticsearch_connector.py # - Handles the connection between Python and Elasticsearch and loads the data to the database.
 ┃ ┗ 📜utils.py # - Utilities related to the project.
 ┣ 📜.env
 ┣ 📜.gitignore 
 ┣ 📜READme.md
 ┣ 📜config.py # - Configuration file that contains constant variables.
 ┣ 📜main.py
 ┗ 📜requirements.txt
```

## Process 
TODO
GetData class downloads the .csv files with e-sport matches data. 

[//]: # (class method download_csv&#40;self, limits: int or None, year: list&#41; -> pd.DataFrame:)


[//]: # (Najwazniejse mozliwosci konfiguracji, czyli np lata z plikami csv, limits, etc etc)

[//]: # (opisaywac funkcje opisac jak dla )

[//]: # (Pobieram data frame w klasie GetData)


    


## Setup
TODO

[//]: # (wrzuc link do instalacji elastica)

[//]: # (instalacja kibany)


[//]: # (index+mapping)

[//]: # (wrzucanie do bazy)

## Potential improvements and use cases
Technologies:
- Use a **data orchestration** tool to improve control over data flow [Apache Airflow
](https://airflow.apache.org/) or [Perfect](https://www.prefect.io/). Improve logging and automate the script to update the data daily.
- Update the setup process using [Terraform](https://www.terraform.io/) in order to reuse, and provision **infrastructure as a code**.

Data enrichment:
- Add teams' data from [Leaguepedia API](https://lol.fandom.com/wiki/Help:Leaguepedia_API).
- Backfill missing players' data using [Liquipedia API](https://liquipedia.net/commons/Liquipedia:API_Usage_Guidelines).
- Use social media links associated with a player/team to gain insight into their social media reach, following etc. 

Dataset could be used to:

- Calculate relative skill levels of players using [Elo rating system](https://en.wikipedia.org/wiki/Elo_rating_system).
- Create a classification model that determines whether given team will win the upcoming match.

