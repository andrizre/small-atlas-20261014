import argparse
import os
from pathlib import Path
import re
import secrets

from smallatlas.generator import MOODS, generate_world
from smallatlas.journal import Journal, render_markdown


def _journal_option(command: argparse.ArgumentParser) -> None:
    default = os.environ.get(
        "SMALLATLAS_JOURNAL", str(Path.home() / ".small-atlas" / "worlds.json")
    )
    command.add_argument("--journal", default=default, help="lokasi file jurnal JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="small-atlas",
        description="Rangkai tempat, aturan, penghuni, dan kejadian menjadi benih cerita.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="buat satu dunia tanpa menyimpannya")
    generate.add_argument("--seed", type=int, help="angka untuk mengulang hasil yang sama")
    generate.add_argument("--mood", choices=MOODS, default="puitis")

    save = commands.add_parser("save", help="buat dunia baru dan simpan ke jurnal")
    save.add_argument("--title", required=True, help="judul entri jurnal")
    save.add_argument("--seed", type=int, help="angka untuk mengulang hasil yang sama")
    save.add_argument("--mood", choices=MOODS, default="puitis")
    _journal_option(save)

    listing = commands.add_parser("list", help="daftar dunia di jurnal")
    _journal_option(listing)

    show = commands.add_parser("show", help="tampilkan satu dunia tersimpan")
    show.add_argument("id", help="ID entri dari perintah list atau save")
    _journal_option(show)

    export = commands.add_parser("export", help="ekspor satu dunia sebagai Markdown")
    export.add_argument("id", help="ID entri dari perintah list atau save")
    export.add_argument("--output", type=Path, help="file tujuan; default nama otomatis")
    _journal_option(export)
    return parser


def _print_world(world: object) -> None:
    print(f"Seed: {world.seed} | Nuansa: {world.mood}")
    print(f"\nTempat\n{world.place}")
    print(f"\nAturan dunia\n{world.law}")
    print(f"\nPenghuni\n{world.resident}")
    print(f"\nKejadian hari ini\n{world.event}")
    print(f"\nArah menulis\n{world.writing_prompt}")


def _entry_world(entry: dict[str, object]) -> None:
    print(f"{entry['title']}  [{entry['id']}]")
    print(f"Dibuat: {entry['created_at']}")
    print(f"Seed: {entry['seed']} | Nuansa: {entry['mood']}")
    print(f"\nTempat\n{entry['place']}")
    print(f"\nAturan dunia\n{entry['law']}")
    print(f"\nPenghuni\n{entry['resident']}")
    print(f"\nKejadian hari ini\n{entry['event']}")
    print(f"\nArah menulis\n{entry['writing_prompt']}")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command in {"generate", "save"}:
            seed = args.seed if args.seed is not None else secrets.randbits(32)
            world = generate_world(seed, args.mood)
            if args.command == "generate":
                _print_world(world)
            else:
                entry = Journal(args.journal).add(args.title, world.to_dict())
                print(f"Dunia disimpan: {entry['id']} — {entry['title']}")
                print(f"Seed: {seed} | Jurnal: {args.journal}")
            return

        journal = Journal(args.journal)
        if args.command == "list":
            entries = journal.entries()
            if not entries:
                print("Jurnal masih kosong. Buat entri dengan: small-atlas save --title JUDUL")
                return
            for entry in entries:
                print(
                    f"{entry['id']}  {entry['title']}  "
                    f"({entry['mood']}, {entry['created_at']})"
                )
            return

        entry = journal.get(args.id)
        if args.command == "show":
            _entry_world(entry)
            return

        if args.output is None:
            slug = re.sub(r"[^a-z0-9]+", "-", str(entry["title"]).lower()).strip("-")
            slug = slug or "dunia"
            output = Path(f"small-atlas-{slug}-{entry['id']}.md")
        else:
            output = args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_markdown(entry), encoding="utf-8")
        print(f"Ekspor dibuat: {output}")
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f"small-atlas: error: {error}\n")
