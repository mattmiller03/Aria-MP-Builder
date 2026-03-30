# Commands to Run — Debug adapter 500 error

Run these in order on the Photon server.

## Step 1: Build the image manually so it doesn't get pruned

```bash
cd /home/vropsssh/Aria-MP-Builder/Azure
sudo docker build -t azuregovcloud-test:1.0.0 .
```

## Step 2: Check where adapter.py is inside the container

```bash
sudo docker run --rm azuregovcloud-test:1.0.0 find / -name "adapter.py" 2>/dev/null
```

## Step 3: Try importing the adapter

```bash
sudo docker run --rm --workdir /home/aria-ops-adapter-user/src/app azuregovcloud-test:1.0.0 python3 -c "from adapter import get_adapter_definition; print('OK')"
```

## Step 4: If Step 3 fails, try the alternate path from Step 2

```bash
sudo docker run --rm --workdir /adapter azuregovcloud-test:1.0.0 python3 -c "from adapter import get_adapter_definition; print('OK')"
```

## Step 5: Check what pip packages are in the container

```bash
sudo docker run --rm azuregovcloud-test:1.0.0 pip list
```

## Step 6: Paste all output into ErrorFile.txt
