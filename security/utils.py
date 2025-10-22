import re
import unicodedata

# Define provider rules in a central, extensible dictionary.
KNOWN_PROVIDER_RULES = {
    # Google: Ignores dots, supports '+', has aliases.
    "gmail.com": {"ignore_dots": True, "handle_plus_alias": True, "canonical_domain": "gmail.com"},
    "googlemail.com": {"ignore_dots": True, "handle_plus_alias": True, "canonical_domain": "gmail.com"},
    
    # Microsoft: Dots matter, supports '+'.
    "outlook.com": {"ignore_dots": False, "handle_plus_alias": True},
    "hotmail.com": {"ignore_dots": False, "handle_plus_alias": True},
    "live.com": {"ignore_dots": False, "handle_plus_alias": True},
    
    # Apple: Dots matter, supports '+'.
    "icloud.com": {"ignore_dots": False, "handle_plus_alias": True},
    "me.com": {"ignore_dots": False, "handle_plus_alias": True},
    "mac.com": {"ignore_dots": False, "handle_plus_alias": True},
    
    # Yahoo: Dots matter, '+' is NOT supported (it's a valid character).
    "yahoo.com": {"ignore_dots": False, "handle_plus_alias": False},
    "ymail.com": {"ignore_dots": False, "handle_plus_alias": False},
    
    # Others that support '+' but dots matter.
    "protonmail.com": {"ignore_dots": False, "handle_plus_alias": True},
    "proton.me": {"ignore_dots": False, "handle_plus_alias": True},
    "fastmail.com": {"ignore_dots": False, "handle_plus_alias": True},
    "zoho.com": {"ignore_dots": False, "handle_plus_alias": True},
}


def normalize_email(email: str) -> str:
    """
    Normalizes an email address to a canonical, provider-aware form.

    Features:
    - Lowercases and strips whitespace.
    - Unicode-normalizes to avoid homoglyphs (NFKC).
    - Removes plus-aliasing (sub-addressing) for known providers.
    - Defaults to removing plus-aliasing for unknown providers (aggressive strategy).
    - Removes dot-insensitivity only for Google domains.
    - Trims trailing dots in domain names.
    - Returns original cleaned string if invalid.
    """

    if not isinstance(email, str):
        return email

    # Step 1: Basic cleanup and Unicode normalization
    email_norm = unicodedata.normalize("NFKC", email.strip().lower())

    # Step 2: Quick sanity check
    if "@" not in email_norm or email_norm.count("@") != 1:
        return email_norm  # malformed, return cleaned-up as-is

    local, domain = email_norm.split("@", 1)
    domain = domain.rstrip(".")  # e.g., "gmail.com." → "gmail.com"

    # Step 3: Get rules for this provider
    rules = KNOWN_PROVIDER_RULES.get(domain, {})

    # Step 4: Handle plus-aliasing (sub-addressing)
    # Default to True (aggressive) unless explicitly set to False (e.g., Yahoo)
    if rules.get("handle_plus_alias", True) and "+" in local:
        local = local.split("+", 1)[0]

    # Step 5: Apply provider-specific normalization
    # We only apply these rules if the provider is known
    if rules:
        if rules.get("ignore_dots"):
            local = local.replace(".", "")
        if "canonical_domain" in rules:
            domain = rules["canonical_domain"]
    
    # Note: No 'else' block is needed. For unknown domains,
    # we've already applied plus-aliasing (aggressive) and
    # will now just re-assemble.

    # Step 6: Re-assemble
    normalized = f"{local}@{domain}"

    # Step 7: Basic regex sanity validation
    # Allows subdomains and requires a TLD of 2+ chars.
    if not re.match(r"^[^\s@]+@[^\s@.]+\.[a-zA-Z]{2,}$", normalized):
        return email_norm  # Return cleaned-up, non-normalized email

    return normalized

