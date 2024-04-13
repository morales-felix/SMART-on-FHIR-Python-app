import os
import json
import uuid
import logging
import requests
from flask import Flask, request, render_template, redirect
from oauthlib.oauth2 import WebApplicationClient


####################################################################################################
# Defining application credentials for OAuth 2.0
CLIENT_ID = "client-id"
BASE_URL = "https://launch.smarthealthit.org/v/r4/fhir"
# https://hl7.org/fhir/smart-app-launch/scopes-and-launch-context.html
# For EHR launch, the scope should be "launch", not "launch/patient"
SCOPES = "patient/Patient.rs patient/Observation.rs launch offline_access openid fhirUser"
REDIRECT_URI = "http://localhost:4201/fhir-app/"


####################################################################################################
app = Flask(__name__)
client = WebApplicationClient(CLIENT_ID)
cookie = {}


### 1. Launch the app
# This will happen on the EHR, which needs to send a launch token and a iss.
# The iss should simply equal the FHIR base url, so that's something I can check here
# The launch token will be part of the authorization request
@app.route("/", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def index():
    """
    This is the method the EHR client will trigger upon launch.
    It will redirect to the authorization page.
    """

    # Retrieve the launch parameters from the query string
    launch_token = request.args.get("launch", "")
    iss = request.args.get("iss", "")

    assert (iss == BASE_URL), f"""ISS link is {iss}, but the app's registered link is {BASE_URL}
    (these should match, otherwise there might be a security vulnerability). Please validate."""

    cookie["launch_token"] = launch_token

    return redirect("/authorize")


### 2. Retrieve metadata or SMART configuration
# https://hl7.org/fhir/smart-app-launch/app-launch.html#retrieve-well-knownsmart-configuration
# https://fhir.epic.com/Documentation?docId=oauth2&section=Embedded-Oauth2-Launch_Conformance-Statement
smart_config_url = f"{BASE_URL}/.well-known/smart-configuration"
response = requests.get(smart_config_url, headers={"Accept": "application/fhir+json"}).json()
authorization_uri = response["authorization_endpoint"]
token_uri = response["token_endpoint"]


#### BEGIN ATHORIZATION FLOW ####


## 3. Obtain authorization code
# https://hl7.org/fhir/smart-app-launch/app-launch.html#obtain-authorization-code
# https://fhir.epic.com/Documentation?docId=oauth2&section=Standalone-Oauth2-Launch_Request_Auth_Code
@app.route("/authorize")
def authorization():
    """
    This method prepares an authorization request
    to the authorization server with the necessary parameters.
    """

    # Generate a state
    cookie["state"] = uuid.uuid4().hex

    # Prepare request for authorization server
    auth_url = client.prepare_request_uri(
        uri=authorization_uri,
        redirect_uri=REDIRECT_URI,
        launch=cookie["launch_token"],  # Necessary for EHR launch
        scope=SCOPES,
        state=cookie["state"],
        aud=BASE_URL,   # This is a key difference between OAuth 2.0 and SMART on FHIR
    )

    # Hit the auth server with built-in parameters
    return redirect(auth_url)


### 4. Obtain access token
# https://hl7.org/fhir/smart-app-launch/app-launch.html#obtain-access-token
# https://fhir.epic.com/Documentation?docId=oauth2&section=Standalone-Oauth2-Launch_Access-Token-Request
# Note: This implementation does not use a client secret, so this is a "public client"
@app.route("/fhir-app/", methods=["GET", "POST"])
def callback():
    """
    This method will handle the callback from the authorization server.
    It will then request an access token from the token server.
    """

    try:
        # Prepare request for token server.
        # This method already does a strict state checking behind the scenes
        # (aka, checks that the state returned by the auth server is the same that the client gave)
        token_url, headers, body = client.prepare_token_request(
            token_url=token_uri,
            authorization_response=request.url,
            redirect_url=REDIRECT_URI,
            state=cookie["state"],
            include_client_id=True, # This is another SMART-specific aspect, in case of a public client
        )

        # Send post request to token endpoint
        token_response = requests.post(token_url, headers=headers, data=body)
        cookie["token"] = token_response.json()

        # Add token to the client object so that it can be used later
        client.parse_request_body_response(json.dumps(token_response.json()))

    except Exception:
        error_message = (
            "An error occured when the application tried to obtain an access token."
        )
        return render_template("error.html", error=error_message)

    return redirect("/render_data")


#### AUTHORIZATION FLOW COMPLETE ####


### 5. Access FHIR API for data
@app.route("/render_data", methods=["GET", "POST"])
def render_data():
    """
    This method will render the data obtained from FHIR.
    """

    records = {}
    
    first_name, last_name, dob = _get_patient_data(cookie["token"])
    height = _get_height(cookie["token"])
    systolic_bp, diastolic_bp = _get_bp(cookie["token"])
    hdl = _get_hdl(cookie["token"])
    ldl = _get_ldl(cookie["token"])
    
    records["Name"] = first_name + " " + last_name
    records["Date of Birth"] = dob
    records["Height"] = height
    records["Systolic BP"] = systolic_bp
    records["Diastolic BP"] = diastolic_bp
    records["HDL"] = hdl
    records["LDL"] = ldl
    
    return render_template("render_data.html", data=records)



def _get_patient_data(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{BASE_URL}/Patient/{tokens['patient']}",
        headers={"Accept": "application/fhir+json"}
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        patient = requests.get(uri, headers=headers, data=body, timeout=10).json()

        # Sometimes a resource is returned, but it doesn't have anything useful
        if patient["resourceType"] == "OperationOutcome":
            # print(f"\n{patient}\n")
            raise ValueError(
                f"""
                The patient you selected (FHIR ID: {tokens['patient']})
                does not have patient data available
                """
            )

        # Get the patient name
        try:
            name = patient["name"][0]["text"].title()
            given_name = name.split(" ")[0].lower().title()
            family_name = name.split(" ")[1].lower().title()
        except KeyError:
            try:
                given_name = patient["name"][0]["given"][0].lower().title()
                family_name = patient["name"][0]["family"].lower().title()
            except KeyError:
                print(
                    f"""
                    Patient FHIR ID {tokens['patient']} has either a
                    missing given name or a missing family name
                    """
                )

        # Get Date of Birth
        try:
            birth_date = patient["birthDate"]
        except KeyError:
            birth_date = "No birth date specified in FHIR data"

    except Exception as error:
        raise ValueError(f"Found the following error pulling Patient FHIR resource: {error}") from error

    return given_name, family_name, birth_date


def _get_height(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=8302-2",
        headers={"Accept": "application/fhir+json"}
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        observation = requests.get(uri, headers=headers, data=body, timeout=10)
        
        try:
            observation = observation.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
                ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if observation["resourceType"] == "OperationOutcome":
            height = "No height data available due to OperationOutcome error"
        else:
            if observation["resourceType"] == "Bundle" and observation["total"] > 0:
                entry = observation["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    height = str(round(value, 1)) + " " + unit
                except KeyError:
                    height = "No valid height data available. Either there isn't a value or a unit."
            
            else:
                height = "No height data available due to empty bundle"

    except Exception as error:
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {error}") from error

    return height


def _get_bp(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{BASE_URL}/Observation?patient={tokens['patient']}&category=vital-signs&code=55284-4",
        headers={"Accept": "application/fhir+json"}
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        blood_pressure = requests.get(uri, headers=headers, data=body, timeout=10)
        
        try:
            blood_pressure = blood_pressure.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
                ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if blood_pressure["resourceType"] == "OperationOutcome":
            sys_bp = "No systolic blood pressure available due to OperationOutcome error"
            dias_bp = "No diastolic blood pressure available due to OperationOutcome error"
        else:
            if blood_pressure["resourceType"] == "Bundle" and blood_pressure["total"] > 0:
                entry = blood_pressure["entry"][0]
                try:
                    sys_value = entry["resource"]["component"][0]["valueQuantity"]["value"]
                    sys_unit = entry["resource"]["component"][0]["valueQuantity"]["unit"]
                    sys_bp = str(round(sys_value, 1)) + " " + sys_unit
                except KeyError:
                    sys_bp = "No valid systolic blood pressure available. Either there wasn't a value or a unit."
                    
                try:
                    dias_value = entry["resource"]["component"][1]["valueQuantity"]["value"]
                    dias_unit = entry["resource"]["component"][1]["valueQuantity"]["unit"]
                    dias_bp = str(round(dias_value, 1)) + " " + dias_unit
                except KeyError:
                    dias_bp = "No valid diastolic blood pressure available. Either there wasn't a value or a unit."
            
            else:
                sys_bp = "No systolic blood pressure available due to empty bundle"
                dias_bp = "No diastolic blood pressure available due to empty bundle"

    except Exception as error:
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {error}") from error

    return sys_bp, dias_bp


def _get_hdl(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=2085-9",
        headers={"Accept": "application/fhir+json"}
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        hdl = requests.get(uri, headers=headers, data=body, timeout=10)
        
        try:
            hdl = hdl.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
                ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if hdl["resourceType"] == "OperationOutcome":
            good_chol = "No HDL available due to OperationOutcome error"
        else:
            if hdl["resourceType"] == "Bundle" and hdl["total"] > 0:
                entry = hdl["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    good_chol = str(round(value, 1)) + " " + unit
                except KeyError:
                    good_chol = "No HDL available. Either there wasn't a value or a unit."
            
            else:
                good_chol = "No HDL available due to empty bundle"

    except Exception as error:
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {error}") from error

    return good_chol


def _get_ldl(tokens):

    # Getting data in the way prescribed by OAuthLib package
    uri, headers, body = client.add_token(
        f"{BASE_URL}/Observation?patient={tokens['patient']}&category=laboratory&code=18262-6",
        headers={"Accept": "application/fhir+json"}
    )

    try:
        # Getting data in the way prescribed by OAuthLib package
        ldl = requests.get(uri, headers=headers, data=body, timeout=10)
        
        try:
            ldl = ldl.json()
        except json.JSONDecodeError as error:
            raise ValueError(
                """
                Observation data not returned in JSON format.  
                You probably haven't set the correct scope permissions,  
                or registered the app with the EHR vendor  
                so that it has access to this resource in Read or Search mode.
                """
                ) from error

        # Sometimes a resource is returned, but it doesn't have anything useful
        if ldl["resourceType"] == "OperationOutcome":
            bad_chol = "No LDL available due to OperationOutcome error"
        else:
            print(ldl)
            if ldl["resourceType"] == "Bundle" and ldl["total"] > 0:
                entry = ldl["entry"][0]
                try:
                    value = entry["resource"]["valueQuantity"]["value"]
                    unit = entry["resource"]["valueQuantity"]["unit"]
                    bad_chol = str(round(value, 1)) + " " + unit
                except KeyError:
                    bad_chol = "No LDL available. Either there wasn't a value or a unit."
            
            else:
                bad_chol = "No LDL available due to empty bundle"

    except Exception as error:
        raise ValueError(f"Found the following error pulling Observation FHIR resource: {error}") from error

    return bad_chol


if __name__ == "__main__":
    # This creates a secret key (needed for session to work)
    app.secret_key = os.urandom(24)

    # This is to allow for endpoints to be http instead of https
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    logging.basicConfig(level=logging.DEBUG)
    # app.run(ssl_context='adhoc', debug=True, host='0.0.0.0', port=4201)
    app.run(debug=True, host="0.0.0.0", port=4201)
