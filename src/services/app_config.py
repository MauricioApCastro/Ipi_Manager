import json
from pathlib import Path


def config_path(db):
    db_path = Path(getattr(db, "db_path", "data/escola.db")).resolve()
    return db_path.parent / "app_config.json"


def carregar_config(db):
    caminho = config_path(db)
    if not caminho.exists():
        return {}
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def salvar_config(db, config):
    caminho = config_path(db)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def obter_config(db, chave, padrao=""):
    return carregar_config(db).get(chave, padrao)


def definir_config(db, chave, valor):
    config = carregar_config(db)
    config[chave] = valor
    salvar_config(db, config)
