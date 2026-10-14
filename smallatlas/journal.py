from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import uuid


class Journal:
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()

    def entries(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Jurnal bukan JSON yang valid: {self.path}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
            raise ValueError(f"Struktur jurnal tidak valid: {self.path}")
        if any(not isinstance(entry, dict) for entry in data["entries"]):
            raise ValueError(f"Ada entri jurnal yang tidak valid: {self.path}")
        return data["entries"]

    def add(self, title: str, world: dict[str, int | str]) -> dict[str, object]:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Judul tidak boleh kosong.")
        entries = self.entries()
        entry: dict[str, object] = {
            "id": uuid.uuid4().hex[:8],
            "title": clean_title,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            **world,
        }
        entries.append(entry)
        self._write(entries)
        return entry

    def get(self, identifier: str) -> dict[str, object]:
        for entry in self.entries():
            if entry.get("id") == identifier:
                return entry
        raise KeyError(f"Entri dengan ID '{identifier}' tidak ditemukan.")

    def _write(self, entries: list[dict[str, object]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                json.dump({"entries": entries}, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()


def render_markdown(entry: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# {entry['title']}",
            "",
            f"- ID: `{entry['id']}`",
            f"- Dibuat: {entry['created_at']}",
            f"- Seed: `{entry['seed']}`",
            f"- Nuansa: {entry['mood']}",
            "",
            f"## Tempat\n\n{entry['place']}",
            f"## Aturan dunia\n\n{entry['law']}",
            f"## Penghuni\n\n{entry['resident']}",
            f"## Kejadian hari ini\n\n{entry['event']}",
            f"## Arah menulis\n\n{entry['writing_prompt']}",
            "",
        ]
    )
