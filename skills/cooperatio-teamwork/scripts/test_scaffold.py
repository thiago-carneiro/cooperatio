"""Tests for scaffold.py (run: python -m pytest test_scaffold.py)."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

import scaffold


def load_validator_module():
    spec = importlib.util.spec_from_file_location(
        "cooperatio_validator_for_scaffold_tests", scaffold.VALIDATOR_SRC)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_creates_the_recipe_layout(tmp_path: Path) -> None:
    out = tmp_path / "teamwork"
    created = scaffold.scaffold("Demo", ["writer", "reviewer"], out)
    names = {path.relative_to(out).as_posix() for path in created}
    assert {
        "00-brief.md",
        "01-sources-of-truth.md",
        "02-canon.json",
        "05-contracts/02-canon.schema.json",
        "03-artifacts.json",
        "06-gates.md",
        "07-rubric.md",
        "07-rubric.sha256",
        "layout.json",
        "lessons.md",
        "open-notes.json",
        "priors.json",
        "state/notes.jsonl",
        "state/round-record.jsonl",
        "04-roles/writer.md",
        "04-roles/reviewer.md",
    } <= names
    # the copied validator is asserted by its own test: it exists only when
    # the corpus is reachable relative to the skill


def test_creates_the_empty_recipe_directories(tmp_path: Path) -> None:
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    for name in scaffold.EMPTY_DIRS:
        assert (out / name).is_dir()


def test_json_files_parse(tmp_path: Path) -> None:
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    canon = json.loads((out / "02-canon.json").read_text(encoding="utf-8"))
    assert canon["target"] == "Demo"
    artifacts = json.loads((out / "03-artifacts.json").read_text(encoding="utf-8"))
    assert isinstance(artifacts, list)
    priors = json.loads((out / "priors.json").read_text(encoding="utf-8"))
    assert priors == {"instances": []}


def test_target_canon_has_no_method_sections(tmp_path: Path) -> None:
    """The canon of a target has no method-vocabulary sections of the corpus."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    text = (out / "02-canon.json").read_text(encoding="utf-8")
    for banned in ("Method terms", "Terms to avoid", "Fixed lists"):
        assert banned not in text
    for section in scaffold.CANON_SECTIONS:
        assert section in text


def test_canon_carries_the_sections_the_validator_consumes(tmp_path: Path) -> None:
    """The JSON canon opens with the validator's consumed keys, empty."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    canon = json.loads((out / "02-canon.json").read_text(encoding="utf-8"))
    for key in scaffold.CANON_CONSUMED_KEYS:
        assert canon[key] == []


def test_canon_declares_the_schema_version_the_validator_reads(tmp_path: Path) -> None:
    """I5 of the panel: the canon declares its schema version; the validator
    refuses a different one, so the cell's own canon must carry what the
    copied validator consumes."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    canon = json.loads((out / "02-canon.json").read_text(encoding="utf-8"))
    assert canon["version"] == "v1"
    validator = load_validator_module()
    assert validator.CANON_SCHEMA_VERSION == "v1"


def test_canon_schema_requires_the_consumed_keys(tmp_path: Path) -> None:
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    schema = json.loads((out / "05-contracts" / "02-canon.schema.json")
                         .read_text(encoding="utf-8"))
    assert schema["required"] == ["version", *scaffold.CANON_CONSUMED_KEYS]
    assert schema["properties"]["terms to avoid"]["items"] == {"type": "string"}
    # the target's own sections stay free: the schema does not close the object
    assert "additionalProperties" not in schema


def test_layout_json_maps_every_gate_to_the_json_parser(tmp_path: Path) -> None:
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    layout = json.loads((out / "layout.json").read_text(encoding="utf-8"))
    assert layout["version"] == 1
    assert layout["artifacts"]["canon"] == "02-canon.json"
    assert layout["artifacts"]["artifacts"] == "03-artifacts.json"
    assert layout["artifacts"]["gates-and-rubric"] == "06-gates.md"
    assert layout["artifacts"]["roles-dir"] == "04-roles"
    assert layout["artifacts"]["rubric"] == "07-rubric.md"
    assert layout["artifacts"]["sensitivity"] == "08-validator/sensitivity.md"
    assert layout["registry"] == "priors.json"
    assert set(layout["gates"]) == set(scaffold.BUILTIN_GATES)
    assert set(layout["gates"].values()) == {"builtin-json-canon"}


def test_layout_json_carries_only_keys_the_validator_reads(tmp_path: Path) -> None:
    """I12 of the panel: the validator refuses a layout key it does not read
    (exit 2), so the scaffold must emit known keys only — and its embedded
    gate list must be the validator's, or the merged gate map would name two
    parsers."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    layout = json.loads((out / "layout.json").read_text(encoding="utf-8"))
    validator = load_validator_module()
    assert set(layout) <= set(validator.LAYOUT_TOP_KEYS)
    assert set(layout["artifacts"]) <= set(validator.LAYOUT_ARTIFACT_KEYS)
    assert set(scaffold.BUILTIN_GATES) == set(validator.BUILTIN_GATES)
    assert validator.merge_layout(validator.DEFAULT_LAYOUT, layout)["artifacts"]["canon"] == \
        "02-canon.json"


def test_layout_json_points_the_sensitivity_gate_at_the_cell_report(tmp_path: Path) -> None:
    """v0.2.3 (medium finding of instance 004): the cell's layout names its
    own sensitivity report, so p-sensitivity is measured instead of pending."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    layout = json.loads((out / "layout.json").read_text(encoding="utf-8"))
    assert layout["artifacts"]["sensitivity"] == "08-validator/sensitivity.md"


def test_layout_json_points_the_frozen_rubric_gate_at_the_cell_rubric(tmp_path: Path) -> None:
    """v0.3.0 (probe C of the panel): the cell's layout names its own rubric
    file, so --freeze-rubric and p-frozen-rubric resolve it in the cell
    instead of falling back to the corpus convention."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    layout = json.loads((out / "layout.json").read_text(encoding="utf-8"))
    assert layout["artifacts"]["rubric"] == "07-rubric.md"


def test_gates_template_carries_the_size_ranges_table(tmp_path: Path) -> None:
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    text = (out / "06-gates.md").read_text(encoding="utf-8")
    assert "### Size ranges" in text
    assert "| Document | Minimum | Maximum |" in text


def test_canon_schema_uses_only_supported_keywords_and_accepts_its_canon(
        tmp_path: Path) -> None:
    """The cell's own contract must pass the cell's keyword census (edge 8)."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    validator = load_validator_module()
    schema = json.loads((out / "05-contracts" / "02-canon.schema.json")
                        .read_text(encoding="utf-8"))
    canon = json.loads((out / "02-canon.json").read_text(encoding="utf-8"))
    assert validator.unsupported_keywords(schema) == []
    assert validator.check_against_schema(canon, schema, "$") == []


def test_canon_schema_accepts_recorded_facts_as_objects(tmp_path: Path) -> None:
    """Rework 2 of the v0.4.0 review: the cell records the numbers it states
    about priors as objects (number, context with the mark, section); the
    cell's contract accepts that form, refuses another, and the validator
    loads it."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    validator = load_validator_module()
    schema = json.loads((out / "05-contracts" / "02-canon.schema.json").read_text(encoding="utf-8"))
    canon = json.loads((out / "02-canon.json").read_text(encoding="utf-8"))
    assert canon["recorded facts"] == []
    canon["recorded facts"] = [{"number": "18", "context": "roles [prior:000-x]", "section": "1.1"}]
    assert validator.check_against_schema(canon, schema, "$") == []
    loaded = validator.json_recorded_facts(canon["recorded facts"])
    assert loaded[0].numbers == ["18"] and loaded[0].sections == ["1.1"]
    assert loaded[0].prior_id == "000-x"
    canon["recorded facts"] = ["18 roles"]
    assert validator.check_against_schema(canon, schema, "$") != []


def test_role_card_has_all_seven_fields_in_bold(tmp_path: Path) -> None:
    """The cards use `**Field:**`, the format the `p-card` gate reads."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    card = (out / "04-roles" / "writer.md").read_text(encoding="utf-8")
    for field in scaffold.ROLE_CARD_FIELDS:
        assert f"**{field}:**" in card


def test_role_card_links_to_the_canon(tmp_path: Path) -> None:
    """I6 of the panel: the reference is a markdown link, the form the
    `p-canon-link` gate reads — a code span alone links nothing. The v0.3.1
    review added the second half: the target has to resolve from the card's
    own folder (`04-roles/`), or the link leads nowhere either."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    card_path = out / "04-roles" / "writer.md"
    card = card_path.read_text(encoding="utf-8")
    target = "../02-canon.json"
    assert f"[02-canon.json]({target})" in card
    assert (card_path.parent / target).resolve() == (out / "02-canon.json").resolve()
    assert (card_path.parent / target).is_file()


def test_gates_template_carries_no_placeholder_gate(tmp_path: Path) -> None:
    """I6 of the panel: the `g-<name>` placeholder row made the first real
    run of a filled cell exit 2 on 'no implementation'; the table ships
    empty, with the instruction beside it."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    gates = (out / "06-gates.md").read_text(encoding="utf-8")
    assert "g-<name>" not in gates
    layout = json.loads((out / "layout.json").read_text(encoding="utf-8"))
    assert all(not gate.startswith("g-") for gate in layout["gates"])


def test_artifacts_template_schema_is_null_or_a_schema_path(tmp_path: Path) -> None:
    """I6 of the panel: the schema cell of the template record used to be
    the placeholder string '05-contracts/<artifact>.schema.json or null',
    which the validator's detection (ends with .schema.json) never sees."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    records = json.loads((out / "03-artifacts.json").read_text(encoding="utf-8"))
    for record in records:
        assert record["schema"] is None or record["schema"].endswith(".schema.json")


def test_validator_is_copied_into_the_cell(tmp_path: Path) -> None:
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    copy = out / "08-validator" / "validator.py"
    assert copy.exists()
    assert copy.read_text(encoding="utf-8") == scaffold.VALIDATOR_SRC.read_text(
        encoding="utf-8")


def test_sensitivity_script_and_contracts_are_copied_into_the_cell(tmp_path: Path) -> None:
    """CR3 and IM21 (v0.5.0): the cell gets the sensitivity script, a
    perturbation set as data, and the note and round contracts."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    for source, relative in scaffold.CORPUS_COPIES:
        assert (out / relative).read_text(encoding="utf-8") == \
            (scaffold.CORPUS_APPLICATION / source).read_text(encoding="utf-8")
    perts = json.loads((out / "08-validator" / "perturbations.json").read_text(encoding="utf-8"))
    assert [p["gate"] for p in perts] == ["p-terms", "p-anonymity", "p-card"]
    assert perts[2]["document"] == "04-roles/writer.md"
    layout = json.loads((out / "layout.json").read_text(encoding="utf-8"))
    assert layout["artifacts"]["perturbations"] == "08-validator/perturbations.json"


def test_the_contract_of_the_note_state_ledger_is_copied_into_the_cell(tmp_path: Path) -> None:
    """Regression (the review of v0.5.0): the cell got an empty
    state/notes-status.jsonl and no contract for it; the scaffold copies
    notes-status.schema.json next to the other contracts."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    copy = out / "05-contracts" / "notes-status.schema.json"
    source = scaffold.CORPUS_APPLICATION / "05-contracts" / "notes-status.schema.json"
    assert copy.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
    assert json.loads(copy.read_text(encoding="utf-8"))["contract_version"] == "1"
    assert (out / "state" / "notes-status.jsonl").read_text(encoding="utf-8") == ""


def test_size_ranges_table_has_a_separator_of_three_columns(tmp_path: Path) -> None:
    """K13 of the panel that reviewed v0.4.2: the header had three columns
    and the separator two."""
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    text = (out / "06-gates.md").read_text(encoding="utf-8")
    assert "| Document | Minimum | Maximum |\n| --- | --- | --- |\n" in text


def test_validator_copy_skips_gracefully_when_corpus_is_absent(
        tmp_path: Path, monkeypatch, capsys) -> None:
    """K10 of the panel that reviewed v0.4.2: copied alone, the skill creates
    the cell without the scripts, and the note says the cell has no
    validator until one is copied in (it used to say nothing was lost)."""
    monkeypatch.setattr(scaffold, "CORPUS_APPLICATION", tmp_path / "nowhere")
    out = tmp_path / "cell"
    scaffold.scaffold("Demo", ["writer"], out)
    assert not (out / "08-validator" / "validator.py").exists()
    assert not (out / "08-validator" / "sensitivity.py").exists()
    note = capsys.readouterr().out
    assert "note:" in note
    assert "has no validator or sensitivity test until you copy them in" in note


def test_rubric_uses_the_new_verdicts(tmp_path: Path) -> None:
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    rubric = (out / "07-rubric.md").read_text(encoding="utf-8")
    assert "accepted" in rubric
    assert "accepted with conditions" in rubric
    assert "acceptable" not in rubric


def test_state_files_are_empty(tmp_path: Path) -> None:
    out = tmp_path / "teamwork"
    scaffold.scaffold("Demo", ["writer"], out)
    assert (out / "state" / "notes.jsonl").read_text(encoding="utf-8") == ""
    assert (out / "state" / "round-record.jsonl").read_text(encoding="utf-8") == ""


def test_refuses_to_overwrite_non_empty_destination(tmp_path: Path) -> None:
    (tmp_path / "keep.txt").write_text("x", encoding="utf-8")
    with pytest.raises(scaffold.ScaffoldError):
        scaffold.scaffold("Demo", ["writer"], tmp_path)
    assert (tmp_path / "keep.txt").read_text(encoding="utf-8") == "x"


@pytest.mark.parametrize("roles", [[], ["Bad"], ["a", "a"]])
def test_rejects_invalid_roles(tmp_path: Path, roles: list[str]) -> None:
    with pytest.raises(scaffold.ScaffoldError):
        scaffold.scaffold("Demo", roles, tmp_path / "out")


def test_rejects_empty_target(tmp_path: Path) -> None:
    with pytest.raises(scaffold.ScaffoldError):
        scaffold.scaffold("  ", ["writer"], tmp_path / "out")


def test_main_creates_and_reports_exit_zero(tmp_path: Path, capsys) -> None:
    out = tmp_path / "cell"
    code = scaffold.main(["--target", "Demo", "--roles", "writer", "--out", str(out)])
    assert code == 0
    assert (out / "00-brief.md").exists()
    assert "00-brief.md" in capsys.readouterr().out


def test_main_refuses_and_reports_exit_two(tmp_path: Path, capsys) -> None:
    (tmp_path / "taken").mkdir()
    (tmp_path / "taken" / "x.txt").write_text("x", encoding="utf-8")
    code = scaffold.main(
        ["--target", "Demo", "--roles", "writer", "--out", str(tmp_path / "taken")]
    )
    assert code == 2
    assert "error" in capsys.readouterr().err


def test_main_turns_io_errors_into_exit_two(tmp_path: Path, capsys) -> None:
    """The documented contract: an OSError from the filesystem is exit 2."""
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    code = scaffold.main(
        ["--target", "Demo", "--roles", "writer", "--out", str(blocker / "cell")]
    )
    assert code == 2
    assert "error" in capsys.readouterr().err


def test_failed_build_leaves_no_partial_cell(tmp_path: Path, monkeypatch) -> None:
    """Regression (C14): a failure in the middle of the build must leave no
    partial cell at the destination and no staging folder behind."""
    original = scaffold.write_json_new

    def fail_on_layout(path: Path, data: object) -> None:
        if path.name == "layout.json":
            raise OSError("disk full while writing the layout")
        original(path, data)

    monkeypatch.setattr(scaffold, "write_json_new", fail_on_layout)
    out = tmp_path / "cell"
    with pytest.raises(OSError):
        scaffold.scaffold("Demo", ["writer"], out)
    assert not out.exists()
    assert list(tmp_path.iterdir()) == []


def test_successful_build_leaves_no_staging_folder(tmp_path: Path) -> None:
    """The staging folder is renamed into the destination and disappears."""
    out = tmp_path / "cell"
    scaffold.scaffold("Demo", ["writer"], out)
    assert (out / "layout.json").exists()
    assert [p.name for p in tmp_path.iterdir()] == ["cell"]


def test_empty_existing_destination_is_replaced_atomically(tmp_path: Path) -> None:
    """An existing EMPTY destination is replaced; nothing inside it is
    merged or kept (the rename swaps the folder in one step)."""
    out = tmp_path / "cell"
    out.mkdir()
    scaffold.scaffold("Demo", ["writer"], out)
    assert (out / "00-brief.md").exists()
    assert [p.name for p in tmp_path.iterdir()] == ["cell"]
