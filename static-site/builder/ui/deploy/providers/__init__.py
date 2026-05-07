# deploy providers package
from deploy.providers.vercel     import VercelProvider
from deploy.providers.netlify    import NetlifyProvider
from deploy.providers.docker     import DockerProvider
from deploy.providers.cloudflare import CloudflareProvider

PROVIDERS = {
    "vercel":      VercelProvider,
    "netlify":     NetlifyProvider,
    "docker":      DockerProvider,
    "cloudflare":  CloudflareProvider,
}

def get_provider(name: str, **kwargs):
    cls = PROVIDERS.get(name)
    if not cls:
        raise ValueError(f"Unknown deploy provider: {name}. Available: {list(PROVIDERS)}")
    return cls(**kwargs)
