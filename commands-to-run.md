# Commands to Run — SDK Offline Install

## On Windows PC (internet connected)

Download the missing C extension wheels for Linux Python 3.11:

```powershell
pip download "lxml>=4.9.2,<5.0.0" --python-version 3.11 --platform manylinux2014_x86_64 --only-binary=:all: -d C:\aria-wheels
pip download "Pillow>=9.3,<11.0" --python-version 3.11 --platform manylinux2014_x86_64 --only-binary=:all: -d C:\aria-wheels
pip download "validators>=0.20.0,<0.21.0" --python-version 3.11 --platform manylinux2014_x86_64 --only-binary=:all: -d C:\aria-wheels
pip download "pyyaml" --python-version 3.11 --platform manylinux2014_x86_64 --only-binary=:all: -d C:\aria-wheels
```

Transfer updated wheels folder to Photon server:

```powershell
scp -r C:\aria-wheels vropsssh@<photon-server>:/home/vropsssh/Aria-MP-Builder/aria-wheels
```

## On Photon Server (air-gapped)

```bash
cd /home/vropsssh/Aria-MP-Builder

pip install --no-index --find-links /home/vropsssh/Aria-MP-Builder/aria-wheels vmware-aria-operations-integration-sdk

pip install --no-index --find-links /home/vropsssh/Aria-MP-Builder/aria-wheels vmware-aria-operations-integration-sdk-lib

pip install --no-index --find-links /home/vropsssh/Aria-MP-Builder/aria-wheels requests
```

## Verify

```bash
mp-build --version
mp-test --version
pip show pillow
pip show lxml
pip show vmware-aria-operations-integration-sdk
```

## Run Preflight Check

```bash
sed -i 's/\r$//' Azure/preflight_check.sh
chmod +x Azure/preflight_check.sh
./Azure/preflight_check.sh
```
