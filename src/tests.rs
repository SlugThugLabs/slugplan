use super::{Error, PLANNING_DIR, README, README_NAME, Report, ensure as ensure_planning};
use std::fs;

type TestResult = Result<(), String>;

#[track_caller]
fn ensure(cond: bool, what: &str) -> TestResult {
    if cond {
        Ok(())
    } else {
        Err(format!("{}: {what}", std::panic::Location::caller()))
    }
}

fn tmp() -> Result<tempfile::TempDir, String> {
    tempfile::tempdir().map_err(|e| format!("tempdir: {e}"))
}

#[test]
fn fresh_root_creates_dir_and_readme() -> TestResult {
    let t = tmp()?;
    let r = ensure_planning(t.path()).map_err(|e| format!("ensure: {e}"))?;
    ensure(
        r == Report {
            created_dir: true,
            created_readme: true,
        },
        "report both true",
    )?;
    let bytes = fs::read(t.path().join(PLANNING_DIR).join(README_NAME))
        .map_err(|e| format!("read readme: {e}"))?;
    ensure(bytes == README.as_bytes(), "readme bytes match")
}

#[test]
fn second_call_creates_nothing_and_keeps_readme() -> TestResult {
    let t = tmp()?;
    ensure_planning(t.path()).map_err(|e| format!("first: {e}"))?;
    let r = ensure_planning(t.path()).map_err(|e| format!("second: {e}"))?;
    ensure(
        r == Report {
            created_dir: false,
            created_readme: false,
        },
        "report both false",
    )?;
    let bytes = fs::read(t.path().join(PLANNING_DIR).join(README_NAME))
        .map_err(|e| format!("read readme: {e}"))?;
    ensure(bytes == README.as_bytes(), "readme unchanged")
}

#[test]
fn existing_user_readme_is_not_overwritten() -> TestResult {
    let t = tmp()?;
    let dir = t.path().join(PLANNING_DIR);
    fs::create_dir(&dir).map_err(|e| format!("mkdir: {e}"))?;
    let readme = dir.join(README_NAME);
    fs::write(&readme, "mine\n").map_err(|e| format!("write: {e}"))?;
    let r = ensure_planning(t.path()).map_err(|e| format!("ensure: {e}"))?;
    ensure(
        r == Report {
            created_dir: false,
            created_readme: false,
        },
        "report both false",
    )?;
    let bytes = fs::read(&readme).map_err(|e| format!("read: {e}"))?;
    ensure(bytes == b"mine\n", "user readme untouched")
}

#[test]
fn existing_dir_without_readme_gets_readme() -> TestResult {
    let t = tmp()?;
    fs::create_dir(t.path().join(PLANNING_DIR)).map_err(|e| format!("mkdir: {e}"))?;
    let r = ensure_planning(t.path()).map_err(|e| format!("ensure: {e}"))?;
    ensure(
        r == Report {
            created_dir: false,
            created_readme: true,
        },
        "report dir false readme true",
    )?;
    let bytes = fs::read(t.path().join(PLANNING_DIR).join(README_NAME))
        .map_err(|e| format!("read: {e}"))?;
    ensure(bytes == README.as_bytes(), "readme written")
}

#[test]
fn planning_as_regular_file_is_not_a_directory_error() -> TestResult {
    let t = tmp()?;
    let p = t.path().join(PLANNING_DIR);
    fs::write(&p, "file").map_err(|e| format!("write: {e}"))?;
    match ensure_planning(t.path()) {
        Err(Error::NotADirectory { path }) => ensure(path == p, "path names .planning")?,
        other => return Err(format!("expected NotADirectory, got {other:?}")),
    }
    let bytes = fs::read(&p).map_err(|e| format!("read: {e}"))?;
    ensure(bytes == b"file", "file untouched")
}

#[test]
fn missing_root_is_root_error_and_not_created() -> TestResult {
    let t = tmp()?;
    let root = t.path().join("nope");
    match ensure_planning(&root) {
        Err(Error::Root { path, .. }) => ensure(path == root, "path names root")?,
        other => return Err(format!("expected Root, got {other:?}")),
    }
    ensure(!root.exists(), "root not created")
}

#[test]
fn root_that_is_a_file_is_root_error() -> TestResult {
    let t = tmp()?;
    let root = t.path().join("f");
    fs::write(&root, "x").map_err(|e| format!("write: {e}"))?;
    match ensure_planning(&root) {
        Err(Error::Root { source, .. }) => ensure(
            source.kind() == std::io::ErrorKind::NotADirectory,
            "kind NotADirectory",
        ),
        other => Err(format!("expected Root, got {other:?}")),
    }
}

#[test]
fn readme_as_directory_is_left_alone() -> TestResult {
    let t = tmp()?;
    let readme = t.path().join(PLANNING_DIR).join(README_NAME);
    fs::create_dir_all(&readme).map_err(|e| format!("mkdir: {e}"))?;
    let r = ensure_planning(t.path()).map_err(|e| format!("ensure: {e}"))?;
    ensure(!r.created_readme, "created_readme false")?;
    ensure(readme.is_dir(), "still a directory")
}

#[test]
fn shipped_readme_text_points_to_docs() -> TestResult {
    ensure(README.starts_with("# .planning\n"), "starts with heading")?;
    ensure(README.contains("docs/"), "mentions docs/")
}
