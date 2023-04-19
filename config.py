"""
Configuration file that contains constant variables.
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Elasticsearch connector variables
URL = os.getenv("URL")
PORT = int(os.getenv("PORT"))
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

# Leaguepedia fields variable
FIELDS = "ID, OverviewPage, Player, Image, Name, NativeName, NameAlphabet, NameFull, Country, Nationality, NationalityPrimary, Age, Birthdate, ResidencyFormer, Team, Team2, CurrentTeams, TeamSystem, Team2System, Residency, Role, FavChamps, SoloqueueIds, Askfm, Discord, Facebook, Instagram, Lolpros, Reddit, Snapchat, Stream, Twitter, Vk, Website, Weibo, Youtube, TeamLast, RoleLast, IsRetired, ToWildrift, IsPersonality, IsSubstitute, IsTrainee, IsLowercase, IsAutoTeam, IsLowContent"
TEAM_FIELDS = "Name, OverviewPage, Short, Location, TeamLocation, Region, OrganizationPage, Image, Twitter, Youtube, Facebook, Instagram, Discord, Snapchat, Vk, Subreddit, Website, RosterPhoto, IsDisbanded, RenamedTo, IsLowercase"

# OraclesElixir .csv URL links
BASE_URL = "https://drive.google.com/uc?id="
CSV_FILES = {
    "2023": BASE_URL+"1XXk2LO0CsNADBB1LRGOV5rUpyZdEZ8s2",
    "2022": BASE_URL+"1EHmptHyzY8owv0BAcNKtkQpMwfkURwRy",
    "2021": BASE_URL+"1fzwTTz77hcnYjOnO9ONeoPrkWCoOSecA",
    "2020": BASE_URL+"1dlSIczXShnv1vIfGNvBjgk-thMKA5j7d",
    "2019": BASE_URL+"11eKtScnZcpfZcD3w3UrD7nnpfLHvj9_t",
    "2018": BASE_URL+"1GsNetJQOMx0QJ6_FN8M1kwGvU_GPPcPZ",
    "2017": BASE_URL+"11fx3nNjSYB0X8vKxLAbYOrS2Bu6avm9A",
    "2016": BASE_URL+"1muyfpaIqk8_0BFkgLCWXDGNgWSXoPBwG",
    "2015": BASE_URL+"1qyckLuw0-hJM8XqFhlV9l1xAbr3H78T_",
    "2014": BASE_URL+"12syQsRH2QnKrQZTQQ6G5zyVeTG2pAYvu"
}

# Dictionary of countries that need translation to
COUNTRIES_TRANSLATE_DICT = {
    "United States": "USA",
    "China": "CN"
}
