# -*- coding:utf-8 -*-
##############################################################
# Created Date: Monday, November 28th 2022
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################

from geopy.geocoders import Nominatim
import pandas as pd
import geocoder
import googlemaps


def googlemaps_geocoding_from_address(address, api_key) -> tuple:

    # initialize googlemaps client
    gmaps = googlemaps.Client(key=api_key)

    # Geocoding an address
    location_instance = gmaps.geocode(address)

    # get the location
    location_lng_lat = (location_instance[0]['geometry']['location']['lat'], location_instance[0]['geometry']['location']['lng'])

    return location_lng_lat


def geopy_geocoding_from_address(address: str) -> tuple:

    # initialize geopy client
    geo_locator = Nominatim(user_agent="myGeopyGeocoder")

    # Geocoding an address
    try:
        location = geo_locator.geocode(address, timeout=10)
        location_lng_lat = (location.longitude, location.latitude)
    except Exception as e:

        location_lng_lat = (0,0)
        print(
            f"Error: {address} is not able to geocode, for {e}, try to use (0 ,0) to as lng and lat \n")

    return location_lng_lat


def geocoder_geocoding_from_address(address: str) -> tuple:

    # initialize geocoder arcgis client
    location_instance = geocoder.arcgis(address).geojson

    # get the location
    location_lng_lat = (location_instance["features"][0]["geometry"]["coordinates"])

    return location_lng_lat


if __name__ == "__main__":

    # Step 1: input data path
    # path_input = "./geo_referencing_lnglat_.xlsx"
    path_input = "intersection_from_synchro.csv"
    # Step 2: read data
    df = pd.read_csv(path_input)

    # Step 3: get address values
    address_list = df["full_name"].tolist()

    # Step 4: geocoding
    lnglat_values = [geocoder_geocoding_from_address(address) for address in address_list]

    # Step 5: save the result
    for i in range(len(df)):
        df.loc[i, "x_coord"] = lnglat_values[i][0]
        df.loc[i, "y_coord"] = lnglat_values[i][1]

    df.to_csv("geo_referencing_lnglat_geocoded.csv", index=False)
