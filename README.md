# SMART on FHIR Python/Flask App

## Introduction

This project is a Python application developed to display Patient and Observation resources. It is functionally the same as the app showcased in this tutorial: <https://engineering.cerner.com/smart-on-fhir-tutorial/>. However, it is built in Python using the Flask framework, and it is hosted locally. It uses OAuthLib to handle OAuth2.0/SMART on FHIR authentication with the EMR's FHIR server.

It is designed to be launched on SMART Health IT's sandbox (<https://launch.smarthealthit.org/>) with a Provider EHR Launch. To be able to launch this app on Cerner or Epic sandboxes, you would need to register this application with either of them to obtain a client ID, a base URL, and a list of allowed scopes, and then set up those parameters accordingly in the `ehr_launch.py` file.

### Prerequisites

You need to have Python and pip installed on your system. You can download Python from the official website and pip is included in the Python installation. Alternatively, you can use the Anaconda distribution of Python which includes pip and other useful tools.

### Installation

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Create a fresh environment (Python >=3.7 but < 3.10 strongly recommended), and run the following:  
`pip install -r requirements.txt`

If you run into any issues with the installation, try deleting Windows-specific packages from the `requirements.txt` file.

## Usage

Before launching this application in the SMART Health IT sandbox, do the following:  

1. Go to <https://launch.smarthealthit.org/>  

2. Set up the following parameters in the tab named "Client Registration and Validation":  

    - Client Identity Validation: Strict
    - Client ID: `client-id`
    - Allowed Scopes: `patient/Patient.rs patient/Observation.rs launch offline_access openid fhirUser`
    - Allowed Redirect URIs: `http://localhost:4201/fhir-app/`
    - App's Launch URL: `http://localhost:4201/`  
    You can also find these parameters in the `ehr_launch.py` file. The parameters set in the `ehr_launch.py` file and in the sandbox MUST match, otherwise the application will not work.  

3. Go to the "App Launch Options" tab in the SMART Health IT sandbox and select:

    - Launch Type: Provider EHR Launch  
    - FHIR Version: R4  
    - Simulated Error: None  
    - Misc. Options: Do not check the "Simulate launch within the EHR UI  
    - For Patient(s), Provider(s), and Encounter, select any Patient and Provider combination. You don't need to select an Encounter. (You can skip this step if you want to select a Patient and Provider in the application itself. However, that would not be a true EHR launch, but more of a Standalone launch.)  

4. This application currently runs on localhost. To run the application, navigate to the project directory in your machine's Command Prompt/PowerShell/Git Bash/etc., activate the corresponding virtual environment (see Installation above), and run the following command:  
`python ehr_launch.py`  

5. Finally, go back to the SMART Health IT sandbox and click "Launch".
