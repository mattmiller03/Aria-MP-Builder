# Fix Package Versions

## On Windows PC — download correct versions

```powershell
pip download "sen==0.6.2" -d C:\aria-wheels --no-deps
pip download "validators==0.20.0" -d C:\aria-wheels --no-deps
pip download "xmlschema==2.4.0" -d C:\aria-wheels --no-deps
pip download "elementpath==4.4.0" -d C:\aria-wheels --no-deps
pip download "setuptools==78.1.1" -d C:\aria-wheels --no-deps
```

## Transfer to server

```powershell
scp C:\aria-wheels\sen-0.6.2* user@<SERVER>:/opt/aria/wheels/
scp C:\aria-wheels\validators-0.20.0* user@<SERVER>:/opt/aria/wheels/
scp C:\aria-wheels\xmlschema-2.4.0* user@<SERVER>:/opt/aria/wheels/
scp C:\aria-wheels\elementpath-4.4.0* user@<SERVER>:/opt/aria/wheels/
scp C:\aria-wheels\setuptools-78.1.1* user@<SERVER>:/opt/aria/wheels/
```

## On Photon server — install correct versions

```bash
pip3.12 install --force-reinstall --no-index --find-links /opt/aria/wheels "sen==0.6.2"
pip3.12 install --force-reinstall --no-index --find-links /opt/aria/wheels "validators==0.20.0"
pip3.12 install --force-reinstall --no-index --find-links /opt/aria/wheels "xmlschema==2.4.0"
pip3.12 install --force-reinstall --no-index --find-links /opt/aria/wheels "setuptools==78.1.1"
```

## Verify

```bash
mp-build --version
mp-test --version
```



sudo docker rmi azuregovcloud-test:1.0.0 2>/dev/null
sudo docker rmi $(sudo docker images -q --filter "label=mp-test") 2>/dev/null

# Verify latest files have correct permissions and line endings
find /opt/aria/Aria-MP-Builder/Azure -name "*.py" -exec sed -i 's/\r$//' {} +
sed -i 's/\r$//' /opt/aria/Aria-MP-Builder/Azure/Dockerfile
sed -i 's/\r$//' /opt/aria/Aria-MP-Builder/Azure/commands.cfg
chmod -R 755 /opt/aria/Aria-MP-Builder/Azure/

# Retry
cd /opt/aria/Aria-MP-Builder/Azure
sudo mp-test --port 8080