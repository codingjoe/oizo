"""
Sipgate SIP trunk integration.

This module abstracts the Sipgate SIP carrier connection.
All credentials are supplied via environment variables:

    SIPGATE_SIP_HOST       – SIP proxy hostname (e.g. sipgate.de)
    SIPGATE_SIP_PORT       – SIP proxy port (default 5060)
    SIPGATE_SIP_USER       – SIP username / extension
    SIPGATE_SIP_PASSWORD   – SIP password
    SIPGATE_TOKEN_ID       – Sipgate personal-access-token ID  (REST API)
    SIPGATE_TOKEN          – Sipgate personal-access-token      (REST API)
    SIPGATE_BASE_URL       – Sipgate REST API base (default https://api.sipgate.com/v2)
"""
