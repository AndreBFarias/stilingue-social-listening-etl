import os
from pathlib import Path

block_cipher = None
base_dir = os.path.abspath(".")

a = Analysis(
    [os.path.join(base_dir, "src", "__main__.py")],
    pathex=[base_dir],
    binaries=[],
    datas=[
        (os.path.join(base_dir, ".env.example"), "."),
    ],
    hiddenimports=[
        "loguru",
        "tenacity",
        "dotenv",
        "requests",
        "pandas",
        "numpy",
        "src",
        "src.config",
        "src.schemas",
        "src.pipeline",
        "src.api",
        "src.api.client",
        "src.api.endpoints",
        "src.extractors",
        "src.extractors.visao_geral",
        "src.extractors.sentimento_grupos",
        "src.extractors.sentimento_temas",
        "src.extractors.linechart",
        "src.extractors.publicacoes",
        "src.extractors.ranking_evolutivo",
        "src.loaders",
        "src.loaders.csv_writer",
        "src.transformers",
        "src.transformers.transformers",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "scipy",
        "pytest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="stilingue_etl",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)
