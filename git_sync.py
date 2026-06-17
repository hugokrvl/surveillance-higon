"""
Synchronisation git du site local <-> GitHub.
- pull() : récupère les derniers signals.json produits par GitHub Actions.
- push() : envoie portfolio.json (positions) sur GitHub pour le scan cloud.

Règle anti-conflit : le site local ne pousse QUE portfolio.json,
GitHub Actions ne pousse QUE signals.json. Fichiers disjoints.
"""
import subprocess
from pathlib import Path

REPO = Path(__file__).parent


def _git(*args, timeout=30) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=REPO, capture_output=True, text=True, timeout=timeout,
        )
        out = (r.stdout + r.stderr).strip()
        return r.returncode == 0, out
    except Exception as e:
        return False, str(e)


def has_remote() -> bool:
    ok, out = _git("remote")
    return ok and bool(out.strip())


def pull() -> tuple[bool, str]:
    """Récupère les signaux frais. Rebase pour rester linéaire."""
    if not has_remote():
        return False, "Aucun remote GitHub configuré."
    ok, out = _git("pull", "--rebase", "--autostash")
    return ok, out


def push(message: str = "Maj portefeuille (site local)") -> tuple[bool, str]:
    """Commit + push de portfolio.json uniquement."""
    if not has_remote():
        return False, "Aucun remote GitHub configuré."
    _git("add", "portfolio.json")
    ok, out = _git("commit", "-m", message)
    if not ok and "nothing to commit" in out:
        return True, "Rien à synchroniser (déjà à jour)."
    # pull --rebase avant push pour éviter un rejet non-fast-forward
    _git("pull", "--rebase", "--autostash")
    ok, out = _git("push")
    return ok, out
