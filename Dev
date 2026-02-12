config/opensearch-security/config.yml:
---
_meta:
  type: "config"
  config_version: 2

config:
  dynamic:
    # HTTP basic authentication
    http:
      anonymous_auth_enabled: false
      xff:
        enabled: false
        internalProxies: '192\.168\.0\.10|192\.168\.0\.11'
    
    authc:
      # Basic authentication domain
      basic_internal_auth_domain:
        description: "Authenticate via HTTP Basic against internal users database"
        http_enabled: true
        transport_enabled: true
        order: 0
        http_authenticator:
          type: basic
          challenge: true
        authentication_backend:
          type: internal
      
      # OpenID Connect with GitLab
      openid_auth_domain:
        description: "Authenticate via OpenID Connect with GitLab"
        http_enabled: true
        transport_enabled: false
        order: 1
        http_authenticator:
          type: openid
          challenge: false
          config:
            subject_key: preferred_username
            roles_key: groups
            openid_connect_url: https://gitlab.example.com/.well-known/openid-configuration
            # Or specify endpoints manually:
            # openid_connect_idp:
            #   enable_ssl: true
            #   verify_hostnames: true
            #   pemtrustedcas_filepath: /path/to/gitlab-ca.pem
        authentication_backend:
          type: noop

    authz:
      # Roles mapping from GitLab groups
      roles_from_myldap:
        description: "Authorize via LDAP or another method"
        http_enabled: false
        authorization_backend:
          type: noop

# Role-based access control mappings
---
_meta:
  type: "rolesmapping"
  config_version: 2

# Map internal users to roles
all_access:
  reserved: false
  backend_roles:
  - "admin"
  description: "Maps admin to all_access"

# Map GitLab groups to OpenSearch roles
kibana_user:
  reserved: false
  backend_roles:
  - "gitlab-developers"
  - "gitlab-viewers"
  description: "Maps GitLab groups to kibana_user role"

readall:
  reserved: false
  backend_roles:
  - "gitlab-readonly"
  description: "Maps GitLab readonly group to readall role"

# Server settings
server.port: 5601
server.host: "0.0.0.0"
server.name: "opensearch-dashboards"

# OpenSearch connection
opensearch.hosts: ["https://localhost:9200"]
opensearch.ssl.verificationMode: certificate
opensearch.username: "kibanaserver"
opensearch.password: "kibanaserver"
opensearch.requestHeadersAllowlist: ["securitytenant", "Authorization"]

# SSL/TLS settings
opensearch.ssl.certificateAuthorities: ["/path/to/root-ca.pem"]
server.ssl.enabled: true
server.ssl.certificate: /path/to/dashboards.pem
server.ssl.key: /path/to/dashboards-key.pem

# Security plugin settings
opensearch_security.multitenancy.enabled: true
opensearch_security.multitenancy.tenants.preferred: ["Private", "Global"]
opensearch_security.readonly_mode.roles: ["kibana_read_only"]

# Cookie security
opensearch_security.cookie.secure: true
opensearch_security.cookie.ttl: 3600000
opensearch_security.session.ttl: 3600000
opensearch_security.session.keepalive: true

# OpenID Connect configuration for GitLab
opensearch_security.auth.type: ["openid", "basicauth"]
opensearch_security.auth.multiple_auth_enabled: true

# OpenID Connect settings
opensearch_security.openid.connect_url: "https://gitlab.example.com/.well-known/openid-configuration"
opensearch_security.openid.client_id: "your-gitlab-application-id"
opensearch_security.openid.client_secret: "your-gitlab-application-secret"
opensearch_security.openid.base_redirect_url: "https://dashboards.example.com"
opensearch_security.openid.scope: "openid profile email groups"
opensearch_security.openid.header: "Authorization"

# Optional: GitLab-specific settings
opensearch_security.openid.logout_url: "https://gitlab.example.com/users/sign_out"
opensearch_security.openid.verify_hostnames: true
opensearch_security.openid.refresh_tokens: true

# Basic auth settings (fallback)
opensearch_security.basicauth.enabled: true
opensearch_security.basicauth.login.title: "Please login to OpenSearch Dashboards"
opensearch_security.basicauth.login.subtitle: "Use your internal credentials or login with GitLab"

