select
    role_norm,
    role_display,
    role_family
from {{ ref('seed_role_family') }}
