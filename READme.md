# Esports data pipeline

The aim of this project, is to perform Extract, Transform, Load on professional League of Legends e-sport matches data.



The matches data and  comes from Oracle's Elixir, extracted from multiple .csv files: 
[Downloads](https://oracleselixir.com/tools/downloads) 

[//]: # (The data contains 26 million user ratings of over 270,000 users on a collection of over 45,000 movies.)






## Architecture diagram

![Architecture diagram](images/architecture_diagram_v2.png) 

1. Extract the match data from [Oracle's Elixir](https://oracleselixir.com/tools/downloads).
2. Transform and enrich the data with player info using [Leaguepedia API](https://lol.fandom.com/wiki/Help:Leaguepedia_API), country geographic coordinates [GeoData MediaWiki](https://www.mediawiki.org/wiki/Extension:GeoData), and ISO 3166-1 numeric country code [Rest Countries](https://gitlab.com/amatos/rest-countries).
3. Load the data to [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html).
4. Create a dashboard using [Kibana](https://www.elastic.co/guide/en/kibana/master/index.html). 
5. Deploy the application and database on [AWS EC2](https://aws.amazon.com/ec2/).

## Dashboard
TODO
## Process 
TODO

[//]: # (Najwazniejse mozliwosci konfiguracji, czyli np lata z plikami csv, limits, etc etc)

[//]: # (opisaywac funkcje opisac jak dla )

[//]: # (Pobieram data frame w klasie GetData)


## Setup
TODO

[//]: # (wrzuc link do instalacji elastica)

[//]: # (instalacja kibany)

[//]: # (index+mapping)

[//]: # (wrzucanie do bazy)

## Potential use cases
TODO



