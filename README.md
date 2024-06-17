# SMART on FHIR Python/Flask App  

*If you want to run the app without any technical setup (cloning the repository, installing dependencies, etc.), access the app [here](https://launch.smarthealthit.org/?launch_url=https%3A%2F%2Fsmart-on-fhir-python-app.onrender.com%2F&launch=WzAsIiIsIiIsIkFVVE8iLDAsMCwwLCJwYXRpZW50L1BhdGllbnQucnMgcGF0aWVudC9PYnNlcnZhdGlvbi5ycyBsYXVuY2ggb2ZmbGluZV9hY2Nlc3Mgb3BlbmlkIGZoaXJVc2VyIiwiaHR0cHM6Ly9zbWFydC1vbi1maGlyLXB5dGhvbi1hcHAub25yZW5kZXIuY29tL2ZoaXItYXBwLyIsImNsaWVudC1pZCIsIiIsIiIsIiIsIiIsMCwwXQ&tab=0&validation=1). For usage instructions, see [here](https://github.com/morales-felix/SMART-on-FHIR-Python-app/blob/deployment/README.md#usage).*  

## Introduction

This project is a Python application developed to display Patient and Observation resources. It is similar to the app showcased in this [tutorial](https://engineering.cerner.com/smart-on-fhir-tutorial/), but built in Python using the Flask framework and hosted locally. It uses OAuthLib for OAuth2.0/SMART on FHIR authentication with the EMR's FHIR server.

The app is designed to be launched on [SMART Health IT's sandbox](https://launch.smarthealthit.org/) using a Provider EHR Launch. For launching on Cerner or Epic sandboxes, you need to register the application to obtain a client ID, base URL, and allowed scopes, then configure these in the `ehr_launch.py` file.  

### Prerequisites

Ensure you have Python and pip installed on your system. You can download Python from the official website; pip is included. Alternatively, use the Anaconda distribution, which includes pip and other tools.

### Installation

1. Clone the repository to your local machine:  

```bash
git clone https://github.com/morales-felix/SMART-on-FHIR-Python-app.git
```

2. Navigate to the project directory:  

```bash
cd SMART-on-FHIR-Python-app
```  

3. Create a fresh environment (Python >=3.7 but < 3.10 strongly recommended), and run the following:  

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```  

## Usage

Before launching this application in the SMART Health IT sandbox, follow these steps:  

1. Visit [SMART Health IT's sandbox](https://launch.smarthealthit.org/).  

2. Configure the parameters in the "Client Registration and Validation" tab:  

    - Client Identity Validation: Strict
    - Client ID: `client-id`
    - Allowed Scopes: `patient/Patient.rs patient/Observation.rs launch offline_access openid fhirUser`
    - Allowed Redirect URIs: `http://localhost:4201/fhir-app/`
    - App's Launch URL: `http://localhost:4201/`  
    Ensure the parameters in `ehr_launch.py` match these settings.  

3. In the "App Launch Options" tab, set:

    - Launch Type: Provider EHR Launch  
    - FHIR Version: R4  
    - Simulated Error: None  
    - Misc. Options: Leave "Simulate launch within the EHR UI" unchecked
    - Select any Patient and Provider combination to trigger what's known as "EHR Launch". No need to select an Encounter. (You can skip selecting a Patient and Provider at this stage, and do it after clicking "Launch", to trigger what's known as a "Standalone Launch").

4. To run the application locally, navigate to the project directory in your terminal, activate the virtual environment, and execute:  

```bash
python ehr_launch.py
```  

5. Go back to the SMART Health IT sandbox and click "Launch".  

This setup should enable you to run and test the app with the SMART Health IT sandbox, simulating interactions with FHIR resources in a secure and controlled environment.
