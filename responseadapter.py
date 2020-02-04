import re

MAPPING = [
    {"regexp": "<DSTransactionId>([^<]*)</DSTransactionId>", "field": "dsTransID", "default": "00000000-0000-0000-0000-000000000000"},
    {"regexp": "<Verification>([^<]*)</Verification>", "field": "authenticationValue"},
    {"regexp": "<Eci>([^<]*)</Eci>", "field": "eci"},
    {"regexp": "<ACSUrl>([^<]*)</ACSUrl>", "field": "acsURL"},
    {"regexp": "<AuthenticationStatus>([^<]*)</AuthenticationStatus>", "field": "transStatus", "default": "U"},
    # challenge only
    {"regexp": "<ACSChallengeMandatedIndicator>([^<]*)</ACSChallengeMandatedIndicator>", "field": "acsChallengeMandated", "default": "Y", "condition": "data[\"transStatus\"] == \"C\""},

    # not implemented
    {"regexp": "<Result name=\"acsTransID\">([^<]*)</Result>", "field": "acsTransID", "default": "00000000-0000-0000-0000-000000000000"},
    {"regexp": "<Result name=\"threeDSServerTransID\">([^<]*)</Result>", "field": "threeDSServerTransID", "default": "00000000-0000-0000-0000-000000000000"},
    {"regexp": "<Result name=\"threeDSServerRefNumber\">([^<]*)</Result>", "field": "threeDSServerRefNumber", "default": "NSOFTWARE"},
    {"regexp": "<Result name=\"dsReferenceNumber\">([^<]*)</Result>", "field": "dsReferenceNumber", "default": "DS"},
    {"regexp": "<Result name=\"acsReferenceNumber\">([^<]*)</Result>", "field": "acsReferenceNumber", "default": "ACS"},
    # challenge only
    {"regexp": "<Result name=\"authenticationType\">([^<]*)</Result>", "field": "authenticationType", "default": "01", "condition": "data[\"transStatus\"] == \"C\""},

]


class ResponseAdapter(object):
    __response = ""
    __data = {}

    def __init__(self, response, data):
        self.__response = response
        self.__data = data

    def adapt_response(self):
        print("Got response: " + self.__response)
        data = self.__data
        for mapping in MAPPING:
            match = re.search(mapping["regexp"], self.__response)
            if match is not None and len(match.groups()) > 0:
                data[mapping["field"]] = match.groups()[0]
            else:
                print("[WARNING] Unable to satisfy mapping " + str(mapping))
                if not mapping["field"] in data and "default" in mapping:
                    if not "condition" in mapping or eval(mapping["condition"], locals(), globals()):
                        data[mapping["field"]] = mapping["default"]
