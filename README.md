# WIEHACK4.0 Portal
Portal for the [WIEHack 4.0](https://wiehack.bvpieee.in/) hackathon being organized by [BVPIEEE](https://www.bvpieee.in/).

## Gallery 🖼️
[![HvnOUlt.md.png](https://iili.io/HvnOUlt.md.png)](https://freeimage.host/i/HvnOUlt)
[![HvnOgUX.md.png](https://iili.io/HvnOgUX.md.png)](https://freeimage.host/i/HvnOgUX)
[![HvnOSfI.md.png](https://iili.io/HvnOSfI.md.png)](https://freeimage.host/i/HvnOSfI)
[![HvnOviN.md.png](https://iili.io/HvnOviN.md.png)](https://freeimage.host/i/HvnOviN)

## Features ✨
- User Authentication: There is authentication for 3 different types of users: Participants, Judges, Admin.
- Participant Dashboard: The portal will be used by participants to submit presentations, youtube links and github links after each round.
- Judges Dashboard: It will be used by judges to view all the submissions after each round
- Automation Scripts: Since the event is hosted on Unstop, hence we receive the registrations from Unstop. The portal provides automation scripts to automatically generate user registrations on our platform from the data received from Unstop. We also have automation scripts to update/restrict the team's access to the portal after each round based on weather they are selected for next round or not

## Technical Features ✨
- Backend is built using Django
- [AWS S3](https://aws.amazon.com/s3/) buckets and [AWS CDN](https://aws.amazon.com/cloudfront/) for storing and retrieving the static files (user presentations).
- [Google Sheets API](https://developers.google.com/sheets/api/guides/concepts) from Google Cloud, used in automation scripts for CRUD operations on Google Sheets.
- Backend is hosted on [Digital Ocean's App Platform](https://www.digitalocean.com/products/app-platform).
- PostgreSQL is used as the production database.

## Installation 🖥️
1. Download [Python](https://www.python.org/), if not installed already
2. `cd backend` to go in the backend directory
3. Run `pip install -r requirements.txt` to install all the dependencies
4. Rename `example.env` to `.env` & add the respective enviroment variables
5. Run `python manage.py migrate` to migrate the database
6. Run `python manage.py runserver` to start the server

## License ⚖️ 
wiehack-portal is released under the [MIT license](https://github.com/anubhav06/wiehack-portal/blob/main/LICENSE)
