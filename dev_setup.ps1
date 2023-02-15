echo "Setting up development environment..."

echo "...Removing previous virtual environment"
$venvFolder = ".\.venv"
if (Test-Path $venvFolder) {
    Remove-Item $venvFolder -Recurse -Force
}

echo "...Getting Python version from .\pyproject.toml"
try {
    $pythonVersion = (select-string -path .\pyproject.toml -pattern 'python *= *"\^(\d+\.\d+\.?\d*)"').matches.groups[1].value
} catch {
    echo "Failed to get Python version from pyproject.toml"
    exit 1
}
echo "...Found Python $pythonVersion as required version"

echo "Installing Python $pythonVersion"
pyenv update
try {
    pyenv install $pythonVersion
} catch {
    echo "Failed to install Python $pythonVersion"
    exit 1
}
pyenv local $pythonVersion
echo "...Creating a new virtual environment at $venvFolder"
python -m venv $venvFolder

echo "...Installing dependencies"
.venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install poetry
python -m poetry lock
python -m poetry install
echo "...Done!"
echo "Setup complete."