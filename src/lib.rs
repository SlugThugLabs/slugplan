//! Creates a project's `.planning/` folder and its `README.md` the same way
//! in every slug tool.
//!
//! Anything that already exists is left untouched: an existing README is
//! never overwritten or read.
//!
//! ```no_run
//! use std::path::Path;
//!
//! fn main() -> Result<(), slugplan::Error> {
//!     slugplan::ensure(Path::new("."))?;
//!     Ok(())
//! }
//! ```

use std::fmt;
use std::fs::{self, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};

/// Name of the planning folder inside a project root.
pub const PLANNING_DIR: &str = ".planning";
/// Name of the README file inside the planning folder.
pub const README_NAME: &str = "README.md";
/// Text written to a newly created planning README.
pub const README: &str = include_str!("planning_readme.md");

/// What [`ensure`] created.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Report {
    /// `.planning/` was created by this call.
    pub created_dir: bool,
    /// `.planning/README.md` was created by this call.
    pub created_readme: bool,
}

/// Why [`ensure`] failed.
#[derive(Debug)]
#[non_exhaustive]
pub enum Error {
    /// `root` does not exist or is not a directory. slugplan never creates the project root.
    Root {
        /// The project root given to [`ensure`].
        path: PathBuf,
        /// The underlying error.
        source: io::Error,
    },
    /// `.planning` exists but is not a directory.
    NotADirectory {
        /// Path of the `.planning` entry.
        path: PathBuf,
    },
    /// Creating `.planning` failed.
    CreateDir {
        /// Path of the `.planning` entry.
        path: PathBuf,
        /// The underlying error.
        source: io::Error,
    },
    /// Creating or writing the README failed.
    WriteReadme {
        /// Path of the README.
        path: PathBuf,
        /// The underlying error.
        source: io::Error,
        /// The error from removing the partial file, if that failed too.
        cleanup: Option<io::Error>,
    },
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Root { path, source } => write!(
                f,
                "cannot use {} as the project root: {source}",
                path.display()
            ),
            Self::NotADirectory { path } => {
                write!(f, "{} exists but is not a directory", path.display())
            }
            Self::CreateDir { path, source } => {
                write!(f, "could not create directory {}: {source}", path.display())
            }
            Self::WriteReadme {
                path,
                source,
                cleanup,
            } => {
                write!(f, "could not write {}: {source}", path.display())?;
                if let Some(cleanup) = cleanup {
                    write!(f, " (removing the partial file also failed: {cleanup})")?;
                }
                Ok(())
            }
        }
    }
}

impl std::error::Error for Error {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::Root { source, .. }
            | Self::CreateDir { source, .. }
            | Self::WriteReadme { source, .. } => Some(source),
            Self::NotADirectory { .. } => None,
        }
    }
}

/// Makes sure `<root>/.planning/` and `<root>/.planning/README.md` exist.
///
/// Existing entries are never modified: an existing README is not read or
/// overwritten. `root` itself is never created.
///
/// # Errors
///
/// Returns [`Error::Root`] if `root` is missing or not a directory,
/// [`Error::NotADirectory`] if `.planning` exists as a non-directory,
/// [`Error::CreateDir`] if `.planning` cannot be created, and
/// [`Error::WriteReadme`] if the README cannot be created or written (the
/// partial file is removed).
pub fn ensure(root: &Path) -> Result<Report, Error> {
    let root_meta = fs::metadata(root).map_err(|source| Error::Root {
        path: root.to_path_buf(),
        source,
    })?;
    if !root_meta.is_dir() {
        return Err(Error::Root {
            path: root.to_path_buf(),
            source: io::Error::new(io::ErrorKind::NotADirectory, "not a directory"),
        });
    }

    let dir = root.join(PLANNING_DIR);
    let created_dir = create_planning_dir(&dir)?;
    let created_readme = create_readme(&dir.join(README_NAME))?;
    Ok(Report {
        created_dir,
        created_readme,
    })
}

fn create_planning_dir(dir: &Path) -> Result<bool, Error> {
    match fs::create_dir(dir) {
        Ok(()) => Ok(true),
        Err(e) if e.kind() == io::ErrorKind::AlreadyExists => match fs::metadata(dir) {
            Ok(meta) if meta.is_dir() => Ok(false),
            Ok(_) => Err(Error::NotADirectory {
                path: dir.to_path_buf(),
            }),
            Err(source) => Err(Error::CreateDir {
                path: dir.to_path_buf(),
                source,
            }),
        },
        Err(source) => Err(Error::CreateDir {
            path: dir.to_path_buf(),
            source,
        }),
    }
}

fn create_readme(path: &Path) -> Result<bool, Error> {
    let mut file = match OpenOptions::new().write(true).create_new(true).open(path) {
        Ok(file) => file,
        Err(e) if e.kind() == io::ErrorKind::AlreadyExists => return Ok(false),
        Err(source) => {
            return Err(Error::WriteReadme {
                path: path.to_path_buf(),
                source,
                cleanup: None,
            });
        }
    };
    let written = file
        .write_all(README.as_bytes())
        .and_then(|()| file.sync_all());
    match written {
        Ok(()) => Ok(true),
        Err(source) => {
            drop(file);
            let cleanup = fs::remove_file(path).err();
            Err(Error::WriteReadme {
                path: path.to_path_buf(),
                source,
                cleanup,
            })
        }
    }
}

#[cfg(test)]
mod tests;
