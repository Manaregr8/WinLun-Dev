import geoip2.database

reader = geoip2.database.Reader("data/GeoLite2-City.mmdb")

def ip_to_geo(ip_address: str) -> dict:
    try:
        response = reader.city(ip_address)

        return{
            "ip": ip_address,
            "continent": response.continent.names.get("en", None),
            "country": response.country.names.get("en", None),
            "city": response.city.names.get("en", None),
            "latitude": response.location.latitude,
            "longitude": response.location.longitude,
        }
    
    except Exception as e:
        return {"ip":ip_address, "error": str(e)}