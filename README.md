Here are two very simple scraper scripts for retrieving info on mobile apps from their respective stores that I made for managing the http://scoolapps.cz/ content library. They output either human-readable information or JSON for piping into other processes.

Usage
-----

```
./Scraper.py -i [appid] [options]
-h, --help                 Prints help
-j, --json                 Outputs JSON instead of human readable info
-i, --id ID                Required. ID of the app to get info on
-e, --encoding ENCODING    Sets the encoding to use
-l, --locale LOCALE        Sets the language to use
```

Requirements
------------
Python 2.7 and BeautifulSoup. That's it!

### Windows Store Scraper

Accepts the GUID found in Windows Store links as the [appid]
e.g. `http://apps.microsoft.com/windows/en-us/app/b188f2d6-ba88-47a3-b5f1-5823dd67146e`

Accepts Microsoft locales for setting the store language.
List can be found here: [MSDN](http://msdn.microsoft.com/en-us/library/ee825488.aspx)

### Google Play Scraper

Accepts the Android package names as the [appid]
eg. `http://play.google.com/store/apps/details?id=**cz.nature.biolog**&hl=en`

### App Store Scraper?

There's no need for one! Apple already has a public search API! See more here: [iTunes Search API](https://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html)