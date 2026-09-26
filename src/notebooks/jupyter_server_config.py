import os


token = os.environ.get("JUPYTER_TOKEN", "").strip()
if not token:
    raise RuntimeError("JUPYTER_TOKEN deve ser fornecido em runtime.")

c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = "/workspace"
c.ServerApp.log_level = "WARNING"
c.IdentityProvider.token = token
