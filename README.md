# SMART on FHIR Python/Flask App

## Introduction

This project is a Python application developed to display Patient and Observation resources. It is functionally the same as the app showcased in this [tutorial](https://engineering.cerner.com/smart-on-fhir-tutorial/). However, it is built in Python using the Flask framework, and it's being hosted on [Render](https://render.com/). It uses OAuthLib to handle OAuth2.0/SMART on FHIR authentication with the EMR's FHIR server.

It is designed to be launched on [SMART Health IT's sandbox](https://launch.smarthealthit.org/) with a Provider EHR Launch. To be able to launch this app on Cerner or Epic sandboxes, you would need to register this application with either of them to obtain a client ID, a base URL, and a list of allowed scopes, and then set up those parameters accordingly in the `ehr_launch.py` file.

## Usage

To launch this application, [click here](https://launch.smarthealthit.org/?launch_url=https%3A%2F%2Fsmart-on-fhir-python-app.onrender.com%2F&launch=WzAsIiIsIiIsIkFVVE8iLDAsMCwwLCJwYXRpZW50L1BhdGllbnQucnMgcGF0aWVudC9PYnNlcnZhdGlvbi5ycyBsYXVuY2ggb2ZmbGluZV9hY2Nlc3Mgb3BlbmlkIGZoaXJVc2VyIiwiaHR0cHM6Ly9zbWFydC1vbi1maGlyLXB5dGhvbi1hcHAub25yZW5kZXIuY29tL2ZoaXItYXBwLyIsImNsaWVudC1pZCIsIiIsIiIsIiIsIiIsMCwwXQ&tab=0&validation=1)  

From here, you can directly click "Launch", and the SMART Health IT sandbox will prompt you to select a Patient and a Provider. After selecting a Patient and Provider, the application will display the Patient's name and a list of Observations associated with that Patient. This way of executing the launch is called a Standalone launch (app is launched without knowing the "Context", aka, which Provider is executing the app, and which Patient is being viewed).

Another option is to select the Patient and Provider before clicking "Launch" in the SMART Health IT sandbox. The options right on top of the Launch button allow you to select a Patient and Provider. This way of launching the appplication is called a EHR Launch (app is launched with "Context").

In any case, you can select any Patient and Provider combination. You don't need to select an Encounter.