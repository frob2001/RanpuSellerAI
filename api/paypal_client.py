import os
import logging

from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.logging.configuration.api_logging_configuration import (
    LoggingConfiguration,
    RequestLoggingConfiguration,
    ResponseLoggingConfiguration
)
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient

# Assuming you use environment variables or your config to store PayPal credentials:
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')

# Set up PayPal logging. (In production, mask_sensitive_headers=True is best.)
paypal_logging_config = LoggingConfiguration(
    log_level=logging.INFO,
    mask_sensitive_headers=True,  # For sandbox debugging (True in production!)
    request_logging_config=RequestLoggingConfiguration(log_headers=True, log_body=True),
    response_logging_config=ResponseLoggingConfiguration(log_headers=True, log_body=True)
)

# Create the PayPal client
paypal_client = PaypalServersdkClient(
    client_credentials_auth_credentials=ClientCredentialsAuthCredentials(
        o_auth_client_id=PAYPAL_CLIENT_ID,
        o_auth_client_secret=PAYPAL_CLIENT_SECRET
    ),
    logging_configuration=paypal_logging_config
)
